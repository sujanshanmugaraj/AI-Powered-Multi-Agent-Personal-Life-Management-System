"""
Finance Agent - Budget management and financial planning
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FinanceAgent(BaseAgent):
    """Agent that manages budget reminders and financial planning"""
    
    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("finance", llm, memory_system)
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate finance recommendation
        
        Args:
            state: Workflow state with mood_data and financial status
        
        Returns:
            Finance recommendation with priority based on mood
        """
        try:
            mood = state.get("mood_data", {}).get("mood", "neutral")
            stress_score = state.get("mood_data", {}).get("stress_score", 0.5)
            
            # Get memory context - budget status, past patterns
            memory_context = await self.get_memory_context(state)
            budget_status = memory_context.get("budget_status", "normal")
            
            # Adjust priority based on mood
            if stress_score > 0.7:
                # High stress - defer complex financial tasks
                proposal_text = "Defer detailed budget review to tomorrow. Quick check: balance is sufficient."
                priority = 0.3
                confidence = 0.85
                reasoning = "High stress detected. Complex financial tasks increase anxiety. Review can wait."
                potential_conflicts = []
            elif stress_score < 0.3:
                # Low stress - time for detailed review
                proposal_text = "Conduct detailed budget review and spending analysis"
                priority = 0.8
                confidence = 0.9
                reasoning = "Low stress period. Good time for thorough financial review."
                potential_conflicts = []
            else:
                # Normal stress - quick check
                proposal_text = "Quick spending review (5 minutes). Check if on budget."
                priority = 0.6
                confidence = 0.85
                reasoning = "Quick budget check keeps you informed without cognitive overload."
                potential_conflicts = []
            
            # Adjust if budget emergency
            if budget_status == "critical":
                priority = 0.95
                proposal_text = "URGENT: Budget review needed. Account balance critically low."
            
            proposal = self._build_standard_proposal(
                proposal_text=proposal_text,
                priority=priority,
                confidence=confidence,
                reasoning=reasoning,
                memory_used=[k for k in memory_context.keys()],
                conflicts=potential_conflicts
            )
            
            proposal["budget_status"] = budget_status
            
            self.log_proposal(proposal)
            return proposal
            
        except Exception as e:
            logger.error(f"Error in Finance Agent: {e}")
            return self._build_error_proposal(str(e))
    
    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        """Build error proposal with fallback"""
        return {
            "agent": self.name,
            "proposal": "Quick budget check (default)",
            "priority": 0.4,
            "confidence": 0.3,
            "reasoning": f"Error during recommendation: {error_msg}. Using minimal default.",
            "memory_used": [],
            "potential_conflicts": [],
            "budget_status": "unknown"
        }
