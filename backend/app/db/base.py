from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.x ORM models.
    """
    pass


# Import models so Base.metadata is fully populated whenever Base is imported
from app.models import organization, user, patient, doctor, department, ward, bed, appointment, queue_entry, notification, audit_log, model_prediction, system_setting  # noqa: F401
