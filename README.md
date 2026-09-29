# LifeTrack AI

**Plan. Track. Analyze. Improve.**

LifeTrack AI is a personal progress management platform designed for students. It allows users to create long-term goals, generate AI-powered roadmaps, track weekly progress, compare planned vs actual work, receive AI-generated analysis, and dynamically adjust their roadmap.

![LifeTrack AI](https://img.shields.io/badge/LifeTrack-AI-indigo) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Next.js](https://img.shields.io/badge/Next.js-15-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)

## Features

- **Smart Goal Creation** — Define goals across categories: Academics, Coding, Fitness, Career, Personal Development
- **AI-Powered Roadmaps** — Generate intelligent weekly breakdowns customized for your timeline and level
- **Weekly Check-ins** — Log progress, hours, challenges, and self-assessment each week
- **Automated Progress Calculations** — Task completion %, time completion %, consistency %, streaks
- **AI Weekly Analysis** — Get structured feedback: what went well, what was delayed, recommendations
- **Adaptive Roadmap** — AI suggests roadmap adjustments based on your actual progress
- **Analytics Dashboard** — Recharts visualizations for progress, planned vs actual, trends
- **Monthly Reviews** — Month-over-month comparison and long-term trend analysis
- **Multi-category Support** — Track academics, coding, fitness, and custom goals simultaneously

## Architecture

```
Frontend (Next.js + React + TypeScript)
    ↓ HTTP REST API
FastAPI Backend (Python)
    ↓
Service Layer → SQLAlchemy → PostgreSQL/SQLite
    ↓
AI Service → LLM API (with mock fallback)
```

## Tech Stack

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui**-style components
- **Recharts** for data visualization
- **Lucide React** for icons

### Backend
- **Python 3.11+** with **FastAPI**
- **SQLAlchemy 2.0** ORM
- **Pydantic v2** for validation
- **PostgreSQL** (production) / **SQLite** (development)
- **Alembic** for migrations
- **JWT** authentication with bcrypt password hashing

## Project Structure

```
lifetrack-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User model
│   │   │   ├── goal.py          # Goal with categories & status
│   │   │   ├── roadmap.py       # Roadmap, Week, Task models
│   │   │   ├── checkin.py       # WeeklyCheckin, CheckinTask
│   │   │   ├── progress.py      # ProgressRecord
│   │   │   └── analysis.py      # AIAnalysis, RoadmapAdjustment
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API route handlers
│   │   │   ├── auth.py          # /api/auth/*
│   │   │   ├── goals.py         # /api/goals/*
│   │   │   ├── roadmap.py       # /api/goals/{id}/roadmap/*
│   │   │   ├── checkins.py      # /api/goals/{id}/checkins/*
│   │   │   ├── analytics.py     # /api/dashboard/analytics
│   │   │   └── ai.py            # /api/goals/{id}/analyze
│   │   ├── services/            # Business logic layer
│   │   ├── ai/                  # AI service abstraction
│   │   │   ├── ai_service.py    # Abstract interface
│   │   │   ├── mock_ai_service.py # Mock with realistic responses
│   │   │   ├── prompts.py       # Prompt templates
│   │   │   └── schemas.py       # AI response models
│   │   ├── utils/               # Security, helpers
│   │   └── dependencies/        # FastAPI dependencies
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Pytest test suite
│   ├── seed_data.py             # Demo data script
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── page.tsx             # Landing page
│   │   ├── about/               # About page
│   │   ├── contact/             # Contact page
│   │   ├── login/               # Login page
│   │   ├── register/            # Register page
│   │   ├── dashboard/           # Dashboard with stats & charts
│   │   ├── goals/               # Goal management
│   │   │   ├── new/             # Create goal form
│   │   │   └── [goalId]/        # Goal detail with roadmap
│   │   │       └── checkin/     # Weekly check-in form
│   │   └── monthly-review/      # Monthly review page
│   ├── components/              # Reusable UI components
│   │   ├── ui/                  # shadcn-style primitives
│   │   ├── layout/              # Navbar, Sidebar, Footer
│   │   └── dashboard/           # Dashboard-specific components
│   ├── services/                # API client services
│   ├── contexts/                # React contexts (Auth)
│   ├── hooks/                   # Custom React hooks
│   ├── types/                   # TypeScript interfaces
│   ├── lib/                     # Utilities & constants
│   └── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Run the server (auto-creates SQLite database)
uvicorn app.main:app --reload --port 8000

# (Optional) Seed demo data
python seed_data.py
```

The API will be available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env.local    # Windows
# cp .env.example .env.local    # macOS/Linux

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Demo Login
After running the seed script:
- **Email:** alex@demo.com
- **Password:** password123

## API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user profile |

### Goals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/goals` | Create a new goal |
| GET | `/api/goals` | List all user goals |
| GET | `/api/goals/{id}` | Get goal details |
| PUT | `/api/goals/{id}` | Update a goal |
| DELETE | `/api/goals/{id}` | Delete a goal |

### Roadmap
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/goals/{id}/roadmap/generate` | Generate AI roadmap |
| GET | `/api/goals/{id}/roadmap` | Get active roadmap |
| PUT | `/api/roadmap/weeks/{id}` | Update a week |
| PUT | `/api/roadmap/tasks/{id}` | Update/complete a task |
| POST | `/api/roadmap/tasks/{weekId}` | Add task to week |
| DELETE | `/api/roadmap/tasks/{id}` | Delete a task |

### Check-ins
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/goals/{id}/checkins` | Submit weekly check-in |
| GET | `/api/goals/{id}/checkins` | List check-in history |
| GET | `/api/goals/{id}/checkins/{cid}` | Get check-in detail |

### Analytics & AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/goals/{id}/progress` | Get progress records |
| GET | `/api/dashboard/analytics` | Dashboard overview |
| POST | `/api/goals/{id}/analyze` | AI weekly analysis |
| POST | `/api/goals/{id}/roadmap/adjust` | Apply roadmap adjustment |
| POST | `/api/goals/{id}/monthly-review` | Monthly review |

## Database Schema

```
users ─────────── goals ─────────── roadmaps ─────── roadmap_weeks ─── tasks
                    │                    │                  │
                    ├── weekly_checkins ─┤     roadmap_adjustments
                    │        │          │
                    │   checkin_tasks    │
                    │                   │
                    ├── progress_records │
                    │                   │
                    └── ai_analyses ────┘
```

## AI Integration

The AI service uses an abstract interface pattern:

- **`AIService`** — Abstract base class defining the interface
- **`MockAIService`** — Context-aware mock that generates realistic responses based on goal category
- Future: `OpenAIService`, `AnthropicService`, etc.

The mock service generates category-specific roadmaps:
- **Python/Coding:** Variables → Control Flow → Functions → Data Structures → OOP → Projects
- **DSA/Algorithms:** Arrays → Linked Lists → Trees → Graphs → Dynamic Programming
- **Fitness:** Foundation → Volume → Strength → Recovery cycles

All AI calls go through FastAPI — the frontend never directly calls AI providers.

## Progress Calculations

Calculated in Python (not by AI):
- **Task Completion:** `completed_tasks / planned_tasks × 100`
- **Time Completion:** `actual_hours / planned_hours × 100`
- **Consistency:** Average of task and time completion
- **Streak:** Consecutive weeks with check-ins

## Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./lifetrack.db` |
| `SECRET_KEY` | JWT signing key | (change in production!) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `60` |
| `AI_API_KEY` | LLM API key (optional) | (empty = mock) |
| `AI_PROVIDER` | AI provider selection | `mock` |

### Frontend (`frontend/.env.local`)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Testing

```bash
cd backend

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v
```

## Core User Flow

```
Register → Login → Dashboard → Create Goal → Generate AI Roadmap
→ Review/Edit Roadmap → Work on Tasks → Weekly Check-in
→ Backend Calculates Progress → AI Analyzes Week
→ View Dashboard Analytics → AI Suggests Roadmap Adjustment
→ User Approves/Rejects → Continue Tracking
```

## Future Improvements

- [ ] Real LLM integration (OpenAI, Anthropic, Gemini)
- [ ] PostgreSQL for production deployment
- [ ] Export progress reports (PDF/CSV)
- [ ] Email reminders for weekly check-ins
- [ ] Goal sharing and collaboration
- [ ] Mobile app (React Native)
- [ ] Spaced repetition for academic goals
- [ ] Calendar integration
- [ ] Dark mode
- [ ] Notification system

## License

This project is built for educational and portfolio purposes.
