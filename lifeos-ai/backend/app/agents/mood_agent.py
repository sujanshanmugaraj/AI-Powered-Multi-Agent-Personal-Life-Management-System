"""
Mood Agent - Detects user emotional state from natural, colloquial, multilingual text.

Handles:
  - Formal English:   "I am feeling stressed today"
  - Casual English:   "bro im so done, meh, hyped, kill it"
  - Hindi/Hinglish:   "yaar thaka hoon, bilkul thak gaya"
  - Emojis:           😭 😤 💪 🔥 😴 🥱
  - Intensifiers:     very, so, super, bahut, zyada, ekdum
"""

from app.agents.base_agent import BaseAgent
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


# ── Keyword banks ──────────────────────────────────────────────────────────
# Each list maps words/phrases/emojis to a mood category.
# Add as many synonyms, slang, Hindi, Hinglish words as needed.

MOOD_KEYWORDS: Dict[str, list] = {
    "stressed": [
        # English formal
        "stress", "stressed", "anxious", "anxiety", "overwhelmed", "overloaded",
        "worried", "worrying", "tense", "pressure", "burnout", "burnt out",
        "panic", "panicking", "freak out", "freaking out", "can't cope",
        # English casual/slang
        "losing it", "losing my mind", "going crazy", "too much", "drowning",
        "swamped", "slammed", "crushed", "done", "so done", "deadline",
        "bro too much", "man its a lot",
        # Emojis
        "😤", "😰", "😨", "😱", "😓", "🤯",
        # Hindi / Hinglish
        "tension", "takleef", "pareshaan", "pareshan", "bahut kaam", "zyada kaam",
        "dimag kharab", "dimak kharab", "ghutan", "ghabrahat",
    ],
    "tired": [
        # English formal
        "tired", "exhausted", "fatigued", "drained", "weary", "lethargic",
        "sluggish", "sleepy", "drowsy", "low energy", "no energy",
        # English casual/slang
        "meh", "blah", "dead", "dead tired", "wiped", "wiped out",
        "burnt", "zonked", "out of it", "barely awake", "can't keep eyes open",
        "dragging", "groggy", "zombie", "numb",
        # Emojis
        "😴", "🥱", "😪", "💤",
        # Hindi / Hinglish
        "thaka", "thaka hua", "thak gaya", "thak gayi", "thaki", "bahut thaka",
        "neend", "neend nahi", "nahi soya", "so nahi paya", "raat ko",
        "uthna nahi tha", "bore", "bored", "aaj kuch nahi",
    ],
    "energetic": [
        # English formal
        "energetic", "motivated", "productive", "focused", "alert", "vibrant",
        "enthusiastic", "driven", "inspired", "refreshed", "recharged",
        # English casual/slang
        "hyped", "pumped", "fired up", "let's go", "ready to go", "kill it",
        "crush it", "smash it", "beast mode", "on fire", "on a roll",
        "killing it", "ready to crush", "game on", "go time", "grind time",
        "grind", "let's get it", "100%", "all in", "locked in",
        # Emojis
        "💪", "🔥", "⚡", "🚀", "😤", "💥",
        # Hindi / Hinglish
        "josh", "mast", "zabardast", "bindaas", "full on", "ekdum ready",
        "dum hai", "aaj mazaa aayega", "kuch karenge aaj",
    ],
    "happy": [
        # English formal
        "happy", "joyful", "content", "pleased", "cheerful", "delighted",
        "elated", "positive", "optimistic", "grateful", "blessed",
        # English casual/slang
        "great", "awesome", "amazing", "fantastic", "wonderful", "good vibes",
        "loving it", "stoked", "thrilled", "over the moon", "vibing",
        "feels good", "feeling good", "good day", "best day",
        # Simple everyday happy words
        "good", "fine", "okay", "ok", "alright", "decent", "not bad",
        "doing well", "doing good", "pretty good", "all good", "going well",
        "nice day", "lovely", "solid", "pleasant",
        # Emojis
        "😄", "😁", "🥳", "🎉", "😊", "😍", "❤️", "🌟",
        # Hindi / Hinglish
        "khush", "mast hu", "bahut accha", "sab theek", "badhiya",
        "aaj acha din hai", "maja aa raha", "accha", "theek", "theek hai",
    ],
    "sad": [
        # English formal
        "sad", "depressed", "down", "unhappy", "miserable", "hopeless",
        "dejected", "gloomy", "melancholy", "heartbroken",
        # English casual/slang
        "not okay", "not good", "rough", "tough day", "rough day",
        "it sucks", "everything sucks", "low", "feeling low",
        # Emojis
        "😔", "😢", "😭", "💔", "😞", "😿",
        # Hindi / Hinglish
        "dukhi", "udaas", "rona aa raha", "dil nahi lag raha",
        "kuch bhi acha nahi lag raha",
    ],
    "calm": [
        # English formal
        "calm", "peaceful", "relaxed", "serene", "tranquil", "at ease",
        "composed", "steady", "balanced",
        # English casual/slang
        "chill", "chilling", "chilled out", "laid back", "easygoing",
        "no worries", "all good", "taking it easy",
        # Emojis
        "😌", "🧘", "☮️", "🌿",
        # Hindi / Hinglish
        "shant", "sukoon", "aram se", "thanda", "bilkul thanda",
    ],
}

# Intensifier words that boost scores
INTENSIFIERS = [
    "very", "extremely", "so", "really", "super", "quite", "totally",
    "completely", "absolutely", "insanely", "ridiculously", "mega",
    # Hindi
    "bahut", "zyada", "ekdum", "bilkul", "pura", "poora", "aur bhi",
]

# Negation words — if present before a mood keyword, invert it
NEGATIONS = [
    "not", "no", "never", "don't", "dont", "didn't", "didn't", "can't",
    "cant", "nahi", "na", "naa",
]

# Scores per mood: (stress, energy)
MOOD_SCORES: Dict[str, Tuple[float, float]] = {
    "stressed":  (0.80, 0.35),
    "anxious":   (0.85, 0.40),
    "tired":     (0.25, 0.20),
    "energetic": (0.10, 0.90),
    "happy":     (0.08, 0.75),
    "sad":       (0.55, 0.25),
    "calm":      (0.15, 0.60),
    "neutral":   (0.25, 0.50),  # was 0.50 — neutral is NOT stressed
}


class MoodAgent(BaseAgent):
    """Agent that detects and classifies user emotional state from natural text."""

    def __init__(self, llm: Any = None, memory_system: Any = None):
        super().__init__("mood", llm, memory_system)

    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_text = state.get("user_text", "")
            memory_context = await self.get_memory_context(state)

            mood, score_map = self._detect_mood(user_text)
            stress_score, energy_score = self._get_scores(mood, user_text)
            confidence = self._calculate_confidence(user_text, mood, score_map)
            reasoning = self._build_reasoning(user_text, mood, stress_score, energy_score, memory_context)

            proposal = self._build_standard_proposal(
                proposal_text=f"Detected mood: {mood}. Stress level: {stress_score:.2f}, Energy level: {energy_score:.2f}",
                priority=1.0,
                confidence=confidence,
                reasoning=reasoning,
                memory_used=list(memory_context.keys()),
                conflicts=[],
            )
            proposal["mood"]         = mood
            proposal["stress_score"] = stress_score
            proposal["energy_score"] = energy_score

            self.log_proposal(proposal)
            return proposal

        except Exception as e:
            logger.error(f"Error in Mood Agent: {e}", exc_info=True)
            return self._build_error_proposal(str(e))

    # ── Core detection ────────────────────────────────────────────────────

    def _detect_mood(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Score each mood category by counting keyword matches.
        Applies intensifiers (multiplier) and simple negation detection.
        Returns (dominant_mood, score_map).
        """
        text_lower = text.lower()
        words = text_lower.split()

        # Count intensifiers using full-word matching (not substring)
        word_set = set(words)
        intensifier_boost = sum(1 for w in INTENSIFIERS if w in word_set)

        scores: Dict[str, float] = {m: 0.0 for m in MOOD_KEYWORDS}

        for mood, keywords in MOOD_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    # Check for negation in the 3 words before the keyword
                    kw_pos = text_lower.find(kw)
                    prefix = text_lower[max(0, kw_pos - 25): kw_pos]
                    negated = any(neg in prefix.split() for neg in NEGATIONS)

                    hit = -1.0 if negated else 1.0
                    hit *= (1.0 + intensifier_boost * 0.3)   # boost per intensifier
                    scores[mood] += hit

        # If no signal at all → neutral
        if all(v <= 0 for v in scores.values()):
            return "neutral", {m: 0 for m in scores}

        # Suppress negative scores
        scores = {m: max(0.0, v) for m, v in scores.items()}
        dominant = max(scores, key=scores.get)
        return dominant, scores

    def _get_scores(self, mood: str, text: str) -> Tuple[float, float]:
        """Return (stress_score, energy_score) for a mood, adjusted by intensifiers."""
        stress, energy = MOOD_SCORES.get(mood, (0.5, 0.5))

        word_set = set(text.lower().split())
        intensifier_count = sum(1 for w in INTENSIFIERS if w in word_set)

        # Stronger intensifiers push stress up / energy in expected direction
        if mood in ("stressed", "anxious", "sad"):
            stress  = min(1.0, stress  + intensifier_count * 0.05)
            energy  = max(0.0, energy  - intensifier_count * 0.03)
        elif mood in ("energetic", "happy"):
            energy  = min(1.0, energy  + intensifier_count * 0.05)
            stress  = max(0.0, stress  - intensifier_count * 0.03)
        elif mood in ("tired"):
            energy  = max(0.0, energy  - intensifier_count * 0.04)

        return round(stress, 2), round(energy, 2)

    def _calculate_confidence(self, text: str, mood: str, score_map: Dict[str, float]) -> float:
        """Higher confidence for longer text, clear mood signals, and non-neutral."""
        confidence = 0.55

        if len(text) > 15:  confidence += 0.10
        if len(text) > 40:  confidence += 0.10
        if mood != "neutral": confidence += 0.15

        # If top mood score dominates clearly
        scores = list(score_map.values())
        top = max(scores) if scores else 0
        if top >= 3: confidence += 0.10

        return round(min(1.0, confidence), 2)

    def _build_reasoning(self, text: str, mood: str, stress: float,
                          energy: float, memory_context: Dict) -> str:
        lines = [f"Detected '{mood}' mood from your input."]

        mood_comments = {
            "stressed":  f"Stress signals found — stress={round(stress*100)}%, energy={round(energy*100)}%.",
            "tired":     f"Fatigue indicators detected — energy is low ({round(energy*100)}%).",
            "energetic": f"High energy detected ({round(energy*100)}%) — great time for productive tasks!",
            "happy":     f"Positive mood detected — stress low ({round(stress*100)}%), energy good ({round(energy*100)}%).",
            "sad":       f"Low mood detected — plan will be gentle and supportive.",
            "calm":      f"Calm and balanced state — ideal for focused work.",
            "neutral":   f"Neutral baseline — balanced plan suggested.",
        }
        lines.append(mood_comments.get(mood, ""))

        # Historical context
        avg_stress = memory_context.get("avg_stress_7d")
        if avg_stress is not None:
            if stress > avg_stress + 0.15:
                lines.append(f"Today is more stressful than your 7-day average ({round(avg_stress*100)}%).")
            elif stress < avg_stress - 0.15:
                lines.append(f"You seem less stressed than usual (avg {round(avg_stress*100)}%) — good sign!")

        return " ".join(filter(None, lines))

    def _build_error_proposal(self, error_msg: str) -> Dict[str, Any]:
        return {
            "agent":              self.name,
            "mood":               "neutral",
            "stress_score":       0.5,
            "energy_score":       0.5,
            "confidence":         0.3,
            "proposal":           "Unable to detect mood, defaulting to neutral",
            "reasoning":          f"Error during mood detection: {error_msg}. Using neutral defaults.",
            "memory_used":        [],
            "potential_conflicts": [],
            "priority":           1.0,
        }
