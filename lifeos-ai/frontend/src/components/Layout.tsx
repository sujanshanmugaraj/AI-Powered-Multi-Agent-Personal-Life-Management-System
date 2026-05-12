import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import classNames from 'classnames'
import { useAppStore } from '@store/appStore'

interface NavLink {
  path: string
  label: string
  icon: React.ReactNode
}

export const Navigation: React.FC = () => {
  const location = useLocation()
  const { sidebarOpen, toggleSidebar } = useAppStore()

  const navLinks: NavLink[] = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/mood', label: 'Mood Check-in', icon: '😊' },
    { path: '/plan', label: 'Daily Plan', icon: '📅' },
    { path: '/history', label: 'History', icon: '📈' },
    { path: '/insights', label: 'Insights', icon: '💡' },
  ]

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={toggleSidebar}
        className="fixed bottom-6 right-6 z-40 md:hidden bg-primary-500 text-white p-3 rounded-full shadow-lg hover:bg-primary-600 transition-colors"
      >
        ☰
      </button>

      {/* Sidebar */}
      <aside
        className={classNames(
          'fixed left-0 top-0 h-screen w-64 bg-gradient-to-b from-primary-900 to-primary-800 text-white transition-transform md:translate-x-0 z-30',
          !sidebarOpen && '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="p-6 border-b border-primary-700">
          <h1 className="text-2xl font-bold">🤖 LifeOS</h1>
          <p className="text-xs text-primary-200 mt-1">AI Personal Assistant</p>
        </div>

        {/* Navigation Links */}
        <nav className="mt-8">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={classNames(
                'flex items-center px-6 py-3 text-sm font-medium transition-colors',
                location.pathname === link.path
                  ? 'bg-primary-700 border-r-4 border-primary-300'
                  : 'hover:bg-primary-700'
              )}
            >
              <span className="mr-3 text-lg">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-primary-700 text-xs text-primary-200">
          <p>Version 1.0</p>
          <p className="mt-2">© 2026 LifeOS AI</p>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          onClick={toggleSidebar}
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-20"
        />
      )}
    </>
  )
}

export const Header: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const { isDarkMode, toggleDarkMode } = useAppStore()

  return (
    <header className="bg-white dark:bg-gray-900 shadow-soft dark:shadow-none border-b dark:border-gray-700 px-6 py-4 mb-6">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h2>
          {subtitle && <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-200"
          title="Toggle dark mode"
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  )
}

interface MainLayoutProps {
  children: React.ReactNode
  title: string
  subtitle?: string
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children, title, subtitle }) => {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
      {/* Sidebar Navigation */}
      <Navigation />

      {/* Main Content */}
      <main className="flex-1 md:ml-64">
        <Header title={title} subtitle={subtitle} />
        <div className="px-6 pb-12 max-w-7xl">
          <div className="animate-fadeIn">{children}</div>
        </div>
      </main>
    </div>
  )
}
