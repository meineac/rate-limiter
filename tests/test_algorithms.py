"""Unit tests for the algorithm registry and limiter instantiation."""

import pytest

from app.algorithms import get_limiter
from app.algorithms.fixed_window import FixedWindowLimiter
from app.algorithms.sliding_window import SlidingWindowLimiter


class TestGetLimiter:
    """Tests for the get_limiter() factory function."""

    def test_get_fixed_window_limiter(self):
        """get_limiter('fixed_window') should return a FixedWindowLimiter."""
        limiter = get_limiter("fixed_window")
        assert isinstance(limiter, FixedWindowLimiter)

    def test_get_sliding_window_limiter(self):
        """get_limiter('sliding_window') should return a SlidingWindowLimiter."""
        limiter = get_limiter("sliding_window")
        assert isinstance(limiter, SlidingWindowLimiter)

    def test_get_unknown_limiter_raises_value_error(self):
        """get_limiter() with an unknown strategy should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            get_limiter("unknown")

    def test_get_empty_string_raises_value_error(self):
        """get_limiter('') should raise ValueError."""
        with pytest.raises(ValueError):
            get_limiter("")


class TestLimiterInterfaces:
    """Verify that limiter instances expose the expected interface."""

    def test_fixed_window_has_check_method(self):
        """FixedWindowLimiter should have an async check() method."""
        limiter = FixedWindowLimiter()
        assert callable(getattr(limiter, "check", None))

    def test_sliding_window_has_check_method(self):
        """SlidingWindowLimiter should have an async check() method."""
        limiter = SlidingWindowLimiter()
        assert callable(getattr(limiter, "check", None))

    def test_fixed_window_initial_state(self):
        """A new FixedWindowLimiter should have no cached script."""
        limiter = FixedWindowLimiter()
        assert limiter._script is None

    def test_sliding_window_initial_state(self):
        """A new SlidingWindowLimiter should have no cached script."""
        limiter = SlidingWindowLimiter()
        assert limiter._script is None
