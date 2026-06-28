"""Algorithm registry – maps strategy names to limiter implementations."""

from app.algorithms.fixed_window import FixedWindowLimiter
from app.algorithms.sliding_window import SlidingWindowLimiter

_limiters = {
    "fixed_window": FixedWindowLimiter(),
    "sliding_window": SlidingWindowLimiter(),
}


def get_limiter(strategy: str):
    """Return the limiter instance for the given strategy name.

    Raises ValueError if the strategy is unknown.
    """
    limiter = _limiters.get(strategy)
    if not limiter:
        raise ValueError(f"Unknown strategy: {strategy}")
    return limiter
