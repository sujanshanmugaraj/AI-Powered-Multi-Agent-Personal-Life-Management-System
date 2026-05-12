# LifeOS AI Frontend

Advanced React frontend for the LifeOS AI multi-agent system.

## Features

- 🎨 Modern React 18 with TypeScript
- 🎯 Vite for fast builds
- 🎭 Tailwind CSS for styling
- 📊 Chart.js for data visualization
- 🔄 React Query for API state management
- 🗂️ Zustand for global state
- 📱 Fully responsive design
- ♿ Accessible components
- 🌙 Dark mode support

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
src/
├── components/        # Reusable UI components
├── pages/            # Page components
├── services/         # API client
├── hooks/            # Custom React hooks
├── store/            # Global state (Zustand)
├── types/            # TypeScript interfaces
├── utils/            # Utility functions
├── App.tsx           # Main app component
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## Technology Stack

- **Frontend Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** Zustand + React Query
- **Charts:** Chart.js + react-chartjs-2
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **Notifications:** React Hot Toast

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api/v1`.

**Available Endpoints:**
- `POST /mood` - Analyze mood
- `POST /daily-plan` - Generate daily plan
- `POST /feedback` - Submit feedback
- `GET /history` - Get history

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000/api/v1
```

## Pages

1. **Dashboard** - Overview and statistics
2. **Mood Check-in** - Mood analysis
3. **Daily Plan** - Daily task planning
4. **History** - View past data
5. **Insights** - Advanced analytics

## Components

- `Button` - Styled button component
- `Card` - Container component
- `Form` - Input, TextArea, Select
- `MoodSelector` - Mood selection UI
- `Layout` - Main layout with sidebar
- `Navigation` - Side navigation

## Styling

Uses Tailwind CSS with custom theme colors:
- Primary: Sky blue
- Success: Green
- Warning: Amber
- Danger: Red

## Scripts

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
npm run type-check   # Check types
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting
- Lazy loading routes
- Image optimization
- Efficient state management
- Optimized re-renders with React Query

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

---

**Status:** Production Ready  
**Version:** 1.0.0
