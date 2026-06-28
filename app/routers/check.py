"""Rate-limit check endpoint."""

import hashlib
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms import get_limiter
from app.auth import verify_api_key
from app.database import get_db
from app.models import Rule, Service
from app.redis import get_redis
from app.schemas import CheckRequest, CheckResponse

router = APIRouter(prefix="", tags=["Rate Limiting"])


@router.post("/check", response_model=CheckResponse)
async def check_rate_limit(
    body: CheckRequest,
    service: Service = Depends(verify_api_key),
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Check whether a request is allowed under the specified rule."""
    # 1. Look up the rule and verify ownership
    try:
        rule_uuid = UUID(body.rule_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=404, detail="Rule not found")

    result = await db.execute(select(Rule).where(Rule.id == rule_uuid))
    rule = result.scalars().first()
    if not rule or rule.service_id != service.id:
        raise HTTPException(status_code=404, detail="Rule not found")

    # 2. Build the Redis key
    api_hash = hashlib.sha256(service.api_key.encode()).hexdigest()[:8]
    redis_key = f"rl:{api_hash}:{rule.strategy}:{rule.window}:{body.key}"

    # 3. Get the appropriate limiter and check
    limiter = get_limiter(rule.strategy)
    allowed, remaining, reset_at = await limiter.check(
        redis, redis_key, rule.limit, rule.window
    )

    return CheckResponse(
        allowed=allowed,
        remaining=remaining,
        reset_at=reset_at,
    )

