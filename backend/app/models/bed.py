from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import BedStatus


class Bed(Base):
    __tablename__ = "beds"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id", ondelete="CASCADE"), nullable=False, index=True)
    bed_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[BedStatus] = mapped_column(SQLEnum(BedStatus), default=BedStatus.AVAILABLE, nullable=False, index=True)
    current_patient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    ward = relationship("Ward", back_populates="beds")
    current_patient = relationship("Patient", back_populates="beds")
