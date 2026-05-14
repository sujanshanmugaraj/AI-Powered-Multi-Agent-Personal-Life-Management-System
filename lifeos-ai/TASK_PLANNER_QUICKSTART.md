# 🚀 Quick Start Guide - Daily Task Planner

## Setup (First Time)

### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Ensure databases are running
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379

# Start server
python app/main.py
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

---

## Workflow

### 1️⃣ **Log Your Mood** (Required First Step)
```
GET http://localhost:5173 → "Log Mood" page
Input: "I'm feeling energetic and excited today!"
AI analyzes mood, stress, energy levels
```

### 2️⃣ **Create Task Plan**
```
Navigate to "Task Planner" page
Click "+ Add Task"

Input:
- Title: "Complete quarterly report"
- Importance: 5 (Critical)
- Duration: 90 minutes
- Category: Work

AI agent:
- Analyzes your mood & energy
- Calculates priority score
- Estimates completion probability
- Suggests best timing
```

### 3️⃣ **Track Completion**
```
View tasks in today's list
Click status buttons:
- ✅ Mark complete
- ⏭️ Skip
- 🗑️ Delete

Real-time summary updates
```

### 4️⃣ **View Analytics**
```
Check progress:
- Daily completion rate
- Tasks by category
- Estimated completion %

Weekly insights:
- Most productive day
- Average completion rate
- Completion patterns
- AI-generated recommendations
```

---

## API Usage Examples

### Add Task & Generate Plan
```bash
curl -X POST http://localhost:8000/api/v1/tasks/plan?user_id=1 \
  -H "Content-Type: application/json" \
  -d '[
    {
      "title": "Complete report",
      "importance": 5,
      "estimated_duration": 60
    }
  ]'
```

### Get Today's Tasks
```bash
curl http://localhost:8000/api/v1/tasks/today?user_id=1
```

### Update Task Status
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/task/1?user_id=1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Get Daily Summary
```bash
curl http://localhost:8000/api/v1/tasks/summary/today?user_id=1
```

### Get Weekly Summary
```bash
curl http://localhost:8000/api/v1/tasks/summary/weekly?user_id=1
```

---

## Features at a Glance

| Feature | Where | How |
|---------|-------|-----|
| **Add Tasks** | Task Planner → + Add Task | Fill form, click Create |
| **Update Status** | Task List | Click ✅ / ⏭️ / 🗑️ buttons |
| **Daily Summary** | Task Planner | Auto-loads, shows % complete |
| **Weekly Stats** | Show History button | View productivity trends |
| **Task History** | Show History button | 30-day rolling view |
| **Mood Boosters** | Task Planner page | Suggested under pending tasks |
| **Timing Hints** | Task details | Shows "morning/afternoon/evening" |
| **Completion %" | Each task | Probability based on mood/energy |

---

## Understanding the Scoring

### Priority Score (0-1)
```
High Priority (>0.8):
- Important tasks (5/5)
- Matches current mood
- Good energy available

Medium Priority (0.5-0.8):
- Moderate importance
- Fits current state
- Reasonable effort

Low Priority (<0.5):
- Less critical
- Different timing better
- Consider rescheduling
```

### Completion Probability
```
Very Likely (>0.8):
- Good energy & low stress
- Short duration (< 30 min)
- Similar past success

Likely (0.6-0.8):
- Decent conditions
- Medium effort

Uncertain (< 0.6):
- Challenging conditions
- Consider breaking down
- Mood-boosting first
```

---

## Data & Persistence

### Where Data Lives
```
Redis (Fast Access):
- Today's tasks (24-hour cache)

PostgreSQL (Permanent):
- All tasks with history
- Status changes
- Completion records

ChromaDB (Smart Search):
- Task similarity index
- Pattern matching

Neo4j (Relationships):
- Task dependencies
- User-mood-task correlations
```

### Data Lifecycle
```
Session → Redis (fast)
↓ (persisted)
PostgreSQL (durable)
↓ (indexed)
ChromaDB (searchable)
↓ (correlated)
Neo4j (patterns)
```

---

## Troubleshooting

### "Please log your mood first"
✅ Solution: Go to Dashboard → Log Mood before creating tasks

### Tasks not appearing
✅ Solution: 
- Refresh page
- Check if mood was logged
- Verify user_id in requests

### Completion rate not updating
✅ Solution:
- Click status button (must be ✅ or ⏭️)
- Refresh page after status change
- Check browser console for errors

### Missing summaries
✅ Solution:
- Ensure at least 1 task exists
- Wait for Redis cache to populate (few seconds)
- Try different date range

---

## Example Use Cases

### Case 1: Stressful Day
```
Mood: Stressed (stress: 0.8, energy: 0.3)
↓
Agent prioritizes:
1. Short, achievable tasks (< 30 min)
2. Stress-reducing activities (walk, breathing)
3. Health & social tasks
4. Delays complex work

Suggestions:
- "Take a 5-min breathing exercise"
- "Step outside for fresh air"
- "Call a friend"
```

### Case 2: Energetic Day
```
Mood: Energetic (stress: 0.2, energy: 0.9)
↓
Agent prioritizes:
1. Complex, challenging tasks
2. Important projects
3. Collaborative work
4. Learning goals

Suggestions:
- "Tackle the hardest task first"
- "Help teammates"
- "Start that ambitious project"
```

### Case 3: Tired Day
```
Mood: Tired (stress: 0.5, energy: 0.2)
↓
Agent prioritizes:
1. Routine tasks (< 15 min)
2. Energy-boosting activities
3. Breaks & rest
4. Defer demanding work

Suggestions:
- "10-minute power walk"
- "Quick nap (10 min)"
- "Stretch & hydrate"
```

---

## Best Practices

✅ **DO:**
- Log mood **before** planning tasks
- Update task status as you go (don't wait till end of day)
- Review weekly summary (learn patterns)
- Check mood-boosting suggestions when stressed
- Use importance ratings honestly

❌ **DON'T:**
- Create too many tasks at once (5-8 is optimal)
- Ignore mood data (it affects prioritization)
- Forget to update status (impacts analytics)
- Copy tasks from previous day (use history instead)
- Expect 100% completion (realistic is 70-80%)

---

## Support

For issues, check:
1. Logs: `backend/app/main.py` output
2. Database: Verify PostgreSQL/Redis running
3. API: Test endpoints with curl
4. Frontend: Check browser console (F12)

See `DAILY_TASK_PLANNER.md` for full documentation.
