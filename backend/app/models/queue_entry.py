from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Date, Float, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import QueueStatus, PriorityLevel


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    token_number: Mapped[str] = mapped_column(String(20), nullable=False)
    queue_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False, index=True)
    priority: Mapped[PriorityLevel] = mapped_column(SQLEnum(PriorityLevel), default=PriorityLevel.NORMAL, nullable=False)
    status: Mapped[QueueStatus] = mapped_column(SQLEnum(QueueStatus), default=QueueStatus.WAITING, nullable=False, index=True)
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    called_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    predicted_wait_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_wait_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # consultation_start - check_in_time
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    appointment = relationship("Appointment", back_populates="queue_entry")
    patient = relationship("Patient", back_populates="queue_entries")
    doctor = relationship("Doctor", back_populates="queue_entries")
    department = relationship("Department", back_populates="queue_entries")
    predictions = relationship("ModelPrediction", back_populates="queue_entry")

