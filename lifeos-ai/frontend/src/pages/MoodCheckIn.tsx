import React, { useState, useRef, useEffect } from 'react'
import { useAppStore } from '@store/appStore'
import { useMoodAnalysis } from '@hooks/useApi'
import toast from 'react-hot-toast'

const MOOD_OPTIONS = [
  { emoji: '😤', label: 'Stressed',  value: 'stressed',  color: '#ef4444', desc: 'too much going on rn' },
  { emoji: '😴', label: 'Tired',     value: 'tired',     color: '#6366f1', desc: 'low energy, meh' },
  { emoji: '⚡', label: 'Energetic', value: 'energetic', color: '#f59e0b', desc: 'ready to go!!' },
  { emoji: '😄', label: 'Happy',     value: 'happy',     color: '#22c55e', desc: 'vibing fr' },
  { emoji: '😌', label: 'Calm',      value: 'calm',      color: '#06b6d4', desc: 'chill mode on' },
  { emoji: '😔', label: 'Sad',       value: 'sad',       color: '#3b82f6', desc: 'not okay but it\'s ok' },
  { emoji: '😰', label: 'Anxious',   value: 'anxious',   color: '#ec4899', desc: 'butterflies 🦋' },
  { emoji: '😐', label: 'Neutral',   value: 'neutral',   color: '#94a3b8', desc: 'just existing' },
]

const PROMPTS = [
  "yo what's the vibe today? 👀",
  "spill — how u actually feeling? 💬",
  "no cap, how's the mental state rn? 🧠",
  "real talk, what's going on with you? 🫂",
  "bestie check-in time ✨ what's up?",
]

const BAR: React.FC<{ pct: number; color: string; label: string }> = ({ pct, color, label }) => {
  const [width, setWidth] = useState(0)
  useEffect(() => { setTimeout(() => setWidth(pct), 150) }, [pct])
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-slate-400 font-medium">{label}</span>
        <span className="font-bold" style={{ color }}>{pct}%</span>
      </div>
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${width}%`, background: `linear-gradient(90deg, ${color}88, ${color})`, transition: 'width 1.2s cubic-bezier(0.4,0,0.2,1)' }}
        />
      </div>
    </div>
  )
}

export const MoodCheckInPage: React.FC = () => {
  const { user, setCurrentMood } = useAppStore()
  const [selected, setSelected]   = useState<string | null>(null)
  const [freeText, setFreeText]   = useState('')
  const [shouldFetch, setShouldFetch] = useState(false)
  const [promptIdx]               = useState(() => Math.floor(Math.random() * PROMPTS.length))
  const textareaRef               = useRef<HTMLTextAreaElement>(null)

  const { data: moodData, isLoading } = useMoodAnalysis(
    user?.id || '',
    freeText || selected || '',
    shouldFetch,
  )

  useEffect(() => {
    if (moodData) {
      setCurrentMood(moodData)
      toast.success('mood analyzed! 🧠', { style: { background: '#1e1b4b', color: '#e2e8f0', border: '1px solid #7c3aed' } })
      setShouldFetch(false)
    }
  }, [moodData, setCurrentMood])

  const handleSubmit = () => {
    if (!freeText.trim() && !selected) {
      toast.error('tell me something first bestie 😭')
      return
    }
    setShouldFetch(true)
  }

  const handleMoodPillClick = (val: string) => {
    setSelected(val)
    const opt = MOOD_OPTIONS.find(m => m.value === val)
    if (opt && !freeText) setFreeText(`feeling ${opt.label.toLowerCase()}, ${opt.desc}`)
    textareaRef.current?.focus()
  }

  const detectedMood = MOOD_OPTIONS.find(m => m.value === moodData?.mood)
  const stressPct    = moodData ? Math.round(moodData.stress_score * 100) : 0
  const energyPct    = moodData ? Math.round(moodData.energy_score * 100) : 0
  const confPct      = moodData ? Math.round(moodData.confidence  * 100) : 0

  return (
    <div className="min-h-screen p-6 md:p-10 max-w-4xl mx-auto">

      {/* Back nav */}
      <a href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-purple-400 text-sm mb-8 transition-colors">
        ← back to dashboard
      </a>

      {/* Header */}
      <div className="mb-8 animate-slideUp">
        <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Syne, sans-serif' }}>
          mood check-in <span className="gradient-text">✨</span>
        </h1>
        <p className="text-slate-400 text-lg">{PROMPTS[promptIdx]}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Left: Input section */}
        <div className="lg:col-span-3 space-y-5">

          {/* Mood pills */}
          <div className="glass-card p-5 animate-slideUp delay-100">
            <p className="text-xs text-slate-500 font-semibold tracking-widest uppercase mb-4">Quick pick</p>
            <div className="flex flex-wrap gap-2">
              {MOOD_OPTIONS.map((m) => {
                const isActive = selected === m.value
                return (
                  <button
                    key={m.value}
                    onClick={() => handleMoodPillClick(m.value)}
                    className="mood-pill transition-all duration-200"
                    style={{
                      background:   isActive ? `${m.color}25` : 'rgba(255,255,255,0.04)',
                      border:       `1px solid ${isActive ? m.color : 'rgba(255,255,255,0.08)'}`,
                      color:        isActive ? m.color : '#94a3b8',
                      boxShadow:    isActive ? `0 0 15px ${m.color}40` : 'none',
                      transform:    isActive ? 'scale(1.05)' : 'scale(1)',
                    }}
                  >
                    {m.emoji} {m.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Free-text input */}
          <div className="glass-card p-5 animate-slideUp delay-200">
            <p className="text-xs text-slate-500 font-semibold tracking-widest uppercase mb-3">Or just say it</p>
            <textarea
              ref={textareaRef}
              className="input-genz"
              rows={4}
              placeholder="e.g. yaar aaj bahut thaka hoon 😴  •  super stressed about deadline 😤  •  feeling hyped ngl 💪"
              value={freeText}
              onChange={e => setFreeText(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) handleSubmit() }}
            />
            <p className="text-xs text-slate-600 mt-2">hint: use any language, slang, emojis — we get it all 🌍</p>
          </div>

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="btn-neon w-full py-4 text-base flex items-center justify-center gap-3 relative overflow-hidden"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-purple-300 border-t-transparent rounded-full animate-spin" />
                <span>AI is reading the vibes...</span>
              </>
            ) : (
              <>
                <span className="text-xl">🧠</span>
                <span>analyze my vibe</span>
                <span className="text-xs text-purple-300 ml-1">(⌘ Enter)</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-4">
          {moodData ? (
            <>
              {/* Main mood card */}
              <div
                className="glass-card p-6 animate-bounce-in"
                style={{ border: `1px solid ${detectedMood?.color || '#a855f7'}40`, boxShadow: `0 0 30px ${detectedMood?.color || '#a855f7'}15` }}
              >
                <p className="text-xs text-slate-500 font-semibold tracking-widest uppercase mb-4">Detected Vibe</p>
                <div className="text-center mb-5">
                  <div className="text-7xl mb-3 animate-float">{detectedMood?.emoji || '😐'}</div>
                  <h2 className="text-2xl font-black text-white capitalize" style={{ fontFamily: 'Syne, sans-serif' }}>
                    {moodData.mood}
                  </h2>
                  <p className="text-sm text-slate-400 mt-1 italic">"{detectedMood?.desc}"</p>
                </div>

                {/* Bars */}
                <div className="space-y-4">
                  <BAR pct={stressPct} color="#ec4899" label="Stress Level" />
                  <BAR pct={energyPct} color="#06b6d4" label="Energy Level" />
                  <BAR pct={confPct}   color="#a855f7" label="AI Confidence" />
                </div>
              </div>

              {/* Reasoning */}
              <div className="glass-card p-4 animate-slideUp">
                <p className="text-xs text-slate-500 font-semibold tracking-widest uppercase mb-2">AI's Take</p>
                <p className="text-sm text-slate-300 leading-relaxed">{moodData.reasoning}</p>
              </div>

              {/* CTA */}
              <a
                href="/plan"
                className="btn-neon btn-neon-cyan w-full py-4 flex items-center justify-center gap-2 text-sm"
              >
                <span>📅</span> generate today's plan
              </a>
            </>
          ) : (
            /* Empty state */
            <div className="glass-card p-8 text-center animate-fadeIn h-full flex flex-col items-center justify-center gap-4 min-h-64">
              <div className="text-6xl animate-float">🎯</div>
              <div>
                <p className="text-white font-bold text-lg mb-1">your vibe meter</p>
                <p className="text-slate-500 text-sm">pick a mood or type something and AI will analyze your emotional state in real time</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tips strip */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3 animate-slideUp delay-400">
        {[
          { emoji: '💧', tip: 'Drink water rn seriously' },
          { emoji: '🚶', tip: '10-min walk = instant serotonin' },
          { emoji: '📵', tip: 'Phone down for 30 mins' },
          { emoji: '💤', tip: '7-9 hrs sleep is non-negotiable' },
        ].map((t, i) => (
          <div key={i} className="glass-card p-3 flex items-center gap-3">
            <span className="text-xl flex-shrink-0">{t.emoji}</span>
            <p className="text-xs text-slate-400">{t.tip}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
