"""
LangGraph workflow for agent orchestration
"""

import logging
from typing import Dict, Any, List, Optional
from app.agents.mood_agent import MoodAgent
from app.agents.health_agent import HealthAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.learning_agent import LearningAgent
from app.agents.schedule_agent import ScheduleAgent
from app.agents.mediator_agent import MediatorAgent

logger = logging.getLogger(__name__)

class DailyPlannerGraph:
    """LangGraph workflow for daily planning"""

    def __init__(self):
        """Agents are created fresh per-request so they get live memory."""
        pass

    def _make_agents(self, memory_system=None):
        """Instantiate all agents with the given memory system."""
        return {
            "mood":     MoodAgent(memory_system=memory_system),
            "health":   HealthAgent(memory_system=memory_system),
            "finance":  FinanceAgent(memory_system=memory_system),
            "learning": LearningAgent(memory_system=memory_system),
            "schedule": ScheduleAgent(memory_system=memory_system),
            "mediator": MediatorAgent(memory_system=memory_system),
        }

    async def execute(self, user_id: int, user_text: str, date: str,
                      db=None) -> Dict[str, Any]:
        """
        Execute complete workflow for daily plan generation.

        Args:
            user_id:   User ID
            user_text: User's mood/status input
            date:      Date for the plan
            db:        SQLAlchemy Session — when provided, agents get real history

        Returns:
            Final plan and explanations
        """
        try:
            # Build memory system from the live DB session
            memory_system = None
            if db is not None:
                from app.memory.memory_system import MemorySystem
                memory_system = MemorySystem(db=db)

            agents = self._make_agents(memory_system)

            # Initialize state
            state = {
                "user_id":          user_id,
                "user_text":        user_text,
                "date":             date,
                "mood_data":        {},
                "agent_proposals":  {},
                "schedule_conflicts": [],
                "user_preferences": await self._load_user_preferences(user_id, memory_system),
            }

            # Step 1: Mood Agent
            logger.info("Step 1: Running Mood Agent...")
            mood_proposal = await agents["mood"].generate_proposal(state)
            state["mood_data"] = mood_proposal
            state["agent_proposals"]["mood"] = mood_proposal

            # Step 2: Parallel agents
            logger.info("Step 2: Running parallel agents...")
            parallel_results = await self._run_parallel_agents(state, agents)
            state["agent_proposals"].update(parallel_results)

            # Step 3: Detect conflicts
            logger.info("Step 3: Detecting conflicts...")
            conflicts = self._detect_conflicts(state)
            state["schedule_conflicts"] = conflicts

            # Step 4: Mediator
            logger.info("Step 4: Running Mediator Agent...")
            final_proposal = await agents["mediator"].generate_proposal(state)

            return {
                "status":            "success",
                "plan":              final_proposal.get("final_plan", []),
                "explanation":       final_proposal.get("reasoning", ""),
                "agent_proposals":   state["agent_proposals"],
                "conflicts_resolved": final_proposal.get("conflicts_resolved", 0),
            }

        except Exception as e:
            logger.error(f"Error executing workflow: {e}", exc_info=True)
            return {
                "status":      "error",
                "error":       str(e),
                "plan":        [],
                "explanation": "Error generating plan",
            }


    async def _run_parallel_agents(self, state: Dict[str, Any], agents: Dict) -> Dict[str, Any]:
        """Run health, finance, learning, schedule agents sequentially (parallel-ready)."""
        results = {}
        try:
            results["health"]   = await agents["health"].generate_proposal(state)
            results["finance"]  = await agents["finance"].generate_proposal(state)
            results["learning"] = await agents["learning"].generate_proposal(state)
            results["schedule"] = await agents["schedule"].generate_proposal(state)
        except Exception as e:
            logger.error(f"Error in parallel agents: {e}", exc_info=True)
        return results

    def _detect_conflicts(self, state: Dict[str, Any]) -> List[Dict]:
        """Detect scheduling conflicts from schedule agent output."""
        try:
            schedule_proposal = state["agent_proposals"].get("schedule", {})
            return schedule_proposal.get("conflicts", [])
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []

    async def _load_user_preferences(self, user_id: int,
                                     memory_system=None) -> Dict[str, Any]:
        """Load user preferences — uses memory when available."""
        try:
            if memory_system:
                prefs = await memory_system.retrieve(user_id, "preferences", agent_name="system")
                if prefs:
                    return prefs
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")

        return {
            "time_preference":      "morning",
            "intensity_preference": "medium",
            "break_frequency":      60,
        }

