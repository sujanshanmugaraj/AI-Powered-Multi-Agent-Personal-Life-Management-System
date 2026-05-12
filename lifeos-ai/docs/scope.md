# Project Scope: Collaborative AI Agents for Personal Life Management

## Problem Statement

Most AI assistants are **single-agent reactive systems**: user asks → chatbot replies. They don't understand context, don't resolve conflicts between different life domains, and don't learn from user feedback over time.

**The Problem:**
- User has conflicting needs: stressed (needs rest) but has deadlines (needs work)
- No system coordinates across mood, health, finance, learning, and scheduling
- No personalization based on repeated feedback
- No memory of what actually worked for this user before

## Solution Overview

**Collaborative AI Agents** is a multi-agent system where specialized domain agents discuss, negotiate conflicts, and create personalized daily life plans. The system:
- Detects user mood and energy levels
- Coordinates 6+ domain-specific agents
- Resolves conflicts through negotiation
- Learns from user feedback over time
- Provides transparent explanations for all recommendations

## Target User

**Primary:**
- Busy professionals/students managing multiple life domains
- People wanting data-driven life optimization
- Users interested in AI explainability

**Use Cases:**
1. **Daily Planning**: User inputs mood + tasks → system creates balanced daily schedule
2. **Weekly Reflection**: Analyze which plan types user actually completed
3. **Mood-Aware Adaptation**: "You're stressed—reduce workload today"
4. **Goal Tracking**: Learn long-term which activities improve user's life
5. **Conflict Resolution**: "Gym + study time overlaps → do light walk instead"

## Supported Domains

| Domain   | Agent           | Responsibilities                                      |
| -------- | --------------- | ----------------------------------------------------- |
| Emotion  | Mood Agent      | Detect stress, energy, emotional state                |
| Health   | Health Agent    | Suggest workouts, rest, wellness                      |
| Finance  | Finance Agent   | Budget reminders, spending reviews                    |
| Learning | Learning Agent  | Track goals, suggest study sessions                   |
| Schedule | Schedule Agent  | Find free time, detect conflicts                      |
| Decision | Mediator Agent  | Resolve conflicts, create final plan                  |

## Daily Planner Use Case

**Input:**
```
User: "I feel stressed today. I have a college assignment due, want to study ML, 
        skipped gym yesterday, and my bank balance is low."
```

**Process:**
1. Mood Agent detects: stress_score=0.82, energy_score=0.31
2. Health Agent suggests: light 15-min walk (not intense gym)
3. Finance Agent defers: budget review → tomorrow
4. Learning Agent shortens: 30-min ML study (not 2 hours)
5. Schedule Agent finds: 90 minutes available for focused work
6. Mediator Agent resolves: assignment first (deadline), then ML study, then walk

**Output:**
```
Today's Personalized Plan:
1. 10 min meditation (stress reduction)
2. Complete assignment 10 AM–12 PM (deadline priority)
3. 15 min walk at lunch (light health activity)
4. 30 min ML study 3–3:30 PM (learning goal, shortened)
5. Budget review → postponed to tomorrow (respecting stress)

Explanation:
Your high stress level and low energy today triggered a recovery-focused plan. 
The system prioritized deadline work and light physical activity over intense 
workouts or heavy studying.
```

## Weekly Reflection Use Case

After 7 days of feedback, system analyzes:
- Which plan types user completed: e.g., "meditation + short study = 85% completion"
- Which activities improved mood: e.g., "walks improved mood 70% of time"
- Patterns: e.g., "When stressed, user never completes gym. Prefers yoga/walks"
- Goals: e.g., "ML study goal: achieved 4/7 days (57%)"

System adapts future recommendations based on this data.

## Mood-Aware Planning Use Case

**High Stress + Low Energy:**
- Reduce heavy tasks
- Add recovery activities
- Defer non-urgent items

**Low Stress + High Energy:**
- Add challenging goals
- Increase productivity tasks
- Include stretch goals

**Neutral Mood + Medium Energy:**
- Balance work and rest
- Include all domains
- Normal priority planning

## Architecture Decision

The system uses:
- **LLMs** for reasoning and plan generation
- **LangGraph** for agent workflow coordination
- **AutoGen** for agent negotiation/discussion
- **Memory** (Redis/ChromaDB/Neo4j) for learning from feedback
- **Bandit Learning** to optimize recommendations over time
- **PostgreSQL** for structured user data
- **FastAPI** for backend API
- **React** for frontend dashboard

## Success Metrics

1. **User Satisfaction**: Feedback rating > 4/5
2. **Plan Completion**: > 70% of recommended tasks completed
3. **Mood Improvement**: User's reported mood improves after following plan
4. **Agent Agreement**: < 30% conflict rate before mediator
5. **Learning**: System recommendations improve after 2 weeks of feedback

## Scope Boundaries

**In Scope:**
- 6 core agents (Mood, Health, Finance, Learning, Schedule, Mediator)
- Daily planning (24-hour horizon)
- Multi-agent negotiation
- User feedback loops
- Memory persistence
- Bandit learning optimization

**Out of Scope (v2):**
- Habit formation tracking
- Social interactions
- Calendar integration (initial version uses manual time blocks)
- Mobile app (web-first)
- Multi-user teams

## Timeline Estimate

- **Phase 0-2 (Docs + Backend):** 3-5 days
- **Phase 3-5 (Memory + Agents):** 5-7 days
- **Phase 6-9 (Negotiation + API):** 3-5 days
- **Phase 10-12 (Frontend + Testing + Deploy):** 5-7 days

**Total: 4-5 weeks for production-ready version**

## Project Success Definition

✅ A working system where:
- User inputs mood/tasks
- 6 agents generate proposals with different priorities
- Mediator resolves conflicts and explains reasoning
- System learns from feedback (bandit learning)
- All components are tested
- System is deployable with Docker
- Code is production-ready and interview-ready
