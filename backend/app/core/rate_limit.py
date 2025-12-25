"""
Rate limiting utilities
"""

import time

from fastapi import HTTPException, Request, status

# In-memory rate limit store (replace with Redis in production)
_rate_limit_store: dict[str, dict[str, float]] = {}


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 3600,  # 1 hour
    identifier: str | None = None,
) -> None:
    """
    Check if request should be rate limited

    Args:
        request: FastAPI request object
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        identifier: Custom identifier (defaults to IP address)
    """
    # Get identifier (IP or custom)
    if identifier is None:
        identifier = get_client_ip(request)

    current_time = time.time()
    window_start = current_time - window_seconds

    # Initialize user data if not exists
    if identifier not in _rate_limit_store:
        _rate_limit_store[identifier] = {}

    user_data = _rate_limit_store[identifier]

    # Clean old timestamps
    user_data = {
        timestamp: value
        for timestamp, value in user_data.items()
        if float(timestamp) > window_start
    }
    _rate_limit_store[identifier] = user_data

    # Check if limit exceeded
    if len(user_data) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds.",
        )

    # Add current request
    user_data[str(current_time)] = current_time


async def auth_rate_limit(request: Request) -> None:
    """Rate limit for auth endpoints (100 requests per hour for free tier)"""
    check_rate_limit(request, max_requests=100, window_seconds=3600)


async def general_rate_limit(request: Request) -> None:
    """General rate limit (500 requests per hour)"""
    check_rate_limit(request, max_requests=500, window_seconds=3600)
