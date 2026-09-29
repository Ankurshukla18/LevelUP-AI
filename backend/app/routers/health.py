import time
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from ..database import check_database_connection
from ..config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/db")
def health_check_db():
    """
    Database Health Check Endpoint.
    Verifies that FastAPI can successfully connect to the database (PostgreSQL/SQLite)
    and execute queries. Returns 200 OK when healthy, 503 Service Unavailable when unreachable.
    """
    result = check_database_connection()
    if result.get("connected"):
        return {
            "status": "ok",
            "connected": True,
            "database": "connected",
            "dialect": result.get("dialect"),
            "latency_ms": result.get("latency_ms"),
            "message": "Database connection verified successfully"
        }
    else:
        # Prevent exposing raw DB exception or internal connection details in production
        is_prod = getattr(settings, "ENVIRONMENT", "").lower() == "production"
        err_msg = "Database connection failed" if is_prod else result.get("error")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "connected": False,
                "database": result.get("dialect"),
                "latency_ms": result.get("latency_ms"),
                "error": err_msg,
                "message": "Database connection failed or temporarily unavailable"
            }
        )


@router.get("")
def health_check_api():
    """General API liveness health check."""
    return {
        "status": "ok",
        "service": "LevelUp AI Backend",
        "timestamp": time.time()
    }
