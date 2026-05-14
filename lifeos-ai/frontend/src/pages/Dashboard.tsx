import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useStatistics, useMoodHistory } from '@hooks/useApi'
import { format } from 'date-fns'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const MOOD_EMOJI: Record<string, string> = {
  stressed: '😤', tired: '😴', energetic: '⚡', happy: '😄',
  sad: '😔', calm: '😌', anxious: '😰', neutral: '😐',
}

const MOOD_COLOR: Record<string, string> = {
  stressed: '#ef4444', tired: '#6366f1', energetic: '#f59e0b',
  happy: '#22c55e', sad: '#3b82f6', calm: '#06b6d4', anxious: '#ec4899', neutral: '#94a3b8',
}

/* ── Floating particle background ── */
const Particles: React.FC = () => (
  <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
    {[...Array(18)].map((_, i) => (
      <div
        key={i}
        className="absolute rounded-full"
        style={{
          width:  `${Math.random() * 4 + 2}px`,
          height: `${Math.random() * 4 + 2}px`,
          left:   `${Math.random() * 100}%`,
          bottom: '-10px',
          background: ['#a855f7','#ec4899','#06b6d4','#22c55e'][i % 4],
          animation: `particle-float ${8 + Math.random() * 10}s ${Math.random() * 8}s linear infinite`,
          opacity: 0.6,
        }}
      />
    ))}
  </div>
)

/* ── Sidebar nav ── */
const NAV = [
  { href: '/',        icon: '🏠', label: 'Home'    },
  { href: '/mood',    icon: '🧠', label: 'Mood'    },
  { href: '/plan',    icon: '📅', label: 'Plan'    },
  { href: '/history', icon: '🕰️', label: 'History' },
  { href: '/insights',icon: '📊', label: 'Insights'},
]

const Sidebar: React.FC<{ userName: string }> = ({ userName }) => {
  const active = window.location.pathname
  const handleLogout = () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_email')
    window.location.href = '/login'
  }
  return (
    <aside
      className="fixed left-0 top-0 h-screen w-64 flex flex-col z-50 glass-strong"
      style={{ borderRight: '1px solid rgba(168,85,247,0.15)' }}
    >
      {/* Logo */}
      <div className="p-6 border-b" style={{ borderColor: 'rgba(168,85,247,0.15)' }}>
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center text-xl animate-float"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #ec4899)' }}
          >
            ✨
          </div>
          <div>
            <h1 className="font-bold text-white text-lg leading-none" style={{ fontFamily: 'Syne, sans-serif' }}>
              LifeOS
            </h1>
            <p className="text-xs text-purple-400 mt-0.5">AI Life Manager</p>
          </div>
        </div>
      </div>

      {/* User */}
      <div className="px-6 py-4 border-b" style={{ borderColor: 'rgba(168,85,247,0.1)' }}>
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold"
            style={{ background: 'linear-gradient(135deg, #a855f7, #06b6d4)' }}
          >
            {userName[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{userName}</p>
            <p className="text-xs text-slate-400">Active now 🟢</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV.map((item) => {
          const isActive = active === item.href
          return (
            <Link
              key={item.href}
              to={item.href}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 no-underline"
              style={{
                background: isActive ? 'linear-gradient(135deg, rgba(168,85,247,0.25), rgba(236,72,153,0.15))' : 'transparent',
                color:      isActive ? '#e2e8f0' : '#94a3b8',
                border:     isActive ? '1px solid rgba(168,85,247,0.3)' : '1px solid transparent',
                boxShadow:  isActive ? '0 0 20px rgba(168,85,247,0.15)' : 'none',
                display: 'flex'
              }}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
              {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-400" />}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t" style={{ borderColor: 'rgba(168,85,247,0.1)' }}>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 transition-all hover:bg-red-500/10 hover:text-red-300"
        >
          <span>🚪</span> Logout
        </button>
      </div>
    </aside>
  )
}

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const userName = localStorage.getItem('user_name') || 'User'
  const userId   = localStorage.getItem('user_id')   || ''
  const { data: stats }  = useStatistics(userId)
  const { data: moods }  = useMoodHistory(userId, 7)
  const [chartData, setChartData] = useState<any>(null)
  const [greeting, setGreeting] = useState('')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const h = new Date().getHours()
    if (h < 12)      setGreeting("gm bestie ☀️")
    else if (h < 17) setGreeting("hey 👋")
    else             setGreeting("evening vibes 🌙")
    setTimeout(() => setVisible(true), 100)
  }, [])

  useEffect(() => {
    if (moods && moods.length > 0) {
      setChartData({
        labels: moods.map((m) => format(new Date(m.created_at || ''), 'MMM dd')).reverse(),
        datasets: [
          {
            label: 'Stress %',
            data: [...moods].reverse().map((m) => Math.round((m.stress_score || 0) * 100)),
            borderColor: '#ec4899',
            backgroundColor: 'rgba(236,72,153,0.08)',
            tension: 0.5,
            fill: true,
            pointBackgroundColor: '#ec4899',
            pointRadius: 4,
            pointHoverRadius: 7,
          },
          {
            label: 'Energy %',
            data: [...moods].reverse().map((m) => Math.round((m.energy_score || 0) * 100)),
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6,182,212,0.08)',
            tension: 0.5,
            fill: true,
            pointBackgroundColor: '#06b6d4',
            pointRadius: 4,
            pointHoverRadius: 7,
          },
        ],
      })
    }
  }, [moods])

  const STATS = [
    { icon: '🧠', label: 'Dominant Mood',  value: `${MOOD_EMOJI[stats?.average_mood || 'neutral'] || '😐'} ${stats?.average_mood || 'N/A'}`, color: '#a855f7' },
    { icon: '📅', label: 'Plans Created',  value: stats?.total_plans ?? 0,                                                                        color: '#06b6d4' },
    { icon: '📉', label: 'Avg Stress',     value: stats?.average_stress ? `${Math.round(stats.average_stress * 100)}%` : 'N/A',                   color: '#ec4899' },
    { icon: '⚡', label: 'Avg Energy',     value: stats?.average_energy ? `${Math.round(stats.average_energy * 100)}%` : 'N/A',                   color: '#22c55e' },
  ]

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--bg-dark)' }}>
      <Particles />
      <Sidebar userName={userName} />

      {/* Main content */}
      <main className="flex-1 ml-64 p-8 relative z-10">

        {/* Header */}
        <div className={`mb-8 transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <p className="text-sm text-purple-400 font-semibold mb-1 tracking-widest uppercase">{greeting}</p>
          <h1 className="text-4xl font-black text-white" style={{ fontFamily: 'Syne, sans-serif' }}>
            What's the vibe,{' '}
            <span className="gradient-text">{userName}?</span>
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            {format(new Date(), 'EEEE, MMMM do')} · Your AI crew is ready 🤖
          </p>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {STATS.map((s, i) => (
            <div
              key={i}
              className="stat-card animate-slideUp"
              style={{ animationDelay: `${i * 80}ms`, borderTop: `2px solid ${s.color}30` }}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">{s.icon}</span>
                <span className="tag-chip">LIVE</span>
              </div>
              <p className="text-xs text-slate-400 font-medium mb-1">{s.label}</p>
              <p className="text-2xl font-bold text-white capitalize" style={{ color: s.color }}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* Chart + Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Chart */}
          <div className="lg:col-span-2 glass-card p-6 animate-slideUp delay-200">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-white font-bold text-lg" style={{ fontFamily: 'Syne, sans-serif' }}>
                  Mood Trends
                </h3>
                <p className="text-slate-400 text-sm">Last 7 days — stress vs energy</p>
              </div>
              <span className="tag-chip">📈 LIVE</span>
            </div>
            {chartData ? (
              <Line
                data={chartData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { labels: { color: '#94a3b8', font: { family: 'Space Grotesk' } } },
                    tooltip: { backgroundColor: 'rgba(0,0,0,0.8)', titleColor: '#e2e8f0', bodyColor: '#94a3b8' },
                  },
                  scales: {
                    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 0, max: 100 },
                  },
                }}
              />
            ) : (
              <div className="h-64 flex flex-col items-center justify-center gap-3 text-slate-500">
                <span className="text-5xl animate-float">📊</span>
                <p className="text-sm">No data yet — go log your first mood!</p>
                <Link to="/mood" className="btn-neon text-sm no-underline">Check in now →</Link>
              </div>
            )}
          </div>

          {/* Quick actions */}
          <div className="glass-card p-6 animate-slideUp delay-300">
            <h3 className="text-white font-bold text-lg mb-5" style={{ fontFamily: 'Syne, sans-serif' }}>
              Quick Actions
            </h3>
            <div className="space-y-3">
              {[
                { href: '/mood',    emoji: '🧠', label: 'Check in mood',   sub: 'How u feeling rn?',    color: '#a855f7' },
                { href: '/plan',    emoji: '📅', label: 'Generate plan',   sub: 'Let AI cook 🍳',        color: '#06b6d4' },
                { href: '/history', emoji: '🕰️', label: 'View history',   sub: 'Your journey so far',   color: '#ec4899' },
                { href: '/insights',emoji: '📊', label: 'See insights',   sub: 'Numbers don\'t lie',    color: '#22c55e' },
              ].map((item) => (
                <div
                  key={item.href}
                  onClick={() => navigate(item.href)}
                  className="flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group cursor-pointer relative z-20"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
                  onMouseEnter={e => (e.currentTarget.style.borderColor = `${item.color}40`)}
                  onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)')}
                >
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 transition-transform group-hover:scale-110"
                    style={{ background: `${item.color}20`, border: `1px solid ${item.color}30` }}
                  >
                    {item.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.sub}</p>
                  </div>
                  <span className="text-slate-600 group-hover:text-slate-400 transition-colors">→</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mood log feed */}
        {moods && moods.length > 0 && (
          <div className="glass-card p-6 animate-slideUp delay-400">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-white font-bold text-lg" style={{ fontFamily: 'Syne, sans-serif' }}>
                Recent Mood Logs
              </h3>
              <Link to="/history" className="text-xs text-purple-400 hover:text-purple-300 transition-colors no-underline">
                View all →
              </Link>
            </div>
            <div className="space-y-3">
              {moods.slice(0, 5).map((m, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 p-3 rounded-xl"
                  style={{ background: 'rgba(255,255,255,0.03)', animationDelay: `${i * 60}ms` }}
                >
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                    style={{ background: `${MOOD_COLOR[m.mood] || '#94a3b8'}20`, border: `1px solid ${MOOD_COLOR[m.mood] || '#94a3b8'}30` }}
                  >
                    {MOOD_EMOJI[m.mood] || '😐'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white capitalize">{m.mood}</p>
                    <p className="text-xs text-slate-500">{m.created_at ? format(new Date(m.created_at), 'MMM dd, h:mm a') : ''}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400">Stress: <span className="text-pink-400 font-semibold">{Math.round((m.stress_score || 0) * 100)}%</span></p>
                    <p className="text-xs text-slate-400">Energy: <span className="text-cyan-400 font-semibold">{Math.round((m.energy_score || 0) * 100)}%</span></p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
