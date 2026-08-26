from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import UserRole, BedStatus, PriorityLevel, AppointmentStatus, QueueStatus


# Department Schemas
class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: Optional[str] = None
    active: bool


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None


# Doctor Schemas
class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    department_id: int
    employee_number: str
    specialization: Optional[str] = None
    consultation_duration: int
    is_available: bool
    department: Optional[DepartmentResponse] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Patient Schemas
class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    patient_number: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


# Appointment Schemas
class AppointmentCreate(BaseModel):
    doctor_id: int
    department_id: int
    appointment_date: date
    appointment_time: time
    appointment_type: str = "WALK_IN"
    priority: PriorityLevel = PriorityLevel.NORMAL
    reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    department_id: int
    appointment_date: date
    appointment_time: time
    appointment_type: str
    priority: PriorityLevel
    status: AppointmentStatus
    reason: Optional[str] = None
    created_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None
    department: Optional[DepartmentResponse] = None


# Queue Schemas
class CheckInRequest(BaseModel):
    appointment_id: int
    priority: Optional[PriorityLevel] = None


class QueueEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    patient_id: int
    doctor_id: int
    department_id: int
    token_number: str
    queue_date: date
    priority: PriorityLevel
    status: QueueStatus
    check_in_time: datetime
    called_time: Optional[datetime] = None
    consultation_start: Optional[datetime] = None
    consultation_end: Optional[datetime] = None
    predicted_wait_minutes: Optional[float] = None
    actual_wait_minutes: Optional[float] = None
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None
    department: Optional[DepartmentResponse] = None


# Ward & Bed Schemas
class WardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ward_type: str
    floor: int
    capacity: int
    active: bool


class BedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ward_id: int
    bed_number: str
    status: BedStatus
    current_patient_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    ward: Optional[WardResponse] = None
    current_patient: Optional[PatientResponse] = None


class AssignBedRequest(BaseModel):
    patient_id: int


class TransferBedRequest(BaseModel):
    new_bed_id: int


# Notification Schema
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


# Audit Log Schema
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata_json: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime


# Analytics / Dashboard Schemas
class DashboardMetricsResponse(BaseModel):
    total_patients: int
    today_appointments: int
    waiting_patients: int
    active_doctors: int
    available_beds: int
    occupied_beds: int
    avg_wait_minutes: float
    completed_consultations_today: int
    queue_by_department: List[dict]
    bed_occupancy_by_ward: List[dict]


# ML Prediction & Forecast Schemas
class PredictWaitingTimeRequest(BaseModel):
    queue_entry_id: int


class PredictWaitingTimeResponse(BaseModel):
    queue_entry_id: int
    predicted_wait_minutes: float
    confidence_interval: str = "±3.5 mins"
    model_version: str = "v1.0.0-xgboost"


class ForecastDemandRequest(BaseModel):
    department_id: int
    horizon_hours: int = Field(default=6, description="1, 6, 12, or 24 hours ahead")


class ForecastDemandResponse(BaseModel):
    department_id: int
    horizon_hours: int
    predicted_arrivals: int
    predicted_queue_depth: int
    recommended_doctor_capacity: int
    forecast_sequence: List[dict]
