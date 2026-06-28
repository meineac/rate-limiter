"""Abstract base class for rate-limiting algorithms."""

from abc import ABC, abstractmethod

import redis.asyncio as redis


class RateLimiter(ABC):
    @abstractmethod
    async def check(
        self, redis_client: redis.Redis, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        """Check rate limit.

        Returns:
            A tuple of (allowed, remaining, reset_at).
        """
        pass
