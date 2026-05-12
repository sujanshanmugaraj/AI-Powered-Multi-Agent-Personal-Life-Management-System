// Utility function to format numbers
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num)
}

// Utility to get initials from name
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

// Utility to format percentage
export const formatPercent = (value: number): string => {
  return `${Math.round(value * 100)}%`
}

// Utility to get color based on value
export const getStatusColor = (value: number): string => {
  if (value >= 0.7) return 'text-success-600'
  if (value >= 0.4) return 'text-warning-600'
  return 'text-danger-600'
}
