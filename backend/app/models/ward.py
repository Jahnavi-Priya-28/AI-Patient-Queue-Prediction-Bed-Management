from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Ward(Base):
    __tablename__ = "wards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    ward_type: Mapped[str] = mapped_column(String(50), nullable=False) # General, ICU, Surgical, Pediatric
    floor: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    beds = relationship("Bed", back_populates="ward", cascade="all, delete-orphan")
