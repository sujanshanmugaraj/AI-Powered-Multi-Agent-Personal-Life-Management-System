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

# ============ Daily Plan Endpoints ============

class DailyPlanRequest(BaseModel):
    user_id: int
    date: str = Field(default_factory=lambda: date.today().isoformat())

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

# ============ Error Response ============

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
