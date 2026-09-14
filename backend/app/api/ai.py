from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIResponse
from app.services.ai_service import chat, operations_summary, queue_insights, capacity_insights

router = APIRouter(prefix="/ai", tags=["GenAI Assistant"])


@router.post("/chat", response_model=AIResponse)
def ai_chat(req: AIChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat(db, current_user, req.message)


@router.post("/operations-summary", response_model=AIResponse)
def ai_operations_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return operations_summary(db, current_user)


@router.post("/queue-insights", response_model=AIResponse)
def ai_queue_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return queue_insights(db, current_user)


@router.post("/capacity-insights", response_model=AIResponse)
def ai_capacity_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return capacity_insights(db, current_user)
