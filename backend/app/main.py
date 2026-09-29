import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from .database import check_database_connection
from .config import settings
from .routers import (
    auth_router,
    goals_router,
    roadmap_router,
    checkins_router,
    analytics_router,
    ai_router,
    health_router,
)

# Import all models so Alembic and Base know about them
from .models import (  # noqa: F401
    User,
    Goal,
    Roadmap,
    RoadmapWeek,
    Task,
    WeeklyCheckin,
    CheckinTask,
    ProgressRecord,
    AIAnalysis,
    RoadmapAdjustment,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Non-blocking database connection check on startup
    # Note: Schema is managed via Alembic migrations, NOT Base.metadata.create_all()
    health = check_database_connection()
    if health.get("connected"):
        logger.info(f"Database connected successfully ({health.get('dialect')}, latency: {health.get('latency_ms')}ms)")
    else:
        logger.warning(
            f"Database currently unreachable at startup: {health.get('error')}. "
            "FastAPI will start anyway. Database-dependent endpoints will return 503 until connection is restored."
        )
    yield


app = FastAPI(
    title="LevelUp AI",
    description="AI-powered personal progress management platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Global database connection error handler
@app.exception_handler(OperationalError)
async def db_operational_exception_handler(request: Request, exc: OperationalError):
    logger.error(f"Database operational error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database is temporarily unavailable. Please check DATABASE_URL and ensure PostgreSQL is running.",
            "error_type": "DatabaseUnavailable"
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(goals_router)
app.include_router(roadmap_router)
app.include_router(checkins_router)
app.include_router(analytics_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to LevelUp AI Backend",
        "docs": "/docs",
        "health": "/api/health/db",
        "version": "1.0.0",
    }
