import json
import logging
import time
from datetime import date
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.bed import Bed
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.enums import BedStatus, QueueStatus, UserRole
from app.models.patient import Patient
from app.models.queue_entry import QueueEntry
from app.models.user import User
from app.models.ward import Ward
from app.schemas.ai import AIResponse

logger = logging.getLogger(__name__)

try:
    from google import genai
except ImportError:
    genai = None


SAFE_SYSTEM_PROMPT = """You are PatientFlow AI, an operational assistant. Use only the supplied authorized facts. Never invent numbers, records, appointments, beds, staff, or actions. Never diagnose or prescribe. If data is unavailable, say so. Return valid JSON with exactly these fields: summary (string), key_findings (array of strings), recommendations (array of strings), warnings (array of strings), data_sources (array of strings). Keep the response concise and practical."""


def _base_response(summary: str, sources: list[str], warning: str | None = None) -> AIResponse:
    return AIResponse(summary=summary, warnings=[warning] if warning else [], data_sources=sources, model=settings.GEMINI_MODEL, available=False if warning else True)


def _patient_context(db: Session, user: User) -> dict[str, Any]:
    patient = user.patient_profile
    if not patient:
        return {"role": "PATIENT", "data": "Patient profile unavailable."}
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient.id, Appointment.organization_id == user.organization_id).order_by(Appointment.appointment_date.desc()).limit(10).all()
    queue = db.query(QueueEntry).filter(QueueEntry.patient_id == patient.id, QueueEntry.organization_id == user.organization_id, QueueEntry.queue_date == date.today()).all()
    return {"role": "PATIENT", "appointments": [{"date": str(a.appointment_date), "time": str(a.appointment_time), "status": a.status.value, "department_id": a.department_id} for a in appointments], "queue": [{"token": q.token_number, "status": q.status.value, "predicted_wait_minutes": q.predicted_wait_minutes} for q in queue]}


def _staff_context(db: Session, user: User) -> dict[str, Any]:
    if user.role == UserRole.DOCTOR and user.doctor_profile:
        appointments = db.query(Appointment).filter(Appointment.doctor_id == user.doctor_profile.id, Appointment.organization_id == user.organization_id, Appointment.appointment_date == date.today()).all()
        queue = db.query(QueueEntry).filter(QueueEntry.doctor_id == user.doctor_profile.id, QueueEntry.organization_id == user.organization_id, QueueEntry.queue_date == date.today()).all()
        return {"role": user.role.value, "today_appointments": len(appointments), "queue": [{"status": q.status.value, "predicted_wait_minutes": q.predicted_wait_minutes} for q in queue]}

    org_id = user.organization_id
    metrics = {
        "patients": db.query(func.count(Patient.id)).filter(Patient.organization_id == org_id).scalar() or 0,
        "today_appointments": db.query(func.count(Appointment.id)).filter(Appointment.organization_id == org_id, Appointment.appointment_date == date.today()).scalar() or 0,
        "waiting_queue": db.query(func.count(QueueEntry.id)).filter(QueueEntry.organization_id == org_id, QueueEntry.queue_date == date.today(), QueueEntry.status == QueueStatus.WAITING).scalar() or 0,
        "active_doctors": db.query(func.count(Doctor.id)).filter(Doctor.organization_id == org_id, Doctor.is_available == True).scalar() or 0,
        "available_beds": db.query(func.count(Bed.id)).join(Ward).filter(Ward.organization_id == org_id, Bed.status == BedStatus.AVAILABLE).scalar() or 0,
        "occupied_beds": db.query(func.count(Bed.id)).join(Ward).filter(Ward.organization_id == org_id, Bed.status == BedStatus.OCCUPIED).scalar() or 0,
    }
    departments = db.query(Department.name, func.count(QueueEntry.id)).outerjoin(QueueEntry, (QueueEntry.department_id == Department.id) & (QueueEntry.queue_date == date.today()) & (QueueEntry.organization_id == org_id)).filter(Department.organization_id == org_id).group_by(Department.name).all()
    return {"role": user.role.value, "organization_id": org_id, "metrics": metrics, "department_queue": [{"department": name, "waiting": count} for name, count in departments]}


def authorized_context(db: Session, user: User) -> dict[str, Any]:
    return _patient_context(db, user) if user.role == UserRole.PATIENT else _staff_context(db, user)


def _fallback(context: dict[str, Any], feature: str) -> AIResponse:
    if context.get("role") == "PATIENT":
        return _base_response("AI insights are temporarily unavailable. You can still use your appointment and queue information in PatientFlow.", ["authorized patient appointments", "authorized patient queue"], "Gemini is not configured or is temporarily unavailable.")
    return _base_response("AI insights are temporarily unavailable. You can still use all standard PatientFlow operational features.", [feature], "Gemini is not configured or is temporarily unavailable.")


def _call_gemini(context: dict[str, Any], user_message: str, feature: str) -> AIResponse:
    if not settings.GEMINI_API_KEY or genai is None:
        return _fallback(context, feature)
    started = time.perf_counter()
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = f"{SAFE_SYSTEM_PROMPT}\nFeature: {feature}\nAuthorized context:\n{json.dumps(context, default=str)}\nUser request: {user_message}"
        response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json\n", "", 1).strip()
        parsed = AIResponse.model_validate_json(raw)
        parsed.model = settings.GEMINI_MODEL
        parsed.available = True
        logger.info("AI feature=%s user_id=%s role=%s organization_id=%s success=true latency_ms=%d", feature, context.get("user_id", "unknown"), context.get("role"), context.get("organization_id"), int((time.perf_counter() - started) * 1000))
        return parsed
    except Exception as exc:
        logger.warning("AI feature=%s success=false error_type=%s", feature, type(exc).__name__)
        return _fallback(context, feature)


def chat(db: Session, user: User, message: str) -> AIResponse:
    context = authorized_context(db, user)
    return _call_gemini(context, message, "role-aware chat")


def operations_summary(db: Session, user: User) -> AIResponse:
    if user.role not in {UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="You do not have permission to access operational summaries")
    return _call_gemini(db_context := authorized_context(db, user), "Summarize overall status, bottlenecks, queue, capacity, forecast risks, and recommended actions.", "operations summary")


def queue_insights(db: Session, user: User) -> AIResponse:
    if user.role not in {UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="You do not have permission to access queue insights")
    return _call_gemini(authorized_context(db, user), "Explain the current queue bottleneck and workload imbalance using only the supplied facts.", "queue insights")


def capacity_insights(db: Session, user: User) -> AIResponse:
    if user.role not in {UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="You do not have permission to access capacity insights")
    return _call_gemini(authorized_context(db, user), "Explain current bed and operational capacity risks using only the supplied facts.", "capacity insights")
