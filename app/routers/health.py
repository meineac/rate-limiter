"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.redis import get_redis
from app.schemas import HealthResponse

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """Check the health of Redis and Postgres dependencies."""
    redis_status = "ok"
    postgres_status = "ok"

    try:
        await redis.ping()
    except Exception:
        redis_status = "error"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        postgres_status = "error"

    if redis_status == "ok" and postgres_status == "ok":
        overall = "ok"
    else:
        overall = "degraded"

    return HealthResponse(
        status=overall,
        redis=redis_status,
        postgres=postgres_status,
    )
