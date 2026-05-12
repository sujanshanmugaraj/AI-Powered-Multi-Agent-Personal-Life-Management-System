import React from 'react'
import { useAppStore } from '@store/appStore'
import { useStatistics, useMoodHistory } from '@hooks/useApi'
import { Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, ArcElement, BarElement,
  CategoryScale, LinearScale, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const MOOD_COLORS: Record<string, string> = {
  happy: '#22c55e', calm: '#06b6d4', energetic: '#f59e0b',
  stressed: '#ef4444', tired: '#6366f1', sad: '#3b82f6',
  anxious: '#ec4899', neutral: '#94a3b8',
}

const MOOD_EMOJI: Record<string, string> = {
  happy: '😄', calm: '😌', energetic: '⚡',
  stressed: '😤', tired: '😴', sad: '😔',
  anxious: '😰', neutral: '😐',
}

const CHART_OPTS = {
  plugins: {
    legend: { labels: { color: '#94a3b8', font: { family: 'Space Grotesk' }, padding: 16 } },
    tooltip: { backgroundColor: 'rgba(0,0,0,0.85)', titleColor: '#e2e8f0', bodyColor: '#94a3b8' },
  },
}

export const InsightsPage: React.FC = () => {
  const { user } = useAppStore()
  const { data: stats } = useStatistics(user?.id || '')
  const { data: moods } = useMoodHistory(user?.id || '', 30)

  // Build real mood distribution from history
  const moodCounts: Record<string, number> = {}
  if (moods) {
    moods.forEach((m) => { moodCounts[m.mood] = (moodCounts[m.mood] || 0) + 1 })
  }
  const moodLabels  = Object.keys(moodCounts)
  const moodValues  = Object.values(moodCounts)
  const moodColours = moodLabels.map((m) => MOOD_COLORS[m] || '#94a3b8')

  const doughnutData = {
    labels: moodLabels.map((m) => `${MOOD_EMOJI[m] || ''} ${m}`),
    datasets: [{
      data:            moodValues,
      backgroundColor: moodColours.map((c) => `${c}cc`),
      borderColor:     moodColours,
      borderWidth:     1,
      hoverOffset:     8,
    }],
  }

  // Avg stress per mood for bar chart
  const moodStress: Record<string, number[]> = {}
  if (moods) {
    moods.forEach((m) => {
      if (!moodStress[m.mood]) moodStress[m.mood] = []
      moodStress[m.mood].push(m.stress_score * 100)
    })
  }
  const barLabels = Object.keys(moodStress)
  const barValues = barLabels.map((m) => {
    const arr = moodStress[m]
    return Math.round(arr.reduce((a, b) => a + b, 0) / arr.length)
  })

  const barData = {
    labels: barLabels.map((m) => `${MOOD_EMOJI[m] || ''} ${m}`),
    datasets: [{
      label: 'Avg Stress %',
      data:            barValues,
      backgroundColor: barLabels.map((m) => `${MOOD_COLORS[m] || '#94a3b8'}80`),
      borderColor:     barLabels.map((m) => MOOD_COLORS[m] || '#94a3b8'),
      borderWidth:     1,
      borderRadius:    8,
    }],
  }

  const barOpts = {
    ...CHART_OPTS,
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, min: 0, max: 100 },
    },
  }

  // Stats
  const avgStress  = stats?.average_stress  ? Math.round(stats.average_stress  * 100) : null
  const avgEnergy  = stats?.average_energy  ? Math.round(stats.average_energy  * 100) : null
  const topMood    = stats?.average_mood    || 'N/A'
  const totalPlans = stats?.total_plans     ?? 0
  const satisfaction = stats?.positive_feedback_percentage ?? null

  const KPI = [
    { icon: '🧠', label: 'Dominant Mood',     value: `${MOOD_EMOJI[topMood] || ''} ${topMood}`, color: '#a855f7' },
    { icon: '📉', label: 'Avg Stress',         value: avgStress  !== null ? `${avgStress}%`  : 'N/A', color: '#ec4899' },
    { icon: '⚡', label: 'Avg Energy',         value: avgEnergy  !== null ? `${avgEnergy}%`  : 'N/A', color: '#06b6d4' },
    { icon: '📅', label: 'Total Plans',        value: totalPlans,                                      color: '#22c55e' },
  ]

  const TIPS = [
    { emoji: '📝', title: 'Pattern detected',     body: 'You tend to feel more stressed early in the week. Schedule lighter tasks on Mondays.', color: '#06b6d4' },
    { emoji: '🔥', title: 'Keep the streak!',     body: 'Consistent check-ins help the AI learn faster — every day counts.',                    color: '#22c55e' },
    { emoji: '💡', title: 'Mood × productivity',  body: 'When calm, tackle deep work. When stressed, keep tasks small and winnable.',           color: '#a855f7' },
    { emoji: '🎯', title: 'Feedback = smarter AI',body: 'The more you rate your plans, the more personalised they become over time.',            color: '#f59e0b' },
  ]

  return (
    <div className="min-h-screen p-6 md:p-10 max-w-5xl mx-auto">

      {/* Back */}
      <a href="/dashboard" className="inline-flex items-center gap-2 text-slate-400 hover:text-purple-400 text-sm mb-8 transition-colors">
        ← back to dashboard
      </a>

      {/* Header */}
      <div className="mb-8 animate-slideUp">
        <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
          your insights <span className="gradient-text">📊</span>
        </h1>
        <p className="text-slate-400">the numbers don't lie — here's your vibe breakdown 🔍</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {KPI.map((k, i) => (
          <div
            key={i}
            className="stat-card animate-slideUp"
            style={{ animationDelay: `${i * 70}ms`, borderTop: `2px solid ${k.color}40` }}
          >
            <span className="text-2xl block mb-2">{k.icon}</span>
            <p className="text-xs text-slate-400 mb-1 font-medium">{k.label}</p>
            <p className="text-xl font-black capitalize" style={{ color: k.color }}>{k.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        {/* Doughnut */}
        <div className="glass-card p-6 animate-slideUp delay-200">
          <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-4">
            Mood Split — Last 30 Days
          </p>
          {moodLabels.length > 0 ? (
            <div className="h-64 flex items-center justify-center">
              <Doughnut data={doughnutData} options={{ ...CHART_OPTS, maintainAspectRatio: false }} />
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center gap-3 text-slate-500">
              <span className="text-4xl animate-float">🌱</span>
              <p className="text-sm">log some moods first!</p>
            </div>
          )}
        </div>

        {/* Bar */}
        <div className="glass-card p-6 animate-slideUp delay-300">
          <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-4">
            Avg Stress by Mood
          </p>
          {barLabels.length > 0 ? (
            <div className="h-64">
              <Bar data={barData} options={{ ...barOpts, maintainAspectRatio: false }} />
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center gap-3 text-slate-500">
              <span className="text-4xl animate-float">📊</span>
              <p className="text-sm">no data yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Satisfaction bar if we have it */}
      {satisfaction !== null && (
        <div className="glass-card p-5 mb-8 animate-slideUp delay-300">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-white">Plan Satisfaction Score</p>
            <span className="text-neon-green font-black text-xl">{satisfaction}%</span>
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill progress-green" style={{ width: `${satisfaction}%` }} />
          </div>
          <p className="text-xs text-slate-500 mt-2">based on your 👍 / 👎 feedback on generated plans</p>
        </div>
      )}

      {/* Tips / Recommendations */}
      <div className="glass-card p-6 animate-slideUp delay-400">
        <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase mb-5">
          Personalised Tips
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {TIPS.map((t, i) => (
            <div
              key={i}
              className="p-4 rounded-xl"
              style={{ background: `${t.color}0d`, border: `1px solid ${t.color}25` }}
            >
              <p className="font-bold text-sm mb-1 flex items-center gap-2" style={{ color: t.color }}>
                {t.emoji} {t.title}
              </p>
              <p className="text-xs text-slate-400 leading-relaxed">{t.body}</p>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
