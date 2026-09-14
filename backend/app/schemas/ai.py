from typing import List
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class AIResponse(BaseModel):
    summary: str
    key_findings: List[str] = []
    recommendations: List[str] = []
    warnings: List[str] = []
    data_sources: List[str] = []
    model: str = "gemini-2.5-flash"
    available: bool = True
