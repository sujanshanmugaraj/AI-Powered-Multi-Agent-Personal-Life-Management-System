# 📋 Daily Task Planner - Complete Implementation Guide

## Overview

A comprehensive **AI-powered Daily Task Planning System** integrated into LifeOS AI that helps users:
- ✅ Create and prioritize daily tasks based on mood and energy levels
- 📊 Suggest mood-boosting activities
- 💾 Track task completion with detailed analytics
- 📈 View historical patterns and weekly insights
- 🎯 Adjust task recommendations based on learned patterns

---

## 🏗️ Architecture

```
User Input (Task + Mood)
    ↓
┌─────────────────────────────────────────────┐
│    Frontend (React - TaskPlanner.tsx)       │
│  - Add/Edit/Delete tasks                    │
│  - Update status (completed/pending/skip)   │
│  - View daily & weekly summaries            │
│  - Real-time analytics                      │
└─────────────────────────────────────────────┘
    ↓ HTTP (REST API)
┌─────────────────────────────────────────────┐
│  Backend API (FastAPI - task_endpoints.py)  │
│  POST   /api/v1/tasks/plan                  │
│  GET    /api/v1/tasks/today                 │
│  PUT    /api/v1/tasks/task/{id}             │
│  DELETE /api/v1/tasks/task/{id}             │
│  GET    /api/v1/tasks/summary/*             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Task Planning Agent (task_planner_agent.py)│
│  - Analyzes mood & energy levels            │
│  - Prioritizes tasks intelligently          │
│  - Suggests mood-boosting activities        │
│  - Estimates completion probability         │
│  - Recommends task timing                   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│    Multi-Layer Memory System                │
│  ┌─────────────────────────────────────┐   │
│  │ Redis: Fast access to today's tasks │   │
│  │ (24-hour TTL)                       │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ PostgreSQL: Durable task records &  │   │
│  │ historical data                     │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ ChromaDB: Semantic search for       │   │
│  │ similar tasks & patterns            │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ Neo4j: Task dependencies &          │   │
│  │ relationships                       │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 📁 Files Created/Modified

### Backend - New Files

| File | Purpose |
|------|---------|
| `backend/app/agents/task_planner_agent.py` | Task Planning Agent - prioritizes & suggests tasks |
| `backend/app/memory/task_memory.py` | Task Memory - multi-layer persistence |
| `backend/app/api/task_endpoints.py` | Task API - REST endpoints for task management |

### Backend - Modified Files

| File | Changes |
|------|---------|
| `backend/app/main.py` | Added task_router import and registration |
| `backend/app/workflows/daily_planner.py` | Integrated TaskPlannerAgent into workflow |

### Frontend - New Files

| File | Purpose |
|------|---------|
| `frontend/src/pages/TaskPlanner.tsx` | Task Planner UI Component |
| `frontend/src/pages/index.ts` | Updated exports (added TaskPlanner) |

---

## 🎯 Features

### 1. **Intelligent Task Planning**
```python
# Task Planner Agent analyzes:
- User mood (stressed, tired, energetic, happy, neutral)
- Stress score (0-1)
- Energy level (0-1)
- Task importance (1-5)
- Estimated duration
- Task category (work, health, learning, personal, social)

# Returns:
- Prioritized task list (sorted by AI score)
- Completion probability for each task
- Suggested timing (morning/afternoon/evening)
- Mood-boosting suggestions
```

### 2. **Multi-Layer Memory**
```
Redis (Session):
- Caches today's tasks for fast access
- 24-hour TTL

PostgreSQL (Durable):
- Stores all tasks with status
- Historical records for analytics
- User preferences & settings

ChromaDB (Semantic):
- Indexes tasks for semantic search
- Finds similar tasks & patterns
- Enables ML-based recommendations

Neo4j (Graph):
- Task dependencies & relationships
- User-task-mood correlations
- Workflow patterns
```

### 3. **Daily Summary**
```markdown
# Daily Task Summary - 2026-05-14

## Stats
- Total Tasks: 8
- Completed: 6 (75%)
- Pending: 2
- Skipped: 0
- Average Importance: 3.5/5

## By Category
- work: 3
- health: 2
- learning: 2
- personal: 1

## ✅ Completed
- [Complete project report] (work)
- [30-min workout] (health)
- [Learn React hooks] (learning)
- ...

## ⏳ Pending
- ...

## 📊 Insights
- High completion rate today! You're on fire 🔥
- Most productive: Morning (09:00-12:00)
- Best performing category: Work
```

### 4. **Weekly Analytics**
```json
{
  "week_start": "2026-05-12",
  "week_end": "2026-05-18",
  "total_tasks": 42,
  "total_completed": 35,
  "avg_completion_rate": 0.833,
  "most_productive_day": "2026-05-15",
  "insights": [
    "🌟 Excellent week! Completed 83% of tasks",
    "📈 Most productive day: Wednesday",
    "🎯 Most common: Work tasks",
    "💡 Pattern: Higher completion on mornings"
  ]
}
```

---

## 🔌 API Endpoints

### Create Task Plan
```http
POST /api/v1/tasks/plan?user_id=1
Content-Type: application/json

[
  {
    "title": "Complete project report",
    "importance": 5,
    "estimated_duration": 60
  }
]

Response:
{
  "plan_id": 0,
  "tasks": [
    {
      "id": 1,
      "title": "Complete project report",
      "importance": 5,
      "estimated_duration": 60,
      "status": "pending",
      "ai_priority": 0.85,
      "completion_probability": 0.72,
      "date": "2026-05-14",
      "created_at": "2026-05-14T10:30:00Z"
    }
  ],
  "explanation": "## Daily Task Plan (Mood: energetic) ..."
}
```

### Get Today's Tasks
```http
GET /api/v1/tasks/today?user_id=1

Response: [Task, Task, ...]
```

### Update Task Status
```http
PUT /api/v1/tasks/task/1?user_id=1
Content-Type: application/json

{"status": "completed"}
```

### Delete Task
```http
DELETE /api/v1/tasks/task/1?user_id=1
```

### Get Today's Summary
```http
GET /api/v1/tasks/summary/today?user_id=1

Response:
{
  "date": "2026-05-14",
  "total_tasks": 8,
  "completed": 6,
  "pending": 2,
  "skipped": 0,
  "completion_rate": 0.75,
  "summary_markdown": "# Daily Summary..."
}
```

### Get Weekly Summary
```http
GET /api/v1/tasks/summary/weekly?user_id=1

Response:
{
  "week_start": "2026-05-12",
  "week_end": "2026-05-18",
  "total_tasks": 42,
  "total_completed": 35,
  "avg_completion_rate": 0.833,
  "insights": [...]
}
```

### Get Task History
```http
GET /api/v1/tasks/history?user_id=1&days=30

Response:
{
  "total_days": 25,
  "total_tasks": 145,
  "completed_total": 108,
  "history": [
    {
      "date": "2026-05-14",
      "total": 8,
      "completed": 6,
      "completion_rate": 0.75,
      "tasks": [...]
    }
  ]
}
```

---

## 🧠 Task Planning Algorithm

### Priority Calculation
```python
# Base importance (user-provided, 1-5)
base_importance = 0.8

# Mood adjustment
if stress_score > 0.7:
    # Prioritize stress-reducing tasks (health, social, personal)
    mood_adjustment = 0.85 if category.stress_impact < 0 else 0.6
else:
    mood_adjustment = 0.7

# Duration factor (shorter tasks when stressed/tired)
duration_factor = max(0.3, 1.0 - (duration / 120.0))

# Final priority score
final_priority = (
    base_importance * 0.4 +
    mood_adjustment * 0.3 +
    duration_factor * 0.2 +
    category_weight * 0.1
)

# Completion probability
completion_prob = energy_score * stress_factor * duration_factor
```

### Mood-Based Recommendations

```python
# When STRESSED (stress > 0.7):
- Suggest shorter tasks (5-15 min)
- Recommend stress-reducing activities:
  - Take 5-min breathing exercise
  - Step outside for fresh air
  - Listen to calming music
- Lower priority for demanding work
- Suggest breaks every 30 min

# When TIRED (energy < 0.4):
- Suggest quick wins (10-30 min)
- Recommend energy-boosting activities:
  - Quick 10-minute walk
  - Energizing music
  - Power nap (10 min)
- Focus on routine tasks
- Suggest afternoon for reset

# When ENERGETIC (energy > 0.8):
- Prioritize challenging tasks
- Suggest complex projects
- Encourage helping others
- Recommend morning for important work

# When HAPPY (mood = happy):
- Encourage engagement
- Suggest collaborative tasks
- Recommend sharing positivity
```

---

## 💾 Data Models

### Task Model (Database)
```python
class UserTask(Base):
    __tablename__ = "user_tasks"
    
    id: int                 # Primary key
    user_id: int           # Foreign key to User
    plan_id: int           # Optional link to daily plan
    date: str              # YYYY-MM-DD
    title: str             # Task title
    importance: int        # 1-5
    estimated_duration: int # Minutes
    status: str            # pending/completed/skipped
    ai_included: bool      # AI put it in plan?
    ai_suggestion: str     # AI notes
    ai_priority: float     # 0-1 AI score
    completed_at: datetime # When completed
    created_at: datetime   # Creation time
```

### Task Memory Structure
```python
# Redis Key: tasks:{user_id}:{date}
{
    "date": "2026-05-14",
    "tasks": [...],
    "saved_at": "2026-05-14T10:30:00Z",
    "count": 8
}

# ChromaDB Collection: "tasks"
Metadata:
{
    "user_id": 1,
    "task_id": 1,
    "importance": 5,
    "category": "work",
    "date": "2026-05-14",
    "completed": false
}
```

---

## 🎨 Frontend Usage

### Import & Use
```tsx
import { TaskPlanner } from '@pages'

export function App() {
  return (
    <div>
      <TaskPlanner />
    </div>
  )
}
```

### Components
```tsx
// Add Task Form
<form onSubmit={handleAddTask}>
  <input value={newTask.title} />
  <input type="range" min="1" max="5" />
  <input type="number" value={newTask.estimated_duration} />
</form>

// Today's Progress Card
<Card>
  - Total: 8
  - Completed: 6 (75%)
  - Progress Bar
</Card>

// Task List
<Card>
  - Task Title
  - Duration & Importance
  - Status Buttons (✅ Completed, ⏭️ Skip, 🗑️ Delete)
</Card>

// Weekly Summary
<Card>
  - Total completed
  - Average rate
  - Insights
</Card>
```

---

## 🔄 Integration with Daily Planner

The Task Planner is fully integrated into the daily planner workflow:

```python
# daily_planner.py
async def execute(..., user_tasks: list = None):
    # Task planner runs as part of parallel agents
    state = {
        "user_tasks": user_tasks,
        "mood_data": mood_proposal,
        ...
    }
    
    # Parallel execution
    results["task_planner"] = await agents["task_planner"].generate_proposal(state)
    
    # Mediator agent considers task plan in final recommendations
    final_proposal = await agents["mediator"].generate_proposal(state)
```

---

## 📊 Learning & Analytics

### Task-Mood Correlation
```python
# Stored in Redis/PostgreSQL for 30 days
{
    "date": "2026-05-14",
    "mood": "energetic",
    "stress_score": 0.3,
    "energy_score": 0.85,
    "tasks_completed": 6,
    "completion_rate": 0.75,
    "learning_points": [
        "Energetic mood correlates with higher completion",
        "Best performance during mornings",
        "Work tasks have highest completion rate"
    ]
}
```

### Pattern Recognition
```
Insights Generated:
- Productivity patterns (peak hours)
- Category preferences
- Mood impact on completion
- Optimal task load
- Best task types when stressed/tired
```

---

## 🚀 Quick Start

### 1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
# Ensure PostgreSQL is running
python app/main.py
```

### 2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

### 3. **First Use**
1. Log mood (via MoodCheckIn)
2. Navigate to Task Planner
3. Add first task
4. Agent auto-prioritizes based on mood
5. Mark tasks as complete/skip
6. View summary & insights

---

## 🎯 Key Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Task Creation | ✅ | Add/edit/delete tasks |
| Mood Integration | ✅ | Tasks prioritized by mood & energy |
| Completion Tracking | ✅ | Mark tasks complete/skip/pending |
| Daily Summary | ✅ | Real-time stats & markdown export |
| Weekly Analytics | ✅ | Patterns, insights, productivity metrics |
| Task History | ✅ | 30-day rolling history |
| Semantic Search | ✅ | Find similar tasks |
| Mood Boosters | ✅ | AI-suggested activities |
| Timing Suggestions | ✅ | Best time to do task |
| Multi-layer Memory | ✅ | Redis, PostgreSQL, ChromaDB, Neo4j |

---

## 📝 Notes

- All tasks are timezone-aware
- Summaries reset daily at midnight UTC
- Weekly summaries: Monday-Sunday
- Completion probability ranges from 0.1 to 0.99
- Priority scores are normalized (0-1)
- Task data is persisted across sessions

---

## 🔮 Future Enhancements

- [ ] Recurring tasks
- [ ] Task dependencies & blocking
- [ ] Collaborative tasks (shared with others)
- [ ] Voice input for quick task creation
- [ ] Calendar integration
- [ ] Mobile app notifications
- [ ] Pomodoro timer integration
- [ ] Task suggestions from past patterns
- [ ] AI-generated task decomposition
- [ ] Real-time collaboration

