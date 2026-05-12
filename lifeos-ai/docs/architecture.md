# Architecture Documentation

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│        (Dashboard, Mood Check-in, Plan View, Feedback)         │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  (REST API, Request validation, Response formatting)            │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow Engine                    │
│                  (Orchestrates agent execution)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────┬──────────────────┬──────────────────────┐
│   Mood Agent     │   Health Agent   │   Finance Agent      │
│  (LLM + Prompt)  │ (LLM + Prompt)   │   (LLM + Prompt)     │
└──────────────────┴──────────────────┴──────────────────────┘
                              ↕
┌──────────────────┬──────────────────┬──────────────────────┐
│ Learning Agent   │ Schedule Agent   │  Memory System       │
│ (LLM + Prompt)   │ (Time algebra)   │ (Redis+ChromaDB+...) │
└──────────────────┴──────────────────┴──────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────┐
│              AutoGen Negotiation Service                      │
│     (Optional agent discussion if conflicts detected)         │
└──────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────┐
│                   Mediator Agent                              │
│       (Conflict resolution, Plan creation, Explanation)      │
└──────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────┬─────────────────┬────────────────────────┐
│   PostgreSQL       │     Redis       │   ChromaDB / FAISS     │
│ (Structured data)  │ (Session state) │ (Vector memory)        │
└────────────────────┴─────────────────┴────────────────────────┘
                              ↕
                       Neo4j (Graph DB)
              (Relationships: User-Goal-Habit-Decision)
```

---

## Component Details

### 1. Frontend (React + Tailwind)

**Location:** `frontend/src/`

**Pages:**
- `/login` - User authentication
- `/dashboard` - Main dashboard with today's plan
- `/mood-checkin` - Mood input form
- `/daily-plan` - Full plan view with agent breakdown
- `/feedback` - Rate plan, mark completed tasks
- `/history` - Past plans and analytics
- `/settings` - User preferences

**Key Components:**
```
App/
├── Auth/
│   └── LoginForm
├── Dashboard/
│   ├── MoodWidget
│   ├── DailyPlan
│   └── AgentBreakdown
├── MoodCheckin/
│   └── MoodForm
├── Feedback/
│   └── FeedbackForm
├── History/
│   ├── PlansTimeline
│   └── MoodChart
└── Common/
    ├── Header
    └── Sidebar
```

**State Management:** Redux or Zustand
**API Client:** Axios/React Query

---

### 2. FastAPI Backend

**Location:** `backend/app/`

**Structure:**
```
backend/
├── app/
│   ├── main.py          # FastAPI app initialization
│   ├── config.py        # Environment config
│   ├── models/          # Pydantic models (request/response)
│   ├── agents/          # Agent implementations
│   ├── workflows/       # LangGraph workflows
│   ├── memory/          # Memory system interfaces
│   ├── services/        # Business logic
│   ├── api/             # API endpoints (routers)
│   └── database/        # Database connections
├── requirements.txt
├── .env
└── Dockerfile
```

**Key Dependencies:**
```
fastapi==0.104.1
pydantic==2.5.0
sqlalchemy==2.0.23
redis==5.0.0
langchain==0.1.0
langgraph==0.0.19
autogen==0.1.0
chromadb==0.4.15
neo4j==5.14.0
python-dotenv==1.0.0
```

**Core Endpoints:**

```
POST /api/v1/mood
├── Input: {"user_id": 1, "text": "..."}
└── Output: Mood classification

POST /api/v1/daily-plan
├── Input: {"user_id": 1, "date": "2026-05-11"}
└── Output: Final plan with agent breakdown

POST /api/v1/feedback
├── Input: {"user_id": 1, "plan_id": 10, "rating": "up", ...}
└── Output: Feedback saved

GET /api/v1/history
├── Input: {"user_id": 1}
└── Output: Past plans and analytics

GET /api/v1/health
└── Output: System health check
```

---

### 3. LangGraph Workflow

**Location:** `backend/app/workflows/daily_planner_graph.py`

**Execution Flow:**

```
START
  ↓
MOOD_AGENT (single)
  ↓ (mood data)
RETRIEVE_CONTEXT (parallel)
  ├─→ Load user preferences
  ├─→ Load calendar
  └─→ Query vector DB for similar days
  ↓
PARALLEL_AGENTS (concurrent execution)
  ├─→ HEALTH_AGENT
  ├─→ FINANCE_AGENT
  ├─→ LEARNING_AGENT
  └─→ SCHEDULE_AGENT
  ↓
CONFLICT_DETECTION
  ├─ If conflicts detected → AutoGen negotiation
  └─ If no conflicts → skip negotiation
  ↓
MEDIATOR_AGENT (single)
  ↓ (final plan)
MEMORY_UPDATE (async)
  ├─→ Save to PostgreSQL
  ├─→ Save to Redis (current session)
  ├─→ Save to ChromaDB (vector embedding)
  └─→ Update Neo4j graph
  ↓
END
```

**LangGraph Definition (Pseudocode):**

```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("mood_agent", mood_agent_node)
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("health_agent", health_agent_node)
workflow.add_node("finance_agent", finance_agent_node)
workflow.add_node("learning_agent", learning_agent_node)
workflow.add_node("schedule_agent", schedule_agent_node)
workflow.add_node("conflict_detection", conflict_detection_node)
workflow.add_node("autogen_negotiation", autogen_negotiation_node)
workflow.add_node("mediator_agent", mediator_agent_node)
workflow.add_node("memory_update", memory_update_node)

# Add edges
workflow.set_entry_point("mood_agent")
workflow.add_edge("mood_agent", "retrieve_context")
workflow.add_edge("retrieve_context", ["health_agent", "finance_agent", 
                                       "learning_agent", "schedule_agent"])
# ... (convergent node pattern)
workflow.add_edge(["health_agent", "finance_agent", "learning_agent", 
                   "schedule_agent"], "conflict_detection")

# Conditional routing
workflow.add_conditional_edges(
    "conflict_detection",
    detect_conflicts,
    {True: "autogen_negotiation", False: "mediator_agent"}
)

workflow.add_edge("autogen_negotiation", "mediator_agent")
workflow.add_edge("mediator_agent", "memory_update")
workflow.set_finish_point("memory_update")

graph = workflow.compile()
```

**State Definition:**

```python
from typing import TypedDict

class AgentState(TypedDict):
    user_id: int
    date: str
    mood_data: dict
    health_proposal: dict
    finance_proposal: dict
    learning_proposal: dict
    schedule_data: dict
    user_preferences: dict
    past_similar_days: list
    conflicts: list
    final_plan: dict
    explanation: str
    created_at: str
```

---

### 4. Memory System

**Location:** `backend/app/memory/`

**Four-Layer Memory Architecture:**

#### Layer 1: Redis (Session Memory)

**Use Case:** Fast access to current session, active proposals

**TTL:** 24 hours

**Keys:**
```
user:{user_id}:current_mood → {"mood": "stressed", ...}
user:{user_id}:session_proposals → [agent_proposals]
user:{user_id}:active_plan → {final_plan_dict}
```

**Operations:** O(1) get/set

---

#### Layer 2: PostgreSQL (Structured Memory)

**Use Case:** Historical data, feedback, metrics

**Tables:**
```
users
├── id (PK)
├── name
├── email
├── created_at

mood_logs
├── id (PK)
├── user_id (FK)
├── mood
├── stress_score
├── energy_score
├── raw_text
├── created_at

daily_plans
├── id (PK)
├── user_id (FK)
├── plan_json
├── explanation
├── created_at

feedback
├── id (PK)
├── user_id (FK)
├── plan_id (FK)
├── rating (up/down)
├── completed_tasks (list)
├── comments
├── created_at

agent_actions
├── id (PK)
├── plan_id (FK)
├── agent_name
├── proposal_json
├── priority_score
├── created_at

bandit_rewards
├── id (PK)
├── user_id (FK)
├── action_name
├── reward_value
├── context (mood, energy, etc.)
├── created_at
```

**Operations:** O(log n) queries with proper indexing

---

#### Layer 3: ChromaDB / FAISS (Vector Memory)

**Use Case:** Semantic search for similar past plans/situations

**Stored Vectors:**
- Plan summaries (vectorized with embeddings)
- Mood descriptions
- User preferences
- Feedback comments

**Example Query:**
```
Find past plans where user was "stressed and had low energy"
Vector search in ChromaDB → return 5 most similar plans
```

**Implementation:**
```python
from chromadb import ChromaClient

client = ChromaClient()
collection = client.get_or_create_collection("daily_plans")

# Store
collection.add(
    ids=[plan_id],
    embeddings=[vector],
    metadatas=[{"user_id": user_id, "created_at": date}],
    documents=[plan_summary]
)

# Retrieve
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5
)
```

**Operations:** O(log n) approximate nearest neighbor search

---

#### Layer 4: Neo4j (Graph Memory)

**Use Case:** Relationship tracking, pattern discovery

**Node Types:**
```
User
├── id, name, email

Goal
├── id, title, domain (health/learning/finance)

Mood
├── type, stress_level, energy_level

Action
├── name, type, duration

Activity
├── name, category (workout/study/break)

Feedback
├── rating, timestamp
```

**Relationships:**
```
(User)-[:HAS_GOAL {active: true}]->(Goal)
(User)-[:EXPERIENCED {date: "2026-05-11"}]->(Mood)
(User)-[:PREFERRED {strength: 0.8}]->(Activity)
(Agent)-[:SUGGESTED {priority: 0.8}]->(Action)
(Action)-[:RECEIVED_FEEDBACK {rating: "positive"}]->(Feedback)
(Goal)-[:COMPLETED_BY]->(Activity)
(Mood)-[:CORRELATES_WITH]->(Activity)
```

**Example Query:**
```cypher
MATCH (u:User {id: 1})-[:EXPERIENCED]->(m:Mood)
WHERE m.stress_level > 0.7
MATCH (u)-[:PREFERRED]->(a:Activity)
RETURN a, COUNT(*) as frequency
ORDER BY frequency DESC
```

**Operations:** O(m) where m is edges, optimized for pattern matching

---

### 5. Bandit Learning System

**Location:** `backend/app/learning/bandit_learning.py`

**Algorithm:** Epsilon-Greedy

```python
class BanditLearner:
    def __init__(self, epsilon=0.1):
        self.epsilon = epsilon  # Exploration rate
        self.actions = {}  # {action: {"count": n, "reward": sum}}
    
    def select_action(self):
        if random() < self.epsilon:
            return random_action()  # Explore
        else:
            return max_reward_action()  # Exploit
    
    def update_reward(self, action, reward):
        self.actions[action]["count"] += 1
        self.actions[action]["reward"] += reward
```

**Actions Tracked:**
```
Health:
├── heavy_workout_60min
├── moderate_workout_45min
├── light_walk_20min
├── yoga_30min
└── rest_day

Learning:
├── deep_study_120min
├── regular_study_60min
├── light_review_30min
├── flashcard_15min
└── video_45min

Finance:
├── deep_review_60min
├── quick_check_5min
└── defer_to_tomorrow

Timing:
├── morning
├── afternoon
└── evening
```

**Reward Formula:**

```
reward = completion_bonus + mood_delta + recency_weight

completion_bonus = +1 if completed, -0.5 if skipped
mood_delta = (mood_after - mood_before) * 0.5
recency_weight = 1.2 if recent (last 3 days), 1.0 if older
```

**Learning Over Time:**

Week 1: Explore (epsilon=0.1, try all actions)
Week 2: Mixed (epsilon=0.05, mostly best actions)
Week 4+: Exploit (epsilon=0.01, strongly prefer learned best actions)

---

### 6. AutoGen Negotiation (Optional)

**Location:** `backend/app/services/negotiation_service.py`

**When Triggered:** If conflicts detected > threshold (2+)

**Process:**

```
1. All agents present proposals
2. Mediator identifies conflicts
3. AutoGen groupchat initiated:
   - Moderator (Mediator Agent)
   - Participants (conflicting agents)
   - Max turns: 3
4. Each agent explains rationale
5. Mediator proposes resolution
6. Agents vote (accept/reject)
7. If agreement → proceed, else → Mediator decides
```

**Example Negotiation:**

```
Mediator: "Health suggests 45-min gym, Learning suggests 90-min study, 
           Schedule has only 100 min free. Conflict detected."

Health: "User's energy is high. 45-min gym is needed for stress relief."

Learning: "ML goal deadline is 4 days away. 90 min is minimum needed."

Schedule: "Available blocks: 10-12 (120 min), 3-4 (60 min), 7-9 (120 min)."

Mediator: "Proposal: 45-min gym in morning block (10-10:45), 
          90-min study in evening block (7-8:30). Both needs met."

All agents: "Agree."
```

---

## Database Schema

### PostgreSQL Tables

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Mood Logs
CREATE TABLE mood_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mood VARCHAR(50),
    stress_score FLOAT,
    energy_score FLOAT,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (user_id, created_at)
);

-- Daily Plans
CREATE TABLE daily_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_json JSONB,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (user_id, created_at)
);

-- Feedback
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_id INTEGER REFERENCES daily_plans(id),
    rating VARCHAR(10),  -- 'up', 'down', 'neutral'
    completed_tasks TEXT[],
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (user_id, plan_id, created_at)
);

-- Agent Actions
CREATE TABLE agent_actions (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES daily_plans(id),
    agent_name VARCHAR(50),
    proposal_json JSONB,
    priority_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (plan_id, agent_name)
);

-- Bandit Rewards
CREATE TABLE bandit_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action_name VARCHAR(100),
    reward_value FLOAT,
    context_json JSONB,  -- mood, energy, day_of_week, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (user_id, action_name, created_at)
);
```

---

## Deployment Architecture

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/lifeos
      - REDIS_URL=redis://redis:6379
      - NEO4J_URL=neo4j://neo4j:7687
    depends_on:
      - postgres
      - redis
      - neo4j
      - chromadb

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: lifeos
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:latest
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7687:7687"
      - "7474:7474"
    volumes:
      - neo4j_data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma

volumes:
  postgres_data:
  neo4j_data:
  chromadb_data:
```

---

## API Response Format (Standardized)

All endpoints return:

```json
{
  "status": "success" | "error",
  "data": {
    // endpoint-specific data
  },
  "meta": {
    "timestamp": "2026-05-11T14:30:00Z",
    "version": "v1"
  },
  "errors": [
    // error details if status = "error"
  ]
}
```

---

## Security Considerations

1. **Authentication:** JWT tokens (FastAPI + OAuth2)
2. **Authorization:** Role-based access (user, admin)
3. **Data Validation:** Pydantic models + FastAPI validation
4. **Rate Limiting:** 100 requests/minute per user
5. **CORS:** Frontend origin only
6. **Secrets:** .env file (never commit)
7. **SQL Injection:** SQLAlchemy ORM (parameterized queries)
8. **Encryption:** Passwords hashed (bcrypt), sensitive data encrypted at rest

---

## Monitoring & Logging

- **Logging:** Python logging module + centralized logs
- **Metrics:** Agent response times, success rates, error rates
- **Alerting:** Health check endpoint monitors all services
- **Profiling:** Memory usage, database query times

---

## Scalability Notes

**Current Design (Single-user focus):**
- Suitable for 100-1000 users
- Single FastAPI instance
- PostgreSQL with basic indexing

**Future Scaling:**
- Horizontal scaling: Load balancer + multiple API instances
- Database sharding: Partition by user_id
- Caching layer: Redis cache for frequent queries
- Async queues: Celery for batch processing feedback
- Microservices: Separate services per agent (if load high)
