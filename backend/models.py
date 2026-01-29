from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import uuid

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    parent_company: Optional[str] = None
    business_partner: Optional[str] = None
    budget: Optional[float] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: uuid.UUID
    current_progress: float = 0.0
    actual_spend: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

class InitialAnalysisResponse(BaseModel):
    analysis: str
    project_id: uuid.UUID
