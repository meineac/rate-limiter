"""Sliding-window rate-limiting algorithm backed by a Lua script."""

import math
import time

import redis.asyncio as redis

from app.algorithms.base import RateLimiter

# Lua script for atomic sliding-window increment.
# KEYS[1] = previous window key
# KEYS[2] = current window key
# ARGV[1] = 2 * window (TTL for the current key)
# ARGV[2] = current timestamp (now)
# ARGV[3] = current_window start time
#
# Returns: curr_count (after INCR), prev_count, elapsed
_LUA_SCRIPT = """
local prev_count = redis.call('GET', KEYS[1])
if prev_count == false then
    prev_count = 0
else
    prev_count = tonumber(prev_count)
end

local curr_count = redis.call('INCR', KEYS[2])

if curr_count == 1 then
    redis.call('EXPIRE', KEYS[2], tonumber(ARGV[1]))
end

local elapsed = tonumber(ARGV[2]) - tonumber(ARGV[3])

return {curr_count, prev_count, elapsed}
"""


class SlidingWindowLimiter(RateLimiter):
    """Sliding-window rate limiter.

    Combines the count from the previous fixed window (weighted by how much
    of that window still overlaps with the sliding window) with the current
    window's count.
    """

    def __init__(self) -> None:
        self._script: redis.client.Script | None = None

    async def check(
        self, redis_client: redis.Redis, key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        now = int(time.time())
        current_window = (now // window) * window
        previous_window = current_window - window

        curr_key = f"{key}:{current_window}"
        prev_key = f"{key}:{previous_window}"

        # Register the script once, then reuse it
        if self._script is None:
            self._script = redis_client.register_script(_LUA_SCRIPT)

        result = await self._script(
            keys=[prev_key, curr_key],
            args=[2 * window, now, current_window],
        )

        curr_count, prev_count, elapsed = int(result[0]), int(result[1]), int(result[2])

        # Weighted calculation
        weight = (window - elapsed) / window
        weighted = prev_count * weight + curr_count

        allowed = weighted <= limit
        remaining = max(0, limit - math.ceil(weighted))
        reset_at = current_window + window

        return allowed, remaining, reset_at
