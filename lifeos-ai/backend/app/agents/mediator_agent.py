"""
Mediator Agent - Conflict resolution and final human-friendly plan creation.

Produces natural-language, adaptive daily plans — NOT raw agent data dumps.
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import logging
import random

logger = logging.getLogger(__name__)


# ── Human-friendly task templates ──────────────────────────────────────────
# Each key is a (mood, energy_level) tuple or just a mood.
# Values are lists of natural-language variants so plans feel fresh each time.

GREET_TEMPLATES = {
    "stressed": [
        "Take a slow breath — today's plan is designed to ease your load 🌿",
        "You're carrying a lot. This plan gives you space to recover 💙",
        "Rough day? Here's a gentle but productive plan to get through it 🤝",
    ],
    "tired": [
        "Low energy today — keeping it light and manageable for you 🌙",
        "Rest is part of the plan. Here's a gentle schedule ☕",
        "Tired but still here — this plan respects that 💤",
    ],
    "energetic": [
        "You're fired up! Let's make the most of this energy ⚡",
        "High energy day — time to get things DONE 🚀",
        "Feeling great? Let's channel that into a productive day 💪",
    ],
    "happy": [
        "Great vibes today! Here's a balanced plan to keep them going 😄",
        "Happy days are productive days — here's your schedule 🌟",
    ],
    "calm": [
        "Calm and focused — perfect for deep work today 🎯",
        "Steady energy. Let's use it well 🧘",
    ],
    "neutral": [
        "Steady day ahead — here's a balanced plan to keep you on track 📋",
        "Not too high, not too low — a solid day's plan 📅",
    ],
}

HEALTH_LABELS = {
    "15-minute light walk":         "🚶 15-min light walk (great for clearing your head)",
    "gentle yoga":                  "🧘 Gentle yoga session (stress release)",
    "10-minute stretching":         "🤸 10-min stretching break",
    "rest day":                     "😴 Rest & recovery time",
    "30-minute regular workout":    "🏋️ 30-min workout session",
    "45-minute running":            "🏃 45-min run or cardio",
    "gym workout":                  "🏋️ Gym session",
    "60-minute intense gym workout":"💪 60-min intense workout",
}

FINANCE_LABELS = {
    "quick spending review":        "💰 5-min quick budget check (just a glance!)",
    "defer":                        "📌 Finance review deferred — focus on recovery today",
    "detailed budget review":       "📊 Detailed budget & spending review",
    "urgent":                       "🚨 Urgent: check your account balance",
}

BREAK_MESSAGES = [
    "☕ Short break — grab a coffee or stretch your legs",
    "🌬️ 5-min breather — step away from the screen",
    "💧 Hydration break — drink some water!",
    "👀 Eye rest — look out the window for a minute",
]

WIND_DOWN = [
    "🌙 Wind down — review what you accomplished today",
    "📓 End-of-day journal — note 3 wins from today",
    "🎵 Relax & decompress — you made it through the day",
]


def _friendly_health(proposal: str, mood: str, intensity: str) -> str:
    """Convert raw health proposal text into a friendly task label."""
    lower = proposal.lower()
    for key, label in HEALTH_LABELS.items():
        if key in lower:
            return label
    # Fallback: clean up the raw text
    return f"🏃 {proposal.strip()}"


def _friendly_finance(proposal: str, stress_score: float) -> str:
    """Convert raw finance proposal into a friendly task label."""
    lower = proposal.lower()
    if "defer" in lower or "tomorrow" in lower:
        return FINANCE_LABELS["defer"]
    if "urgent" in lower or "critical" in lower:
        return FINANCE_LABELS["urgent"]
    if "detailed" in lower or "thorough" in lower:
        return FINANCE_LABELS["detailed budget review"]
    return FINANCE_LABELS["quick spending review"]


def _friendly_learning(proposal: str, subject: str = None, duration: int = 30, mode: str = "regular") -> str:
    """Convert raw learning proposal into a friendly task label."""
    lower = proposal.lower()
    if "no active" in lower or "not set" in lower:
        return None  # skip — no goals set yet
    subj = subject or "your learning goal"
    emoji = "📚"
    if "code" in subj.lower() or "python" in subj.lower():
        emoji = "💻"
    elif "math" in subj.lower():
        emoji = "📐"
    mode_desc = {"deep": "deep focus session", "review": "light review session", "regular": "study session"}
    desc = mode_desc.get(mode, "study session")
    return f"{emoji} {duration}-min {subj} {desc}"


def _add_minutes(time_str: str, minutes: int) -> str:
    """Add minutes to HH:MM string."""
    try:
        h, m = map(int, time_str.split(":"))
        total = h * 60 + m + minutes
        return f"{total // 60:02d}:{total % 60:02d}"
    except Exception:
        return time_str


class MediatorAgent(BaseAgent):
    """Resolves conflicts and builds a human-friendly, adaptive daily plan."""

    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("mediator", llm, memory_system)

    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            mood_data        = state.get("mood_data", {})
            all_proposals    = state.get("agent_proposals", {})
            schedule_conflicts = state.get("schedule_conflicts", [])

            conflicts    = self._identify_conflicts(all_proposals)
            resolved     = self._resolve_conflicts(all_proposals, conflicts, mood_data, schedule_conflicts)
            final_plan   = self._build_friendly_plan(resolved, mood_data, all_proposals)
            explanation  = self._build_explanation(conflicts, final_plan, mood_data)

            proposal = self._build_standard_proposal(
                proposal_text="Final personalized daily plan created",
                priority=1.0,
                confidence=0.9,
                reasoning=explanation,
                memory_used=["mood_data", "all_proposals"],
                conflicts=[],
            )
            proposal["final_plan"]        = final_plan
            proposal["conflicts_resolved"] = len(conflicts)
            proposal["plan_items"]         = len(final_plan)

            self.log_proposal(proposal)
            return proposal

        except Exception as e:
            logger.error(f"Error in Mediator Agent: {e}", exc_info=True)
            return self._build_error_proposal(str(e))

    # ── Conflict detection (unchanged logic) ─────────────────────────────

    def _identify_conflicts(self, proposals: Dict) -> List[Dict]:
        conflicts = []
        for agent_name, proposal in proposals.items():
            if isinstance(proposal, dict):
                pot = proposal.get("potential_conflicts", [])
                if pot:
                    conflicts.append({
                        "agent":         agent_name,
                        "conflicts_with": pot,
                        "proposal":      proposal.get("proposal", ""),
                        "priority":      proposal.get("priority", 0),
                    })
        return conflicts

    def _resolve_conflicts(self, proposals: Dict, conflicts: List[Dict],
                           mood_data: Dict, schedule_conflicts: List[Dict]) -> List[Dict]:
        stress = mood_data.get("stress_score", 0.5)
        sorted_proposals = sorted(
            [(n, p) for n, p in proposals.items() if isinstance(p, dict)],
            key=lambda x: x[1].get("priority", 0),
            reverse=True,
        )
        resolved = []
        for agent_name, proposal in sorted_proposals:
            if any(c["agent"] == agent_name for c in conflicts):
                adapted = self._adapt_proposal(proposal, stress)
                resolved.append(adapted)
            else:
                resolved.append(proposal)
        return resolved

    def _adapt_proposal(self, proposal: Dict, stress_score: float) -> Dict:
        adapted = proposal.copy()
        if stress_score > 0.7:
            if "duration" in adapted:
                adapted["duration"] = max(10, int(adapted["duration"] * 0.6))
            intensity_map = {"very_high": "high", "high": "medium", "medium": "low", "low": "very_low"}
            if "intensity" in adapted:
                adapted["intensity"] = intensity_map.get(adapted["intensity"], adapted["intensity"])
            adapted["stress_adapted"] = True
        return adapted

    # ── The main plan builder ─────────────────────────────────────────────

    def _build_friendly_plan(self, resolved_plan: List[Dict],
                              mood_data: Dict, all_proposals: Dict) -> List[Dict]:
        """
        Build a natural-language, human-friendly daily schedule.
        Skips agent-internal data (mood raw text, schedule availability text).
        Each plan item has: time, task, duration, emoji-friendly label.
        """
        mood         = mood_data.get("mood", "neutral")
        stress       = mood_data.get("stress_score", 0.5)
        energy       = mood_data.get("energy_score", 0.5)
        final_plan: List[Dict] = []
        current_time = "09:00"

        # ── 1. Greeting / intention block ─────────────────────────────────
        greeting_options = GREET_TEMPLATES.get(mood, GREET_TEMPLATES["neutral"])
        greeting = random.choice(greeting_options)
        final_plan.append({
            "time":     f"{current_time}-{_add_minutes(current_time, 5)}",
            "task":     greeting,
            "duration": 5,
            "agent":    "mediator",
            "priority": 1.0,
            "reason":   "Daily intention setting",
        })
        current_time = _add_minutes(current_time, 5)

        # ── 2. Stress relief / morning ritual if stressed ─────────────────
        if stress > 0.6:
            final_plan.append({
                "time":     f"{current_time}-{_add_minutes(current_time, 10)}",
                "task":     "🧘 Morning breathing or quick meditation (5–10 mins)",
                "duration": 10,
                "agent":    "health",
                "priority": 0.95,
                "reason":   "Stress reduction before starting tasks",
            })
            current_time = _add_minutes(current_time, 10)

        # ── 3. Process each agent proposal in priority order ─────────────
        agents_processed = set(["mood"])   # skip mood agent's raw data block

        for proposal in resolved_plan:
            if not isinstance(proposal, dict):
                continue

            agent = proposal.get("agent", "")

            # Skip mood and schedule agents — they don't produce user-facing tasks
            if agent in ("mood", "schedule", "mediator") or agent in agents_processed:
                continue

            agents_processed.add(agent)

            task_text = None
            duration  = proposal.get("duration", 30)

            # ── Health task ───────────────────────────────────────────────
            if agent == "health":
                raw = proposal.get("proposal", "")
                activity = proposal.get("activity", raw)
                intensity = proposal.get("intensity", "medium")
                task_text = _friendly_health(activity or raw, mood, intensity)
                # If high stress adapted the duration
                if proposal.get("stress_adapted"):
                    task_text += " (shortened for today)"

            # ── Finance task ──────────────────────────────────────────────
            elif agent == "finance":
                raw = proposal.get("proposal", "")
                task_text = _friendly_finance(raw, stress)
                duration  = 5 if "quick" in task_text.lower() else 15

            # ── Learning task ─────────────────────────────────────────────
            elif agent == "learning":
                raw      = proposal.get("proposal", "")
                subject  = proposal.get("subject", "")
                mode     = proposal.get("study_mode", "regular")
                task_text = _friendly_learning(raw, subject, duration, mode)

            # ── Any other custom agent ────────────────────────────────────
            else:
                raw = proposal.get("proposal", "")
                if raw and "detected mood" not in raw.lower() and "available time blocks" not in raw.lower():
                    task_text = f"📌 {raw}"

            # Only add if we have a meaningful task
            if not task_text:
                continue

            end_time = _add_minutes(current_time, duration)
            final_plan.append({
                "time":     f"{current_time}-{end_time}",
                "task":     task_text,
                "duration": duration,
                "agent":    agent,
                "priority": proposal.get("priority", 0.5),
                "reason":   self._simple_reason(proposal, mood, stress, energy),
            })
            current_time = end_time

            # Short break after long tasks (>= 45 min)
            if duration >= 45:
                break_msg = random.choice(BREAK_MESSAGES)
                break_end = _add_minutes(current_time, 10)
                final_plan.append({
                    "time":     f"{current_time}-{break_end}",
                    "task":     break_msg,
                    "duration": 10,
                    "agent":    "mediator",
                    "priority": 0.5,
                    "reason":   "Recovery between intense tasks",
                })
                current_time = break_end

        # ── 4. Wind-down block at end ─────────────────────────────────────
        wind_down_time = "20:30"   # fixed near end of day
        final_plan.append({
            "time":     f"{wind_down_time}-{_add_minutes(wind_down_time, 15)}",
            "task":     random.choice(WIND_DOWN),
            "duration": 15,
            "agent":    "mediator",
            "priority": 0.6,
            "reason":   "End-of-day reflection",
        })

        return final_plan

    # ── Helpers ───────────────────────────────────────────────────────────

    def _simple_reason(self, proposal: Dict, mood: str, stress: float, energy: float) -> str:
        """Generate a short, plain-English reason for this task."""
        agent = proposal.get("agent", "")
        if agent == "health":
            if stress > 0.7:
                return "Light activity helps lower cortisol when you're stressed"
            elif energy > 0.7:
                return "High energy — great time to work out"
            return "Regular movement keeps you focused and healthy"
        elif agent == "finance":
            if stress > 0.7:
                return "Quick check only — no heavy thinking when stressed"
            return "Staying on top of finances reduces long-term stress"
        elif agent == "learning":
            if stress > 0.7:
                return "Shorter session to keep learning without overloading"
            return "Consistent study builds momentum towards your goals"
        return proposal.get("reasoning", "")[:80] if proposal.get("reasoning") else ""

    def _build_explanation(self, conflicts: List[Dict], final_plan: List[Dict], mood_data: Dict) -> str:
        mood   = mood_data.get("mood", "neutral")
        stress = mood_data.get("stress_score", 0.5)
        energy = mood_data.get("energy_score", 0.5)

        lines = []
        lines.append(f"Your plan for today is tailored to your '{mood}' mood "
                      f"(stress {round(stress*100)}%, energy {round(energy*100)}%).")

        if stress > 0.7:
            lines.append("High stress detected — recovery tasks are prioritised and heavy work is reduced.")
        elif energy > 0.7:
            lines.append("High energy today — plan includes productive and intensive sessions.")

        if conflicts:
            lines.append(f"{len(conflicts)} scheduling conflict(s) were resolved automatically.")

        lines.append(f"Your schedule has {len(final_plan)} items across the day.")
        return " ".join(lines)

    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        return {
            "agent":             self.name,
            "proposal":          "Unable to create final plan",
            "priority":          1.0,
            "confidence":        0.2,
            "reasoning":         f"Error during plan creation: {error_msg}",
            "memory_used":       [],
            "potential_conflicts": [],
            "final_plan":        [],
            "conflicts_resolved": 0,
            "plan_items":        0,
        }
