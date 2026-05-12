# Agent Roles and Specifications

## Agent Framework Overview

All agents inherit from `BaseAgent` and follow a standardized interface:

### BaseAgent Interface

```python
class BaseAgent:
    def __init__(self, name: str, llm, memory_system):
        self.name = name
        self.llm = llm
        self.memory = memory_system
    
    async def generate_proposal(self, state: dict) -> dict:
        """Generate proposal based on current state"""
        raise NotImplementedError
    
    def get_memory_context(self):
        """Retrieve relevant past decisions from memory"""
        raise NotImplementedError
```

### Proposal Format (All Agents Output)

```json
{
  "agent": "agent_name",
  "proposal": "Specific recommendation text",
  "priority": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "Why this proposal",
  "memory_used": ["past_similar_situations"],
  "potential_conflicts": ["other_agent_names"]
}
```

---

## 1. Mood Agent

**Responsibility:** Detect and classify user's emotional state

**Input Sources:**
- User's text input
- Historical mood data
- Activity completion feedback

**Core Function:**
```python
async def generate_proposal(self, state: dict) -> dict:
    """
    Input: user_text, user_id, date
    Output: mood_classification, stress_score, energy_score, confidence
    """
```

**Output Example:**

```json
{
  "agent": "mood",
  "mood": "stressed",
  "stress_score": 0.82,
  "energy_score": 0.31,
  "confidence": 0.91,
  "reasoning": "Text contains 'stressed', 'tired', and 'overwhelmed'. Similar to day-3 which had high cortisol.",
  "memory_used": ["similar_past_days_with_stress"],
  "potential_conflicts": []
}
```

**Memory Integration:**
- Store: Mood classification + user feedback on accuracy
- Retrieve: Past similar emotional states and what helped
- Learn: Refine mood detection based on user corrections

**LLM Prompt:**
```
Analyze the user's emotional state:

User input: "{user_text}"
Historical patterns: {similar_past_moods}

Detect:
- Primary mood (stressed, tired, anxious, neutral, energetic, etc.)
- Stress level (0-1)
- Energy level (0-1)
- Confidence in detection (0-1)

Provide reasoning based on keywords and historical patterns.
```

---

## 2. Health Agent

**Responsibility:** Suggest physical activity and wellness based on mood, fitness history, and goals

**Input Sources:**
- Mood data from Mood Agent
- User's fitness history
- Current fatigue level
- Past workout completion rates

**Core Function:**
```python
async def generate_proposal(self, state: dict) -> dict:
    """
    Input: mood, stress_score, energy_score, user_fitness_level
    Output: activity_suggestion, intensity, duration, priority
    """
```

**Output Example (High Stress, Low Energy):**

```json
{
  "agent": "health",
  "proposal": "15-minute light walk or gentle yoga",
  "intensity": "low",
  "duration": "15 minutes",
  "priority": 0.75,
  "confidence": 0.88,
  "reasoning": "User is stressed and fatigued. Light movement reduces cortisol. Past data: user completed 92% of walks but only 30% of intense gym sessions when stressed.",
  "memory_used": ["stress_recovery_preferences", "completion_rates_by_intensity"],
  "potential_conflicts": ["schedule_agent (time availability)"]
}
```

**Output Example (Normal Mood, High Energy):**

```json
{
  "agent": "health",
  "proposal": "45-minute gym workout with strength training",
  "intensity": "high",
  "duration": "45 minutes",
  "priority": 0.9,
  "confidence": 0.85,
  "reasoning": "Energy is high, stress is low. User has gym motivation today. Past data: user completed 88% of workouts on high-energy days.",
  "memory_used": ["energy_correlated_activities"],
  "potential_conflicts": []
}
```

**Decision Logic:**

| Mood       | Energy | Stress | Suggestion          | Intensity |
| ---------- | ------ | ------ | ------------------- | --------- |
| Stressed   | Low    | High   | Walk or yoga        | Low       |
| Stressed   | High   | High   | Running or gym       | Medium    |
| Neutral    | Medium | Medium | Regular workout     | Medium    |
| Energetic  | High   | Low    | Intense gym or sport| High      |
| Tired      | Low    | Low    | Stretching or rest  | Very Low  |

**Bandit Learning:**
- Action: Heavy workout, medium walk, light yoga, rest day
- Reward: User completed (yes/no), mood improved (yes/no), repeated (yes/no)

---

## 3. Finance Agent

**Responsibility:** Budget management, spending analysis, financial reminders

**Input Sources:**
- User's mood (defer non-urgent tasks if stressed)
- Current budget status
- Pending financial tasks
- Past user behavior around financial reviews

**Core Function:**
```python
async def generate_proposal(self, state: dict) -> dict:
    """
    Input: mood, stress_score, budget_status, pending_financial_tasks
    Output: financial_suggestion, priority, timing
    """
```

**Output Example (High Stress):**

```json
{
  "agent": "finance",
  "proposal": "Defer detailed budget review to tomorrow. Quick check: remaining balance is $500 (safe).",
  "priority": 0.30,
  "confidence": 0.9,
  "reasoning": "High stress detected. Complex financial tasks increase anxiety. User's past data: 78% of budget reviews completed when done on neutral/low-stress days. Today's balance is sufficient, review can wait.",
  "memory_used": ["stress_financial_task_correlation", "current_budget_safety"],
  "potential_conflicts": []
}
```

**Output Example (Normal Mood, Low Energy):**

```json
{
  "agent": "finance",
  "proposal": "Quick spending review: $200 spent this week (on track). Budget check complete.",
  "priority": 0.6,
  "confidence": 0.85,
  "reasoning": "Quick 5-minute task suitable for low-energy periods. Keeps user informed without cognitive overload.",
  "memory_used": ["quick_task_preferences"],
  "potential_conflicts": []
}
```

**Mood-Aware Priorities:**

| Mood       | Task Type             | Priority | Action                    |
| ---------- | --------------------- | -------- | ------------------------- |
| Stressed   | Deep analysis         | 0.2      | Defer to calmer day       |
| Stressed   | Balance check         | 0.4      | Quick 5-min review        |
| Neutral    | Regular budget review | 0.7      | Normal schedule           |
| Energetic  | Investment planning   | 0.9      | Detailed analysis         |
| Tired      | Quick check           | 0.3      | Minimal, defer if possible |

---

## 4. Learning Agent

**Responsibility:** Track learning goals, suggest study sessions, monitor progress

**Input Sources:**
- User's learning goals (stored in memory)
- Stress and energy levels
- Past study completion rates
- Goal deadlines
- Subject difficulty

**Core Function:**
```python
async def generate_proposal(self, state: dict) -> dict:
    """
    Input: goals, deadline, mood, stress_score, energy_score
    Output: study_suggestion, subject, duration, priority
    """
```

**Output Example (ML Goal, Stressed):**

```json
{
  "agent": "learning",
  "proposal": "30-minute ML study session on transformers (review mode, not deep dive)",
  "subject": "Machine Learning - Transformers",
  "duration": "30 minutes",
  "priority": 0.75,
  "confidence": 0.88,
  "reasoning": "ML goal deadline is 5 days away. Stress is high, so shortened session. Review is less cognitive-intensive than new material. Past data: user completed 85% of 30-min sessions vs 40% of 2-hour sessions when stressed.",
  "memory_used": ["goal_deadlines", "session_length_completion_rates", "preferred_study_styles"],
  "potential_conflicts": ["finance_agent (time overlap)"]
}
```

**Output Example (High Energy, Neutral Mood):**

```json
{
  "agent": "learning",
  "proposal": "90-minute deep ML study session on transformers architecture",
  "subject": "Machine Learning - Transformers",
  "duration": "90 minutes",
  "priority": 0.95,
  "confidence": 0.92,
  "reasoning": "Energy is high, stress is low. Deep learning session appropriate. No deadline pressure (5 days away). Past data: user completes 92% of challenging 90-min sessions on high-energy days.",
  "memory_used": ["energy_study_correlation", "deadline_urgency"],
  "potential_conflicts": []
}
```

**Bandit Learning Actions:**
- Deep study 120+ min
- Regular study 60 min
- Light review 30 min
- Flashcard session 15 min
- Video learning 45 min
- No study (rest day)

Reward: Completion rate, user retention, deadline met, mood after study

---

## 5. Schedule Agent

**Responsibility:** Find available time slots, detect conflicts, create time blocks

**Input Sources:**
- User's calendar or manual time blocks
- Proposals from other agents
- Task durations
- User's time preferences (morning/afternoon/evening)

**Core Function:**
```python
async def generate_proposal(self, state: dict) -> dict:
    """
    Input: calendar, proposed_tasks, user_time_preferences
    Output: available_slots, conflicts, recommended_schedule
    """
```

**Output Example:**

```json
{
  "agent": "schedule",
  "proposal": "Available time blocks: 10-12 PM (2h), 3-4 PM (1h), 6-7:30 PM (1.5h)",
  "available_slots": [
    {"start": "10:00", "end": "12:00", "duration": 120},
    {"start": "15:00", "end": "16:00", "duration": 60},
    {"start": "18:00", "end": "19:30", "duration": 90}
  ],
  "conflicts": [
    {
      "task1": "gym (45 min)",
      "task2": "assignment work",
      "overlap": "12-1 PM",
      "resolution": "Move gym to 3 PM or light walk at lunch"
    }
  ],
  "priority": 1.0,
  "confidence": 0.95,
  "reasoning": "Based on user calendar. Morning meeting 9-10, lunch 12-1, evening commitment 8-9. Gym and assignment overlap detected.",
  "memory_used": ["user_calendar", "time_preferences"],
  "potential_conflicts": ["health_agent", "learning_agent"]
}
```

**Conflict Detection:**
- Task overlaps → flag for mediator
- Insufficient time → reduce duration or defer
- Back-to-back tasks > 3h → suggest break

---

## 6. Mediator Agent

**Responsibility:** Resolve conflicts, prioritize proposals, create final daily plan

**Input Sources:**
- All 5 agents' proposals
- User's historical preferences
- Conflict resolution history
- Final user outcomes from past plans

**Core Function:**
```python
async def resolve_conflicts(self, proposals: list[dict]) -> dict:
    """
    Input: all_agent_proposals, user_preferences
    Output: final_plan, conflict_resolution_log, explanation
    """
```

**Conflict Resolution Logic:**

1. **Identify Conflicts:**
   - Schedule conflicts (overlapping times)
   - Priority conflicts (too many high-priority tasks)
   - Domain conflicts (e.g., rest vs. study)

2. **Resolution Strategies:**
   - **Time Reallocation:** Move tasks to available slots
   - **Intensity Reduction:** Make tasks lighter/shorter
   - **Defer:** Move to tomorrow if not urgent
   - **Combine:** Merge compatible tasks (study during walking)

3. **Priority Ranking:**
   - Mood-based (if stressed, recovery > productivity)
   - Deadline-based (urgent deadlines first)
   - Historical (what user actually completes)
   - Health-based (never skip essential wellness)

**Output Example:**

```json
{
  "agent": "mediator",
  "final_plan": [
    {
      "time": "10:00-12:00",
      "task": "Complete college assignment",
      "agents_involved": ["schedule", "learning"],
      "rationale": "Deadline today. Highest priority."
    },
    {
      "time": "12:00-12:30",
      "task": "Lunch + 15-min light walk",
      "agents_involved": ["health", "schedule"],
      "rationale": "Stress relief + gentle movement. Schedule conflict resolved: gym → walk."
    },
    {
      "time": "15:00-15:30",
      "task": "ML study session (review mode)",
      "agents_involved": ["learning", "health"],
      "rationale": "Learning goal maintained. Duration shortened due to stress."
    },
    {
      "time": "18:00-19:00",
      "task": "Rest + dinner",
      "agents_involved": ["health", "mood"],
      "rationale": "Stressed day. Recovery time needed."
    }
  ],
  "deferred": [
    {
      "task": "Budget review",
      "agent": "finance",
      "reason": "High stress. Can be done tomorrow."
    }
  ],
  "conflicts_resolved": 2,
  "explanation": "Your high stress today triggered a recovery-focused plan. Assignment work prioritized (deadline), intense gym replaced with light walk (stress-appropriate), budget review deferred. Total commitment: 4.5 hours of planned activities.",
  "memory_used": ["user_stress_preferences", "conflict_resolution_history", "deadline_data"],
  "priority": 1.0,
  "confidence": 0.93
}
```

---

## Agent Communication Protocol

### State Flow

```
State = {
    "user_id": int,
    "date": str,
    "mood_data": dict (from Mood Agent),
    "health_proposal": dict (from Health Agent),
    "finance_proposal": dict (from Finance Agent),
    "learning_proposal": dict (from Learning Agent),
    "schedule_data": dict (from Schedule Agent),
    "user_preferences": dict (from memory),
    "past_similar_days": list (from ChromaDB)
}
```

### Execution Order

```
1. Mood Agent → output mood state
2. Schedule Agent → retrieve calendar (parallel)
3. Health/Finance/Learning Agents → generate proposals (parallel)
4. Conflict Detection → identify overlaps
5. Mediator Agent → resolve conflicts → final plan
6. Memory Update → store decisions + feedback
```

### Error Handling

- Agent timeout (2 min) → use default proposal
- LLM API error → use cached agent response
- Missing data → agent uses default values

---

## Agent Memory Integration

Each agent has access to 4 memory types:

| Memory Type | Use Case                                      | Lookup Speed |
| ----------- | --------------------------------------------- | ------------ |
| Redis       | Current session state, active proposals       | ~1ms         |
| ChromaDB    | Similar past days, past successful proposals  | ~50ms        |
| Neo4j       | User-goal-habit relationships, agent patterns | ~100ms       |
| PostgreSQL  | Structured history, feedback scores           | ~10ms        |

Example: **Learning Agent → Find similar high-stress days where user still completed learning goals**

```sql
SELECT * FROM daily_plans 
WHERE user_id = 1 AND stress_score > 0.7 AND learning_completed = true
ORDER BY created_at DESC LIMIT 5
```

---

## Agent Performance Metrics

Each agent tracks:

| Metric              | How measured                                    |
| ------------------- | ----------------------------------------------- |
| Proposal Quality    | % of proposals included in final plan           |
| Accuracy            | % of proposals user found helpful (from feedback) |
| Conflict Rate       | % of proposals that conflict with others        |
| Learning Efficiency | Improvement in acceptance rate over 4 weeks     |
| Response Time       | Latency to generate proposal                    |

---

## Extending Agents (Future)

Template for adding new agents:

```python
class NewAgent(BaseAgent):
    def __init__(self, name: str, llm, memory):
        super().__init__(name, llm, memory)
        self.domain = "new_domain"
    
    async def generate_proposal(self, state: dict) -> dict:
        # 1. Get relevant memory
        context = self.get_memory_context(state)
        
        # 2. Build prompt
        prompt = self._build_prompt(state, context)
        
        # 3. Query LLM
        response = await self.llm.generate(prompt)
        
        # 4. Parse + structure response
        proposal = self._parse_response(response, state)
        
        # 5. Return standardized format
        return proposal
```

Possible future agents: Social (relationships), Career (job planning), Family (household), Creative, Nutrition
