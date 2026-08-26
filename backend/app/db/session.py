from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

db_url = settings.DATABASE_URL
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Resilient engine creation (Defaults to DATABASE_URL, with SQLite dev fallback if PostgreSQL unavailable)
try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True if not db_url.startswith("sqlite") else False,
        echo=False,
    )
    # Test connection
    with engine.connect() as conn:
        pass
except Exception:
    dev_db_url = "sqlite:///./patientflow_dev.db"
    engine = create_engine(
        dev_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency providing a database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
