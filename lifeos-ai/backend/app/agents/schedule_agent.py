"""
Schedule Agent - Time block management and conflict detection
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ScheduleAgent(BaseAgent):
    """Agent that manages time blocks and detects scheduling conflicts"""
    
    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("schedule", llm, memory_system)
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schedule proposal with available time blocks
        
        Args:
            state: Workflow state with calendar and task proposals
        
        Returns:
            Available time slots and conflict information
        """
        try:
            # Get memory context - user calendar, time preferences
            memory_context = await self.get_memory_context(state)
            calendar = memory_context.get("calendar", [])
            user_preferences = state.get("user_preferences", {})
            
            # Parse calendar for free slots
            free_slots = self._find_free_slots(calendar)
            
            # Get other agent proposals to detect conflicts
            other_proposals = state.get("agent_proposals", {})
            conflicts = self._detect_conflicts(free_slots, other_proposals, calendar)
            
            # Build schedule suggestion
            schedule_suggestion = self._build_schedule(free_slots, other_proposals)
            
            proposal_text = f"Available time blocks: {self._format_slots(free_slots)}"
            if conflicts:
                proposal_text += f". {len(conflicts)} conflict(s) detected."
            
            priority = 0.9  # Schedule is critical
            confidence = 0.85 if calendar else 0.5
            
            reasoning = self._build_reasoning(free_slots, conflicts, memory_context)
            
            proposal = self._build_standard_proposal(
                proposal_text=proposal_text,
                priority=priority,
                confidence=confidence,
                reasoning=reasoning,
                memory_used=[k for k in memory_context.keys()],
                conflicts=[]
            )
            
            proposal["available_slots"] = free_slots
            proposal["conflicts"] = conflicts
            proposal["suggested_schedule"] = schedule_suggestion
            proposal["total_free_time"] = sum(slot["duration"] for slot in free_slots)
            
            self.log_proposal(proposal)
            return proposal
            
        except Exception as e:
            logger.error(f"Error in Schedule Agent: {e}")
            return self._build_error_proposal(str(e))
    
    def _find_free_slots(self, calendar: List[Dict]) -> List[Dict]:
        """Find free time slots in user calendar"""
        
        # Default: assume full day if no calendar
        if not calendar:
            return [
                {"start": "09:00", "end": "12:00", "duration": 180},
                {"start": "14:00", "end": "18:00", "duration": 240},
                {"start": "19:00", "end": "21:00", "duration": 120}
            ]
        
        # Sort calendar events by time
        sorted_events = sorted(calendar, key=lambda x: x.get("start", "00:00"))
        
        free_slots = []
        current_time = "09:00"  # Work day starts 9 AM
        end_of_day = "21:00"     # Work day ends 9 PM
        
        for event in sorted_events:
            event_start = event.get("start", "00:00")
            event_end = event.get("end", "00:00")
            
            if current_time < event_start:
                duration = self._time_diff(current_time, event_start)
                if duration > 15:  # Only count slots > 15 min
                    free_slots.append({
                        "start": current_time,
                        "end": event_start,
                        "duration": duration
                    })
            
            current_time = max(current_time, event_end)
        
        # Add final slot until end of day
        if current_time < end_of_day:
            duration = self._time_diff(current_time, end_of_day)
            if duration > 15:
                free_slots.append({
                    "start": current_time,
                    "end": end_of_day,
                    "duration": duration
                })
        
        return free_slots
    
    def _time_diff(self, start: str, end: str) -> int:
        """Calculate time difference in minutes"""
        try:
            start_h, start_m = map(int, start.split(":"))
            end_h, end_m = map(int, end.split(":"))
            return (end_h * 60 + end_m) - (start_h * 60 + start_m)
        except:
            return 0
    
    def _detect_conflicts(self, free_slots: List[Dict], 
                         proposals: Dict, calendar: List[Dict]) -> List[Dict]:
        """Detect scheduling conflicts between proposals"""
        
        conflicts = []
        
        # Get task durations from proposals
        tasks = []
        for agent_name, proposal in proposals.items():
            if isinstance(proposal, dict) and proposal.get("duration"):
                tasks.append({
                    "agent": agent_name,
                    "duration": proposal["duration"],
                    "name": proposal.get("proposal", "task")
                })
        
        total_free_time = sum(slot["duration"] for slot in free_slots)
        total_needed_time = sum(task["duration"] for task in tasks)
        
        if total_needed_time > total_free_time:
            conflicts.append({
                "type": "insufficient_time",
                "message": f"Total tasks need {total_needed_time}min but only {total_free_time}min available",
                "suggestion": "Reduce task durations or defer some tasks"
            })
        
        return conflicts
    
    def _build_schedule(self, free_slots: List[Dict], proposals: Dict) -> List[Dict]:
        """Build suggested schedule by fitting proposals into free slots"""
        
        # Sort proposals by priority (if available)
        sorted_proposals = sorted(
            proposals.items(),
            key=lambda x: x[1].get("priority", 0) if isinstance(x[1], dict) else 0,
            reverse=True
        )
        
        schedule = []
        slot_idx = 0
        
        for agent_name, proposal in sorted_proposals:
            if not isinstance(proposal, dict) or not proposal.get("duration"):
                continue
            
            required_duration = proposal["duration"]
            
            # Find suitable slot
            while slot_idx < len(free_slots):
                slot = free_slots[slot_idx]
                if slot["duration"] >= required_duration:
                    schedule.append({
                        "time": f"{slot['start']}-{slot['end']}",
                        "task": proposal.get("proposal", "task"),
                        "agent": agent_name,
                        "duration": required_duration
                    })
                    break
                slot_idx += 1
        
        return schedule
    
    def _format_slots(self, slots: List[Dict]) -> str:
        """Format free slots for display"""
        if not slots:
            return "No free time available"
        
        formatted = []
        for slot in slots[:3]:  # Show top 3 slots
            formatted.append(f"{slot['start']}-{slot['end']} ({slot['duration']}min)")
        
        return ", ".join(formatted)
    
    def _build_reasoning(self, free_slots: List[Dict], 
                        conflicts: List[Dict], memory_context: Dict) -> str:
        """Build reasoning for schedule proposal"""
        
        reasoning = f"Found {len(free_slots)} free time blocks. "
        
        total_free = sum(slot["duration"] for slot in free_slots)
        reasoning += f"Total available: {total_free} minutes. "
        
        if conflicts:
            reasoning += f"{len(conflicts)} conflict(s) detected and flagged for mediator. "
        
        if memory_context.get("user_time_preference"):
            reasoning += f"User prefers {memory_context['user_time_preference']} work sessions."
        
        return reasoning
    
    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        """Build error proposal with fallback"""
        return {
            "agent": self.name,
            "proposal": "Unable to analyze schedule",
            "priority": 0.8,
            "confidence": 0.2,
            "reasoning": f"Error during schedule analysis: {error_msg}",
            "memory_used": [],
            "potential_conflicts": [],
            "available_slots": [],
            "conflicts": [],
            "suggested_schedule": [],
            "total_free_time": 0
        }
