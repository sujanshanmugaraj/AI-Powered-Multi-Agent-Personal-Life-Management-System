import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAppStore } from '@store/appStore'
import { useDailyPlan, useSubmitFeedback, useUpdateTaskStatus } from '@hooks/useApi'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const AGENT_EMOJI: Record<string, string> = {
  mood: '🧠', health: '💪', finance: '💰', learning: '📚',
  schedule: '🗓️', mediator: '🤖',
}

const AGENT_COLOR: Record<string, string> = {
  mood: '#a855f7', health: '#22c55e', finance: '#f59e0b',
  learning: '#06b6d4', schedule: '#ec4899', mediator: '#94a3b8',
}

interface BusySlot { start: string; end: string; label: string }
interface UserTaskInput { title: string; importance: number; estimated_duration: number }

export const DailyPlanPage: React.FC = () => {
  const { user, currentPlan, setCurrentPlan } = useAppStore()
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [shouldFetch, setShouldFetch]   = useState(false)
  const [feedback, setFeedback]         = useState('')
  const [completedTasks, setCompletedTasks] = useState<string[]>([])

  // ── Busy slots ──────────────────────────────────────────────────────────────
  const [busySlots, setBusySlots] = useState<BusySlot[]>([])
  const [newSlot, setNewSlot]     = useState<BusySlot>({ start: '', end: '', label: '' })
  const [showBusyForm, setShowBusyForm] = useState(false)

  const addBusySlot = () => {
    if (!newSlot.start || !newSlot.end) {
      toast.error('add start & end time first 🕐')
      return
    }
    if (newSlot.start >= newSlot.end) {
      toast.error('end time must be after start time ⏰')
      return
    }
    setBusySlots(prev => [...prev, { ...newSlot, label: newSlot.label || `Busy ${newSlot.start}–${newSlot.end}` }])
    setNewSlot({ start: '', end: '', label: '' })
    toast.success('blocked time added ✅')
  }

  const removeBusySlot = (idx: number) =>
    setBusySlots(prev => prev.filter((_, i) => i !== idx))
  // ── User Tasks ──────────────────────────────────────────────────────────────
  const [userTasks, setUserTasks] = useState<UserTaskInput[]>([])
  const [newTask, setNewTask] = useState<UserTaskInput>({ title: '', importance: 3, estimated_duration: 30 })
  const [showTaskForm, setShowTaskForm] = useState(false)

  const addUserTask = () => {
    if (!newTask.title.trim()) {
      toast.error('Task title cannot be empty')
      return
    }
    setUserTasks(prev => [...prev, newTask])
    setNewTask({ title: '', importance: 3, estimated_duration: 30 })
    toast.success('Task added')
  }

  const removeUserTask = (idx: number) => {
    setUserTasks(prev => prev.filter((_, i) => i !== idx))
  }
  // ────────────────────────────────────────────────────────────────────────────

  const { data: plan, isLoading: planLoading } = useDailyPlan(
    user?.id || '', selectedDate, shouldFetch, busySlots, userTasks
  )
  const { mutate: submitFeedback, isPending: feedbackLoading } = useSubmitFeedback()
  const { mutate: updateTask } = useUpdateTaskStatus()

  // Local state for toggling DB tasks quickly without waiting for refetch
  const [localSavedTasks, setLocalSavedTasks] = useState<any[]>([])

  React.useEffect(() => {
    if (plan) {
      setCurrentPlan(plan)
      setLocalSavedTasks(plan.saved_tasks || [])
      setShouldFetch(false)
    }
  }, [plan, setCurrentPlan])

  const toggleTaskStatus = (task: any) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed'
    // Optimistic UI update
    setLocalSavedTasks(prev =>
      prev.map(t => (t.id === task.id ? { ...t, status: newStatus } : t))
    )
    updateTask({ taskId: task.id, status: newStatus })
  }

  const handleGeneratePlan = () => setShouldFetch(true)

  const handleSubmitFeedback = () => {
    const planId = currentPlan?.plan_id ?? currentPlan?.id
    if (!planId) {
      toast.error('generate a plan first bestie 😭')
      return
    }
    const lower = feedback.toLowerCase()
    const rating =
      lower.includes('great') || lower.includes('good') || lower.includes('love') || lower.includes('awesome') || lower.includes('perfect')
        ? 'up'
        : lower.includes('bad') || lower.includes('poor') || lower.includes('terrible') || lower.includes('hate') || lower.includes('wrong')
        ? 'down'
        : 'neutral'

    submitFeedback(
      { user_id: String(user?.id || ''), plan_id: String(planId), rating: rating as any, completed_tasks: completedTasks, comments: feedback },
      {
        onSuccess: () => { toast.success('feedback noted! 🙏'); setFeedback(''); setCompletedTasks([]) },
        onError:   (err: any) => toast.error(err?.response?.data?.detail || 'failed to submit feedback'),
      }
    )
  }

  return (
    <div className="min-h-screen p-6 md:p-10 max-w-5xl mx-auto">

      {/* Back */}
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-slate-400 hover:text-purple-400 text-sm mb-8 transition-colors no-underline">
        ← back to dashboard
      </Link>

      {/* Header */}
      <div className="mb-8 animate-slideUp">
        <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
          today's plan <span className="gradient-text">📅</span>
        </h1>
        <p className="text-slate-400">AI-crafted just for your vibe — let's get it 🚀</p>
      </div>

      {/* Date + Generate */}
      <div className="glass-card p-5 mb-4 animate-slideUp delay-100">
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="text-xs text-slate-400 font-semibold tracking-wider uppercase block mb-2">Date</label>
            <input
              type="date"
              className="input-genz"
              value={selectedDate}
              onChange={(e) => { setSelectedDate(e.target.value); setShouldFetch(false) }}
            />
          </div>
          <button
            onClick={handleGeneratePlan}
            disabled={planLoading}
            className="btn-neon py-3 px-8 flex items-center gap-2 flex-shrink-0"
          >
            {planLoading
              ? <><div className="w-4 h-4 border-2 border-purple-300 border-t-transparent rounded-full animate-spin" /> cooking...</>
              : <>✨ generate plan</>
            }
          </button>
        </div>
      </div>

      {/* Tasks Card */}
      <div
        className="mb-6 animate-slideUp delay-125 rounded-2xl p-5"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <div
          onClick={() => setShowTaskForm(f => !f)}
          className="flex items-center justify-between cursor-pointer select-none"
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">🎯</span>
            <div>
              <p className="text-sm font-bold text-white">My Tasks Today</p>
              <p className="text-xs text-slate-500">
                {userTasks.length === 0
                  ? 'Add things you need to get done today'
                  : `${userTasks.length} task(s) to schedule`}
              </p>
            </div>
          </div>
          <span className="text-slate-400 text-sm">{showTaskForm ? '▲ collapse' : '▼ expand'}</span>
        </div>

        {showTaskForm && (
          <div className="mt-4 space-y-3" onClick={e => e.stopPropagation()}>
            {/* Existing tasks */}
            {userTasks.map((task, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-4 py-2 rounded-xl text-sm"
                style={{ background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.25)' }}
              >
                <div>
                  <span className="text-cyan-400 font-bold">{task.title}</span>
                  <span className="text-slate-400 ml-2">({task.estimated_duration}m • Imp: {task.importance}/5)</span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); removeUserTask(idx) }}
                  className="text-slate-500 hover:text-red-400 transition-colors text-xs ml-4"
                >
                  ✕ remove
                </button>
              </div>
            ))}

            {/* Add new task form */}
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 mt-2">
              <div className="sm:col-span-6">
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Task Title</label>
                <input
                  type="text"
                  className="input-genz"
                  style={{ fontSize: '14px', padding: '10px 14px' }}
                  placeholder="e.g. Finish report, Buy groceries..."
                  value={newTask.title}
                  onChange={e => setNewTask(s => ({ ...s, title: e.target.value }))}
                  onKeyDown={e => { if (e.key === 'Enter') addUserTask() }}
                />
              </div>
              <div className="sm:col-span-3">
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Mins</label>
                <input
                  type="number"
                  className="input-genz"
                  style={{ fontSize: '14px', padding: '10px 14px' }}
                  min={5} step={5}
                  value={newTask.estimated_duration}
                  onChange={e => setNewTask(s => ({ ...s, estimated_duration: parseInt(e.target.value) || 30 }))}
                />
              </div>
              <div className="sm:col-span-3">
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Imp (1-5)</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    className="input-genz"
                    style={{ fontSize: '14px', padding: '10px 14px' }}
                    min={1} max={5}
                    value={newTask.importance}
                    onChange={e => setNewTask(s => ({ ...s, importance: parseInt(e.target.value) || 3 }))}
                  />
                  <button
                    onClick={e => { e.stopPropagation(); addUserTask() }}
                    className="btn-neon-cyan text-sm flex-shrink-0"
                    style={{
                      padding: '10px 18px',
                      background: 'rgba(6,182,212,0.15)',
                      border: '1px solid rgba(6,182,212,0.4)',
                    }}
                  >
                    + add
                  </button>
                </div>
              </div>
            </div>
            
            {userTasks.length > 0 && (
              <p className="text-xs text-slate-500 italic pt-1">
                🤖 The AI will prioritize these and schedule them at the best time based on your mood.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Busy Times Card — uses inline style to avoid glass-card overflow:hidden */}
      <div
        className="mb-6 animate-slideUp delay-150 rounded-2xl p-5"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        {/* Header toggle — div not button so it doesn't conflict with nested inputs */}
        <div
          onClick={() => setShowBusyForm(f => !f)}
          className="flex items-center justify-between cursor-pointer select-none"
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">🔒</span>
            <div>
              <p className="text-sm font-bold text-white">My Busy Times</p>
              <p className="text-xs text-slate-500">
                {busySlots.length === 0
                  ? 'Tell the AI what times to skip — it plans around them'
                  : `${busySlots.length} blocked time(s) added`}
              </p>
            </div>
          </div>
          <span className="text-slate-400 text-sm">{showBusyForm ? '▲ collapse' : '▼ expand'}</span>
        </div>

        {showBusyForm && (
          <div className="mt-4 space-y-3" onClick={e => e.stopPropagation()}>
            {/* Existing busy slots */}
            {busySlots.map((slot, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-4 py-2 rounded-xl text-sm"
                style={{ background: 'rgba(236,72,153,0.1)', border: '1px solid rgba(236,72,153,0.25)' }}
              >
                <div>
                  <span className="text-pink-400 font-bold">{slot.start} – {slot.end}</span>
                  <span className="text-slate-400 ml-2">{slot.label}</span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); removeBusySlot(idx) }}
                  className="text-slate-500 hover:text-red-400 transition-colors text-xs ml-4"
                >
                  ✕ remove
                </button>
              </div>
            ))}

            {/* Add new slot form */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Start</label>
                <input
                  type="time"
                  className="input-genz"
                  style={{ fontSize: '14px', padding: '10px 14px' }}
                  value={newSlot.start}
                  onChange={e => setNewSlot(s => ({ ...s, start: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">End</label>
                <input
                  type="time"
                  className="input-genz"
                  style={{ fontSize: '14px', padding: '10px 14px' }}
                  value={newSlot.end}
                  onChange={e => setNewSlot(s => ({ ...s, end: e.target.value }))}
                />
              </div>
              <div className="sm:col-span-2">
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Label (optional)</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input-genz flex-1"
                    style={{ fontSize: '14px', padding: '10px 14px' }}
                    placeholder="e.g. Team meeting, Class..."
                    value={newSlot.label}
                    onChange={e => setNewSlot(s => ({ ...s, label: e.target.value }))}
                    onKeyDown={e => { if (e.key === 'Enter') addBusySlot() }}
                  />
                  <button
                    onClick={e => { e.stopPropagation(); addBusySlot() }}
                    className="btn-neon text-sm flex-shrink-0"
                    style={{
                      padding: '10px 18px',
                      background: 'rgba(236,72,153,0.15)',
                      border: '1px solid rgba(236,72,153,0.4)',
                    }}
                  >
                    + block
                  </button>
                </div>
              </div>
            </div>

            {busySlots.length > 0 && (
              <p className="text-xs text-slate-500 italic pt-1">
                🤖 The AI will schedule everything around these blocked times automatically
              </p>
            )}
          </div>
        )}
      </div>

      {/* Plan content */}
      {currentPlan ? (
        <div className="space-y-6 animate-slideUp delay-200">

          {/* Explanation */}
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-3">AI's Take on Your Day</p>
            <p className="text-slate-300 leading-relaxed">{currentPlan.explanation}</p>
            {currentPlan.mood && (
              <div className="flex gap-4 mt-4 pt-4 border-t border-white/5">
                <span className="text-xs text-slate-400">
                  Mood: <span className="text-purple-400 font-bold capitalize">{currentPlan.mood.mood}</span>
                </span>
                <span className="text-xs text-slate-400">
                  Stress: <span className="text-pink-400 font-bold">{Math.round(currentPlan.mood.stress_score * 100)}%</span>
                </span>
                <span className="text-xs text-slate-400">
                  Energy: <span className="text-cyan-400 font-bold">{Math.round(currentPlan.mood.energy_score * 100)}%</span>
                </span>
              </div>
            )}
          </div>

          {/* Plan Timeline */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase">Your Schedule</p>
              <span className="text-xs text-slate-400">
                tick tasks as you finish them ✅
              </span>
            </div>

            {/* Completion progress bar */}
            {currentPlan.plan.length > 0 && (
              <div className="mb-5">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Progress today</span>
                  <span className="text-purple-400 font-bold">
                    {completedTasks.length} / {currentPlan.plan.length} done
                  </span>
                </div>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill progress-purple transition-all duration-700"
                    style={{ width: `${(completedTasks.length / currentPlan.plan.length) * 100}%` }}
                  />
                </div>
              </div>
            )}

            <div className="space-y-3">
              {currentPlan.plan.map((item: any, idx: number) => {
                const isCompleted = completedTasks.includes(item.task)
                const agentColor  = AGENT_COLOR[item.agent || 'mediator'] || '#94a3b8'
                return (
                  <div
                    key={idx}
                    className="flex items-start gap-4 p-4 rounded-xl transition-all duration-200"
                    style={{
                      background:   isCompleted ? 'rgba(34,197,94,0.08)' : 'rgba(255,255,255,0.03)',
                      border:       `1px solid ${isCompleted ? 'rgba(34,197,94,0.25)' : 'rgba(255,255,255,0.06)'}`,
                      borderLeft:   `3px solid ${isCompleted ? '#22c55e' : agentColor}`,
                    }}
                  >
                    {/* Step number */}
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black flex-shrink-0 mt-0.5"
                      style={{ background: `${agentColor}20`, color: agentColor, border: `1px solid ${agentColor}30` }}
                    >
                      {idx + 1}
                    </div>

                    {/* Task */}
                    <div className="flex-1 min-w-0">
                      {item.time && (
                        <span className="text-xs font-bold mr-2" style={{ color: agentColor }}>
                          {item.time}
                        </span>
                      )}
                      <span className={`text-sm font-medium ${isCompleted ? 'line-through text-slate-500' : 'text-white'}`}>
                        {item.task}
                      </span>
                      {item.reason && (
                        <p className="text-xs text-slate-500 mt-1 italic">{item.reason}</p>
                      )}
                    </div>

                    {/* Custom checkbox */}
                    <button
                      onClick={() => {
                        if (isCompleted) setCompletedTasks(completedTasks.filter((t) => t !== item.task))
                        else setCompletedTasks([...completedTasks, item.task])
                      }}
                      className="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 mt-0.5"
                      title={isCompleted ? 'Mark as not done' : 'Mark as done'}
                      style={{
                        background: isCompleted ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.05)',
                        border:     `2px solid ${isCompleted ? '#22c55e' : 'rgba(255,255,255,0.15)'}`,
                        boxShadow:  isCompleted ? '0 0 12px rgba(34,197,94,0.3)' : 'none',
                        transform:  isCompleted ? 'scale(1.05)' : 'scale(1)',
                      }}
                    >
                      {isCompleted && <span className="text-green-400 text-sm font-black">✓</span>}
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {/* User Tasks (DB Tracked) */}
          {localSavedTasks.length > 0 && (
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-3">Tasks Tracked</p>
              <div className="space-y-2">
                {localSavedTasks.map((task: any) => {
                  const isDone = task.status === 'completed'
                  return (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-3 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}
                    >
                      <div className="flex-1">
                        <span className={`text-sm font-bold ${isDone ? 'line-through text-slate-500' : 'text-cyan-400'}`}>
                          {task.title}
                        </span>
                        <span className="text-xs text-slate-500 ml-2">({task.estimated_duration}m)</span>
                        {!task.ai_included && (
                          <p className="text-xs text-red-400 mt-1 italic">
                            Skipped: {task.ai_suggestion}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => toggleTaskStatus(task)}
                        className="btn-genz text-xs px-3 py-1 ml-4"
                        style={{
                          background: isDone ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.05)',
                          color: isDone ? '#4ade80' : '#94a3b8',
                          borderColor: isDone ? 'rgba(34,197,94,0.3)' : 'transparent',
                        }}
                      >
                        {isDone ? 'completed' : 'mark done'}
                      </button>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Agent proposals */}
          {currentPlan.agent_proposals && currentPlan.agent_proposals.length > 0 && (
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-4">Agent Recommendations</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentPlan.agent_proposals.map((ap: any, idx: number) => {
                  const color = AGENT_COLOR[ap.agent] || '#94a3b8'
                  const emoji = AGENT_EMOJI[ap.agent] || '🤖'
                  return (
                    <div
                      key={idx}
                      className="p-4 rounded-xl"
                      style={{ background: `${color}08`, border: `1px solid ${color}20` }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-bold capitalize flex items-center gap-1.5" style={{ color }}>
                          {emoji} {ap.agent}
                        </span>
                        <span className="text-xs text-slate-500">
                          {Math.round(ap.priority * 100)}% priority
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{ap.proposal}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Feedback */}
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-4">
              how was the plan? 💬
            </p>
            <textarea
              className="input-genz mb-4"
              rows={3}
              placeholder="be real with me — was it helpful? what flopped? (great / bad / okay)"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
            <div className="flex gap-3">
              {['👍 great', '😐 okay', '👎 nah'].map((label) => {
                const val = label.includes('great') ? 'great' : label.includes('nah') ? 'bad' : 'okay'
                return (
                  <button
                    key={label}
                    onClick={() => setFeedback(val)}
                    className="px-4 py-2 rounded-xl text-sm transition-all"
                    style={{
                      background: feedback === val ? 'rgba(168,85,247,0.2)' : 'rgba(255,255,255,0.04)',
                      border:     `1px solid ${feedback === val ? 'rgba(168,85,247,0.4)' : 'rgba(255,255,255,0.07)'}`,
                      color:      feedback === val ? '#c084fc' : '#64748b',
                    }}
                  >
                    {label}
                  </button>
                )
              })}
            </div>
            <button
              onClick={handleSubmitFeedback}
              disabled={feedbackLoading || !feedback.trim()}
              className="btn-neon w-full py-3 mt-4 flex items-center justify-center gap-2 disabled:opacity-40"
            >
              {feedbackLoading
                ? <><div className="w-4 h-4 border-2 border-purple-300 border-t-transparent rounded-full animate-spin" /> submitting...</>
                : <>submit feedback →</>
              }
            </button>
          </div>

        </div>
      ) : (
        <div className="glass-card p-16 text-center animate-fadeIn">
          <div className="text-7xl mb-5 animate-float">🤖</div>
          <p className="text-white font-bold text-2xl mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
            no plan yet bestie
          </p>
          <p className="text-slate-400 mb-8">pick a date and let the AI cook 🍳</p>
          <button
            onClick={handleGeneratePlan}
            disabled={planLoading}
            className="btn-neon py-4 px-10 flex items-center gap-2 mx-auto text-base"
          >
            {planLoading
              ? <><div className="w-5 h-5 border-2 border-purple-300 border-t-transparent rounded-full animate-spin" /> cooking...</>
              : <>✨ generate my plan</>
            }
          </button>
        </div>
      )}
    </div>
  )
}

export default DailyPlanPage
