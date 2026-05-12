import React, { useState } from 'react'
import { useAppStore } from '@store/appStore'
import { useHistory } from '@hooks/useApi'
import { format } from 'date-fns'

const MOOD_EMOJI: Record<string, string> = {
  stressed: '😤', tired: '😴', energetic: '⚡', happy: '😄',
  sad: '😔', calm: '😌', anxious: '😰', neutral: '😐',
}
const MOOD_COLOR: Record<string, string> = {
  stressed: '#ef4444', tired: '#6366f1', energetic: '#f59e0b',
  happy: '#22c55e', sad: '#3b82f6', calm: '#06b6d4', anxious: '#ec4899', neutral: '#94a3b8',
}

export const HistoryPage: React.FC = () => {
  const { user } = useAppStore()
  const [page, setPage] = useState(1)
  const { data: history, isLoading } = useHistory(user?.id || '', 20, (page - 1) * 20)

  return (
    <div className="min-h-screen p-6 md:p-10 max-w-4xl mx-auto">
      <a href="/dashboard" className="inline-flex items-center gap-2 text-slate-400 hover:text-purple-400 text-sm mb-8 transition-colors">
        ← back to dashboard
      </a>

      <div className="mb-8 animate-slideUp">
        <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
          your journey <span className="gradient-text">🕰️</span>
        </h1>
        <p className="text-slate-400">every vibe, every plan — all your receipts 🧾</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-2xl" />
          ))}
        </div>
      ) : history?.items && history.items.length > 0 ? (
        <>
          <div className="space-y-4">
            {history.items.map((item, idx) => {
              const mood = item.mood
              const moodColor = MOOD_COLOR[mood?.mood || 'neutral'] || '#94a3b8'
              const taskCount = item.plan?.plan?.length ?? 0
              return (
                <div
                  key={idx}
                  className="glass-card p-5 animate-slideUp"
                  style={{ animationDelay: `${idx * 60}ms`, borderLeft: `3px solid ${moodColor}` }}
                >
                  <div className="flex flex-col md:flex-row md:items-center gap-4">

                    {/* Date */}
                    <div className="flex-shrink-0 w-20 text-center">
                      <p className="text-2xl font-black text-white" style={{ fontFamily: 'Syne, sans-serif' }}>
                        {format(new Date(item.created_at), 'dd')}
                      </p>
                      <p className="text-xs text-slate-400 uppercase tracking-wider">
                        {format(new Date(item.created_at), 'MMM')}
                      </p>
                      <p className="text-xs text-slate-600">
                        {format(new Date(item.created_at), 'EEE')}
                      </p>
                    </div>

                    {/* Divider */}
                    <div className="hidden md:block w-px h-16 bg-white/10" />

                    {/* Mood badge */}
                    {mood && (
                      <div
                        className="flex items-center gap-3 px-4 py-2 rounded-xl flex-shrink-0"
                        style={{ background: `${moodColor}15`, border: `1px solid ${moodColor}30` }}
                      >
                        <span className="text-2xl">{MOOD_EMOJI[mood.mood] || '😐'}</span>
                        <div>
                          <p className="text-sm font-bold text-white capitalize">{mood.mood}</p>
                          <p className="text-xs" style={{ color: moodColor }}>
                            stress {Math.round(mood.stress_score * 100)}%
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Plan summary */}
                    {item.plan && taskCount > 0 && (
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-2">
                          {taskCount} tasks planned
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {item.plan.plan.slice(0, 3).map((task, tidx) => {
                            const taskName = typeof task === 'string' ? task : (task as any).task || ''
                            return (
                              <span
                                key={tidx}
                                className="text-xs px-2 py-1 rounded-lg text-slate-400"
                                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.07)' }}
                              >
                                {taskName.length > 28 ? taskName.substring(0, 28) + '…' : taskName}
                              </span>
                            )
                          })}
                          {taskCount > 3 && (
                            <span className="text-xs px-2 py-1 rounded-lg text-purple-400" style={{ background: 'rgba(168,85,247,0.1)' }}>
                              +{taskCount - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Feedback badge */}
                    {item.feedback && (
                      <div className="flex-shrink-0">
                        <span
                          className="text-xs px-3 py-1.5 rounded-full font-bold"
                          style={{
                            background: item.feedback.rating === 'up' ? 'rgba(34,197,94,0.15)' : item.feedback.rating === 'down' ? 'rgba(239,68,68,0.15)' : 'rgba(148,163,184,0.15)',
                            color:      item.feedback.rating === 'up' ? '#22c55e'              : item.feedback.rating === 'down' ? '#ef4444'              : '#94a3b8',
                            border:     `1px solid ${item.feedback.rating === 'up' ? '#22c55e30' : item.feedback.rating === 'down' ? '#ef444430' : '#94a3b830'}`,
                          }}
                        >
                          {item.feedback.rating === 'up' ? '👍 liked it' : item.feedback.rating === 'down' ? '👎 nah' : '➡️ ok'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Pagination */}
          {history.total > 20 && (
            <div className="flex justify-center items-center gap-4 mt-8">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-neon px-5 py-2 text-sm disabled:opacity-30"
              >
                ← prev
              </button>
              <span className="text-slate-400 text-sm">
                {page} / {Math.ceil(history.total / 20)}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page * 20 >= history.total}
                className="btn-neon px-5 py-2 text-sm disabled:opacity-30"
              >
                next →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="glass-card p-16 text-center animate-fadeIn">
          <div className="text-7xl mb-5 animate-float">🌱</div>
          <h2 className="text-2xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
            no history yet
          </h2>
          <p className="text-slate-400 mb-6">your journey starts with your first mood check-in ✨</p>
          <a href="/mood" className="btn-neon py-3 px-8 inline-flex items-center gap-2">
            🧠 check in now
          </a>
        </div>
      )}
    </div>
  )
}
