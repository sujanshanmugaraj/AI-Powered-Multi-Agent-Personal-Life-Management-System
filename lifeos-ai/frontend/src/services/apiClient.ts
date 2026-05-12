import axios, { AxiosInstance } from 'axios'
import { MoodData, DailyPlan, Feedback, HistoryItem, User } from '@types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user_id')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await axios.get('http://localhost:8000/health')
      return response.data
    } catch (error) {
      throw new Error('Backend is not reachable')
    }
  }

  // ============ User Management ============

  async createOrGetUser(name: string, email: string): Promise<User> {
    const response = await this.client.post('/users', { name, email })
    return response.data
  }

  async getUser(userId: string): Promise<User> {
    const response = await this.client.get(`/users/${userId}`)
    return response.data
  }

  // ============ Mood Analysis ============

  // Mood analysis
  async analyzeMood(userId: string, text: string): Promise<MoodData> {
    const response = await this.client.post('/mood', {
      user_id: parseInt(userId),
      text,
    })
    return response.data
  }

  // Daily plan generation
  async generateDailyPlan(userId: string, date: string): Promise<DailyPlan> {
    const response = await this.client.post('/daily-plan', {
      user_id: parseInt(userId),
      date,
    })
    return response.data
  }

  // Submit feedback
  async submitFeedback(feedback: Feedback): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post('/feedback', {
      ...feedback,
      user_id: parseInt(feedback.user_id),
      plan_id: parseInt(feedback.plan_id),
    })
    return response.data
  }

  // Get history — backend returns { mood_logs, plans, total_plans }
  // We merge them into { items, total } for the History page.
  async getHistory(
    userId: string,
    limit: number = 30,
    offset: number = 0
  ): Promise<{ items: HistoryItem[]; total: number }> {
    const response = await this.client.get('/history', {
      params: { user_id: userId, limit, offset },
    })

    const data = response.data

    // Build a unified items list from plans (join matching mood log by date if possible)
    const moodLogs: any[] = data.mood_logs || []
    const plans: any[] = data.plans || []

    // Map plans into HistoryItems, attach a matching mood log when timestamps are close
    const items: HistoryItem[] = plans.map((plan: any) => {
      const planDate = new Date(plan.created_at)
      // Find a mood log within the same day
      const matchingMood = moodLogs.find((log: any) => {
        const logDate = new Date(log.created_at)
        return Math.abs(planDate.getTime() - logDate.getTime()) < 24 * 60 * 60 * 1000
      })
      return {
        id: String(plan.id),
        created_at: plan.created_at,
        plan: { id: String(plan.id), plan: plan.plan, explanation: plan.explanation, agent_proposals: [] },
        mood: matchingMood
          ? {
              mood: matchingMood.mood,
              stress_score: matchingMood.stress_score,
              energy_score: matchingMood.energy_score,
              confidence: 0.8,
              reasoning: '',
            }
          : undefined,
      }
    })

    return { items, total: data.total_plans || items.length }
  }

  // Get mood logs
  async getMoodLogs(userId: string, days: number = 7): Promise<MoodData[]> {
    const response = await this.client.get('/mood-logs', {
      params: {
        user_id: userId,
        days,
      },
    })
    return response.data
  }

  // Get statistics
  async getStatistics(userId: string): Promise<any> {
    const response = await this.client.get('/statistics', {
      params: {
        user_id: userId,
      },
    })
    return response.data
  }
}

export const apiClient = new ApiClient()
