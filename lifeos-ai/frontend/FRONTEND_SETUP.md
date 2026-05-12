"""
FRONTEND SETUP: Advanced React Application for LifeOS AI
"""

# LifeOS AI Frontend - Setup & Build Guide

## 🚀 Overview

A **modern, advanced React 18 frontend** with TypeScript, Tailwind CSS, and production-ready features.

**Technology Stack:**
- React 18 (latest)
- TypeScript for type safety
- Vite for blazing fast builds
- Tailwind CSS for styling
- React Query for server state
- Zustand for client state
- Chart.js for visualizations
- React Router v6 for navigation

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── Button.tsx          # Styled button component
│   │   ├── Card.tsx            # Card component with variants
│   │   ├── Form.tsx            # Form inputs (Input, TextArea, Select)
│   │   ├── Layout.tsx          # Main layout with sidebar
│   │   ├── MoodSelector.tsx    # Mood selection UI
│   │   └── index.ts            # Barrel export
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx       # Dashboard with stats and charts
│   │   ├── MoodCheckIn.tsx     # Mood analysis page
│   │   ├── DailyPlan.tsx       # Daily plan display
│   │   ├── History.tsx         # Historical data view
│   │   ├── Insights.tsx        # Advanced analytics
│   │   └── index.ts
│   ├── hooks/                  # Custom React hooks
│   │   ├── useApi.ts           # API query hooks
│   │   └── index.ts
│   ├── services/               # API client
│   │   ├── apiClient.ts        # Axios client with interceptors
│   │   └── index.ts
│   ├── store/                  # Global state management
│   │   ├── appStore.ts         # Zustand store
│   │   └── index.ts
│   ├── types/                  # TypeScript interfaces
│   │   └── index.ts
│   ├── utils/                  # Utility functions
│   │   └── index.ts
│   ├── App.tsx                 # Main app with routing
│   ├── main.tsx                # Vite entry point
│   └── index.css               # Global styles
├── public/                     # Static assets
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── vite.config.ts              # Vite config
├── tailwind.config.js          # Tailwind config
├── postcss.config.cjs          # PostCSS config
├── .eslintrc.cjs               # ESLint config
├── .prettierrc.json            # Prettier config
├── .gitignore
├── README.md
└── FRONTEND_SETUP.md           # This file
```

## 🔧 Installation

### Prerequisites
- Node.js 16+ (preferably 18+)
- npm or yarn

### Setup Steps

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create environment file
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local

# 4. Start development server
npm run dev

# Backend should be running on http://localhost:8000
# Frontend will be on http://localhost:3000
```

## 🎯 Available Scripts

```bash
# Development
npm run dev           # Start dev server with hot reload

# Production
npm run build         # Build for production
npm run preview       # Preview production build

# Code Quality
npm run lint          # Run ESLint
npm run format        # Format with Prettier
npm run type-check    # Check TypeScript types
```

## 🎨 Components

### Form Components
```tsx
<Input
  label="Email"
  type="email"
  error="Invalid email"
  icon="✉️"
/>

<TextArea
  label="Feedback"
  placeholder="Your thoughts..."
  rows={4}
/>

<Select
  label="Mood"
  options={[
    { value: 'happy', label: 'Happy' },
    { value: 'sad', label: 'Sad' },
  ]}
/>
```

### Display Components
```tsx
<Card title="Stats" subtitle="Overview">
  {/* Content */}
</Card>

<StatCard
  label="Completed"
  value="24"
  icon="✅"
  trend="up"
  trendValue="+5%"
/>

<MoodBadge
  mood="happy"
  stressScore={0.3}
  energyScore={0.8}
/>
```

### Button Variants
```tsx
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="danger">Danger</Button>
<Button variant="success">Success</Button>
<Button isLoading>Loading...</Button>
```

## 📡 API Integration

The frontend connects to FastAPI backend at: `http://localhost:8000/api/v1`

### Available Endpoints

| Method | Endpoint | Usage |
|--------|----------|-------|
| GET | `/health` | Check backend status |
| POST | `/mood` | Analyze mood |
| POST | `/daily-plan` | Generate daily plan |
| POST | `/feedback` | Submit feedback |
| GET | `/history` | Get user history |
| GET | `/statistics` | Get statistics |

### Example API Call

```typescript
import { apiClient } from '@services'

const moodData = await apiClient.analyzeMood('user123', 'I feel stressed')
```

## 🪝 Custom Hooks

```typescript
// Mood Analysis
const { data: mood, isLoading } = useMoodAnalysis(userId, text, enabled)

// Daily Plan
const { data: plan, isLoading } = useDailyPlan(userId, date, enabled)

// History
const { data: history } = useHistory(userId, limit, offset)

// Mutations
const { mutate: submitFeedback } = useSubmitFeedback()
```

## 🗂️ State Management

**Zustand Store:**
```typescript
import { useAppStore } from '@store'

const { user, setUser, isDarkMode, toggleDarkMode } = useAppStore()
```

**Features:**
- User state
- Current mood & plan
- Dark mode toggle
- Sidebar state
- Persistent localStorage

## 🎨 Tailwind Theme

### Custom Colors
- Primary: Sky blue
- Success: Green
- Warning: Amber
- Danger: Red

### Animations
- `animate-fadeIn` - Fade in effect
- `animate-slideUp` - Slide up effect
- `animate-slideDown` - Slide down effect

## 📄 Pages

### 1. Login Page
- User name input
- Simple authentication
- LocalStorage persistence

### 2. Dashboard
- Stats overview (4 cards)
- 7-day mood trend chart
- Quick action buttons
- Recent plans list

### 3. Mood Check-in
- Interactive mood selector (6 moods)
- Mood description input
- Analysis results with scores
- Recommendations sidebar

### 4. Daily Plan
- Date selector
- Plan timeline with checkboxes
- Agent proposals display
- Feedback submission form

### 5. History
- Paginated historical data
- Mood, plan, feedback display
- Date filtering
- Expandable details

### 6. Insights
- Advanced analytics
- Mood distribution chart
- Weekly performance chart
- Personalized recommendations

## 🔄 Data Flow

```
User Input
    ↓
React Component
    ↓
useApi Hook (React Query)
    ↓
apiClient (Axios)
    ↓
Backend API
    ↓
Response
    ↓
useAppStore (Zustand)
    ↓
Component Update (re-render)
```

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm, md, lg, xl
- Sidebar collapses on mobile
- Touch-friendly UI

## ♿ Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- High contrast colors

## ⚡ Performance

- Code splitting with Vite
- Lazy loading routes
- Optimized re-renders
- Image optimization
- Efficient caching with React Query

## 🌙 Dark Mode

Toggle via `useAppStore().toggleDarkMode()`

Automatically saves preference to localStorage.

## 🔐 Error Handling

- API error handling with toast notifications
- Fallback UI states
- Loading states for all async operations
- 401 redirect to login

## 📊 Chart Integration

Uses Chart.js with react-chartjs-2:

```typescript
import { Line, Bar, Doughnut } from 'react-chartjs-2'

<Line data={chartData} options={options} />
```

## 🧪 Best Practices

- Type-safe with TypeScript
- Proper error boundaries
- Loading states
- Optimistic updates
- Cache invalidation
- Clean component structure

## 🚀 Build & Deploy

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
# Output in dist/ directory
```

### Preview Production Build
```bash
npm run preview
```

### Deploy
- Build: `npm run build`
- Upload `dist/` folder to hosting
- Ensure backend API is accessible

## 📝 Environment Variables

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000/api/v1
```

## 🐛 Debugging

- Browser DevTools
- React DevTools extension
- Redux DevTools (via Zustand)
- Network tab for API calls

## 📚 Additional Resources

- React: https://react.dev
- TypeScript: https://www.typescriptlang.org
- Tailwind: https://tailwindcss.com
- Vite: https://vitejs.dev
- React Query: https://tanstack.com/query

## ✅ Checklist Before Deployment

- [ ] Environment variables configured
- [ ] Backend running and accessible
- [ ] All pages tested
- [ ] API calls working
- [ ] No console errors
- [ ] Responsive design verified
- [ ] Dark mode working
- [ ] Build completes without errors
- [ ] Production build previewed

## 📞 Troubleshooting

### Frontend won't load
- Check if backend is running: `http://localhost:8000/health`
- Verify API URL in `.env.local`
- Check browser console for errors

### API calls failing
- Ensure backend is running
- Check CORS configuration
- Verify endpoint paths
- Check network in DevTools

### Build failing
- Delete `node_modules` and `.next`
- Run `npm install` again
- Check Node version (16+)

### Styling issues
- Clear browser cache
- Restart dev server
- Rebuild Tailwind: `npm run build`

---

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** May 11, 2026
