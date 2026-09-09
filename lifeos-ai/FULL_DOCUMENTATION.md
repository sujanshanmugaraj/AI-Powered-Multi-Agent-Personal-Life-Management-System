# LifeOS AI - Complete Project Documentation
# AI-Powered Multi-Agent Personal Life Management System

## 1. PROJECT OVERVIEW

LifeOS AI is a personal life management system that orchestrates 7 specialized AI agents to help a user plan their day. Instead of one monolithic AI, different agents are experts in different life domains. They propose, conflict-detect, and a Mediator synthesizes everything into one human-friendly daily schedule.

### What Problem Does It Solve?

Most productivity apps give the same advice regardless of how you feel. LifeOS AI asks:
- How are you feeling right now? (mood check-in)
- What do you need to accomplish? (user tasks)
- What time is already taken? (busy slots)

It then tailors the entire day's plan to your emotional state:
- If STRESSED: shorter tasks, light exercise, deferred finance reviews
- If ENERGETIC: intense workouts, deep study sessions, ambitious tasks
- If TIRED: minimal activity, rest-focused schedule

### Core Philosophy

  Mood -> Context -> Personalized Plan

The system is adaptive: the more you use it, the better it understands you via:
- Historical mood trend analysis (7-day rolling averages)
- Task completion rate tracking per domain
- Epsilon-greedy bandit learning (reinforcement learning feedback loop)

---

## 2. HIGH-LEVEL ARCHITECTURE

```
+-------------------------------------------------------------+
|                   FRONTEND (React + Vite)                    |
|  Login -> Dashboard -> Mood Check-in -> Daily Plan -> History|
+---------------------------+---------------------------------+
                            | HTTP REST API
+---------------------------v---------------------------------+
|                   BACKEND (FastAPI)                          |
|  /api/v1/mood   /api/v1/daily-plan   /api/v1/feedback       |
+---------------------------+---------------------------------+
                            |
+---------------------------v---------------------------------+
|           MULTI-AGENT WORKFLOW (DailyPlannerGraph)           |
|                                                              |
|   Step 1: MoodAgent           reads user_text                |
|   Step 2a: HealthAgent    +                                  |
|   Step 2b: FinanceAgent   |  run after mood data ready       |
|   Step 2c: LearningAgent  |  (all read mood_data)            |
|   Step 2d: ScheduleAgent  |                                  |
|   Step 2e: TaskPlanner    +                                  |
|   Step 3: Conflict Detection                                 |
|   Step 4: MediatorAgent       synthesizes final plan         |
+---------------------------+---------------------------------+
                            |
+---------------------------v---------------------------------+
|                 MEMORY SYSTEM (SQLite via SQLAlchemy)        |
|   MoodLog  DailyPlan  Feedback  AgentAction  BanditReward    |
+-------------------------------------------------------------+
```

Files:
- Backend entry: backend/app/main.py
- API routes: backend/app/api/router.py
- Workflow: backend/app/workflows/daily_planner.py
- Agents: backend/app/agents/*.py
- Memory: backend/app/memory/memory_system.py
- Learning: backend/app/learning/bandit_learning.py
- LLM: backend/app/llm/langchain_integration.py
- Models: backend/app/models/database.py
- Schemas: backend/app/models/schemas.py
- Config: backend/app/config.py

---

## 3. CORE CONCEPT: MULTI-AGENT SYSTEMS

### What Is a Multi-Agent System?

A Multi-Agent System (MAS) is a paradigm where multiple autonomous software agents each have:
- Their own KNOWLEDGE (domain expertise)
- Their own GOALS (what they optimize for)
- Their own BEHAVIOR (how they decide)
- The ability to COMMUNICATE via standardized messages

Agent          | Domain Expertise     | What It Optimizes
-------------- | -------------------- | -----------------------------------------
MoodAgent      | Emotional NLP        | Accurate mood + energy classification
HealthAgent    | Exercise physiology  | Physical wellness recommendations
FinanceAgent   | Behavioral finance   | Budget review timing
LearningAgent  | Cognitive science    | Study session duration and mode
ScheduleAgent  | Time management      | Available time block detection
TaskPlanner    | Productivity science | Task priority and completion probability
MediatorAgent  | Conflict resolution  | Final human-friendly personalized plan

### Why Multi-Agent Instead of One Big Agent?

1. SEPARATION OF CONCERNS: Each agent can be independently improved/tested/replaced.
2. CONFLICT EMERGENCE: When HealthAgent says "60-min workout" but only 30 min free,
   the Mediator resolves it intelligently. No single agent would do this naturally.
3. PARALLELIZABILITY: Agents 2a-2e can run simultaneously (currently sequential,
   architecturally parallel-ready via asyncio.gather).

### The Proposal Pattern

Every agent communicates using a standardized proposal dictionary:

{
    "agent":               "health",
    "proposal":            "60-min intense gym workout",
    "priority":            0.95,     # 0.0-1.0 importance
    "confidence":          0.80,     # 0.0-1.0 certainty
    "reasoning":           "High energy -> intense workout optimal",
    "memory_used":         ["completion_rate"],
    "potential_conflicts": ["schedule"]  # who might compete for resources
}

This is the shared "language." The MediatorAgent reads all proposals and assembles the plan.

---

## 4. THE AGENT LAYER - EVERY AGENT EXPLAINED

### 4.1 BaseAgent - The Foundation

File: backend/app/agents/base_agent.py

An Abstract Base Class (ABC) - cannot be instantiated directly. Every specialist agent inherits from it.

KEY METHODS:

generate_proposal(state) - ABSTRACT, every subclass must implement:
  @abstractmethod
  async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
      raise NotImplementedError
  The "async" keyword enables non-blocking execution and parallel-ready design.

get_memory_context(state) - Loads historical data from MemorySystem:
  context = await self.memory.retrieve(
      user_id=state.get("user_id"),
      query=f"{self.name}_agent_context",
      agent_name=self.name  # tells MemorySystem which data to return
  )

_build_standard_proposal() - Ensures correct schema + clamped values:
  "priority":   min(1.0, max(0.0, priority))   # Always 0-1
  "confidence": min(1.0, max(0.0, confidence)) # Always 0-1

validate_proposal() - Checks required keys are present
log_proposal() - Debug logging of agent output

---

### 4.2 MoodAgent - Emotional Intelligence Engine

File: backend/app/agents/mood_agent.py

Runs FIRST in the workflow. Its output (mood, stress_score, energy_score) shapes every other agent.

CORE TASK: Convert free-form text like "bro im so done, bahut thaka hoon" into:
{mood: "tired", stress_score: 0.25, energy_score: 0.16}

KEYWORD BANKS - THE NLP APPROACH:

Instead of an expensive LLM call, the system uses hand-crafted keyword banks:

MOOD_KEYWORDS = {
    "stressed": [
        "stress", "overwhelmed", "panicking", "burnt out",  # English formal
        "so done", "drowning", "swamped", "losing it",      # English slang
        "\U0001f624", "\U0001f630", "\U0001f628",           # Emojis
        "pareshaan", "bahut kaam", "dimag kharab"           # Hindi/Hinglish
    ],
    "tired": ["tired", "exhausted", "meh", "zombie", "thaka hoon", "neend"],
    "energetic": ["energetic", "hyped", "pumped", "kill it", "josh", "zabardast"],
    "happy": ["happy", "great", "awesome", "khush", "badhiya"],
    "sad": ["sad", "depressed", "not okay", "dukhi"],
    "calm": ["calm", "peaceful", "chill", "relax", "shant", "sukoon"]
}

Why keyword banks?
- FAST: No API call, O(keywords) lookup
- MULTILINGUAL BY DESIGN: Hindi, Hinglish, emoji, slang in one bank
- INTERPRETABLE: You can see exactly which keyword triggered detection
- EXTENSIBLE: Add new slang without retraining any model

MOOD DETECTION ALGORITHM:

Input: "bro I'm super stressed and so done rn"

1. Lowercase text
2. Count intensifiers: "super", "so" -> intensifier_boost = 2
3. For each mood category:
   - Search for each keyword in text (substring match; works for emojis too)
   - Check if negated: look at 25 chars BEFORE the keyword for negation words
     (not, no, nahi, na, never)
   - hit = 1.0 if not negated, -1.0 if negated
   - hit *= (1.0 + intensifier_boost * 0.3) = 1.6
4. stressed gets score: 1.6 (stressed) + 1.6 (so done) = 3.2
5. All others = 0 -> dominant = "stressed"

Negation example: "not stressed" -> prefix = "not " -> negated=True -> hit=-1.0 -> clamped to 0 -> "stressed" NOT detected

MOOD_SCORES - Converting mood to numbers:

Mood      | Stress | Energy
--------- | ------ | ------
stressed  |  0.80  |  0.35
tired     |  0.25  |  0.20
energetic |  0.10  |  0.90
happy     |  0.08  |  0.75
sad       |  0.55  |  0.25
calm      |  0.15  |  0.60
neutral   |  0.25  |  0.50

Intensifiers adjust scores further:
- stressed/sad/anxious: stress += intensifier_count * 0.05
- energetic/happy: energy += intensifier_count * 0.05
- tired: energy -= intensifier_count * 0.04

CONFIDENCE CALCULATION:
confidence = 0.55 (base)
  + 0.10 if len(text) > 15
  + 0.10 if len(text) > 40
  + 0.15 if mood != "neutral"
  + 0.10 if top mood score >= 3

MEMORY CONTEXT USED:
The MemorySystem returns 7-day mood history for contextual reasoning:
- avg_stress_7d: "Today is more stressful than your weekly average"
- dominant_mood: informs greeting tone
- trend: "improving" badge if stress has been decreasing

---

### 4.3 HealthAgent - Physical Wellness Advisor

File: backend/app/agents/health_agent.py

Recommends physical activity based on mood x energy combination.

ACTIVITY RECOMMENDATION MATRIX:

(Mood, Energy)    | Activity                  | Intensity | Duration | Priority
(stressed, low)   | 15-min light walk/yoga    | low       | 15 min   | 0.75
(stressed, high)  | 45-min run or gym         | medium    | 45 min   | 0.85
(tired, low)      | 10-min stretching/rest    | very_low  | 10 min   | 0.90
(energetic, high) | 60-min intense gym        | high      | 60 min   | 0.95
(neutral, medium) | 30-min regular workout    | medium    | 30 min   | 0.70

KEY DESIGN INSIGHT: Stressed users still get exercise - just calibrated.
- Stressed + low energy -> gentle yoga (releases cortisol gently)
- Stressed + high energy -> 45-min run (burns off cortisol effectively)
- Only tired + low energy gets "rest day"

Energy bucketing:
energy_level = "high" if energy > 0.6 else "low" if energy < 0.4 else "medium"

MEMORY-BASED PERSONALIZATION:
completion_rate = completed_health_tasks / total_health_tasks_in_past_plans
priority *= completion_rate  # rarely complete workouts -> AI stops pushing them
confidence = 0.75 + data_points * 0.05

CONFLICT DECLARATION:
conflicts = ["schedule"]  # always declared
HealthAgent flags schedule because workouts require time.
This tells MediatorAgent to verify free time before scheduling.

---

### 4.4 FinanceAgent - Budget Intelligence

File: backend/app/agents/finance_agent.py

Core insight: FINANCIAL STRESS COMPOUNDS EMOTIONAL STRESS.

STRESS-BASED LOGIC:

stress > 0.7:  DEFER complex reviews
               proposal = "Defer budget review. Quick check only."
               priority = 0.3 (very low - don't stress user further)

stress < 0.3:  DETAILED REVIEW
               proposal = "Conduct detailed budget and spending analysis"
               priority = 0.8 (low stress = good time for deep thinking)

otherwise:     QUICK CHECK
               proposal = "5-min quick budget check"
               priority = 0.6 (moderate)

WHY DEFER FINANCE WHEN STRESSED?
Research in behavioral finance shows people make worse financial decisions when
emotionally dysregulated: panic selling, impulse purchasing, avoidance.
The system protects users from emotionally-driven bad financial decisions.

BUDGET EMERGENCY OVERRIDE:
if budget_status == "critical":
    priority = 0.95  # overrides all rules
    proposal = "URGENT: Budget review needed. Account balance critically low."

"critical" is INFERRED from behavior - if finance tasks are skipped in >60% of past plans.

---

### 4.5 LearningAgent - Study Session Optimizer

File: backend/app/agents/learning_agent.py

Recommends study sessions tuned to cognitive capacity (mood + energy dependent).

STUDY MODE SELECTION (Cognitive Load Theory Applied):

stress > 0.7:  30-min "review" mode
               High stress saturates working memory; spaced repetition more effective

energy > 0.7:  90-min "deep" mode
               High energy = optimal for learning new material and problem-solving

otherwise:     60-min "regular" mode
               Balanced session

ACTIVE GOAL INFERENCE FROM HISTORY:
learn_keywords = {study, learn, read, course, coding, python, math, practice}
Counts frequency across past 10 plans
Top 3 most frequent = "active_goals"

Example: "Python" in 6 of last 10 plans -> Python is #1 active goal automatically
No manual goal setup required - emerges from usage.

PRIORITY FORMULA:
priority = 0.7 + (deadline_urgency * 0.25)  # 0.825 base, up to 1.0 with urgency
confidence = 0.8 + len(completion_history) * 0.02

---

### 4.6 ScheduleAgent - Time Block Manager

File: backend/app/agents/schedule_agent.py

Doesn't decide WHAT to do - determines WHEN time is available.

FREE SLOT DETECTION ALGORITHM:

Work window: 09:00 - 21:00
Algorithm:
  current_time = "09:00"
  for each busy_event (sorted by start):
      if current_time < event.start:
          gap = event.start - current_time
          if gap > 15 minutes: add gap to free_slots
      current_time = max(current_time, event.end)
  add final slot: current_time -> "21:00"

Default with NO calendar:
  09:00-12:00 (180 min)
  14:00-18:00 (240 min)
  19:00-21:00 (120 min)

CONFLICT DETECTION:
if total_task_time_needed > total_free_time:
    conflicts.append({
        "type": "insufficient_time",
        "message": f"Tasks need {needed}min but only {free}min available",
        "suggestion": "Reduce task durations or defer some tasks"
    })

TIME PREFERENCE INFERENCE:
Infers "morning vs afternoon person" from when mood logs are created:
morning_count = count of mood logs between 5am-12pm
afternoon_count = count between 12pm-6pm
Most frequent window = user's inferred work preference

---

### 4.7 TaskPlannerAgent - Daily Task Orchestrator

File: backend/app/agents/task_planner_agent.py

Takes user-provided tasks, computes AI priority scores and completion probabilities.

TASK PRIORITY FORMULA:
final_priority = (
    base_importance  * 0.4 +  # user-rated 1-5 -> normalized 0.2-1.0
    mood_adjustment  * 0.3 +  # mood-based behavioral factor
    duration_factor  * 0.2 +  # shorter = better when stressed
    category_weight  * 0.1    # domain structural weight
)

Why these weights?
- Importance (40%): user's own judgment is the strongest signal
- Mood adjustment (30%): significant behavioral adaptation based on state
- Duration (20%): capacity-based filtering for depleted states
- Category (10%): structural bias only, kept minimal

MOOD ADJUSTMENT LOGIC:
if stress > 0.7:
    stress-reducing categories (health, social, personal): return 0.85
    stress-increasing categories (work, learning): return 0.60

elif energy < 0.4:
    health, personal: return 0.80
    others: return 0.50

else:
    all categories: return 0.70 (normal state)

TASK CATEGORY STRESS IMPACT:
Category  | Weight | Stress Impact
--------- | ------ | -------------
work      |  0.30  | +0.6  (increases stress)
health    |  0.25  | -0.3  (reduces stress)
learning  |  0.20  | +0.4  (moderate stress)
personal  |  0.15  | -0.2  (reduces stress)
social    |  0.10  | -0.4  (significantly reduces stress)

COMPLETION PROBABILITY PREDICTION:
base_prob = 0.70

Energy factor:
  energy < 0.3: base_prob *= 0.50  (very low energy halves probability)
  energy < 0.5: base_prob *= 0.70
  else:         base_prob *= 0.95

Stress factor:
  stress > 0.8: base_prob *= 0.60  (very high stress = low follow-through)
  stress > 0.6: base_prob *= 0.80

Duration factor:
  duration > 90: base_prob *= 0.70  (long tasks less likely in bad state)
  duration > 60: base_prob *= 0.85

Displayed as "Completion: 65%" - honest expectations for the user.

MOOD-BOOSTING SUGGESTIONS:
stressed  -> "Take a 5-minute breathing exercise"
tired     -> "Quick 10-minute walk"
happy     -> "Share your positivity with someone"
energetic -> "Tackle the hardest task first"

---

### 4.8 MediatorAgent - Conflict Resolution & Plan Builder

File: backend/app/agents/mediator_agent.py (538 lines - most complex agent)

The FINAL agent. Reads all 6 proposals, synthesizes them into a human-readable schedule.

PHASE 1 - CONFLICT IDENTIFICATION:
Scans all proposals for declared "potential_conflicts":
for agent_name, proposal in proposals.items():
    if proposal.get("potential_conflicts"):
        conflicts.append({"agent": agent_name, "conflicts_with": ...})

PHASE 2 - CONFLICT RESOLUTION:
Conflicted proposals are ADAPTED (not removed):
if stress_score > 0.7:
    adapted["duration"] = max(10, int(original_duration * 0.6))  # 60% of original
    intensity_map = {
        "very_high": "high",
        "high": "medium",
        "medium": "low",
        "low": "very_low"
    }
    adapted["intensity"] = intensity_map[original_intensity]
    adapted["stress_adapted"] = True  # adds "(shortened for today)" note

PHASE 3 - USER TASK PROCESSING:
for task in user_tasks:
    ai_priority = 0.5 + (importance / 10.0)  # maps 1-5 -> 0.6-1.0

    if stress > 0.8 and importance < 3:
        ai_included = False
        ai_suggestion = "Skipped today due to high stress. Focus on rest."

    elif stress > 0.6 and duration > 60:
        ai_suggestion = "Split this large task into smaller chunks if possible."

    elif energy > 0.8:
        ai_priority += 0.1
        ai_suggestion = "High energy! Good time to tackle this."

PHASE 4 - THE PLAN BUILDER (Core Scheduling Algorithm):

Step 1 - Greeting block at 9:00 AM based on mood:
  stressed  -> "Take a slow breath - today's plan is designed to ease your load"
  energetic -> "You're fired up! Let's make the most of this energy"
  tired     -> "Rest is part of the plan. Here's a gentle schedule"

Step 2 - Stress relief block if stress > 0.6:
  "Morning breathing or quick meditation (5-10 mins)"

Step 3 - Schedule each proposal respecting busy slots:
  def _skip_busy(t):
    while busy blocks remain:
        if t is inside a busy block: advance t to end of block
        if t is past a busy block: move to next block
        else: break  # future block
    return t

  for each proposal (sorted by priority):
      current_time = _skip_busy(current_time)
      plan.append({time: current_time -> current_time+duration, ...})
      current_time += duration
      if duration >= 45: insert 10-min break

Step 4 - Lock busy slots as immovable blocks:
  "LOCKED: Team standup (10:00-11:30)"

Step 5 - Wind-down block at 8:30 PM:
  "End-of-day journal - note 3 wins from today"

Step 6 - Sort entire plan by start time (locked + free chronologically)

FRIENDLY TEXT CONVERSION EXAMPLES:
Raw: "60-minute intense gym workout" -> "60-min intense workout"
Raw: "Defer detailed budget review" -> "Finance review deferred - focus on recovery today"
Raw: "45-min Python study (deep mode)" -> "90-min Python deep focus session"
Raw: User task "Finish report" -> "Finish report (High energy! Good time to tackle this.)"

EXPLANATION BUILDER:
"Your plan for today is tailored to your 'stressed' mood (stress 80%, energy 35%).
High stress detected - recovery tasks are prioritised and heavy work is reduced.
Your 2 blocked time(s) (Team standup, Doctor appointment) are respected.
Wove in your 1 task(s), adjusting based on your current bandwidth.
Your schedule has 8 items across the day."

---

## 5. THE WORKFLOW - HOW EVERYTHING CONNECTS

File: backend/app/workflows/daily_planner.py

SHARED STATE DICT (the communication bus):
state = {
    "user_id":            123,
    "user_text":          "yaar bahut thaka hoon",
    "date":               "2026-09-09",
    "mood_data":          {},    # MoodAgent fills this
    "agent_proposals":    {},    # each agent fills a key
    "schedule_conflicts": [],    # conflict detection fills this
    "busy_slots":         [      # user's pre-existing commitments
        {"start": "10:00", "end": "11:30", "label": "Team standup"}
    ],
    "user_tasks":         [      # tasks user wants to accomplish
        {"title": "Finish report", "importance": 4, "estimated_duration": 60}
    ],
    "user_preferences":   {      # loaded from MemorySystem
        "time_preference": "morning",
        "intensity_preference": "medium"
    }
}

STEP 1 - MoodAgent (MUST run first):
mood_proposal = await agents["mood"].generate_proposal(state)
state["mood_data"] = mood_proposal  # all subsequent agents read this

STEP 2 - Domain agents (parallel-ready):
results["health"]       = await agents["health"].generate_proposal(state)
results["finance"]      = await agents["finance"].generate_proposal(state)
results["learning"]     = await agents["learning"].generate_proposal(state)
results["schedule"]     = await agents["schedule"].generate_proposal(state)
results["task_planner"] = await agents["task_planner"].generate_proposal(state)
# Could use asyncio.gather(*coroutines) for true simultaneous execution

STEP 3 - Conflict Detection:
conflicts = state["agent_proposals"]["schedule"].get("conflicts", [])
state["schedule_conflicts"] = conflicts

STEP 4 - MediatorAgent (MUST run last):
final_proposal = await agents["mediator"].generate_proposal(state)

PER-REQUEST MEMORY SYSTEM:
memory_system = MemorySystem(db=db)  # fresh for each request with live DB session
agents = self._make_agents(memory_system)
# Guarantees agents always query current DB state, not stale cached data

---

## 6. MEMORY SYSTEM - HOW AGENTS REMEMBER YOU

File: backend/app/memory/memory_system.py

The MemorySystem bridges SQLite history and live agents.
BaseAgent.get_memory_context() calls memory.retrieve(user_id, query, agent_name)
which dispatches to a specialized context builder.

PER-AGENT CONTEXT BUILDERS:

MoodAgent - 7-Day Trend:
  Queries: last 20 mood_logs in past 7 days
  Returns: {
      "avg_stress_7d": 0.62,
      "avg_energy_7d": 0.45,
      "dominant_mood": "stressed",
      "mood_log_count": 14,
      "trend": "improving"  # stress today < stress last week
  }

HealthAgent - Completion Rate:
  Scans feedback.completed_tasks for health keywords {walk, gym, yoga, stretch...}
  Compares against plan_json items containing those keywords
  Returns: {
      "completion_rate": 0.73,  # 73% of past health tasks completed
      "data_points": 12         # feedback records analyzed
  }

FinanceAgent - Budget Status Inference:
  Checks how often finance plan items appear in plan_json but NOT completed_tasks
  skip_rate = skipped_finance_tasks / total_finance_tasks_in_plans
  budget_status = "at_risk" if skip_rate > 0.6 else "normal"
  Returns: {"budget_status": "at_risk", "finance_skip_rate": 0.67}

LearningAgent - Active Goals:
  Mines past plans for learning keywords {study, python, math, course...}
  Returns top 3 most frequent as inferred "active goals"
  Returns: {
      "active_goals": [{"subject": "Python", "count": 6}, {"subject": "Math", "count": 2}],
      "deadline_urgency": 0.5,
      "completion_history": [1, 0, 1, 1]  # 1=did learning, 0=skipped
  }

ScheduleAgent - Time Preference:
  Looks at what HOUR of day mood logs were created
  Returns: {"user_time_preference": "morning (9-12)"}

System - User Preferences:
  Infers intensity preference from historical thumbs up/down ratio
  Returns: {
      "time_preference": "morning",
      "intensity_preference": "medium",
      "overall_satisfaction": 0.72,
      "total_feedbacks": 15
  }

BEHAVIORAL INFERENCE PHILOSOPHY:
The system never asks users to configure preferences. It OBSERVES patterns:
- When do you log moods? -> time preference
- What do you complete? -> engagement per domain
- What keywords keep appearing? -> learning goals
- Do you give thumbs up? -> satisfaction and intensity calibration

The system IMPROVES AUTOMATICALLY just from usage.

---

## 7. BANDIT LEARNING - THE AI THAT IMPROVES OVER TIME

File: backend/app/learning/bandit_learning.py

WHAT IS A MULTI-ARMED BANDIT?
Classic reinforcement learning: a row of slot machines with unknown payout probabilities.
Balance EXPLORATION (try new machines) with EXPLOITATION (use the best-known).

In LifeOS AI:
- Each "machine" = a recommendation action ("health:light_walk", "learning:deep_study")
- "Payout" = how satisfied the user was (from feedback)

THE BANDITLEARNER CLASS:
class BanditLearner:
    def __init__(self, epsilon=0.1, decay_rate=0.95):
        self.epsilon = epsilon         # exploration rate: 10% default
        self.decay_rate = decay_rate   # epsilon shrinks after each update
        self.actions = defaultdict(lambda: {"count": 0, "total_reward": 0.0})

EPSILON-GREEDY ACTION SELECTION:
def select_action(available_actions):
    if random.random() < epsilon:
        return random.choice(available_actions)   # EXPLORE (10%)
    else:
        return max(actions, key=lambda a: avg_reward(a))  # EXPLOIT

avg_reward(a) = total_reward[a] / count[a]

WHY EXPLORATION MATTERS:
Without it, the system gets stuck recommending suboptimal early-found actions.
10% random exploration ensures it keeps discovering what works best.

EPSILON DECAY:
After each update:
self.epsilon = self.epsilon * self.decay_rate  # 0.1 -> 0.095 -> 0.090 -> ...
As data accumulates, the system trusts its model more, explores less.

REWARD CALCULATOR:
reward = 0.0

# Signal 1: Explicit rating
if rating == "up":   reward += 1.0
if rating == "down": reward -= 1.0  # neutral -> 0

# Signal 2: Task completion rate (0-0.5 bonus)
completion_rate = len(completed_tasks) / total_plan_tasks
reward += completion_rate * 0.5

# Signal 3: Mood improvement (if tracked)
mood_delta = mood_after - mood_before
reward += mood_delta * 0.5

reward = max(-1.0, min(1.0, reward))  # clamp to [-1, +1]

ADAPTIVE RECOMMENDER:
Wraps BanditLearner and maps domain/mood/energy to available actions:

def _get_available_actions(domain, mood, energy):
    if domain == "health":
        if mood in ["stressed"] and energy == "low":
            return ["light_walk", "yoga", "meditation", "stretching"]
        elif energy == "high":
            return ["gym", "running", "sports", "intense_workout"]

THE LEARNING LOOP:
User generates plan -> BanditRecommender selects activities
-> User completes day
-> User submits feedback (rating + completed tasks)
-> RewardCalculator computes reward
-> BanditLearner.update_reward() updates action statistics
-> Next plan uses updated average rewards
-> epsilon decays slightly
-> System gets smarter each cycle

---

## 8. LANGCHAIN INTEGRATION - THE LLM LAYER

File: backend/app/llm/langchain_integration.py

Current status: Mood detection uses keyword banks (fast, free). LangChain/GPT-4 is the
planned future path for richer semantic analysis.

THE LANGUAGE_INSTRUCTION - Global Prompt Engineering:
Every LLM system prompt gets this appended:

"LANGUAGE & STYLE RULES (always follow):
1. User may write in ANY language (English, Hindi, Tamil, Spanish, French, Arabic...)
   and ANY style - formal, informal, slang, mixed-script (Hinglish), abbreviations (lol, rn, idk).
2. AUTO-DETECT the language of the user's message.
3. ALWAYS reply in that SAME language.
4. Interpret colloquial phrases naturally:
   - 'meh / blah' -> low mood / neutral
   - 'super hyped / lit' -> very high energy
   - 'kinda / sorta' -> moderate degree
5. Keep response tone warm, natural, matching user's style."

This ensures the system is NOT English-only. Works for any language.

LANGCHAIN COMPONENTS:
- ChatOpenAI: GPT-4 model wrapper
- ChatPromptTemplate: System + Human message structure
- SystemMessagePromptTemplate: AI persona and rules
- HumanMessagePromptTemplate: User input with {placeholders}
- LLMChain: Chains prompt -> model -> response
- ConversationBufferMemory: Maintains conversation history in chat() method

AVAILABLE LLM ENDPOINTS:

analyze_mood(user_text)
  Input: Any text in any language
  Output: JSON {mood, stress_score, energy_score, confidence, reasoning}

generate_health_recommendation(mood, energy)
  Input: Mood string + energy float
  Output: 2-3 specific health activities

generate_finance_plan(mood, tasks)
  Input: Mood + available tasks list
  Output: Budget-friendly activities and tips

generate_learning_goal(mood, energy)
  Input: Mood + energy
  Output: One achievable learning task with rationale

resolve_conflicts(proposals)
  Input: List of all agent proposals
  Output: Harmonized final plan

chat(message)
  Input: Any user message (conversational)
  Output: Response in detected language (with ConversationBufferMemory)

---

## 9. DATABASE DESIGN - WHAT GETS STORED

File: backend/app/models/database.py

SQLite default (via SQLAlchemy ORM). Configurable to PostgreSQL via DATABASE_URL env var.

ENTITY RELATIONSHIPS:
users (1) --> (N) mood_logs
users (1) --> (N) daily_plans --> (N) agent_actions
                              --> (N) feedback
                              --> (N) user_tasks
users (1) --> (N) bandit_rewards

TABLE DETAILS:

users:
  id          PK
  name        VARCHAR(255)
  email       VARCHAR(255) UNIQUE
  created_at  DATETIME
  Note: email UNIQUE -> idempotent registration (POST /users returns existing user)

mood_logs:
  id           PK
  user_id      FK -> users.id
  mood         VARCHAR(50)  # "stressed", "energetic", "tired", etc.
  stress_score FLOAT        # 0.0-1.0
  energy_score FLOAT        # 0.0-1.0
  raw_text     TEXT         # original user message (stored for future re-analysis)
  created_at   DATETIME INDEX

daily_plans:
  id          PK
  user_id     FK -> users.id
  plan_json   JSON   # full plan list: [{time, task, duration, agent, priority, reason}]
  explanation TEXT   # human-readable explanation of why plan was structured this way
  created_at  DATETIME INDEX

user_tasks:
  id                 PK
  user_id            FK -> users.id
  plan_id            FK -> daily_plans.id (nullable)
  date               VARCHAR(10)    # "YYYY-MM-DD"
  title              VARCHAR(500)
  importance         INTEGER 1-5    # user-provided
  estimated_duration INTEGER        # minutes
  status             VARCHAR(20)    # "pending" / "completed" / "skipped"
  ai_included        BOOLEAN        # did AI put it in the plan?
  ai_suggestion      TEXT           # AI's note on this task
  ai_priority        FLOAT          # computed by MediatorAgent (0.0-1.0)
  completed_at       DATETIME       # null until completed
  created_at         DATETIME INDEX

feedback:
  id              PK
  user_id         FK -> users.id
  plan_id         FK -> daily_plans.id
  rating          VARCHAR(10)  # "up", "down", "neutral"
  completed_tasks JSON         # ["task text 1", "task text 2"]
  comments        TEXT
  created_at      DATETIME INDEX
  Note: completed_tasks JSON array is the core training signal for MemorySystem

agent_actions:
  id             PK
  plan_id        FK -> daily_plans.id
  agent_name     VARCHAR(50)
  proposal_json  JSON    # full proposal dict from this agent for this plan
  priority_score FLOAT
  created_at     DATETIME
  Purpose: audit log enabling debugging of "why did mediator choose X over Y?"

bandit_rewards:
  id            PK
  user_id       FK -> users.id
  action_name   VARCHAR(100)   # e.g., "daily_plan_42"
  reward_value  FLOAT          # computed reward -1.0 to +1.0
  context_json  JSON
  created_at    DATETIME INDEX

---

## 10. API LAYER - REST ENDPOINTS

File: backend/app/api/router.py
Base path: /api/v1/
Auto-generated interactive docs: http://localhost:8000/docs

POST /api/v1/users - Register or Get User
  Request:  {"name": "Sujan", "email": "sujan@example.com"}
  Response: {"id": 1, "name": "Sujan", "email": "...", "created_at": "..."}
  Idempotent: returns existing user if email already registered

POST /api/v1/mood - Submit Mood Check-in
  Request:  {"user_id": 1, "text": "bahut thaka hoon aaj"}
  Response: {
    "mood": "tired",
    "stress_score": 0.25,
    "energy_score": 0.16,
    "confidence": 0.75,
    "reasoning": "Detected 'tired' mood. Energy is low (16%). Today less stressed than usual."
  }
  Side effect: saves to mood_logs table

GET /api/v1/mood-logs?user_id=1&days=7
  Returns: list of mood logs for past N days

POST /api/v1/daily-plan - Generate Full Daily Plan (MAIN ENDPOINT)
  Request: {
    "user_id": 1,
    "date": "2026-09-09",
    "busy_slots": [{"start": "10:00", "end": "11:30", "label": "Team standup"}],
    "user_tasks": [{"title": "Finish report", "importance": 4, "estimated_duration": 60}]
  }
  Response: {
    "plan_id": 42,
    "plan": [
      {"time": "09:00-09:05", "task": "Low energy today - keeping it light", "agent": "mediator"},
      {"time": "09:05-09:15", "task": "Morning breathing or quick meditation", "agent": "health"},
      {"time": "10:00-11:30", "task": "LOCKED: Team standup", "locked": true},
      {"time": "11:30-12:30", "task": "Finish report (Split into smaller chunks)", "agent": "user_task"},
      {"time": "20:30-20:45", "task": "Wind down and review the day", "agent": "mediator"}
    ],
    "agent_proposals": [...],
    "explanation": "Your plan tailored to 'tired' mood...",
    "saved_tasks": [...]
  }

POST /api/v1/feedback - Submit Plan Feedback
  Request: {
    "user_id": 1, "plan_id": 42,
    "rating": "up",
    "completed_tasks": ["Morning breathing", "Finish report"],
    "comments": "The breathing exercise helped!"
  }
  Response: {"success": true, "message": "Feedback recorded and will improve future recommendations"}
  Side effects: saves feedback, computes reward, saves BanditReward

GET /api/v1/history?user_id=1
  Returns: last 30 mood logs + last 30 plans + task summaries

GET /api/v1/statistics?user_id=1
  Returns: average_mood, average_stress, average_energy, total_plans,
           completion_rate, positive_feedback_percentage, mood_distribution

PUT /api/v1/tasks/{task_id}
  Request:  {"status": "completed"}  // or "skipped" or "pending"
  Response: UserTaskResponse with completed_at timestamp

GET /api/v1/db-view
  Returns: full database snapshot - all users, mood logs, plans, feedback (debug endpoint)

---

## 11. FRONTEND ARCHITECTURE - THE REACT UI

Stack: React 18 + TypeScript + Vite + TailwindCSS + React Query + Zustand

ROUTING (App.tsx):
/login     -> Login (no auth required)
/dashboard -> Dashboard (protected)
/mood      -> MoodCheckInPage (protected)
/plan      -> DailyPlanPage (protected)
/history   -> HistoryPage (protected)
/insights  -> InsightsPage (protected)

ProtectedRoute: checks localStorage.getItem("user_id") -> redirects /login if absent

AUTHENTICATION FLOW:
1. User visits any URL
2. ProtectedRoute: no user_id -> redirect /login
3. Login.tsx: user enters name + email -> POST /api/v1/users
4. Response: {id, name, email} -> stored in localStorage
5. Navigate to /dashboard
6. Dashboard reads user_id from localStorage -> loads stats

STATE MANAGEMENT:
React Query (server state - API data, auto-caches 5 min):
  const { data: stats } = useStatistics(userId)
  const { data: moods } = useMoodHistory(userId, 7)
  const { data: health } = useHealthCheck()

Zustand (local/global state):
  const appStore = {
      user: {id, name, email},
      isDarkMode: boolean,
      setUser: (user) => void,
      toggleDarkMode: () => void
  }

localStorage (persistence across sessions):
  user_id, user_name, user_email, theme

PAGE COMPONENTS:

Dashboard.tsx features:
  - Floating particle background: 18 divs with randomized position, CSS particle-float animation
  - Sidebar: fixed 64px column with logo, user avatar (initials), nav links, logout
  - Stat cards: 4 cards - Dominant Mood, Plans Created, Avg Stress, Avg Energy
  - Mood trend chart: Chart.js Line; 7-day stress vs energy; filled areas
  - Quick actions: 4 clickable cards with hover border color animation
  - Recent mood feed: last 5 mood logs with emoji, timestamp, stress/energy scores

MoodCheckIn.tsx:
  - Large textarea for mood input (any language)
  - Character count indicator
  - Calls POST /api/v1/mood
  - Shows detected mood, scores, reasoning in styled result card

DailyPlan.tsx:
  - Busy slot manager (add/remove time blocks)
  - Task list (title, importance 1-5, duration)
  - "Generate Plan" button -> POST /api/v1/daily-plan
  - Timeline view with agent badges, locked slots, reasons
  - Feedback section: thumbs up/down + completed task checkboxes

DESIGN SYSTEM - DARK GLASSMORPHISM:

Color Palette:
  --bg-dark: #0f0a1e          (deep dark purple - background)
  Primary: #a855f7            (purple - CTAs, highlights)
  Secondary: #ec4899          (pink - stress scores, accents)
  Accent: #06b6d4             (cyan - energy scores, charts)
  Success: #22c55e            (green - completion, positive)

CSS Classes:
  .glass-card: background rgba(255,255,255,0.03) + backdrop-filter blur(20px)
               + border rgba(255,255,255,0.08) + border-radius 20px
  .glass-strong: background rgba(15,10,30,0.85) + blur(30px) (sidebar)
  .btn-neon: gradient(#7c3aed, #ec4899) + box-shadow glow
  .gradient-text: gradient(#a855f7, #06b6d4) applied to text via background-clip
  .tag-chip: small status badge
  .stat-card: metric display card
  .animate-float: floating up-down animation
  .animate-slideUp: entry animation sliding from below
  .particle-float: upward particle drift animation

Typography (Google Fonts):
  Syne - headings (bold, futuristic)
  Space Grotesk - body text (geometric, modern)
  Outfit - UI labels

---

## 12. TECHNOLOGY STACK - EVERY TOOL EXPLAINED

BACKEND:

FastAPI (0.104.1)
  Modern async Python web framework. Auto-generates OpenAPI /docs.
  3x faster than Flask for async workloads. Native Pydantic integration.

Uvicorn (0.24.0)
  ASGI server for FastAPI. Handles async I/O with event loop.

SQLAlchemy (2.0.23)
  ORM - write Python classes, get SQL. Supports SQLite + PostgreSQL same codebase.

Pydantic (2.5.0)
  Request/response validation. Type-safe API contracts. Auto-generates JSON schemas.

LangChain (0.1.0)
  LLM application framework. Prompt templates, chains, memory management.

LangGraph (0.0.19)
  Stateful multi-agent workflow graphs. Powers the step-based pipeline architecture.

OpenAI (1.3.0)
  GPT-4 API client. Used in LangChain integration.

PyAutoGen (0.2.7)
  Microsoft multi-agent framework. Future autonomous agent capabilities.

ChromaDB (0.4.15)
  Vector database for semantic similarity search.
  Planned: find "tasks similar to this one" across history.

FAISS (1.8.0)
  Facebook fast similarity search. Complement to ChromaDB.

Neo4j (5.14.0)
  Graph database. Planned: model task dependencies and relationships.

Redis (5.0.1)
  In-memory cache. TaskMemory uses it for same-day fast task retrieval (24h TTL).

Transformers (4.35.0)
  HuggingFace NLP. DistilBERT for sentiment analysis (alternative to keyword approach).

Sentence-Transformers (2.2.2)
  Semantic embeddings for ChromaDB vector search.

scikit-learn (1.3.2)
  General ML utilities. Pattern detection in mood/task history.

python-dotenv (1.0.0)
  .env file loading for environment-based configuration.

FRONTEND:

React 18: Component model + hooks. Declarative UI updates.
TypeScript: Compile-time type checking. Catches type errors before runtime.
Vite: Fast dev server using native ESM. Much faster than Webpack.
TailwindCSS: Utility-first CSS. Consistent spacing/colors/responsive design.
React Router v6: Declarative client-side routing. ProtectedRoute pattern.
React Query: Server state with auto-caching (5min staleTime), background refetch.
Zustand: 1KB global state. Much simpler than Redux - no boilerplate.
Chart.js + react-chartjs-2: Line charts for mood trends. Customizable.
react-hot-toast: Non-intrusive toast notifications. Success/error feedback.
date-fns: Timezone-safe date formatting utilities.

INFRASTRUCTURE:

Docker: Containerize backend + frontend for consistent deployment.
docker-compose: Orchestrate multi-container setup.
nginx: Serve production React build (dist/). Reverse proxy for backend.
SQLite: Zero-configuration default DB. File-based, easy to reset during dev.

---

## 13. DATA FLOW - END-TO-END WALK-THROUGH

PART A: MOOD CHECK-IN

1. User types: "yaar bahut thaka hoon aaj"
   Browser -> POST /api/v1/mood {user_id: 1, text: "..."}

2. router.py:
   MemorySystem(db=session) created
   MoodAgent(memory_system=memory) created

3. mood_agent.py -> generate_proposal():
   _detect_mood("yaar bahut thaka hoon aaj"):
     INTENSIFIERS found: "bahut" -> intensifier_boost = 1
     "tired" keywords: "thaka hoon" found -> hit = 1.0 * 1.3 = 1.3
     tired score = 1.3
     All others: 0
     dominant = "tired"

   _get_scores("tired"):
     base: stress=0.25, energy=0.20
     "bahut" intensifier: energy -= 0.04 -> energy=0.16
     return (stress=0.25, energy=0.16)

   get_memory_context():
     MemorySystem._mood_context(1):
       query mood_logs last 7 days
       avg_stress_7d = 0.42, avg_energy_7d = 0.45
       trend = "improving" (today stress 0.25 < last stress 0.45)

   reasoning = "Detected 'tired' mood. Energy is low (16%). Today less stressed than usual."

4. Saved: INSERT INTO mood_logs VALUES (1, 'tired', 0.25, 0.16, 'yaar bahut...', NOW)

5. API returns: {mood: "tired", stress_score: 0.25, energy_score: 0.16, confidence: 0.75}

PART B: DAILY PLAN GENERATION

1. Browser -> POST /api/v1/daily-plan {
     user_id: 1, date: "2026-09-09",
     busy_slots: [{start: "14:00", end: "15:30", label: "Doctor appt"}],
     user_tasks: [{title: "Study for exam", importance: 5, estimated_duration: 90}]
   }

2. workflow.execute() called:

3. Step 1 - MoodAgent: mood_data = {tired, 0.25, 0.16}

4. Step 2 - Domain agents:
   HealthAgent: (tired, low energy) -> "10-min stretching", priority=0.72
   FinanceAgent: (stress=0.25 < 0.3) -> "Detailed budget review", priority=0.80
   LearningAgent: (energy=0.16, stress=0.25) -> "60-min regular mode study", priority=0.825
   ScheduleAgent: (doctor busy 14:00-15:30)
     free slots: 09:00-14:00 (300min), 15:30-21:00 (330min)
     total free: 630min, total needed: 85min -> NO conflict
   TaskPlannerAgent: (Study for exam, importance=5, 90min)
     ai_priority = 1.0*0.4 + 0.5*0.3 + 0.8*0.2 + 0.20*0.1 = 0.73
     completion_prob = 0.70 * 0.50 (energy<0.3) * 1.0 * 0.70 (duration>60) = 0.245 -> 25%
     ai_suggestion = "Low energy - this might be challenging today."

5. Step 3: 0 conflicts (plenty of free time)

6. Step 4 - MediatorAgent builds plan:
   09:00-09:05  "Rest is part of the plan. Here's a gentle schedule" (greeting)
   09:05-09:15  "10-min stretching" (health)
   09:15-09:30  "Detailed budget review" (finance, 15min)
   09:30-10:30  "60-min regular study session" (learning)
   10:30-10:40  "Short break" (after 60min task)
   10:40-12:10  "Study for exam (Split into smaller chunks)" (user task, 90min)
   12:10-12:20  "Hydration break" (after 90min task)
   14:00-15:30  "LOCKED: Doctor appt"
   20:30-20:45  "Relax and decompress - you made it through the day"
   Sort by time -> final ordered plan

7. Saved: daily_plans + agent_actions x 6 + user_tasks records

PART C: FEEDBACK

1. Browser -> POST /api/v1/feedback {
     plan_id: 42, rating: "up",
     completed_tasks: ["10-min stretching", "Budget review"]
   }

2. router.py:
   reward = 1.0 (rating="up") + 0.22 (2/9 tasks completed) * 0.5 = 0.61
   INSERT INTO feedback (rating, completed_tasks)
   INSERT INTO bandit_rewards (action="daily_plan_42", reward=0.61)

3. Next plan request:
   HealthAgent memory: "stretching" found in completed_tasks -> completion_rate improves
   FinanceAgent memory: "budget" found -> finance_skip_rate decreases
   BanditLearner: plan_42 got 0.61 -> informs future action selection

---

## 14. KEY ALGORITHMS - DEEP DIVE

ALGORITHM 1: NEGATION-AWARE KEYWORD MOOD DETECTION

def _detect_mood(text):
    text_lower = text.lower()
    word_set = set(text_lower.split())
    intensifier_boost = sum(1 for w in INTENSIFIERS if w in word_set)
    scores = {mood: 0.0 for mood in MOOD_KEYWORDS}

    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:  # substring match (works for emojis)
                kw_pos = text_lower.find(kw)
                prefix = text_lower[max(0, kw_pos-25) : kw_pos]
                negated = any(neg in prefix.split() for neg in NEGATIONS)
                hit = -1.0 if negated else 1.0
                hit *= (1.0 + intensifier_boost * 0.3)
                scores[mood] += hit

    scores = {m: max(0.0, v) for m, v in scores.items()}  # suppress negatives
    return max(scores, key=scores.get), scores

ALGORITHM 2: STRESS-ADAPTIVE SCHEDULING

For each proposal (sorted by priority descending):
    current_time = _skip_busy(current_time)  # advance past busy blocks

    if proposal is conflicted and stress > 0.7:
        duration = max(10, original_duration * 0.6)  # shorten to 60%
        intensity = reduce_one_level(original_intensity)

    plan.append({time, task, duration})
    current_time += duration
    if duration >= 45: insert 10-min break

Sort entire plan by start time -> chronological output

ALGORITHM 3: EPSILON-GREEDY WITH DECAY

Initial: epsilon=0.10, all counts=0

Round 1: random() > epsilon -> exploit
  All have count=0 -> random tie-break -> "health:light_walk"

Round 2 (after reward=0.8):
  actions["health:light_walk"] = {count:1, total_reward:0.8, avg=0.8}
  epsilon = 0.10 * 0.95 = 0.095
  random() = 0.07 < 0.095 -> EXPLORE -> random action

Round 10:
  epsilon = 0.10 * 0.95^9 = 0.063
  "health:yoga" = {count:3, avg=0.85}  <- highest average
  random() = 0.71 > 0.063 -> EXPLOIT -> "health:yoga"

System converges on actions that reliably produce high rewards for THIS user.

ALGORITHM 4: TASK COMPLETION PROBABILITY

P(complete | energy, stress, duration) =
    0.70 (base)
    x energy_factor: 0.50 if energy<0.3 / 0.70 if <0.5 / 0.95 otherwise
    x stress_factor: 0.60 if stress>0.8 / 0.80 if >0.6 / 1.00 otherwise
    x duration_factor: 0.70 if dur>90 / 0.85 if >60 / 1.00 otherwise

Example - Tired (0.16), calm (0.25), 90-min task:
  0.70 x 0.50 x 1.00 x 0.70 = 0.245 -> 25% completion probability
  System adds: "This might be challenging today. Consider splitting."

Example - Energetic (0.85), calm (0.10), 30-min task:
  0.70 x 0.95 x 1.00 x 1.00 = 0.665 -> 67% completion probability

---

## 15. DEPLOYMENT AND DOCKER

ENVIRONMENT VARIABLES (.env):

# Required for LLM features
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# Database (default: SQLite, upgrade to PostgreSQL for production)
DATABASE_URL=sqlite:///./lifeos.db
# PostgreSQL: postgresql://user:pass@host:5432/lifeos

# Optional services (for full feature set)
REDIS_URL=redis://localhost:6379
NEO4J_URL=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
CHROMADB_PATH=./data/chromadb

# Bandit learning settings
BANDIT_EPSILON=0.1       # exploration rate
BANDIT_DECAY_RATE=0.95   # how fast exploration decreases

DEVELOPMENT SETUP:

Backend:
  cd lifeos-ai/backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  -> http://localhost:8000/docs  (API documentation)

Frontend:
  cd lifeos-ai/frontend
  npm install
  npm run dev
  -> http://localhost:5173

DOCKER DEPLOYMENT:
  cd lifeos-ai
  docker compose up --build
  Backend: http://localhost:8000
  Frontend: http://localhost:80

FASTAPI STARTUP (lifespan):
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      Base.metadata.create_all(bind=engine)  # auto-creates all tables
      logger.info("Database tables initialized")
      yield  # app runs here
      logger.info("Shutting down...")

Tables are auto-created on first run - zero migration needed for development.

PRODUCTION ARCHITECTURE:
  Internet
      |
      v
  nginx (port 80/443)
      +--> /          : serve React dist/ folder
      +--> /api/v1/   : proxy to FastAPI (port 8000)

  FastAPI (multiple workers via Gunicorn)
      |
      v
  PostgreSQL (for production) or SQLite (for dev)

---

## SUMMARY: WHAT MAKES LIFEOS AI SPECIAL

Feature                | Implementation
-----------------------|-------------------------------------------------------
Mood-first architecture| Every agent reads mood_data; emotional state drives all decisions
Multi-agent debate     | Agents declare conflicts; Mediator resolves intelligently
Zero-LLM mood detect   | Keyword banks handle 90%+ of cases; no API cost per check-in
Multilingual natively  | Hindi, Hinglish, emojis, slang in keyword banks by design
Behavioral memory      | System learns patterns from usage without explicit config
Reinforcement learning | Thumbs up/down feedback improves plans via epsilon-greedy bandit
Honest AI              | Shows completion probabilities, stress adaptations, reasoning
Schedule respect       | Busy slots honored as locked blocks; AI works around your life
Adaptive scaling       | High stress -> shorter/lighter; High energy -> ambitious plans
Future-ready           | LangChain, ChromaDB, Neo4j, Redis, FAISS all wired in for v2

---

Documentation generated from complete source code analysis - September 2026
LifeOS AI - AI-Powered Multi-Agent Personal Life Management System
