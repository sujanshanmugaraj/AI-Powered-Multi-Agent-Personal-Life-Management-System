import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { apiClient } from '../services/apiClient'

export const Login: React.FC = () => {
  const [name,  setName]  = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !email.trim()) {
      toast.error('fill in both fields bestie 😭')
      return
    }
    setLoading(true)
    try {
      const user = await apiClient.createOrGetUser(name, email)
      localStorage.setItem('user_id',    String(user.id))
      localStorage.setItem('user_name',  user.name)
      localStorage.setItem('user_email', user.email)
      toast.success(`welcome aboard ${user.name} ✨`)
      setTimeout(() => { window.location.href = '/dashboard' }, 700)
    } catch {
      toast.error('something broke 💀 check the backend')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{
        background: 'radial-gradient(ellipse 80% 60% at 50% -30%, rgba(168,85,247,0.2), transparent), #080810',
      }}
    >
      {/* Floating orbs — z-index:-1 so they never block inputs */}
      <div className="fixed inset-0 overflow-hidden" style={{ zIndex: -1, pointerEvents: 'none' }}>
        <div className="absolute w-96 h-96 rounded-full blur-3xl opacity-20 animate-float"
          style={{ background: '#7c3aed', top: '10%', left: '10%' }} />
        <div className="absolute w-72 h-72 rounded-full blur-3xl opacity-15 animate-float delay-300"
          style={{ background: '#ec4899', top: '60%', right: '10%' }} />
        <div className="absolute w-64 h-64 rounded-full blur-3xl opacity-10 animate-float delay-500"
          style={{ background: '#06b6d4', top: '40%', left: '60%' }} />
      </div>

      <div className="w-full max-w-md" style={{ position: 'relative', zIndex: 10 }}>

        {/* Logo block */}
        <div className="text-center mb-10 animate-slideUp">
          <div
            className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl mx-auto mb-5 animate-glow"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #ec4899)' }}
          >
            ✨
          </div>
          <h1 className="text-4xl font-black text-white mb-2 gradient-text" style={{ fontFamily: 'Syne, sans-serif' }}>
            LifeOS
          </h1>
          <p className="text-slate-400 text-lg">your AI life manager is waiting fr 🤖</p>
        </div>

        {/* Card */}
        <div className="glass-card p-8 animate-slideUp delay-100">
          <h2 className="text-xl font-bold text-white mb-1" style={{ fontFamily: 'Syne, sans-serif' }}>
            jump right in 🚀
          </h2>
          <p className="text-slate-400 text-sm mb-6">new or returning — we've got you</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-slate-400 font-semibold tracking-wider uppercase block mb-2">
                your name
              </label>
              <input
                type="text"
                className="input-genz"
                placeholder="Priya, Alex, Ravi..."
                value={name}
                onChange={e => setName(e.target.value)}
                autoComplete="off"
              />
            </div>

            <div>
              <label className="text-xs text-slate-400 font-semibold tracking-wider uppercase block mb-2">
                email
              </label>
              <input
                type="email"
                className="input-genz"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-neon w-full py-4 text-base mt-2 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-purple-300 border-t-transparent rounded-full animate-spin" />
                  setting you up...
                </>
              ) : (
                <>let's go →</>
              )}
            </button>
          </form>

          <p className="text-center text-xs text-slate-600 mt-5">
            existing account? same email = auto login ✅
          </p>
        </div>

        {/* Features strip */}
        <div className="grid grid-cols-3 gap-3 mt-6 animate-slideUp delay-200">
          {[
            { emoji: '🧠', label: 'Mood AI' },
            { emoji: '📅', label: 'Smart Plans' },
            { emoji: '📈', label: 'Insights' },
          ].map((f) => (
            <div key={f.label} className="glass-card p-3 text-center">
              <div className="text-2xl mb-1">{f.emoji}</div>
              <p className="text-xs text-slate-400 font-medium">{f.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
