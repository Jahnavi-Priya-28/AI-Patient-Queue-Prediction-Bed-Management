from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
):
    """
    Persist security or operational audit event into PostgreSQL audit_logs table.
    """
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata,
        ip_address=ip_address,
    )
    db.add(log_entry)
    db.commit()
