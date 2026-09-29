import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

logger = logging.getLogger(__name__)

# Determine if connecting to SQLite or PostgreSQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,  # Checks connection liveness before checking out from pool
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL connection pool configuration
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    })

try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
except Exception as e:
    logger.error(f"Failed to initialize SQLAlchemy engine with provided DATABASE_URL: {e}")
    # Initialize engine anyway so app startup doesn't immediately crash if DB is temporarily unreachable
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Automatically handles rollback on unhandled exceptions and closes the session.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as err:
        logger.error(f"Database error during transaction, performing rollback: {err}")
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


def check_database_connection() -> dict:
    """
    Verifies that the database engine can successfully connect and execute a ping query.
    Returns diagnostic information and latency.
    """
    import time
    start_time = time.time()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start_time) * 1000, 2)
        dialect = engine.dialect.name
        return {
            "connected": True,
            "dialect": dialect,
            "latency_ms": latency_ms,
            "status": "healthy"
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.warning(f"Database health check failed: {e}")
        return {
            "connected": False,
            "dialect": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "latency_ms": latency_ms,
            "status": "unhealthy",
            "error": str(e)
        }
