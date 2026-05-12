"""
Health Agent - Suggests physical activity and wellness
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthAgent(BaseAgent):
    """Agent that suggests health activities based on mood and energy"""
    
    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("health", llm, memory_system)
        
        # Activity recommendations by mood/energy
        self.activity_map = {
            ("stressed", "low"): {
                "activity": "15-minute light walk or gentle yoga",
                "intensity": "low",
                "duration": 15,
                "priority": 0.75
            },
            ("stressed", "high"): {
                "activity": "45-minute running or gym workout",
                "intensity": "medium",
                "duration": 45,
                "priority": 0.85
            },
            ("tired", "low"): {
                "activity": "10-minute stretching or rest day",
                "intensity": "very_low",
                "duration": 10,
                "priority": 0.9
            },
            ("energetic", "high"): {
                "activity": "60-minute intense gym workout",
                "intensity": "high",
                "duration": 60,
                "priority": 0.95
            },
            ("neutral", "medium"): {
                "activity": "30-minute regular workout",
                "intensity": "medium",
                "duration": 30,
                "priority": 0.7
            },
        }
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate health activity suggestion
        
        Args:
            state: Workflow state with mood_data
        
        Returns:
            Health recommendation with activity, intensity, duration
        """
        try:
            mood = state.get("mood_data", {}).get("mood", "neutral")
            stress_score = state.get("mood_data", {}).get("stress_score", 0.5)
            energy_score = state.get("mood_data", {}).get("energy_score", 0.5)
            
            # Get memory context - past workout completion rates
            memory_context = await self.get_memory_context(state)
            
            # Determine energy level
            energy_level = "high" if energy_score > 0.6 else "low" if energy_score < 0.4 else "medium"
            
            # Select activity based on mood and energy
            activity_key = (mood, energy_level)
            if activity_key not in self.activity_map:
                activity_key = ("neutral", "medium")
            
            activity_data = self.activity_map[activity_key]
            
            # Adjust priority based on completion history
            priority = activity_data["priority"]
            if memory_context.get("completion_rate"):
                priority *= memory_context["completion_rate"]
            
            confidence = 0.75 + (memory_context.get("data_points", 0) * 0.05)
            confidence = min(1.0, confidence)
            
            reasoning = self._build_reasoning(
                mood, energy_level, activity_data, memory_context
            )
            
            proposal = self._build_standard_proposal(
                proposal_text=activity_data["activity"],
                priority=priority,
                confidence=confidence,
                reasoning=reasoning,
                memory_used=[k for k in memory_context.keys()],
                conflicts=["schedule"]
            )
            
            # Add health-specific fields
            proposal["intensity"] = activity_data["intensity"]
            proposal["duration"] = activity_data["duration"]
            proposal["activity"] = activity_data["activity"]
            
            self.log_proposal(proposal)
            return proposal
            
        except Exception as e:
            logger.error(f"Error in Health Agent: {e}")
            return self._build_error_proposal(str(e))
    
    def _build_reasoning(self, mood: str, energy_level: str, 
                        activity_data: Dict, memory_context: Dict) -> str:
        """Build reasoning for health recommendation"""
        
        reasoning = f"Based on '{mood}' mood and {energy_level} energy, recommending {activity_data['activity']}. "
        
        if mood == "stressed" and energy_level == "low":
            reasoning += "Light activity reduces cortisol without depleting energy. "
        elif mood == "energetic" and energy_level == "high":
            reasoning += "High energy makes this optimal time for intense workout. "
        elif mood == "tired" and energy_level == "low":
            reasoning += "Minimal activity recommended to prevent further fatigue. "
        
        if memory_context.get("completion_rate"):
            rate = memory_context["completion_rate"]
            reasoning += f"Past data: user completed {rate*100:.0f}% of similar activities."
        
        return reasoning
    
    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        """Build error proposal with fallback"""
        return {
            "agent": self.name,
            "activity": "15-minute light walk",
            "intensity": "low",
            "duration": 15,
            "proposal": "15-minute light walk (default recommendation)",
            "priority": 0.5,
            "confidence": 0.3,
            "reasoning": f"Error during recommendation: {error_msg}. Using safe default.",
            "memory_used": [],
            "potential_conflicts": ["schedule"]
        }
