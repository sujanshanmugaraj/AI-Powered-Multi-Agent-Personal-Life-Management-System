import React, { useState } from 'react'
import { Card } from './Card'

interface MoodSelectorProps {
  onSelect: (mood: string, description: string) => void
  isLoading?: boolean
}

const MOODS = [
  { emoji: '😄', label: 'Happy', value: 'happy', color: 'bg-yellow-100 hover:bg-yellow-200' },
  { emoji: '😌', label: 'Calm', value: 'calm', color: 'bg-blue-100 hover:bg-blue-200' },
  { emoji: '😤', label: 'Stressed', value: 'stressed', color: 'bg-red-100 hover:bg-red-200' },
  { emoji: '😴', label: 'Tired', value: 'tired', color: 'bg-purple-100 hover:bg-purple-200' },
  { emoji: '😕', label: 'Confused', value: 'confused', color: 'bg-orange-100 hover:bg-orange-200' },
  { emoji: '😔', label: 'Sad', value: 'sad', color: 'bg-gray-100 hover:bg-gray-200' },
]

export const MoodSelector: React.FC<MoodSelectorProps> = ({ onSelect, isLoading }) => {
  const [selectedMood, setSelectedMood] = useState<string | null>(null)
  const [description, setDescription] = useState('')

  const handleSubmit = () => {
    if (selectedMood && description.trim()) {
      onSelect(selectedMood, description)
      setSelectedMood(null)
      setDescription('')
    }
  }

  return (
    <Card title="How are you feeling today?" className="mb-6">
      <div className="space-y-6">
        {/* Mood Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {MOODS.map((mood) => (
            <button
              key={mood.value}
              onClick={() => setSelectedMood(mood.value)}
              className={`p-4 rounded-lg text-center transition-all transform hover:scale-105 ${
                mood.color
              } ${selectedMood === mood.value ? 'ring-2 ring-primary-500 scale-105' : ''}`}
            >
              <div className="text-3xl mb-1">{mood.emoji}</div>
              <div className="text-xs font-medium text-gray-700">{mood.label}</div>
            </button>
          ))}
        </div>

        {/* Description Input */}
        {selectedMood && (
          <div className="animate-slideUp">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Tell me more about how you're feeling..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
        )}

        {/* Submit Button */}
        {selectedMood && (
          <button
            onClick={handleSubmit}
            disabled={!description.trim() || isLoading}
            className="w-full bg-primary-500 text-white py-2 rounded-lg hover:bg-primary-600 disabled:bg-gray-300 transition-colors"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Mood'}
          </button>
        )}
      </div>
    </Card>
  )
}

interface MoodBadgeProps {
  mood: string
  stressScore?: number
  energyScore?: number
}

export const MoodBadge: React.FC<MoodBadgeProps> = ({ mood, stressScore, energyScore }) => {
  const moodEmojis: Record<string, string> = {
    happy: '😄',
    calm: '😌',
    stressed: '😤',
    tired: '😴',
    confused: '😕',
    sad: '😔',
  }

  return (
    <div className="inline-flex items-center bg-gradient-to-r from-primary-50 to-primary-100 rounded-full px-4 py-2">
      <span className="text-2xl mr-2">{moodEmojis[mood] || '😐'}</span>
      <div className="text-sm">
        <p className="font-semibold text-gray-900 capitalize">{mood}</p>
        {stressScore !== undefined && energyScore !== undefined && (
          <p className="text-xs text-gray-600">
            Stress: {Math.round(stressScore * 100)}% | Energy: {Math.round(energyScore * 100)}%
          </p>
        )}
      </div>
    </div>
  )
}
