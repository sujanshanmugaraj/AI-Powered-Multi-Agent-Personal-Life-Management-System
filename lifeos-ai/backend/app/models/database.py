"""
SQLAlchemy ORM models for database tables
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mood_logs = relationship("MoodLog", back_populates="user")
    daily_plans = relationship("DailyPlan", back_populates="user")
    feedback_logs = relationship("Feedback", back_populates="user")
    user_tasks = relationship("UserTask", back_populates="user")

class MoodLog(Base):
    """Mood log model"""
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mood = Column(String(50), nullable=False)
    stress_score = Column(Float, nullable=False)
    energy_score = Column(Float, nullable=False)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    user = relationship("User", back_populates="mood_logs")

class DailyPlan(Base):
    """Daily plan model"""
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_json = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="daily_plans")
    agent_actions = relationship("AgentAction", back_populates="plan")
    feedback_logs = relationship("Feedback", back_populates="plan")
    user_tasks = relationship("UserTask", back_populates="plan")

class UserTask(Base):
    """User-provided task for a specific day"""
    __tablename__ = "user_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("daily_plans.id"), nullable=True, index=True)
    date = Column(String(10), nullable=False, index=True)          # YYYY-MM-DD
    title = Column(String(500), nullable=False)
    importance = Column(Integer, default=3)                        # 1 (low) – 5 (critical)
    estimated_duration = Column(Integer, default=30)               # minutes
    status = Column(String(20), default="pending")                 # pending / completed / skipped
    ai_included = Column(Boolean, default=False)                   # did AI put it in the plan?
    ai_suggestion = Column(Text, nullable=True)                    # AI's note on this task
    ai_priority = Column(Float, default=0.5)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="user_tasks")
    plan = relationship("DailyPlan", back_populates="user_tasks")

class Feedback(Base):
    """Feedback model"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("daily_plans.id"), nullable=False, index=True)
    rating = Column(String(10), nullable=False)  # 'up', 'down', 'neutral'
    completed_tasks = Column(JSON, nullable=True)  # stored as JSON list, SQLite-compatible
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="feedback_logs")
    plan = relationship("DailyPlan", back_populates="feedback_logs")

class AgentAction(Base):
    """Agent action/proposal model"""
    __tablename__ = "agent_actions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("daily_plans.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    proposal_json = Column(JSON, nullable=False)
    priority_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    plan = relationship("DailyPlan", back_populates="agent_actions")

class BanditReward(Base):
    """Bandit learning rewards model"""
    __tablename__ = "bandit_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_name = Column(String(100), nullable=False, index=True)
    reward_value = Column(Float, nullable=False)
    context_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
