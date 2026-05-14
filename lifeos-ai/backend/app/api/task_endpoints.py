"""
Task API endpoints - Task management and daily planning features
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.schemas import UserTaskInput, UserTaskResponse, UserTaskUpdateRequest
from app.models.database import User, UserTask, MoodLog, DailyPlan
from app.memory.task_memory import TaskMemory
from app.memory.memory_system import MemorySystem
from app.agents.task_planner_agent import TaskPlannerAgent
from datetime import datetime, date as date_type
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

task_router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# ============ Response Models ============

class TaskPlanResponse(BaseModel):
    """Response for daily task plan generation"""
    plan_id: int
    tasks: List[UserTaskResponse]
    suggestions: List[Dict[str, Any]]
    mood_adjusted: bool
    explanation: str
    created_at: datetime

class DailySummaryResponse(BaseModel):
    """Daily task summary"""
    date: str
    total_tasks: int
    completed: int
    pending: int
    skipped: int
    completion_rate: float
    summary_markdown: str

class WeeklySummaryResponse(BaseModel):
    """Weekly task summary and analytics"""
    week_start: str
    week_end: str
    total_tasks: int
    total_completed: int
    avg_completion_rate: float
    most_productive_day: str
    insights: List[str]

# ============ Task Endpoints ============

@task_router.post("/plan", response_model=TaskPlanResponse)
async def create_task_plan(
    user_id: int,
    tasks: List[UserTaskInput],
    db: Session = Depends(get_db)
):
    """
    Create intelligent daily task plan based on user mood and importance.
    Prioritizes tasks and suggests mood-boosting activities.
    
    Args:
        user_id: User ID
        tasks: List of tasks to plan
    
    Returns:
        Task plan with prioritized assignments and suggestions
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's latest mood
        latest_mood = db.query(MoodLog).filter(
            MoodLog.user_id == user_id
        ).order_by(desc(MoodLog.created_at)).first()
        
        if not latest_mood:
            raise HTTPException(
                status_code=400,
                detail="Please log your mood before creating a task plan"
            )
        
        # Initialize memory and task planner agent
        memory = MemorySystem(db=db)
        task_planner = TaskPlannerAgent(llm=None, memory_system=memory)
        task_memory = TaskMemory(memory)
        
        # Prepare state for agent
        mood_data = {
            "mood": latest_mood.mood,
            "stress_score": latest_mood.stress_score,
            "energy_score": latest_mood.energy_score,
        }
        
        # Convert input tasks to dict format
        user_tasks_dict = []
        for i, task in enumerate(tasks):
            user_tasks_dict.append({
                "id": i + 1,
                "title": task.title,
                "importance": task.importance,
                "estimated_duration": task.estimated_duration,
                "status": "pending",
                "category": "work",  # Default category
                "date": date_type.today().isoformat(),
            })
        
        # Generate task plan using agent
        state = {
            "user_id": user_id,
            "mood_data": mood_data,
            "user_tasks": user_tasks_dict,
        }
        
        proposal = await task_planner.generate_proposal(state)
        
        # Save tasks to database
        today = date_type.today().isoformat()
        saved_tasks = []
        
        for task_dict in user_tasks_dict:
            db_task = UserTask(
                user_id=user_id,
                date=today,
                title=task_dict["title"],
                importance=task_dict["importance"],
                estimated_duration=task_dict["estimated_duration"],
                status="pending",
                ai_included=True,
                ai_suggestion=None,
                ai_priority=0.5,
            )
            db.add(db_task)
            db.flush()
            
            # Index in ChromaDB
            await task_memory.index_task(user_id, {
                "id": db_task.id,
                "title": task_dict["title"],
                "category": "work",
                "date": today,
            })
            
            saved_tasks.append(UserTaskResponse.from_orm(db_task))
        
        db.commit()
        
        # Save to Redis for fast access
        await task_memory.save_today_tasks(user_id, user_tasks_dict)
        
        logger.info(f"Created task plan for user {user_id} with {len(saved_tasks)} tasks")
        
        return TaskPlanResponse(
            plan_id=0,  # Not linked to daily plan
            tasks=saved_tasks,
            suggestions=proposal.get("memory_used", []),
            mood_adjusted=True,
            explanation=proposal["proposal"],
            created_at=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task plan: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@task_router.get("/today", response_model=List[UserTaskResponse])
async def get_today_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all tasks for today"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        today = date_type.today().isoformat()
        tasks = db.query(UserTask).filter(
            UserTask.user_id == user_id,
            UserTask.date == today
        ).order_by(desc(UserTask.ai_priority)).all()
        
        return [UserTaskResponse.from_orm(task) for task in tasks]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving today's tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@task_router.put("/task/{task_id}", response_model=UserTaskResponse)
async def update_task_status(
    task_id: int,
    update: UserTaskUpdateRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Update task status (completed, pending, skipped)"""
    try:
        task = db.query(UserTask).filter(
            UserTask.id == task_id,
            UserTask.user_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.status = update.status
        if update.status == "completed":
            task.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"Updated task {task_id} status to {update.status}")
        
        return UserTaskResponse.from_orm(task)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@task_router.delete("/task/{task_id}")
async def delete_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    try:
        task = db.query(UserTask).filter(
            UserTask.id == task_id,
            UserTask.user_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
        
        logger.info(f"Deleted task {task_id}")
        
        return {"success": True, "message": "Task deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============ Summary & Analytics Endpoints ============

@task_router.get("/summary/today", response_model=DailySummaryResponse)
async def get_today_summary(user_id: int, db: Session = Depends(get_db)):
    """Get today's task summary and completion metrics"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        memory = MemorySystem(db=db)
        task_memory = TaskMemory(memory)
        
        summary = await task_memory.get_task_summary(user_id)
        
        return DailySummaryResponse(
            date=summary["date"],
            total_tasks=summary["total_tasks"],
            completed=summary["completed"],
            pending=summary["pending"],
            skipped=summary["skipped"],
            completion_rate=summary["completion_rate"],
            summary_markdown=summary["summary_markdown"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting today's summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@task_router.get("/summary/date/{date_str}", response_model=DailySummaryResponse)
async def get_date_summary(date_str: str, user_id: int, db: Session = Depends(get_db)):
    """Get task summary for a specific date"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        memory = MemorySystem(db=db)
        task_memory = TaskMemory(memory)
        
        summary = await task_memory.get_task_summary(user_id, date_str)
        
        return DailySummaryResponse(
            date=summary["date"],
            total_tasks=summary["total_tasks"],
            completed=summary["completed"],
            pending=summary["pending"],
            skipped=summary["skipped"],
            completion_rate=summary["completion_rate"],
            summary_markdown=summary["summary_markdown"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting date summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@task_router.get("/summary/weekly", response_model=WeeklySummaryResponse)
async def get_weekly_summary(user_id: int, db: Session = Depends(get_db)):
    """Get weekly task summary with insights and analytics"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        memory = MemorySystem(db=db)
        task_memory = TaskMemory(memory)
        
        summary = await task_memory.get_weekly_summary(user_id)
        stats = summary["weekly_stats"]
        
        return WeeklySummaryResponse(
            week_start=summary["week_start"],
            week_end=summary["week_end"],
            total_tasks=stats["total_tasks"],
            total_completed=stats["total_completed"],
            avg_completion_rate=stats["avg_completion_rate"],
            most_productive_day=stats["most_productive_day"],
            insights=stats["insights"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weekly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@task_router.get("/history")
async def get_task_history(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get task history with completion rates and patterns
    
    Args:
        user_id: User ID
        days: Number of days of history (default: 30)
    
    Returns:
        Task history with patterns and insights
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get task history from database
        start_date = (date_type.today().replace(day=1) - 
                     __import__('datetime').timedelta(days=days)).isoformat()
        
        tasks = db.query(UserTask).filter(
            UserTask.user_id == user_id,
            UserTask.date >= start_date
        ).order_by(desc(UserTask.date)).all()
        
        # Group by date and calculate metrics
        history_by_date = {}
        for task in tasks:
            if task.date not in history_by_date:
                history_by_date[task.date] = {
                    "date": task.date,
                    "total": 0,
                    "completed": 0,
                    "pending": 0,
                    "skipped": 0,
                    "tasks": []
                }
            
            history_by_date[task.date]["total"] += 1
            history_by_date[task.date][task.status] += 1
            history_by_date[task.date]["tasks"].append(UserTaskResponse.from_orm(task))
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_days": len(history_by_date),
            "total_tasks": len(tasks),
            "completed_total": sum(d["completed"] for d in history_by_date.values()),
            "history": sorted(
                [
                    {
                        **history_by_date[date_str],
                        "completion_rate": (
                            history_by_date[date_str]["completed"] /
                            history_by_date[date_str]["total"]
                            if history_by_date[date_str]["total"] > 0 else 0
                        )
                    }
                    for date_str in history_by_date.keys()
                ],
                key=lambda x: x["date"],
                reverse=True
            )
        }
    
    except Exception as e:
        logger.error(f"Error retrieving task history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
