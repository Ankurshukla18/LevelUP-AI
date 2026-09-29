from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routers import auth_router, goals_router, roadmap_router, checkins_router, analytics_router, ai_router

# Import all models so Base.metadata knows about them
from .models import User, Goal, Roadmap, RoadmapWeek, Task, WeeklyCheckin, CheckinTask, ProgressRecord, AIAnalysis, RoadmapAdjustment  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (for development with SQLite)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LifeTrack AI",
    description="AI-powered student progress tracking platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(goals_router)
app.include_router(roadmap_router)
app.include_router(checkins_router)
app.include_router(analytics_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to LifeTrack AI Backend",
        "docs": "/docs",
        "version": "1.0.0",
    }
