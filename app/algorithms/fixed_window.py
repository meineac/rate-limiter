"""Fixed-window rate-limiting algorithm backed by a Lua script."""

import time

import redis.asyncio as redis

from app.algorithms.base import RateLimiter

# Lua script for atomic fixed-window increment.
# KEYS[1] = the window key
# ARGV[1] = TTL (remaining seconds in the window)
#
# Returns: current count after increment
_LUA_SCRIPT = """
local current = redis.call('GET', KEYS[1])
if current == false then
    current = 0
else
    current = tonumber(current)
end

local count = redis.call('INCR', KEYS[1])

if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

return count
"""


class FixedWindowLimiter(RateLimiter):
    """Fixed-window rate limiter.

    Divides time into fixed-size windows and counts requests per window.
    """

    def __init__(self) -> None:
        self._script: redis.client.Script | None = None

    async def check(
        self, redis_client: redis.Redis, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        now = int(time.time())
        window_start = (now // window) * window
        window_key = f"{key}:{window_start}"
        ttl = window - (now - window_start)

        # Register the script once, then reuse it
        if self._script is None:
            self._script = redis_client.register_script(_LUA_SCRIPT)

        count: int = await self._script(keys=[window_key], args=[ttl])

        allowed = count <= limit
        remaining = max(0, limit - count)
        reset_at = window_start + window

        return allowed, remaining, reset_at
