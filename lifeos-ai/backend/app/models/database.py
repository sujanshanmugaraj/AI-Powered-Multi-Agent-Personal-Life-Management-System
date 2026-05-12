"""
SQLAlchemy ORM models for database tables
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
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
    context_json = Column(JSON, nullable=True)  # mood, energy, day_of_week, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
