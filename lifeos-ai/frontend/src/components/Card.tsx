import React from 'react'
import classNames from 'classnames'

interface CardProps {
  children: React.ReactNode
  className?: string
  title?: string
  subtitle?: string
  hoverable?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  title,
  subtitle,
  hoverable = false,
}) => {
  return (
    <div
      className={classNames(
        'bg-white rounded-lg shadow-soft p-6 transition-all',
        hoverable && 'hover:shadow-base hover:scale-105',
        className
      )}
    >
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string | number
  icon?: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, icon, trend, trendValue }) => {
  const trendColors = {
    up: 'text-success-600',
    down: 'text-danger-600',
    neutral: 'text-gray-600',
  }

  return (
    <Card className="hover:shadow-base">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && trendValue && (
            <p className={`text-sm mt-2 ${trendColors[trend]}`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
            </p>
          )}
        </div>
        {icon && <div className="text-3xl text-primary-500">{icon}</div>}
      </div>
    </Card>
  )
}
