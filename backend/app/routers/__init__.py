from fastapi import APIRouter

from .auth import router as auth_router
from .goals import router as goals_router
from .roadmap import router as roadmap_router
from .checkins import router as checkins_router
from .analytics import router as analytics_router
from .ai import router as ai_router

__all__ = [
    "auth_router", "goals_router", "roadmap_router",
    "checkins_router", "analytics_router", "ai_router"
]
