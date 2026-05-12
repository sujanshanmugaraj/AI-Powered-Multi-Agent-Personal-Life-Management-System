import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@services/apiClient'
import { MoodData, DailyPlan, Feedback, HistoryItem } from '@types'

// Mood queries
export const useMoodAnalysis = (userId: string, text: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['mood', userId, text],
    queryFn: () => apiClient.analyzeMood(userId, text),
    enabled: enabled && !!userId && !!text,
    staleTime: 0,
  })
}

export const useMoodHistory = (userId: string, days: number = 7) => {
  return useQuery({
    queryKey: ['mood-history', userId, days],
    queryFn: () => apiClient.getMoodLogs(userId, days),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Daily plan queries
export const useDailyPlan = (userId: string, date: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['daily-plan', userId, date],
    queryFn: () => apiClient.generateDailyPlan(userId, date),
    enabled: enabled && !!userId,
    staleTime: 0,
  })
}

// History queries
export const useHistory = (userId: string, limit: number = 30, offset: number = 0) => {
  return useQuery({
    queryKey: ['history', userId, limit, offset],
    queryFn: () => apiClient.getHistory(userId, limit, offset),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Statistics
export const useStatistics = (userId: string) => {
  return useQuery({
    queryKey: ['statistics', userId],
    queryFn: () => apiClient.getStatistics(userId),
    enabled: !!userId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

// Mutations
export const useSubmitFeedback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (feedback: Feedback) => apiClient.submitFeedback(feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
      queryClient.invalidateQueries({ queryKey: ['statistics'] })
    },
  })
}

// Health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.checkHealth(),
    staleTime: 1000 * 60, // 1 minute
  })
}
