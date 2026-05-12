"""
Learning Agent - Goal tracking and study session recommendations
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LearningAgent(BaseAgent):
    """Agent that tracks learning goals and suggests study sessions"""
    
    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("learning", llm, memory_system)
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate learning recommendation
        
        Args:
            state: Workflow state with goals, mood_data, and deadline info
        
        Returns:
            Learning session recommendation with duration and subject
        """
        try:
            mood = state.get("mood_data", {}).get("mood", "neutral")
            stress_score = state.get("mood_data", {}).get("stress_score", 0.5)
            energy_score = state.get("mood_data", {}).get("energy_score", 0.5)
            
            # Get memory context - goals, deadlines, completion rates
            memory_context = await self.get_memory_context(state)
            goals = memory_context.get("active_goals", [])
            
            if not goals:
                return self._no_goals_proposal()
            
            # Find most urgent goal
            primary_goal = goals[0] if goals else None
            deadline_urgency = memory_context.get("deadline_urgency", 0.5)
            
            # Adjust study duration based on stress and energy
            if stress_score > 0.7:
                duration = 30  # Shorter sessions when stressed
                mode = "review"
            elif energy_score > 0.7:
                duration = 90  # Longer sessions when energetic
                mode = "deep"
            else:
                duration = 60  # Regular sessions
                mode = "regular"
            
            proposal_text = f"{duration}-minute {primary_goal['subject']} study session ({mode} mode)"
            
            # Calculate priority based on deadline
            priority = 0.7 + (deadline_urgency * 0.25)
            priority = min(1.0, priority)
            
            confidence = 0.8 + (len(memory_context.get("completion_history", [])) * 0.02)
            confidence = min(1.0, confidence)
            
            reasoning = self._build_reasoning(
                primary_goal, duration, mode, stress_score, 
                energy_score, deadline_urgency, memory_context
            )
            
            proposal = self._build_standard_proposal(
                proposal_text=proposal_text,
                priority=priority,
                confidence=confidence,
                reasoning=reasoning,
                memory_used=[k for k in memory_context.keys()],
                conflicts=["schedule", "health"]
            )
            
            proposal["subject"] = primary_goal.get("subject", "General Learning")
            proposal["duration"] = duration
            proposal["study_mode"] = mode
            proposal["goal_id"] = primary_goal.get("id")
            
            self.log_proposal(proposal)
            return proposal
            
        except Exception as e:
            logger.error(f"Error in Learning Agent: {e}")
            return self._build_error_proposal(str(e))
    
    def _build_reasoning(self, goal: Dict, duration: int, mode: str, 
                        stress_score: float, energy_score: float,
                        deadline_urgency: float, memory_context: Dict) -> str:
        """Build reasoning for learning recommendation"""
        
        reasoning = f"Goal: {goal.get('subject', 'Learning')}. "
        reasoning += f"Recommending {duration}-minute {mode} session. "
        
        if stress_score > 0.7:
            reasoning += "High stress → shorter session, review mode to reduce cognitive load. "
        elif energy_score > 0.7:
            reasoning += "High energy → longer deep learning session is optimal. "
        
        if deadline_urgency > 0.8:
            reasoning += "Deadline is urgent - prioritize this learning goal. "
        
        completion_history = memory_context.get("completion_history", [])
        if completion_history:
            completion_rate = sum(completion_history) / len(completion_history)
            reasoning += f"Past completion rate: {completion_rate*100:.0f}%."
        
        return reasoning
    
    def _no_goals_proposal(self) -> Dict[str, Any]:
        """Return proposal when no active goals"""
        return {
            "agent": self.name,
            "proposal": "No active learning goals set",
            "priority": 0.0,
            "confidence": 1.0,
            "reasoning": "User has not set any learning goals yet.",
            "memory_used": [],
            "potential_conflicts": [],
            "subject": "N/A",
            "duration": 0,
            "study_mode": "none"
        }
    
    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        """Build error proposal with fallback"""
        return {
            "agent": self.name,
            "proposal": "30-minute general learning session",
            "priority": 0.5,
            "confidence": 0.3,
            "reasoning": f"Error during recommendation: {error_msg}. Using default.",
            "memory_used": [],
            "potential_conflicts": ["schedule", "health"],
            "subject": "General Learning",
            "duration": 30,
            "study_mode": "regular"
        }
