"""
Memory System — queries SQLite history to give agents real context.

Each agent gets personalised data based on:
  - Past mood logs (stress/energy trends)
  - Past plans (what was scheduled)
  - Past feedback (what was actually completed + ratings)
  - Bandit rewards (which agents produced good outcomes)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MemorySystem:
    """Queries the SQLite database to provide historical context to each agent."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Public interface (called by BaseAgent.get_memory_context)           #
    # ------------------------------------------------------------------ #

    async def retrieve(self, user_id: int, query: str, agent_name: str = None) -> Dict[str, Any]:
        """Return relevant historical context for the given agent."""
        if not user_id or not self.db:
            return {}

        try:
            if agent_name == "mood":
                return self._mood_context(user_id)
            elif agent_name == "health":
                return self._health_context(user_id)
            elif agent_name == "finance":
                return self._finance_context(user_id)
            elif agent_name == "learning":
                return self._learning_context(user_id)
            elif agent_name == "schedule":
                return self._schedule_context(user_id)
            elif agent_name == "system":
                return self._user_preferences(user_id)
            else:
                return self._general_context(user_id)
        except Exception as e:
            logger.error(f"MemorySystem.retrieve error (agent={agent_name}): {e}")
            return {}

    async def store(self, user_id: int, data: Dict[str, Any], data_type: str = "general") -> bool:
        """No-op — data is already persisted by the router before the workflow runs."""
        return True

    # ------------------------------------------------------------------ #
    # Agent-specific context builders                                     #
    # ------------------------------------------------------------------ #

    def _mood_context(self, user_id: int) -> Dict[str, Any]:
        """7-day mood trend for the mood agent."""
        from app.models.database import MoodLog
        cutoff = datetime.utcnow() - timedelta(days=7)
        logs = (
            self.db.query(MoodLog)
            .filter(MoodLog.user_id == user_id, MoodLog.created_at >= cutoff)
            .order_by(MoodLog.created_at.desc())
            .limit(20)
            .all()
        )
        if not logs:
            return {}

        avg_stress  = sum(l.stress_score  for l in logs) / len(logs)
        avg_energy  = sum(l.energy_score  for l in logs) / len(logs)
        mood_counts: Dict[str, int] = {}
        for l in logs:
            mood_counts[l.mood] = mood_counts.get(l.mood, 0) + 1
        dominant_mood = max(mood_counts, key=mood_counts.get)

        return {
            "avg_stress_7d":  round(avg_stress, 2),
            "avg_energy_7d":  round(avg_energy, 2),
            "dominant_mood":  dominant_mood,
            "mood_log_count": len(logs),
            "trend": "improving" if len(logs) >= 2 and logs[0].stress_score < logs[-1].stress_score else "stable",
        }

    def _health_context(self, user_id: int) -> Dict[str, Any]:
        """
        Health agent context:
        - completion_rate: fraction of past health tasks the user actually completed
        - data_points:     how many feedback records we have
        """
        from app.models.database import Feedback, DailyPlan

        feedbacks = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(30)
            .all()
        )
        if not feedbacks:
            return {"completion_rate": None, "data_points": 0}

        health_keywords = {"walk", "workout", "gym", "yoga", "stretch", "run", "exercise", "jog"}
        total_health_tasks  = 0
        completed_health    = 0

        for fb in feedbacks:
            plan = self.db.query(DailyPlan).filter(DailyPlan.id == fb.plan_id).first()
            if not plan or not plan.plan_json:
                continue
            for item in plan.plan_json:
                task_text = (item.get("task", "") if isinstance(item, dict) else str(item)).lower()
                if any(kw in task_text for kw in health_keywords):
                    total_health_tasks += 1
                    completed = fb.completed_tasks or []
                    if any(kw in c.lower() for kw in health_keywords for c in completed):
                        completed_health += 1

        completion_rate = (completed_health / total_health_tasks) if total_health_tasks > 0 else None
        return {
            "completion_rate": round(completion_rate, 2) if completion_rate is not None else None,
            "data_points": len(feedbacks),
        }

    def _finance_context(self, user_id: int) -> Dict[str, Any]:
        """
        Finance agent context:
        - budget_status: inferred from how often finance tasks were skipped
        """
        from app.models.database import Feedback, DailyPlan

        feedbacks = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(15)
            .all()
        )
        if not feedbacks:
            return {"budget_status": "normal"}

        finance_keywords = {"budget", "spending", "finance", "money", "expense", "bank"}
        skipped = 0
        total   = 0

        for fb in feedbacks:
            plan = self.db.query(DailyPlan).filter(DailyPlan.id == fb.plan_id).first()
            if not plan or not plan.plan_json:
                continue
            for item in plan.plan_json:
                task_text = (item.get("task", "") if isinstance(item, dict) else str(item)).lower()
                if any(kw in task_text for kw in finance_keywords):
                    total += 1
                    completed = fb.completed_tasks or []
                    if not any(kw in c.lower() for kw in finance_keywords for c in completed):
                        skipped += 1

        skip_rate = (skipped / total) if total > 0 else 0
        budget_status = "normal"
        if skip_rate > 0.6:
            budget_status = "at_risk"   # consistently skipping finance reviews

        return {"budget_status": budget_status, "finance_skip_rate": round(skip_rate, 2)}

    def _learning_context(self, user_id: int) -> Dict[str, Any]:
        """
        Learning agent context:
        - active_goals:        list of inferred study subjects from past plans
        - deadline_urgency:    0.5 default (no real deadlines stored)
        - completion_history:  1/0 per feedback for learning tasks
        """
        from app.models.database import DailyPlan, Feedback

        plans = (
            self.db.query(DailyPlan)
            .filter(DailyPlan.user_id == user_id)
            .order_by(DailyPlan.created_at.desc())
            .limit(10)
            .all()
        )

        learn_keywords = {"study", "learn", "read", "course", "practice", "revise", "review", "coding", "python", "math"}
        subjects_seen = {}

        for plan in plans:
            if not plan.plan_json:
                continue
            for item in plan.plan_json:
                task_text = (item.get("task", "") if isinstance(item, dict) else str(item)).lower()
                if any(kw in task_text for kw in learn_keywords):
                    # use the first matching keyword as the subject proxy
                    for kw in learn_keywords:
                        if kw in task_text:
                            subjects_seen[kw] = subjects_seen.get(kw, 0) + 1
                            break

        # Build goal list from most frequent subjects
        active_goals = []
        for subject, count in sorted(subjects_seen.items(), key=lambda x: -x[1])[:3]:
            active_goals.append({"subject": subject.capitalize(), "id": subject, "count": count})

        # Completion history from feedbacks
        feedbacks = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(10)
            .all()
        )
        completion_history = []
        for fb in feedbacks:
            completed = fb.completed_tasks or []
            did_learn = any(any(kw in c.lower() for kw in learn_keywords) for c in completed)
            completion_history.append(1 if did_learn else 0)

        return {
            "active_goals":        active_goals,
            "deadline_urgency":    0.5,        # no explicit deadlines stored yet
            "completion_history":  completion_history,
        }

    def _schedule_context(self, user_id: int) -> Dict[str, Any]:
        """
        Schedule agent context:
        - calendar: empty (no external calendar integration yet)
        - user_time_preference: inferred from when tasks were completed
        """
        from app.models.database import MoodLog

        logs = (
            self.db.query(MoodLog)
            .filter(MoodLog.user_id == user_id)
            .order_by(MoodLog.created_at.desc())
            .limit(14)
            .all()
        )

        # Infer preferred work time from when user logs their mood
        morning_count = sum(1 for l in logs if 5 <= l.created_at.hour < 12)
        afternoon_count = sum(1 for l in logs if 12 <= l.created_at.hour < 18)
        evening_count = sum(1 for l in logs if 18 <= l.created_at.hour < 24)

        most = max(morning_count, afternoon_count, evening_count)
        if most == morning_count:
            time_pref = "morning (9-12)"
        elif most == afternoon_count:
            time_pref = "afternoon (12-18)"
        else:
            time_pref = "evening (18-21)"

        return {
            "calendar":             [],      # no external calendar connected
            "user_time_preference": time_pref,
        }

    def _user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Overall user preferences inferred from history."""
        from app.models.database import Feedback

        feedbacks = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(20)
            .all()
        )
        if not feedbacks:
            return {
                "time_preference":      "morning",
                "intensity_preference": "medium",
                "break_frequency":      60,
            }

        up_count      = sum(1 for f in feedbacks if f.rating == "up")
        down_count    = sum(1 for f in feedbacks if f.rating == "down")
        total_rated   = up_count + down_count
        satisfaction  = (up_count / total_rated) if total_rated > 0 else 0.5

        intensity = "medium"
        if satisfaction > 0.7:
            intensity = "high"
        elif satisfaction < 0.4:
            intensity = "low"

        return {
            "time_preference":      "morning",
            "intensity_preference": intensity,
            "break_frequency":      60,
            "overall_satisfaction": round(satisfaction, 2),
            "total_feedbacks":      len(feedbacks),
        }

    def _general_context(self, user_id: int) -> Dict[str, Any]:
        """Fallback — returns basic user stats."""
        from app.models.database import MoodLog, DailyPlan, Feedback
        return {
            "mood_logs":  self.db.query(MoodLog).filter(MoodLog.user_id == user_id).count(),
            "plans":      self.db.query(DailyPlan).filter(DailyPlan.user_id == user_id).count(),
            "feedbacks":  self.db.query(Feedback).filter(Feedback.user_id == user_id).count(),
        }
