import time
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from ..database import check_database_connection

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
            "status": "healthy",
            "connected": True,
            "database": result.get("dialect"),
            "latency_ms": result.get("latency_ms"),
            "message": "Database connection verified successfully"
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "connected": False,
                "database": result.get("dialect"),
                "latency_ms": result.get("latency_ms"),
                "error": result.get("error"),
                "message": "Database connection failed or temporarily unavailable"
            }
        )


@router.get("")
def health_check_api():
    """General API liveness health check."""
    return {
        "status": "ok",
        "service": "LifeTrack AI Backend",
        "timestamp": time.time()
    }
