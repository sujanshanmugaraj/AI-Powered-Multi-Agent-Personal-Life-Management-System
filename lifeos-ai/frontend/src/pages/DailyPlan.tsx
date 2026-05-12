import React, { useState } from 'react'
import { useAppStore } from '@store/appStore'
import { useDailyPlan, useSubmitFeedback } from '@hooks/useApi'
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

export const DailyPlanPage: React.FC = () => {
  const { user, currentPlan, setCurrentPlan } = useAppStore()
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [shouldFetch, setShouldFetch]   = useState(false)
  const [feedback, setFeedback]         = useState('')
  const [completedTasks, setCompletedTasks] = useState<string[]>([])

  const { data: plan, isLoading: planLoading } = useDailyPlan(
    user?.id || '', selectedDate, shouldFetch
  )
  const { mutate: submitFeedback, isPending: feedbackLoading } = useSubmitFeedback()

  React.useEffect(() => {
    if (plan) {
      setCurrentPlan(plan)
      setShouldFetch(false)
    }
  }, [plan, setCurrentPlan])

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
      <a href="/dashboard" className="inline-flex items-center gap-2 text-slate-400 hover:text-purple-400 text-sm mb-8 transition-colors">
        ← back to dashboard
      </a>

      {/* Header */}
      <div className="mb-8 animate-slideUp">
        <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
          today's plan <span className="gradient-text">📅</span>
        </h1>
        <p className="text-slate-400">AI-crafted just for your vibe — let's get it 🚀</p>
      </div>

      {/* Date + Generate */}
      <div className="glass-card p-5 mb-6 animate-slideUp delay-100">
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
              {currentPlan.plan.map((item, idx) => {
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


          {/* Agent proposals */}
          {currentPlan.agent_proposals && currentPlan.agent_proposals.length > 0 && (
            <div className="glass-card p-5">
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-4">Agent Recommendations</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentPlan.agent_proposals.map((ap, idx) => {
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
