"""
QUICK REFERENCE: LifeOS AI Command Guide
"""

# LifeOS AI - Quick Reference Guide

## 🚀 Getting Started (5 minutes)

### 1. Navigate to Project
```bash
cd c:\Users\sujan\Desktop\collaborative-ai-agents\lifeos-ai
```

### 2. Install Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Edit .env file with your settings
# Already populated with defaults, just set LLM_API_KEY
```

### 4. Run Tests
```bash
cd ..  # Go back to root
pytest tests/ -v
```

### 5. Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start All Services (Docker)
```bash
# In root directory
docker-compose up -d
```

## 📁 File Navigation

| Path | Purpose | Status |
|------|---------|--------|
| `/docs` | Documentation | ✅ Complete |
| `/backend` | FastAPI app | ✅ Complete |
| `/backend/app/agents` | 6 Agents | ✅ Complete |
| `/backend/app/workflows` | LangGraph | ✅ Complete |
| `/backend/app/memory` | Memory system | ✅ Complete |
| `/backend/app/learning` | Bandit learning | ✅ Complete |
| `/tests` | Unit tests | ✅ Complete |
| `/frontend` | React app | ⏳ TODO |

## 🧪 Testing Commands

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_mood_agent.py -v

# With coverage
pytest tests/ --cov=app

# Single test
pytest tests/test_mood_agent.py::test_mood_detection_stressed -v
```

## 🔌 API Testing

```bash
# Start server first: uvicorn app.main:app --reload

# Test mood endpoint
curl -X POST http://localhost:8000/api/v1/mood \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "text": "I feel stressed"}'

# Test plan endpoint
curl -X POST http://localhost:8000/api/v1/daily-plan \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "date": "2026-05-11"}'

# Test feedback endpoint
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "plan_id": 1,
    "rating": "up",
    "completed_tasks": ["meditation"],
    "comments": "Great!"
  }'
```

## 📊 Understanding the System

### Agent Proposal Format
```python
{
    "agent": "agent_name",
    "proposal": "Recommendation text",
    "priority": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasoning": "Why this recommendation",
    "memory_used": ["source1", "source2"],
    "potential_conflicts": ["other_agents"]
}
```

### Workflow Execution
```
1. Mood Agent runs → stress/energy scores
2. Schedule Agent loads calendar
3. Parallel agents: Health, Finance, Learning, Schedule
4. Conflict detection
5. Mediator resolves conflicts
6. Final plan created
7. Save to memory
```

### Memory Layers
```
Layer 1 (Redis): Session/cache data
Layer 2 (PostgreSQL): Structured historical data
Layer 3 (ChromaDB): Vector embeddings for semantic search
Layer 4 (Neo4j): Relationship graphs
```

## 🎯 Key Files to Modify

### Add New Agent
File: `backend/app/agents/new_agent.py`
```python
from app.agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Implement logic
        return self._build_standard_proposal(...)
```

### Customize Rewards
File: `backend/app/learning/bandit_learning.py`
- Modify `RewardCalculator.calculate_reward()`
- Adjust reward weights and formula

### Add API Endpoint
File: `backend/app/api/router.py`
```python
@router.post("/api/v1/new-endpoint")
async def new_endpoint(request: NewRequest, db: Session = Depends(get_db)):
    # Implement endpoint
```

### Modify Agent Rules
Each agent file (e.g., `health_agent.py`) has:
- `_detect_mood_from_keywords()` - Customize detection logic
- `_build_reasoning()` - Customize explanations
- `activity_map` - Modify recommendations

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs postgres

# Stop services
docker-compose down

# Remove volumes (reset data)
docker-compose down -v

# Rebuild image
docker-compose build --no-cache
```

## 📝 Documentation Structure

| Document | Purpose | Location |
|----------|---------|----------|
| README.md | Project overview | Root |
| QUICKSTART.md | Getting started guide | Root |
| PROJECT_SUMMARY.md | Detailed completion summary | Root |
| scope.md | Project scope & requirements | docs/ |
| agents.md | Agent specifications | docs/ |
| architecture.md | System architecture | docs/ |

## 🔧 Configuration

### Edit Environment Variables
File: `backend/.env`
```
# Change these values as needed
DEBUG=True/False
LLM_MODEL=gpt-4 or other
LLM_API_KEY=your_key_here
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Database Connection
```python
# Current: SQLite (default)
DATABASE_URL=sqlite:///./lifeos.db

# For PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/lifeos_db
```

## 💡 Development Workflow

1. **Make changes** to agent/logic
2. **Write tests** for your changes
3. **Run tests** to verify
4. **Test API** with curl/Postman
5. **Check Docker** services running
6. **Commit** to version control

## ⚡ Performance Tips

- Agents run in parallel (LangGraph)
- Memory retrieval is fast (Redis < 1ms)
- Bandit learning improves over 2 weeks
- Test with `pytest -n auto` for parallel tests

## 🎓 Learning Resources

### About Agents
See: `docs/agents.md` - Detailed agent specifications

### About Architecture
See: `docs/architecture.md` - System design and components

### About Implementation
See: Code comments throughout `backend/app/`

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

### Database Errors
```bash
# Reset database
rm backend/lifeos.db

# Or for Docker:
docker-compose down -v
docker-compose up -d postgres
```

### Tests Failing
```bash
# Run in verbose mode
pytest tests/ -v -s

# Run single test for debugging
pytest tests/test_mood_agent.py::test_name -v -s
```

## 📞 Support

- Check `PROJECT_SUMMARY.md` for complete details
- Read individual agent files for logic
- View tests for usage examples
- Check `.env` for configuration

---

**Last Updated:** May 11, 2026  
**Status:** Production Ready  
**Ready For:** Frontend development, LLM integration, deployment
