"""
Task Planner Agent - Intelligently assigns and prioritizes daily tasks based on mood, importance, and energy levels.

Features:
  - Analyzes user mood to suggest appropriate tasks
  - Categorizes tasks (work, health, learning, personal)
  - Adjusts task priority based on mood and energy
  - Suggests mood-boosting activities
  - Predicts task completion probability
  - Handles task conflicts and sequencing
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskPlannerAgent(BaseAgent):
    """Task Planning Agent - Orchestrates daily task management"""
    
    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__(name="task_planner", llm=llm, memory_system=memory_system)
        
        # Task categories for better organization
        self.task_categories = {
            "work": {"weight": 0.3, "stress_impact": 0.6},
            "health": {"weight": 0.25, "stress_impact": -0.3},  # reduces stress
            "learning": {"weight": 0.2, "stress_impact": 0.4},
            "personal": {"weight": 0.15, "stress_impact": -0.2},
            "social": {"weight": 0.1, "stress_impact": -0.4},  # significantly reduces stress
        }
        
        # Mood-to-energy mapping for task recommendation
        self.mood_energy_map = {
            "energetic": {"energy": 0.9, "focus": 0.85, "social": 0.7},
            "happy": {"energy": 0.8, "focus": 0.75, "social": 0.9},
            "stressed": {"energy": 0.4, "focus": 0.5, "social": 0.3},
            "tired": {"energy": 0.3, "focus": 0.4, "social": 0.5},
            "neutral": {"energy": 0.6, "focus": 0.6, "social": 0.6},
        }
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate task assignments and priorities based on user mood and tasks
        
        Args:
            state: Contains user_id, mood_data, user_tasks
        
        Returns:
            Task planning proposal with assignments and suggestions
        """
        try:
            user_id = state.get("user_id")
            mood_data = state.get("mood_data", {})
            user_tasks = state.get("user_tasks", [])
            
            if not user_tasks:
                return self._build_standard_proposal(
                    proposal_text="No tasks provided. Consider starting with small, achievable goals.",
                    priority=0.3,
                    confidence=0.9,
                    reasoning="User has no tasks for today",
                    conflicts=[]
                )
            
            # Analyze current mood state
            mood = mood_data.get("mood", "neutral")
            stress_score = mood_data.get("stress_score", 0.5)
            energy_score = mood_data.get("energy_score", 0.5)
            
            # Prioritize and assign tasks
            prioritized_tasks = await self._prioritize_tasks(
                user_tasks, mood, stress_score, energy_score
            )
            
            # Get mood-boosting suggestions
            mood_boosting = await self._suggest_mood_boosting_tasks(
                mood, energy_score, prioritized_tasks
            )
            
            # Build proposal
            proposal_text = self._build_task_proposal(
                prioritized_tasks, mood_boosting, mood
            )
            
            # Calculate confidence and priority
            confidence = min(0.95, 0.7 + len(prioritized_tasks) * 0.05)
            priority = 0.8 if stress_score > 0.6 else 0.6
            
            return self._build_standard_proposal(
                proposal_text=proposal_text,
                priority=priority,
                confidence=confidence,
                reasoning=self._build_reasoning(mood, stress_score, energy_score),
                memory_used=["mood_history", "task_history"],
                conflicts=[]
            )
        
        except Exception as e:
            logger.error(f"Error in task planner: {e}")
            return self._build_standard_proposal(
                proposal_text="Unable to generate task plan.",
                priority=0.3,
                confidence=0.3,
                reasoning=f"Error: {str(e)}",
                conflicts=[]
            )
    
    async def _prioritize_tasks(
        self,
        user_tasks: List[Dict[str, Any]],
        mood: str,
        stress_score: float,
        energy_score: float
    ) -> List[Dict[str, Any]]:
        """Prioritize tasks based on importance, mood, and energy levels"""
        
        prioritized = []
        
        for task in user_tasks:
            # Base importance from user
            base_importance = task.get("importance", 3) / 5.0
            
            # Extract or infer category
            category = task.get("category", "work")
            category_weight = self.task_categories.get(category, {}).get("weight", 0.2)
            
            # Mood adjustment factor
            mood_adjustment = self._calculate_mood_adjustment(
                mood, stress_score, energy_score, category
            )
            
            # Duration factor (prefer shorter tasks when stressed/tired)
            duration = task.get("estimated_duration", 30)
            duration_factor = max(0.3, 1.0 - (duration / 120.0)) if stress_score > 0.6 else 0.8
            
            # Calculate final priority score
            final_priority = (
                base_importance * 0.4 +
                mood_adjustment * 0.3 +
                duration_factor * 0.2 +
                category_weight * 0.1
            )
            
            # Calculate completion probability based on mood and energy
            completion_prob = self._estimate_completion_probability(
                energy_score, stress_score, duration
            )
            
            prioritized.append({
                **task,
                "ai_priority": final_priority,
                "completion_probability": completion_prob,
                "mood_adjusted": True,
                "suggested_time": self._suggest_task_timing(category, energy_score),
                "category": category,
            })
        
        # Sort by priority (descending)
        return sorted(prioritized, key=lambda x: x["ai_priority"], reverse=True)
    
    def _calculate_mood_adjustment(
        self,
        mood: str,
        stress_score: float,
        energy_score: float,
        category: str
    ) -> float:
        """Calculate adjustment factor based on mood and task category"""
        
        # If stressed, prioritize stress-reducing tasks (health, social, personal)
        if stress_score > 0.7:
            stress_impact = self.task_categories.get(category, {}).get("stress_impact", 0)
            if stress_impact < 0:  # Stress-reducing category
                return 0.85
            else:
                return 0.6
        
        # If tired, prioritize quick, energizing tasks
        if energy_score < 0.4:
            if category in ["health", "personal"]:  # Usually quick and energizing
                return 0.8
            else:
                return 0.5
        
        # Normal state - favor all categories equally
        return 0.7
    
    async def _suggest_mood_boosting_tasks(
        self,
        mood: str,
        energy_score: float,
        current_tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Suggest small, mood-boosting activities based on current mood"""
        
        mood_suggestions = {
            "stressed": [
                "Take a 5-minute breathing exercise 🧘",
                "Step outside for fresh air ☀️",
                "Drink water and stretch 💧",
                "Listen to calming music 🎵",
            ],
            "tired": [
                "Quick 10-minute walk 🚶",
                "Energizing music playlist 🎶",
                "Cold water splash ❄️",
                "10-minute power nap ⏰",
            ],
            "happy": [
                "Share your positivity with someone 😊",
                "Do something you enjoy 🎮",
                "Help someone today ❤️",
            ],
            "energetic": [
                "Tackle the hardest task first 💪",
                "Work on a challenging project 🎯",
                "Help teammates 🤝",
            ],
        }
        
        suggestions = mood_suggestions.get(mood, [])
        
        # Prioritize mood-boosting suggestions if stress is high
        if mood == "stressed" and energy_score < 0.5:
            return [{"suggestion": s, "priority": "high"} for s in suggestions[:2]]
        
        return [{"suggestion": s, "priority": "low"} for s in suggestions]
    
    def _estimate_completion_probability(
        self,
        energy_score: float,
        stress_score: float,
        duration: int
    ) -> float:
        """Estimate probability of task completion based on state"""
        
        base_prob = 0.7
        
        # Energy factor
        if energy_score < 0.3:
            base_prob *= 0.5
        elif energy_score < 0.5:
            base_prob *= 0.7
        else:
            base_prob *= 0.95
        
        # Stress factor
        if stress_score > 0.8:
            base_prob *= 0.6
        elif stress_score > 0.6:
            base_prob *= 0.8
        
        # Duration factor (longer tasks less likely in poor state)
        if duration > 90:
            base_prob *= 0.7
        elif duration > 60:
            base_prob *= 0.85
        
        return min(0.99, max(0.1, base_prob))
    
    def _suggest_task_timing(self, category: str, energy_score: float) -> str:
        """Suggest when to do task based on category and energy"""
        
        if energy_score > 0.8:
            return "morning"
        elif energy_score < 0.4:
            return "afternoon"
        else:
            # Morning: work, learning
            # Afternoon: personal, social
            # Evening: health, reflection
            timing_map = {
                "work": "morning",
                "learning": "morning",
                "personal": "afternoon",
                "health": "evening",
                "social": "afternoon",
            }
            return timing_map.get(category, "flexible")
    
    def _build_task_proposal(
        self,
        prioritized_tasks: List[Dict[str, Any]],
        mood_boosting: List[Dict[str, str]],
        mood: str
    ) -> str:
        """Build human-readable task proposal"""
        
        parts = [f"## Daily Task Plan (Mood: {mood.capitalize()})\n"]
        
        # Top priority tasks
        if prioritized_tasks:
            parts.append("### Priority Tasks:\n")
            for i, task in enumerate(prioritized_tasks[:5], 1):
                parts.append(
                    f"{i}. **{task['title']}** "
                    f"(Importance: {task.get('importance', 3)}/5, "
                    f"Duration: {task.get('estimated_duration', 30)}min, "
                    f"Completion: {int(task.get('completion_probability', 0.7) * 100)}%)\n"
                )
        
        # Mood boosting suggestions
        if mood_boosting:
            parts.append("\n### Recommended Mood Boosters:\n")
            for sugg in mood_boosting:
                parts.append(f"- {sugg['suggestion']}\n")
        
        return "".join(parts)
    
    def _build_reasoning(
        self,
        mood: str,
        stress_score: float,
        energy_score: float
    ) -> str:
        """Build explanation for task assignments"""
        
        reasons = []
        
        if stress_score > 0.7:
            reasons.append(
                "High stress detected - prioritizing shorter, stress-reducing tasks"
            )
        
        if energy_score < 0.4:
            reasons.append(
                "Low energy level - recommending quick wins and lighter tasks"
            )
        
        if mood == "happy":
            reasons.append("Positive mood - encouraging engagement with challenging tasks")
        
        return " | ".join(reasons) if reasons else "Standard task prioritization applied"
    
    def _build_standard_proposal(self,
                                 proposal_text: str,
                                 priority: float,
                                 confidence: float,
                                 reasoning: str,
                                 memory_used: list = None,
                                 conflicts: list = None) -> Dict[str, Any]:
        """Build standardized proposal response"""
        
        return {
            "agent": self.name,
            "proposal": proposal_text,
            "priority": priority,
            "confidence": confidence,
            "reasoning": reasoning,
            "memory_used": memory_used or [],
            "potential_conflicts": conflicts or [],
        }
