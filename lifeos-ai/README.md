# LifeOS AI - Collaborative Multi-Agent System for Personal Life Management

A production-level collaborative multi-agent AI system that helps you create personalized daily life plans by coordinating domain-specific agents (Mood, Health, Finance, Learning, Schedule) with intelligent conflict resolution and learning from user feedback.

## 🎯 Vision

Transform how people manage their busy lives by:
- Detecting emotional state and adapting recommendations accordingly
- Coordinating multiple life domains (health, learning, finance, etc.)
- Resolving conflicts between competing priorities
- Learning from user feedback to improve over time
- Providing transparent explanations for all decisions

## 🏗️ Architecture

```
User → React Frontend → FastAPI Backend → LangGraph Workflow
                                              ↓
                            ┌─────────────────┼─────────────────┐
                            ↓                 ↓                 ↓
                        Mood Agent      Health Agent      Finance Agent
                            ↓                 ↓                 ↓
                        Learning Agent  Schedule Agent   Memory System
                            ↓                 ↓
                            └─────────────────┼─────────────────┘
                                              ↓
                                    Mediator Agent (Conflict Resolution)
                                              ↓
                                         Final Plan
                                              ↓
                            Redis + PostgreSQL + ChromaDB + Neo4j
```

## 📁 Project Structure

```
lifeos-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection
│   │   ├── agents/              # Agent implementations
│   │   ├── workflows/           # LangGraph workflow
│   │   ├── memory/              # Memory system (Redis, ChromaDB, Neo4j)
│   │   ├── models/              # SQLAlchemy ORM + Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── api/                 # API endpoints
│   │   └── learning/            # Bandit learning
│   ├── tests/                   # Unit tests
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
├── frontend/
│   └── src/                     # React components
├── docs/
│   ├── scope.md                 # Project scope
│   ├── agents.md                # Agent specifications
│   └── architecture.md          # System architecture
└── docker-compose.yml           # Docker setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (optional, SQLite works for dev)
- Redis
- Node.js 18+ (for frontend)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure .env file
cp .env.example .env

# Run database migrations
python app/main.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- **POST /api/v1/mood** - Analyze user mood
- **POST /api/v1/daily-plan** - Generate personalized daily plan
- **POST /api/v1/feedback** - Submit feedback on plan
- **GET /api/v1/history** - Get past plans and analytics
- **GET /health** - Health check

### Example Usage

```python
import requests

# 1. Submit mood
response = requests.post("http://localhost:8000/api/v1/mood", json={
    "user_id": 1,
    "text": "I feel stressed and tired today. Have a college assignment due and want to study ML."
})
mood = response.json()
print(f"Detected mood: {mood['mood']}, Stress: {mood['stress_score']}")

# 2. Get daily plan
response = requests.post("http://localhost:8000/api/v1/daily-plan", json={
    "user_id": 1,
    "date": "2026-05-11"
})
plan = response.json()
print(f"Daily Plan:\n{plan['explanation']}")

# 3. Submit feedback
requests.post("http://localhost:8000/api/v1/feedback", json={
    "user_id": 1,
    "plan_id": 1,
    "rating": "up",
    "completed_tasks": ["assignment", "meditation"],
    "comments": "Great plan, very manageable!"
})
```

## 📊 Agents

### 1. Mood Agent
Detects emotional state from user input using sentiment analysis and LLM.
- **Input:** User text
- **Output:** mood, stress_score, energy_score

### 2. Health Agent
Suggests workout/activity based on mood and fitness history.
- **Input:** Mood data, fitness history
- **Output:** Activity suggestion, intensity, duration

### 3. Finance Agent
Manages budget reminders and financial reviews.
- **Input:** Mood, budget status
- **Output:** Financial recommendation, priority

### 4. Learning Agent
Tracks learning goals and suggests study sessions.
- **Input:** Goals, mood, deadline
- **Output:** Study recommendation, duration

### 5. Schedule Agent
Finds available time blocks and detects conflicts.
- **Input:** Calendar, task durations
- **Output:** Available slots, conflicts

### 6. Mediator Agent
Resolves conflicts and creates final plan.
- **Input:** All agent proposals
- **Output:** Final daily plan with explanations

## 💾 Memory System

**4-Layer Memory Architecture:**

1. **Redis** - Session state (fast access)
2. **PostgreSQL** - Structured historical data
3. **ChromaDB** - Vector memory for semantic search
4. **Neo4j** - Graph memory for relationships

## 🎓 Learning System

- **Algorithm:** Epsilon-greedy bandit learning
- **Actions:** Health activities, learning sessions, finance reviews
- **Rewards:** Completion, mood improvement, user satisfaction
- **Adaptation:** System learns preferences after 2 weeks of feedback

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/test_mood_agent.py -v  # Specific test
```

## 📦 Docker Deployment

```bash
docker-compose up -d
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Neo4j: http://localhost:7474
- ChromaDB: http://localhost:8001

## 🔐 Security

- JWT authentication
- Role-based authorization
- Pydantic validation
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (100 req/min per user)
- CORS enabled for frontend

## 📈 Implementation Progress

- [x] Phase 0: Documentation and scope
- [x] Phase 1: Backend skeleton (FastAPI, DB, Models)
- [ ] Phase 2: Create core agents
- [ ] Phase 3: Memory layer (Redis, ChromaDB, Neo4j)
- [ ] Phase 4-5: LangGraph workflow
- [ ] Phase 6-7: Negotiation and bandit learning
- [ ] Phase 8-9: API endpoints and frontend
- [ ] Phase 10-12: Testing, Docker, deployment

---

**Status:** Building production-grade multi-agent AI system for personal life management
