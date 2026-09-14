from sqlalchemy import String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Ward(Base):
    __tablename__ = "wards"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_ward_org_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    ward_type: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization = relationship("Organization", back_populates="wards")
    beds = relationship("Bed", back_populates="ward", cascade="all, delete-orphan")
