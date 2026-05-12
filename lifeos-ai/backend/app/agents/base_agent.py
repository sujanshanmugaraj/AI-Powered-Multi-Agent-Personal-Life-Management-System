"""
Base agent class - all agents inherit from this
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, llm: Any = None, memory_system: Any = None):
        """
        Initialize agent
        
        Args:
            name: Agent name (e.g., "mood", "health")
            llm: Language model instance
            memory_system: Memory system for context retrieval
        """
        self.name = name
        self.llm = llm
        self.memory = memory_system
    
    @abstractmethod
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposal based on current state
        
        Args:
            state: Current workflow state
        
        Returns:
            Standardized proposal dict with keys:
            - agent: Agent name
            - proposal: Recommendation text
            - priority: 0.0-1.0
            - confidence: 0.0-1.0
            - reasoning: Explanation
            - memory_used: List of memory sources
            - potential_conflicts: List of agent names
        """
        raise NotImplementedError
    
    async def get_memory_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant context from memory
        
        Args:
            state: Current workflow state
        
        Returns:
            Context dict with relevant past decisions/data
        """
        if self.memory is None:
            return {}
        
        try:
            context = await self.memory.retrieve(
                user_id=state.get("user_id"),
                query=f"{self.name}_agent_context",
                agent_name=self.name
            )
            return context
        except Exception as e:
            logger.error(f"Error retrieving memory context: {e}")
            return {}
    
    def _build_standard_proposal(self, 
                                 proposal_text: str,
                                 priority: float,
                                 confidence: float,
                                 reasoning: str,
                                 memory_used: list = None,
                                 conflicts: list = None) -> Dict[str, Any]:
        """
        Build standardized proposal response
        
        Args:
            proposal_text: The recommendation
            priority: 0.0-1.0 importance score
            confidence: 0.0-1.0 confidence level
            reasoning: Why this proposal
            memory_used: List of memory sources
            conflicts: List of potential conflicting agents
        
        Returns:
            Standardized proposal dict
        """
        return {
            "agent": self.name,
            "proposal": proposal_text,
            "priority": min(1.0, max(0.0, priority)),  # Clamp 0-1
            "confidence": min(1.0, max(0.0, confidence)),  # Clamp 0-1
            "reasoning": reasoning,
            "memory_used": memory_used or [],
            "potential_conflicts": conflicts or []
        }
    
    async def validate_proposal(self, proposal: Dict[str, Any]) -> bool:
        """
        Validate proposal format
        
        Args:
            proposal: Proposal dict to validate
        
        Returns:
            True if valid, False otherwise
        """
        required_keys = {"agent", "proposal", "priority", "confidence", "reasoning"}
        return all(key in proposal for key in required_keys)
    
    def log_proposal(self, proposal: Dict[str, Any]):
        """Log agent proposal for debugging"""
        logger.info(f"Agent {self.name} proposal:")
        logger.info(f"  Priority: {proposal['priority']:.2f}")
        logger.info(f"  Confidence: {proposal['confidence']:.2f}")
        logger.info(f"  Proposal: {proposal['proposal']}")
