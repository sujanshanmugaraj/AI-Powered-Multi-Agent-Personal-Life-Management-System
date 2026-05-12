"""
API router for main endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.schemas import (
    MoodRequest, MoodResponse,
    DailyPlanRequest, DailyPlanResponse,
    FeedbackRequest, FeedbackResponse,
    HistoryResponse
)
from app.models.database import User, MoodLog, DailyPlan, Feedback, AgentAction, BanditReward
from app.workflows.daily_planner import DailyPlannerGraph
from app.learning.bandit_learning import AdaptiveRecommender, BanditLearner
from datetime import datetime, timedelta, date as date_type
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize workflow (in production, use dependency injection)
workflow = None
recommender = None

def get_workflow():
    """Get or create workflow instance"""
    global workflow
    if workflow is None:
        workflow = DailyPlannerGraph()
    return workflow

def get_recommender():
    """Get or create recommender instance"""
    global recommender
    if recommender is None:
        bandit = BanditLearner(epsilon=0.1)
        recommender = AdaptiveRecommender(bandit)
    return recommender

# ============ User Management ============

class UserCreateRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/users", response_model=UserResponse)
async def create_or_get_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new user or get existing user by email
    
    Args:
        request: UserCreateRequest with name and email
    
    Returns:
        UserResponse with user details
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return existing_user
        
        # Create new user
        new_user = User(
            name=request.name,
            email=request.email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Created new user: {new_user.email} (ID: {new_user.id})")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Mood Analysis ============

@router.post("/mood", response_model=MoodResponse)
async def analyze_mood(request: MoodRequest, db: Session = Depends(get_db)):
    """
    Analyze user's mood from text input and save to database.
    Uses the full keyword bank (slang, emojis, Hindi/Hinglish).
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build memory system so mood agent can compare to historical trends
        from app.memory.memory_system import MemorySystem
        from app.agents.mood_agent import MoodAgent
        memory = MemorySystem(db=db)
        mood_agent = MoodAgent(memory_system=memory)

        state = {
            "user_id":   request.user_id,
            "user_text": request.text,
            "mood_data": {},
        }
        mood_proposal = await mood_agent.generate_proposal(state)

        mood_data = MoodResponse(
            mood        =mood_proposal.get("mood",         "neutral"),
            stress_score=mood_proposal.get("stress_score", 0.5),
            energy_score=mood_proposal.get("energy_score", 0.5),
            confidence  =mood_proposal.get("confidence",   0.8),
            reasoning   =mood_proposal.get("reasoning",    ""),
        )

        # Save mood log to database
        mood_log = MoodLog(
            user_id     =request.user_id,
            mood        =mood_data.mood,
            stress_score=mood_data.stress_score,
            energy_score=mood_data.energy_score,
            raw_text    =request.text,
        )
        db.add(mood_log)
        db.commit()

        logger.info(f"Mood logged for user {request.user_id}: {mood_data.mood} "
                    f"(stress={mood_data.stress_score}, energy={mood_data.energy_score})")
        return mood_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing mood: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mood-logs")
async def get_mood_logs(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """
    Get user's mood logs for the past N days
    
    Args:
        user_id: User ID
        days: Number of days to retrieve (default: 7)
    
    Returns:
        List of mood data entries
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query mood logs
        mood_logs = db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.created_at >= start_date
        ).order_by(desc(MoodLog.created_at)).all()
        
        return [
            {
                "id": log.id,
                "mood": log.mood,
                "stress_score": log.stress_score,
                "energy_score": log.energy_score,
                "created_at": log.created_at.isoformat()
            }
            for log in mood_logs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mood logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily-plan", response_model=DailyPlanResponse)
async def generate_daily_plan(request: DailyPlanRequest, db: Session = Depends(get_db)):
    """
    Generate personalized daily plan for user and save to database

    Args:
        request: DailyPlanRequest with user_id and date

    Returns:
        DailyPlanResponse with final plan and agent breakdown
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        workflow = get_workflow()

        # Get user's latest mood
        latest_mood = db.query(MoodLog).filter(
            MoodLog.user_id == request.user_id
        ).order_by(desc(MoodLog.created_at)).first()

        user_text = latest_mood.raw_text if latest_mood else "feeling neutral today"

        # Execute full workflow — pass db so agents get real history
        result = await workflow.execute(
            user_id=request.user_id,
            user_text=user_text,
            date=request.date,
            db=db
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))

        # ── Convert agent_proposals dict → list ──────────────────────────────
        # The workflow returns a dict keyed by agent name:
        #   {"mood": {...}, "health": {...}, ...}
        # We need a flat list of dicts with required fields.
        raw_proposals = result.get("agent_proposals", {})
        proposals_list: List[Dict[str, Any]] = []

        if isinstance(raw_proposals, dict):
            for agent_name, prop in raw_proposals.items():
                if not isinstance(prop, dict):
                    continue
                proposals_list.append({
                    "agent":      prop.get("agent", agent_name),
                    "proposal":   str(prop.get("proposal", "")),
                    "priority":   float(prop.get("priority", 0.5)),
                    "confidence": float(prop.get("confidence", 0.5)),
                    "reasoning":  str(prop.get("reasoning", "")),
                })
        elif isinstance(raw_proposals, list):
            proposals_list = [
                {
                    "agent":      p.get("agent", ""),
                    "proposal":   str(p.get("proposal", "")),
                    "priority":   float(p.get("priority", 0.5)),
                    "confidence": float(p.get("confidence", 0.5)),
                    "reasoning":  str(p.get("reasoning", "")),
                }
                for p in raw_proposals if isinstance(p, dict)
            ]

        final_plan = result.get("plan", [])
        explanation = result.get("explanation", "Plan generated successfully")

        # ── Save plan to database ─────────────────────────────────────────────
        plan_data = DailyPlan(
            user_id=request.user_id,
            plan_json=final_plan if final_plan else [],
            explanation=explanation
        )
        db.add(plan_data)
        db.flush()   # get plan_id before committing
        plan_id = plan_data.id

        # Save each agent proposal as an AgentAction row
        for prop in proposals_list:
            agent_action = AgentAction(
                plan_id=plan_id,
                agent_name=prop["agent"],
                proposal_json=prop,
                priority_score=prop["priority"]
            )
            db.add(agent_action)

        db.commit()
        logger.info(
            f"Daily plan generated for user {request.user_id} "
            f"| plan_id={plan_id} | items={len(final_plan)} "
            f"| agents={len(proposals_list)}"
        )

        return DailyPlanResponse(
            plan_id=plan_id,
            plan=final_plan,
            agent_proposals=proposals_list,
            explanation=explanation,
            created_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating daily plan: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submit feedback on daily plan and save to database
    
    Args:
        request: FeedbackRequest with plan rating and completed tasks
    
    Returns:
        FeedbackResponse confirming feedback saved
    """
    try:
        # Verify user and plan exist
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        plan = db.query(DailyPlan).filter(
            DailyPlan.id == request.plan_id,
            DailyPlan.user_id == request.user_id
        ).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Save feedback to database
        feedback = Feedback(
            user_id=request.user_id,
            plan_id=request.plan_id,
            rating=request.rating,
            completed_tasks=request.completed_tasks,
            comments=request.comments
        )
        db.add(feedback)
        
        # Update bandit learning with feedback reward
        reward_value = 1.0 if request.rating == "up" else (0.0 if request.rating == "down" else 0.5)
        completion_rate = len(request.completed_tasks) / max(len(plan.plan_json), 1)
        final_reward = (reward_value + completion_rate) / 2
        
        bandit_reward = BanditReward(
            user_id=request.user_id,
            action_name=f"daily_plan_{request.plan_id}",
            reward_value=final_reward,
            context_json={
                "plan_id": request.plan_id,
                "rating": request.rating,
                "completion_rate": completion_rate
            }
        )
        db.add(bandit_reward)
        db.commit()
        
        logger.info(f"Feedback received for plan {request.plan_id}: {request.rating}")
        
        return FeedbackResponse(
            success=True,
            message="Feedback recorded and will improve future recommendations"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=HistoryResponse)
async def get_history(user_id: int, db: Session = Depends(get_db)):
    """
    Get user's past plans and mood logs
    
    Args:
        user_id: User ID
    
    Returns:
        HistoryResponse with past mood logs and plans
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get mood logs
        mood_logs = db.query(MoodLog).filter(
            MoodLog.user_id == user_id
        ).order_by(desc(MoodLog.created_at)).limit(30).all()
        
        # Get plans
        plans = db.query(DailyPlan).filter(
            DailyPlan.user_id == user_id
        ).order_by(desc(DailyPlan.created_at)).limit(30).all()
        
        return HistoryResponse(
            mood_logs=[
                {
                    "id": log.id,
                    "mood": log.mood,
                    "stress_score": log.stress_score,
                    "energy_score": log.energy_score,
                    "created_at": log.created_at
                }
                for log in mood_logs
            ],
            plans=[
                {
                    "id": plan.id,
                    "plan": plan.plan_json,
                    "explanation": plan.explanation,
                    "created_at": plan.created_at
                }
                for plan in plans
            ],
            total_plans=db.query(DailyPlan).filter(DailyPlan.user_id == user_id).count()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics(user_id: int, db: Session = Depends(get_db)):
    """
    Get user's statistics (mood trends, energy levels, stress patterns)
    
    Args:
        user_id: User ID
    
    Returns:
        Dictionary with statistics
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get mood logs for past 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        mood_logs = db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.created_at >= start_date
        ).all()
        
        # Get plans for past 30 days
        plans = db.query(DailyPlan).filter(
            DailyPlan.user_id == user_id,
            DailyPlan.created_at >= start_date
        ).all()
        
        # Get feedback data
        feedback_logs = db.query(Feedback).filter(
            Feedback.user_id == user_id,
            Feedback.created_at >= start_date
        ).all()
        
        # Calculate statistics
        if mood_logs:
            avg_stress = sum(log.stress_score for log in mood_logs) / len(mood_logs)
            avg_energy = sum(log.energy_score for log in mood_logs) / len(mood_logs)
            mood_counts = {}
            for log in mood_logs:
                mood_counts[log.mood] = mood_counts.get(log.mood, 0) + 1
            top_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "neutral"
        else:
            avg_stress = 0.5
            avg_energy = 0.5
            top_mood = "neutral"
        
        if feedback_logs:
            positive_feedback = sum(1 for f in feedback_logs if f.rating == "up")
            completion_rates = [
                len(f.completed_tasks) / max(len(plans[0].plan_json), 1) 
                if plans else 0 
                for f in feedback_logs if f.completed_tasks
            ]
            avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        else:
            positive_feedback = 0
            avg_completion = 0
        
        return {
            "average_mood": top_mood,
            "average_stress": round(avg_stress, 2),
            "average_energy": round(avg_energy, 2),
            "total_plans": len(plans),
            "completed_tasks": sum(len(f.completed_tasks) for f in feedback_logs if f.completed_tasks),
            "completion_rate": round(avg_completion, 2),
            "positive_feedback_percentage": round((positive_feedback / len(feedback_logs) * 100) if feedback_logs else 0, 1),
            "mood_distribution": dict(
                sorted(
                    [(mood, count) for mood, count in (
                        {log.mood: sum(1 for l in mood_logs if l.mood == log.mood) for log in mood_logs}
                    ).items()],
                    key=lambda x: x[1],
                    reverse=True
                )
            ) if mood_logs else {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Database Viewer ============

@router.get("/db-view")
async def view_database(db: Session = Depends(get_db)):
    """
    Returns a full snapshot of the entire database — all users, moods, plans, feedback.
    Useful for debugging and monitoring.
    """
    try:
        users = db.query(User).order_by(User.id).all()
        result = []

        for user in users:
            mood_logs = (
                db.query(MoodLog)
                .filter(MoodLog.user_id == user.id)
                .order_by(desc(MoodLog.created_at))
                .all()
            )
            plans = (
                db.query(DailyPlan)
                .filter(DailyPlan.user_id == user.id)
                .order_by(desc(DailyPlan.created_at))
                .all()
            )
            feedbacks = (
                db.query(Feedback)
                .filter(Feedback.user_id == user.id)
                .order_by(desc(Feedback.created_at))
                .all()
            )

            result.append({
                "user": {
                    "id":         user.id,
                    "name":       user.name,
                    "email":      user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                },
                "summary": {
                    "total_mood_logs": len(mood_logs),
                    "total_plans":     len(plans),
                    "total_feedbacks": len(feedbacks),
                },
                "mood_logs": [
                    {
                        "id":           log.id,
                        "mood":         log.mood,
                        "stress":       f"{round(log.stress_score * 100)}%",
                        "energy":       f"{round(log.energy_score * 100)}%",
                        "text":         log.raw_text,
                        "created_at":   log.created_at.isoformat() if log.created_at else None,
                    }
                    for log in mood_logs
                ],
                "plans": [
                    {
                        "id":          plan.id,
                        "created_at":  plan.created_at.isoformat() if plan.created_at else None,
                        "explanation": plan.explanation,
                        "tasks": [
                            {
                                "time":  item.get("time", ""),
                                "task":  item.get("task", str(item)),
                                "agent": item.get("agent", ""),
                            }
                            for item in (plan.plan_json or [])
                            if isinstance(item, dict)
                        ],
                    }
                    for plan in plans
                ],
                "feedbacks": [
                    {
                        "id":              fb.id,
                        "plan_id":         fb.plan_id,
                        "rating":          fb.rating,
                        "completed_tasks": fb.completed_tasks,
                        "comments":        fb.comments,
                        "created_at":      fb.created_at.isoformat() if fb.created_at else None,
                    }
                    for fb in feedbacks
                ],
            })

        return {
            "total_users": len(users),
            "database":    "lifeos.db",
            "users":       result,
        }

    except Exception as e:
        logger.error(f"Error in db-view: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

