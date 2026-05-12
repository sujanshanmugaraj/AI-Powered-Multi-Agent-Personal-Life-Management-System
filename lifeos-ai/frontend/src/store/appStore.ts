import { create } from 'zustand'
import { User, MoodData, DailyPlan } from '@types'

interface AppStore {
  user: User | null
  setUser: (user: User | null) => void
  
  currentMood: MoodData | null
  setCurrentMood: (mood: MoodData | null) => void
  
  currentPlan: DailyPlan | null
  setCurrentPlan: (plan: DailyPlan | null) => void
  
  isDarkMode: boolean
  toggleDarkMode: () => void
  
  sidebarOpen: boolean
  toggleSidebar: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  
  currentMood: null,
  setCurrentMood: (mood) => set({ currentMood: mood }),
  
  currentPlan: null,
  setCurrentPlan: (plan) => set({ currentPlan: plan }),
  
  isDarkMode: localStorage.getItem('theme') === 'dark',
  toggleDarkMode: () =>
    set((state) => {
      const newDarkMode = !state.isDarkMode
      localStorage.setItem('theme', newDarkMode ? 'dark' : 'light')
      return { isDarkMode: newDarkMode }
    }),
  
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}))
