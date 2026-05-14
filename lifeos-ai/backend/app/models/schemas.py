"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# ============ Mood Endpoints ============

class MoodRequest(BaseModel):
    user_id: int
    text: str

class MoodResponse(BaseModel):
    mood: str
    stress_score: float
    energy_score: float
    confidence: float
    reasoning: str

# ============ User Task Schemas ============

class UserTaskInput(BaseModel):
    """A task the user wants to accomplish today"""
    title: str
    importance: int = Field(default=3, ge=1, le=5, description="1=low, 5=critical")
    estimated_duration: int = Field(default=30, description="Duration in minutes")

class UserTaskResponse(BaseModel):
    id: int
    title: str
    importance: int
    estimated_duration: int
    status: str           # pending / completed / skipped
    ai_included: bool
    ai_suggestion: Optional[str] = None
    ai_priority: float
    date: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserTaskUpdateRequest(BaseModel):
    status: str  # completed / skipped / pending

# ============ Daily Plan Endpoints ============

class DailyPlanRequest(BaseModel):
    user_id: int
    date: str = Field(default_factory=lambda: date.today().isoformat())
    busy_slots: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="List of busy time blocks e.g. [{\"start\": \"09:00\", \"end\": \"10:30\", \"label\": \"Team meeting\"}]"
    )
    user_tasks: Optional[List[UserTaskInput]] = Field(
        default=None,
        description="Tasks the user wants to accomplish today"
    )

class AgentProposal(BaseModel):
    agent: str
    proposal: str
    priority: float
    confidence: float
    reasoning: str

class DailyPlanResponse(BaseModel):
    plan_id: Optional[int] = None
    plan: List[Dict[str, Any]]
    agent_proposals: List[AgentProposal]
    explanation: str
    created_at: datetime
    saved_tasks: Optional[List[UserTaskResponse]] = None

# ============ Feedback Endpoints ============

class FeedbackRequest(BaseModel):
    user_id: int
    plan_id: int
    rating: str  # 'up', 'down', 'neutral'
    completed_tasks: List[str]
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str

# ============ History Endpoints ============

class MoodLog(BaseModel):
    id: int
    mood: str
    stress_score: float
    energy_score: float
    created_at: datetime

class PlanSummary(BaseModel):
    id: int
    plan: List[Dict[str, Any]]
    explanation: str
    created_at: datetime

class HistoryResponse(BaseModel):
    mood_logs: List[MoodLog]
    plans: List[PlanSummary]
    total_plans: int
    task_summaries: Optional[List[Dict[str, Any]]] = None

# ============ Error Response ============

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
