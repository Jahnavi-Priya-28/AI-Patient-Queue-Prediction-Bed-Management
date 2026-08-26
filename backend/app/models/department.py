from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    doctors = relationship("Doctor", back_populates="department")
    appointments = relationship("Appointment", back_populates="department")
    queue_entries = relationship("QueueEntry", back_populates="department")
