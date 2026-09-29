# LevelUp AI

## Plan. Track. Analyze. Improve.

LevelUp AI is an AI-powered personal progress management platform that helps users set goals, generate personalized roadmaps, track progress, analyze performance, and continuously improve.

![LevelUp AI](https://img.shields.io/badge/LevelUp-AI-indigo) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Next.js](https://img.shields.io/badge/Next.js-15-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)

## Features

- **Smart Goal Creation** — Define goals across categories: Academics, Coding, Fitness, Career, Personal Development
- **AI-Powered Roadmaps** — Generate intelligent weekly breakdowns customized for your timeline and level
- **Google OAuth 2.0 & Email Dual-Auth** — Seamless Google sign-in with mandatory first-time password setup and zero duplicate accounts
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
levelup-ai/
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

## PostgreSQL Setup

Follow this comprehensive guide to configure, migrate, and verify your PostgreSQL database layer for LevelUp AI.

### 1. How to Create / Provision a PostgreSQL Database
- **Local PostgreSQL**:
  ```sql
  -- In psql or pgAdmin:
  CREATE DATABASE "TRACKDB";
  ```
- **Hosted Cloud PostgreSQL**:
  You can provision a managed PostgreSQL instance with providers such as:
  - [Supabase](https://supabase.com)
  - [Neon](https://neon.tech)
  - [AWS RDS](https://aws.amazon.com/rds/postgresql/)
  - [Render](https://render.com)
  - [Railway](https://railway.app)

### 2. Where to Obtain DATABASE_URL
The connection string format follows standard URI conventions:
```
postgresql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE_NAME>
```
*For cloud databases requiring TLS/SSL, append `?sslmode=require`.*

### 3. How to Configure `.env`
Create a `.env` file inside the `backend/` directory by copying `.env.example`:
```bash
copy backend\.env.example backend\.env    # Windows
cp backend/.env.example backend/.env        # macOS/Linux
```
Set your `DATABASE_URL`:
```ini
DATABASE_URL=postgresql://postgres:Ankur2802@localhost:5432/TRACKDB
```
*Note: The application automatically normalizes `postgres://` or `postgresql://` to use the modern `postgresql+psycopg://` driver.*

### 4. How to Install Database Dependencies
Inside your virtual environment:
```bash
cd backend
pip install -r requirements.txt
```
Key database packages installed:
- `SQLAlchemy>=2.0.0`
- `alembic>=1.13.0`
- `psycopg[binary]>=3.1.0`
- `pydantic-settings>=2.0.0`
- `bcrypt>=4.0.0`

### 5. How to Run Migrations
LevelUp AI uses Alembic as the official schema management engine. To apply all migrations up to the latest revision:
```bash
alembic upgrade head
```
To check current revision state:
```bash
alembic current
```
To view migration history:
```bash
alembic history --verbose
```

### 6. How to Rollback Migrations
To revert the most recent migration:
```bash
alembic downgrade -1
```
To revert all migrations back to a clean state:
```bash
alembic downgrade base
```

### 7. How to Seed Demo Data
To safely populate development data (demo user Alex, sample multi-category goals, roadmaps, milestones, tasks, check-ins, progress records, and AI analyses):
```bash
python -m app.seed
```
*The seed script is never executed automatically in production environments.*

### 8. How to Test Database Connectivity
- **Via HTTP Health Check Endpoint**:
  ```bash
  curl http://127.0.0.1:8000/api/health/db
  ```
  Expected Response:
  ```json
  {
    "status": "ok",
    "connected": true,
    "database": "connected",
    "dialect": "postgresql",
    "latency_ms": 1.17,
    "message": "Database connection verified successfully"
  }
  ```
- **Via Automated Tests**:
  ```bash
  pytest tests/test_database_layer.py -v
  ```

### 9. How to Inspect Tables
In `psql`:
```sql
\c TRACKDB
\dt
\d users
\d goals
\d roadmaps
\d milestones
\d tasks
\d weekly_checkins
```
Or via Python CLI:
```bash
python -c "from app.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### 10. Troubleshooting Common Connection Errors
| Error Symptom | Cause | Solution |
|---------------|-------|----------|
| `connection to server at "localhost", port 5432 failed` | PostgreSQL service not running | Start the service: `net start postgresql-x64-18` (Windows) or `sudo systemctl start postgresql` (Linux). |
| `password authentication failed for user "postgres"` | Incorrect credentials in `.env` | Verify your password in `backend/.env`. |
| `database "TRACKDB" does not exist` | Database has not yet been created | Run `CREATE DATABASE "TRACKDB";` in `psql`. |
| `ModuleNotFoundError: No module named 'psycopg'` | Driver not installed in virtual environment | Run `pip install "psycopg[binary]"` inside active venv. |
| `SSL SYSCALL error: EOF detected` | Cloud DB requires SSL mode | Append `?sslmode=require` to `DATABASE_URL`. |


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

### Authentication & OAuth 2.0
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user with email and password |
| POST | `/api/auth/login` | Login with email/username and password |
| GET | `/api/auth/google/url` | Get Google OAuth 2.0 Authorization URL (secrets on backend) |
| POST | `/api/auth/google/callback` | Exchange OAuth code, auto-create user, check password setup |
| POST | `/api/auth/create-password` | Mandatory first-time password setup for new Google users |
| POST | `/api/auth/set-password` | Change/update password for authenticated user |
| GET | `/api/auth/me` | Get current user profile (includes `has_password`, `oauth_provider`) |

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

LevelUp AI features a provider-agnostic, multi-provider AI architecture supporting:
- **OpenAI** — Official OpenAI Python SDK with Responses API & Chat Completions JSON schema support.
- **Google Gemini** — Official `google-genai` SDK with native JSON structured output mode (`gemini-2.5-flash`).
- **Groq** — Official `groq` SDK for ultra-low-latency structured inference (`llama-3.3-70b-versatile`).
- **Mock** — Context-aware offline development fallback.

### Multi-Provider & Automatic Fallback Chain
Configure the primary provider and optional sequential fallback list in `backend/.env`:
```env
AI_PROVIDER=openai
AI_FALLBACK_PROVIDERS=gemini,groq

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5.6-luna

GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
```

- **Unified Interface (`AIProvider`)**: All providers strictly enforce identical Pydantic output models (`RoadmapData`, `AnalysisResult`, `AdjustmentSuggestion`, `MonthlySummary`).
- **Bounded Fallback**: Transient availability issues (429 Rate Limit, 502/503/504 Service Unavailable, Network Timeouts) safely attempt each fallback provider at most once.
- **No Retry Storms**: Schema validation errors are not retried against fallback providers.
- **Security & Privacy**: All LLM calls execute strictly inside the FastAPI backend. API keys and prompt boundaries are never exposed to client browsers or source control.

## Authentication & Security Architecture
 
LevelUp AI supports dual-authentication with a single unified identity:
 
1. **Google OAuth 2.0 / OpenID Connect**:
   - Google client secrets are stored exclusively in the backend `.env` (`GOOGLE_CLIENT_SECRET`).
   - The frontend requests the authorization URL via `GET /api/auth/google/url`.
   - On first sign-in via Google, the user is automatically created in PostgreSQL with `oauth_provider="google"` and `has_password=False`.
 
2. **Mandatory First-Time Password Setup (`/create-password`)**:
   - A new Google user is immediately redirected to `/create-password`.
   - The user must create and confirm a password (minimum 6 characters) before accessing `/dashboard`.
   - Passwords are encrypted using bcrypt hashing (passwords are never stored in plaintext).
   - Once set, the user can sign in using **either** "Continue with Google" or traditional email + password.
 
3. **Zero Duplicate Accounts (Single Identity)**:
   - Both Google OAuth and email login resolve to the **same `user_id`**.
   - If an existing user logs in with Google, their accounts are automatically linked without duplicate rows.
   - An existing Google user with an already configured password bypasses the setup page and enters `/dashboard` directly.
 
 
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
| `AI_PROVIDER` | AI provider selection (`openai`, `gemini`, `groq`, `mock`) | `openai` |

### Frontend (`frontend/.env.local`)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_CONTACT_EMAIL` | Destination email for Contact Us mailto link | `ankuromshukla161@gmail.com` |

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
