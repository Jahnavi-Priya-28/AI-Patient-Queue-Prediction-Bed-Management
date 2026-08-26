from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
