"""
Task Memory System - Multi-layer persistence for task data

Layers:
  - PostgreSQL: Durable task records and history
  - Redis: Fast access to today's tasks
  - ChromaDB: Semantic search for similar tasks and patterns
  - Neo4j: Task relationships and dependencies
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from app.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)

class TaskMemory:
    """Task memory management across all layers"""
    
    def __init__(self, memory_system: MemorySystem):
        """
        Initialize task memory
        
        Args:
            memory_system: Multi-layer memory system instance
        """
        self.memory = memory_system
        self.today = date.today().isoformat()
    
    # ============ Redis (Session/Today) Operations ============
    
    async def save_today_tasks(self, user_id: int, tasks: List[Dict[str, Any]]) -> bool:
        """Save today's tasks to Redis for fast access"""
        try:
            key = f"tasks:{user_id}:{self.today}"
            task_data = {
                "date": self.today,
                "tasks": tasks,
                "saved_at": datetime.utcnow().isoformat(),
                "count": len(tasks)
            }
            await self.memory.save(key, task_data, ttl=86400)  # 24 hour TTL
            logger.info(f"Saved {len(tasks)} tasks for user {user_id} to Redis")
            return True
        except Exception as e:
            logger.error(f"Error saving tasks to Redis: {e}")
            return False
    
    async def get_today_tasks(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Retrieve today's tasks from Redis"""
        try:
            key = f"tasks:{user_id}:{self.today}"
            data = await self.memory.retrieve(key)
            return data.get("tasks", []) if data else None
        except Exception as e:
            logger.error(f"Error retrieving today's tasks: {e}")
            return None
    
    async def update_task_status(
        self,
        user_id: int,
        task_id: int,
        status: str
    ) -> bool:
        """Update task status in Redis"""
        try:
            tasks = await self.get_today_tasks(user_id)
            if tasks:
                for task in tasks:
                    if task.get("id") == task_id:
                        task["status"] = status
                        if status == "completed":
                            task["completed_at"] = datetime.utcnow().isoformat()
                        break
                return await self.save_today_tasks(user_id, tasks)
            return False
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    # ============ ChromaDB (Semantic Search) Operations ============
    
    async def index_task(self, user_id: int, task: Dict[str, Any]) -> bool:
        """Index task in ChromaDB for semantic search"""
        try:
            # Create semantic representation of task
            task_text = f"{task.get('title')} {task.get('category', '')} {task.get('ai_suggestion', '')}"
            
            metadata = {
                "user_id": user_id,
                "task_id": task.get("id"),
                "importance": task.get("importance", 3),
                "category": task.get("category", "work"),
                "date": task.get("date", self.today),
                "completed": task.get("status") == "completed",
            }
            
            await self.memory.save_semantic(
                user_id=user_id,
                content=task_text,
                metadata=metadata,
                collection="tasks"
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing task in ChromaDB: {e}")
            return False
    
    async def search_similar_tasks(
        self,
        user_id: int,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar tasks in ChromaDB"""
        try:
            results = await self.memory.semantic_search(
                user_id=user_id,
                query=query,
                collection="tasks",
                limit=limit
            )
            return results or []
        except Exception as e:
            logger.error(f"Error searching similar tasks: {e}")
            return []
    
    # ============ Task History & Analytics ============
    
    async def get_task_summary(
        self,
        user_id: int,
        date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get daily task summary for analysis"""
        
        date_str = date_str or self.today
        
        summary = {
            "date": date_str,
            "total_tasks": 0,
            "completed": 0,
            "pending": 0,
            "skipped": 0,
            "completion_rate": 0.0,
            "avg_importance": 0.0,
            "tasks_by_category": {},
            "summary_markdown": "",
        }
        
        try:
            # Get task data from memory
            key = f"tasks:{user_id}:{date_str}"
            data = await self.memory.retrieve(key)
            
            if not data or "tasks" not in data:
                return summary
            
            tasks = data["tasks"]
            summary["total_tasks"] = len(tasks)
            
            # Calculate metrics
            completed_tasks = []
            pending_tasks = []
            skipped_tasks = []
            category_counts = {}
            total_importance = 0
            
            for task in tasks:
                status = task.get("status", "pending")
                category = task.get("category", "work")
                importance = task.get("importance", 3)
                
                if status == "completed":
                    summary["completed"] += 1
                    completed_tasks.append(task)
                elif status == "skipped":
                    summary["skipped"] += 1
                    skipped_tasks.append(task)
                else:
                    summary["pending"] += 1
                    pending_tasks.append(task)
                
                category_counts[category] = category_counts.get(category, 0) + 1
                total_importance += importance
            
            # Calculate averages
            if tasks:
                summary["completion_rate"] = summary["completed"] / len(tasks)
                summary["avg_importance"] = total_importance / len(tasks)
            
            summary["tasks_by_category"] = category_counts
            
            # Build markdown summary
            summary["summary_markdown"] = self._build_summary_markdown(
                date_str, summary, completed_tasks, pending_tasks, skipped_tasks
            )
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating task summary: {e}")
            return summary
    
    async def get_weekly_summary(self, user_id: int) -> Dict[str, Any]:
        """Get weekly task summary for analysis"""
        
        weekly_summary = {
            "week_start": (date.today() - timedelta(days=date.today().weekday())).isoformat(),
            "week_end": (date.today() + timedelta(days=6 - date.today().weekday())).isoformat(),
            "days": {},
            "weekly_stats": {
                "total_tasks": 0,
                "total_completed": 0,
                "avg_completion_rate": 0.0,
                "most_productive_day": "",
                "most_common_category": "",
                "insights": []
            }
        }
        
        try:
            current_date = date.today() - timedelta(days=date.today().weekday())
            
            for i in range(7):
                date_str = (current_date + timedelta(days=i)).isoformat()
                daily_summary = await self.get_task_summary(user_id, date_str)
                weekly_summary["days"][date_str] = daily_summary
                
                weekly_summary["weekly_stats"]["total_tasks"] += daily_summary["total_tasks"]
                weekly_summary["weekly_stats"]["total_completed"] += daily_summary["completed"]
            
            # Calculate weekly metrics
            if weekly_summary["weekly_stats"]["total_tasks"] > 0:
                weekly_summary["weekly_stats"]["avg_completion_rate"] = (
                    weekly_summary["weekly_stats"]["total_completed"] /
                    weekly_summary["weekly_stats"]["total_tasks"]
                )
            
            # Find most productive day
            max_completed = 0
            for date_str, summary in weekly_summary["days"].items():
                if summary["completed"] > max_completed:
                    max_completed = summary["completed"]
                    weekly_summary["weekly_stats"]["most_productive_day"] = date_str
            
            # Generate insights
            weekly_summary["weekly_stats"]["insights"] = self._generate_insights(
                weekly_summary
            )
            
            return weekly_summary
        
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            return weekly_summary
    
    def _build_summary_markdown(
        self,
        date_str: str,
        summary: Dict[str, Any],
        completed: List[Dict[str, Any]],
        pending: List[Dict[str, Any]],
        skipped: List[Dict[str, Any]]
    ) -> str:
        """Build markdown format summary"""
        
        parts = []
        parts.append(f"# Daily Task Summary - {date_str}\n")
        
        # Statistics
        parts.append("## Stats\n")
        parts.append(
            f"- **Total Tasks**: {summary['total_tasks']}\n"
            f"- **Completed**: {summary['completed']} "
            f"({int(summary['completion_rate'] * 100)}%)\n"
            f"- **Pending**: {summary['pending']}\n"
            f"- **Skipped**: {summary['skipped']}\n"
            f"- **Average Importance**: {summary['avg_importance']:.1f}/5\n"
        )
        
        # Category breakdown
        if summary["tasks_by_category"]:
            parts.append("\n## By Category\n")
            for category, count in summary["tasks_by_category"].items():
                parts.append(f"- {category.capitalize()}: {count}\n")
        
        # Completed tasks
        if completed:
            parts.append("\n## ✅ Completed\n")
            for task in completed:
                parts.append(f"- [{task['title']}] ({task.get('category', 'work')})\n")
        
        # Pending tasks
        if pending:
            parts.append("\n## ⏳ Pending\n")
            for task in pending:
                parts.append(
                    f"- {task['title']} "
                    f"(Importance: {task.get('importance', 3)}/5)\n"
                )
        
        # Skipped tasks
        if skipped:
            parts.append("\n## ⏭️ Skipped\n")
            for task in skipped:
                parts.append(f"- {task['title']}\n")
        
        return "".join(parts)
    
    def _generate_insights(self, weekly_summary: Dict[str, Any]) -> List[str]:
        """Generate insights from weekly data"""
        
        insights = []
        stats = weekly_summary["weekly_stats"]
        
        # Completion rate insight
        if stats["avg_completion_rate"] > 0.8:
            insights.append(
                f"🌟 Excellent week! You completed {int(stats['avg_completion_rate'] * 100)}% "
                f"of your tasks ({stats['total_completed']}/{stats['total_tasks']})"
            )
        elif stats["avg_completion_rate"] > 0.6:
            insights.append(
                f"Good progress! You completed {int(stats['avg_completion_rate'] * 100)}% "
                f"of your tasks this week."
            )
        else:
            insights.append(
                f"Consider lighter task loads. You completed {int(stats['avg_completion_rate'] * 100)}% "
                f"of tasks this week."
            )
        
        # Most productive day
        if stats["most_productive_day"]:
            day_name = datetime.fromisoformat(stats["most_productive_day"]).strftime("%A")
            insights.append(f"📈 Most productive day: {day_name}")
        
        # Category insights
        if stats["most_common_category"]:
            insights.append(f"🎯 Most common category: {stats['most_common_category']}")
        
        return insights
    
    # ============ Task-Mood Correlation ============
    
    async def correlate_tasks_with_mood(
        self,
        user_id: int,
        date_str: str,
        mood_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Correlate completed tasks with mood data for learning"""
        
        correlation = {
            "date": date_str,
            "mood": mood_data.get("mood"),
            "stress_score": mood_data.get("stress_score"),
            "energy_score": mood_data.get("energy_score"),
            "tasks_completed": 0,
            "completion_rate": 0.0,
            "learning_points": []
        }
        
        try:
            summary = await self.get_task_summary(user_id, date_str)
            
            correlation["tasks_completed"] = summary["completed"]
            if summary["total_tasks"] > 0:
                correlation["completion_rate"] = summary["completed"] / summary["total_tasks"]
            
            # Generate learning insights
            correlation["learning_points"] = self._generate_learning_points(
                mood_data, summary
            )
            
            # Save for future reference
            key = f"task_mood_correlation:{user_id}:{date_str}"
            await self.memory.save(key, correlation, ttl=2592000)  # 30 day TTL
            
            return correlation
        
        except Exception as e:
            logger.error(f"Error correlating tasks with mood: {e}")
            return correlation
    
    def _generate_learning_points(
        self,
        mood_data: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> List[str]:
        """Generate learning insights from mood-task correlation"""
        
        points = []
        mood = mood_data.get("mood", "neutral")
        completion_rate = summary.get("completion_rate", 0)
        
        if mood == "stressed" and completion_rate < 0.5:
            points.append(
                "Stressed mood led to lower completion. Consider shorter tasks when stressed."
            )
        
        if mood == "energetic" and completion_rate > 0.7:
            points.append(
                "Energetic mood correlates with higher task completion. "
                "Plan important tasks for energetic days."
            )
        
        if mood == "tired" and completion_rate > 0.6:
            points.append(
                "Even while tired, you completed tasks. Good persistence!"
            )
        
        return points
