// User Type
export interface User {
  id: string
  name: string
  email: string
  created_at?: string
}

// API Response Types
export interface MoodData {
  mood: string
  stress_score: number
  energy_score: number
  confidence: number
  reasoning: string
  created_at?: string
}

export interface AgentProposal {
  agent: string
  proposal: string
  priority: number
  confidence: number
  reasoning: string
  memory_used: string[]
  potential_conflicts: string[]
}

export interface PlanItem {
  time?: string
  task: string
  duration?: number
  agent?: string
  priority?: number
  reason?: string
}

export interface DailyPlan {
  id?: string
  plan_id?: number       // returned by backend after generation
  plan: PlanItem[]
  agent_proposals: AgentProposal[]
  explanation: string
  created_at?: string
  mood?: MoodData
  saved_tasks?: any[]
}

export interface Feedback {
  user_id: string
  plan_id: string
  rating: 'up' | 'down' | 'neutral'
  completed_tasks: string[]
  comments: string
}

export interface HistoryItem {
  id: string
  created_at: string
  mood?: MoodData
  plan?: DailyPlan
  feedback?: Feedback
  task_summaries?: any[]
}

// UI State Types
export interface LoadingState {
  mood: boolean
  plan: boolean
  feedback: boolean
  history: boolean
}

export interface ErrorState {
  mood: string | null
  plan: string | null
  feedback: string | null
  history: string | null
}

export interface AppState {
  user: User | null
  currentMood: MoodData | null
  currentPlan: DailyPlan | null
  history: HistoryItem[]
  loading: LoadingState
  error: ErrorState
}
