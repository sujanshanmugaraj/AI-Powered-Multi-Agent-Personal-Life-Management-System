import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useAppStore } from '@store/appStore'
import { useHealthCheck } from '@hooks/useApi'

// Seed dark class from localStorage before first render
if (localStorage.getItem('theme') === 'dark') {
  document.documentElement.classList.add('dark')
}

// Pages
import { Dashboard } from '@pages/Dashboard'
import { MoodCheckInPage } from '@pages/MoodCheckIn'
import { DailyPlanPage } from '@pages/DailyPlan'
import { HistoryPage } from '@pages/History'
import { InsightsPage } from '@pages/Insights'
import { Login } from '@pages/Login'

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
})

// Protected Route
interface ProtectedRouteProps {
  element: React.ReactElement
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ element }) => {
  const userId = localStorage.getItem('user_id')
  return userId ? element : <Navigate to="/login" replace />
}

// App content component with health check inside QueryClientProvider
const AppContent: React.FC = () => {
  const userId = localStorage.getItem('user_id')
  const { data: health } = useHealthCheck()

  return (
    <Router>
      <Routes>
        <Route path="/" element={userId ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
        <Route path="/login" element={userId ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
        <Route path="/mood" element={<ProtectedRoute element={<MoodCheckInPage />} />} />
        <Route path="/plan" element={<ProtectedRoute element={<DailyPlanPage />} />} />
        <Route path="/history" element={<ProtectedRoute element={<HistoryPage />} />} />
        <Route path="/insights" element={<ProtectedRoute element={<InsightsPage />} />} />
        <Route path="*" element={<Navigate to={userId ? "/dashboard" : "/login"} replace />} />
      </Routes>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'rgba(15,10,30,0.95)',
            color: '#e2e8f0',
            border: '1px solid rgba(168,85,247,0.3)',
            borderRadius: '14px',
            fontFamily: 'Space Grotesk, sans-serif',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 0 30px rgba(168,85,247,0.15)',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: '#0f0a1e' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#0f0a1e' } },
        }}
      />

      {/* Backend offline warning */}
      {!health && (
        <div className="fixed bottom-24 right-6 glass-card px-4 py-3 text-sm text-yellow-400 flex items-center gap-2 animate-slideUp">
          <span>⚠️</span> backend seems offline
        </div>
      )}
    </Router>
  )
}

// Main App
function App() {
  const setUser = useAppStore((state) => state.setUser)
  const isDarkMode = useAppStore((state) => state.isDarkMode)

  // Sync dark class on <html> whenever isDarkMode changes
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDarkMode])

  // Initialize user from localStorage on app start
  useEffect(() => {
    const userId = localStorage.getItem('user_id')
    const userName = localStorage.getItem('user_name')
    const userEmail = localStorage.getItem('user_email')

    if (userId && userName && userEmail) {
      setUser({
        id: parseInt(userId),
        name: userName,
        email: userEmail,
      })
    }
  }, [setUser])

  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}

export default App
