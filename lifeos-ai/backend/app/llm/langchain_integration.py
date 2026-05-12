"""
LangChain integration for LLM interactions.
Supports colloquial/informal input and auto-detects the user's language,
responding in the same language.
"""

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared instruction appended to EVERY system prompt.
# Handles:
#   1. Colloquial / informal / slang input  (e.g. "feelin kinda meh rn lol")
#   2. Multilingual auto-detection          (Hindi, Tamil, Spanish, French, …)
# ---------------------------------------------------------------------------
LANGUAGE_INSTRUCTION = (
    "\n\n"
    "LANGUAGE & STYLE RULES (always follow these):\n"
    "1. The user may write in ANY language (English, Hindi, Tamil, Spanish, French, "
    "Arabic, Japanese, etc.) and in ANY style — formal, informal, slang, mixed-script "
    "(e.g. Hinglish, Tanglish), or abbreviations (lol, rn, tbh, idk, etc.).\n"
    "2. AUTO-DETECT the language of the user's message.\n"
    "3. ALWAYS reply in that SAME language (or the dominant language if mixed).\n"
    "4. Interpret colloquial phrases naturally:\n"
    "   - 'meh / blah / meh vibes' → low mood / neutral\n"
    "   - 'super hyped / lit / on fire' → very high energy / excitement\n"
    "   - 'stressed out / freaking out' → high stress\n"
    "   - 'chill / low-key' → relaxed / low energy\n"
    "   - 'kinda / sorta' → moderate degree\n"
    "   Extend this reasoning to equivalent phrases in any other language.\n"
    "5. Keep your response tone warm, natural, and matching the user's style "
    "(casual if they're casual, formal if they're formal)."
)


class LangChainLLM:
    """LangChain LLM wrapper for all agent interactions.

    All methods accept colloquial / multilingual user input and
    automatically respond in the detected language.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=False
        )
        self.memory = ConversationBufferMemory()

    # ------------------------------------------------------------------
    # Mood Analysis
    # ------------------------------------------------------------------
    async def analyze_mood(self, user_text: str) -> dict:
        """Analyze mood from user text.

        Handles informal, slang, and multilingual input.
        Returns JSON with mood, stress_score, energy_score, confidence, reasoning.
        """
        system_msg = (
            "You are an expert mood analyzer. Analyze the user's text and extract:\n"
            "1. Primary mood (happy, sad, stressed, neutral, excited, focused, etc.)\n"
            "2. Stress score (0-1)\n"
            "3. Energy score (0-1)\n"
            "4. Confidence (0-1)\n"
            "5. Detailed reasoning\n"
            "Return ONLY valid JSON:\n"
            "{\"mood\": \"\", \"stress_score\": 0.5, \"energy_score\": 0.5, "
            "\"confidence\": 0.8, \"reasoning\": \"\"}\n"
            "The 'reasoning' field should be written in the same language the user used."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template("{text}")
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(text=user_text)

        logger.info(f"LangChain mood analysis: {response}")
        return response

    # ------------------------------------------------------------------
    # Health Recommendation
    # ------------------------------------------------------------------
    async def generate_health_recommendation(self, mood: str, energy: float) -> str:
        """Generate health recommendation based on mood and energy.

        Responds in the same language as inferred from the mood descriptor.
        """
        system_msg = (
            "You are a friendly health and wellness coach. "
            "Given the user's current mood and energy level, suggest 2-3 specific, "
            "practical health activities for today. Be concise, warm, and actionable."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template(
                    "Mood: {mood}\nEnergy Level: {energy}"
                )
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(mood=mood, energy=energy)
        return response

    # ------------------------------------------------------------------
    # Finance Plan
    # ------------------------------------------------------------------
    async def generate_finance_plan(self, mood: str, available_tasks: list) -> str:
        """Generate a budget-friendly activity plan based on mood and tasks.

        Accepts and responds in any language.
        """
        system_msg = (
            "You are a practical finance advisor. "
            "Given the user's mood and their list of available tasks, "
            "suggest budget-friendly activities and spending tips for today. "
            "Be specific and encouraging."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template(
                    "Mood: {mood}\nAvailable tasks: {tasks}"
                )
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(mood=mood, tasks=str(available_tasks))
        return response

    # ------------------------------------------------------------------
    # Learning Goal
    # ------------------------------------------------------------------
    async def generate_learning_goal(self, mood: str, energy: float) -> str:
        """Suggest a learning task appropriate to mood and energy.

        Accepts colloquial mood descriptors in any language.
        """
        system_msg = (
            "You are an encouraging learning coach. "
            "Given the user's mood and energy level, suggest one achievable learning task "
            "for today. Explain briefly why it suits their current state."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template(
                    "Mood: {mood}\nEnergy: {energy}"
                )
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(mood=mood, energy=energy)
        return response

    # ------------------------------------------------------------------
    # Conflict Resolution
    # ------------------------------------------------------------------
    async def resolve_conflicts(self, proposals: list) -> str:
        """Use LLM to resolve conflicts between agent proposals.

        Produces a final harmonious plan; language follows dominant proposal language.
        """
        system_msg = (
            "You are a conflict resolution expert for daily planning. "
            "Given multiple agent proposals for a user's daily plan, resolve any conflicts "
            "and produce one clear, harmonious final plan. "
            "Consider mood, health, finance, learning, and schedule priorities. "
            "Be decisive and brief."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template("{proposals}")
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(proposals=str(proposals))
        return response

    # ------------------------------------------------------------------
    # Free-form Chat (colloquial / multilingual entry point)
    # ------------------------------------------------------------------
    async def chat(self, user_message: str) -> str:
        """General-purpose conversational endpoint.

        Accepts any language or style (slang, mixed script, etc.)
        and responds naturally in the same language.
        """
        system_msg = (
            "You are LifeOS, a warm and helpful AI personal assistant. "
            "Help the user with their day — planning, mood, health, finance, learning, "
            "or just having a conversation. Be supportive, concise, and friendly."
            + LANGUAGE_INSTRUCTION
        )

        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(system_msg),
                HumanMessagePromptTemplate.from_template("{message}")
            ]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt, memory=self.memory)
        response = await chain.arun(message=user_message)
        return response


# Global instance
langchain_llm = LangChainLLM()
