from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # XGBoost_WaitTime or LSTM_Demand
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    queue_entry_id: Mapped[Optional[int]] = mapped_column(ForeignKey("queue_entries.id", ondelete="CASCADE"), nullable=True)
    prediction_value: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_unit: Mapped[str] = mapped_column(String(20), default="minutes", nullable=False)
    confidence_or_metric: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    queue_entry = relationship("QueueEntry", back_populates="predictions")
