import redis.asyncio as redis

from app.config import settings

redis_pool: redis.Redis | None = None


async def init_redis() -> None:
    global redis_pool
    redis_pool = redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


async def close_redis() -> None:
    global redis_pool
    if redis_pool is not None:
        await redis_pool.aclose()
        redis_pool = None


def get_redis() -> redis.Redis:
    if redis_pool is None:
        raise RuntimeError("Redis pool is not initialized. Call init_redis() first.")
    return redis_pool
