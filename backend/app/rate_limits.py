import time

from app.extensions import limiter

STRICT_LIMIT = "5 per minute"
FALLBACK_WAIT_SECONDS = 60


def strict_limit():
    return limiter.limit(STRICT_LIMIT)


def seconds_until_reset() -> int:
    current = limiter.current_limit
    if current is None:
        return FALLBACK_WAIT_SECONDS
    remaining = current.reset_at - int(time.time())
    return max(1, min(remaining, current.limit.get_expiry()))


def describe_wait(seconds: int) -> str:
    return "1 second" if seconds == 1 else f"{seconds} seconds"
