"""
Circuit breaker and resilience patterns for external service calls
"""

import asyncio
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

from circuitbreaker import circuit
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServiceUnavailableError(Exception):
    """Raised when an external service is unavailable"""

    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""

    pass


class CircuitBreakerConfig:
    """Configuration for circuit breakers"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception


# Circuit breaker configurations for different services
CIRCUIT_CONFIGS = {
    "claude_api": CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=(ServiceUnavailableError, RateLimitError),
    ),
    "local_llm": CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60,
        expected_exception=ServiceUnavailableError,
    ),
    "database": CircuitBreakerConfig(
        failure_threshold=10, recovery_timeout=30, expected_exception=Exception
    ),
    "redis": CircuitBreakerConfig(
        failure_threshold=5, recovery_timeout=15, expected_exception=Exception
    ),
}


def circuit_breaker(service_name: str):
    """
    Circuit breaker decorator for service calls

    Args:
        service_name: Name of the service (must be in CIRCUIT_CONFIGS)
    """
    if service_name not in CIRCUIT_CONFIGS:
        raise ValueError(f"Unknown service: {service_name}")

    config = CIRCUIT_CONFIGS[service_name]

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create circuit breaker
        circuit_breaker_func = circuit(
            failure_threshold=config.failure_threshold,
            recovery_timeout=config.recovery_timeout,
            expected_exception=config.expected_exception,
        )(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await circuit_breaker_func(*args, **kwargs)
                else:
                    return circuit_breaker_func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Circuit breaker triggered for {service_name}",
                    service=service_name,
                    error=str(e),
                    error_type=type(e).__name__,
                )

                # Transform circuit breaker exception to service unavailable
                if "CircuitBreakerOpenException" in str(type(e)):
                    raise ServiceUnavailableError(
                        f"{service_name} is temporarily unavailable. Please try again later."
                    )

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return circuit_breaker_func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Circuit breaker triggered for {service_name}",
                    service=service_name,
                    error=str(e),
                    error_type=type(e).__name__,
                )

                if "CircuitBreakerOpenException" in str(type(e)):
                    raise ServiceUnavailableError(
                        f"{service_name} is temporarily unavailable. Please try again later."
                    )

                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def resilient_retry(
    max_attempts: int = 3,
    wait_min: float = 1.0,
    wait_max: float = 10.0,
    retry_exceptions: tuple = (Exception,),
):
    """
    Retry decorator with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        retry_exceptions: Tuple of exception types to retry on
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        retry_func = retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(retry_exceptions),
            reraise=True,
        )(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await retry_func(*args, **kwargs)
                else:
                    return retry_func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"All retry attempts failed for {func.__name__}",
                    function=func.__name__,
                    max_attempts=max_attempts,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return retry_func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"All retry attempts failed for {func.__name__}",
                    function=func.__name__,
                    max_attempts=max_attempts,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class GracefulDegradation:
    """
    Context manager for graceful service degradation
    """

    def __init__(
        self,
        service_name: str,
        fallback_value: Any = None,
        fallback_func: Callable | None = None,
        suppress_errors: bool = True,
    ):
        self.service_name = service_name
        self.fallback_value = fallback_value
        self.fallback_func = fallback_func
        self.suppress_errors = suppress_errors
        self.logger = get_logger(f"degradation.{service_name}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self.suppress_errors:
            self.logger.warning(
                f"Service degradation triggered for {self.service_name}",
                service=self.service_name,
                error=str(exc_val),
                error_type=exc_type.__name__,
            )

            # Return fallback value or call fallback function
            if self.fallback_func:
                return (
                    await self.fallback_func()
                    if asyncio.iscoroutinefunction(self.fallback_func)
                    else self.fallback_func()
                )
            else:
                return self.fallback_value

        return False  # Don't suppress the exception


class TimeoutManager:
    """Timeout management for async operations"""

    @staticmethod
    async def with_timeout(
        coro, timeout_seconds: float, operation_name: str = "operation"
    ):
        """
        Run coroutine with timeout

        Args:
            coro: Coroutine to run
            timeout_seconds: Timeout in seconds
            operation_name: Name for logging
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except TimeoutError:
            logger.warning(
                f"Operation timeout: {operation_name}",
                operation=operation_name,
                timeout_seconds=timeout_seconds,
            )
            raise ServiceUnavailableError(
                f"{operation_name} timed out after {timeout_seconds} seconds"
            )


class ErrorHandler:
    """Centralized error handling utilities"""

    @staticmethod
    def classify_error(error: Exception) -> dict[str, Any]:
        """
        Classify error for appropriate handling

        Returns:
            Dictionary with error classification information
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "is_retryable": False,
            "is_user_error": False,
            "http_status": 500,
            "user_message": "An internal error occurred",
        }

        # Network/Connection errors (retryable)
        if any(
            keyword in str(error).lower()
            for keyword in ["connection", "timeout", "network", "dns", "socket"]
        ):
            error_info.update(
                {
                    "is_retryable": True,
                    "http_status": 503,
                    "user_message": "Service temporarily unavailable. Please try again.",
                }
            )

        # Rate limiting errors (retryable after delay)
        elif any(
            keyword in str(error).lower()
            for keyword in ["rate limit", "too many requests", "quota exceeded"]
        ):
            error_info.update(
                {
                    "is_retryable": True,
                    "http_status": 429,
                    "user_message": "Too many requests. Please wait before trying again.",
                }
            )

        # Authentication errors (not retryable, user action needed)
        elif any(
            keyword in str(error).lower()
            for keyword in [
                "unauthorized",
                "authentication",
                "invalid token",
                "expired",
            ]
        ):
            error_info.update(
                {
                    "is_user_error": True,
                    "http_status": 401,
                    "user_message": "Authentication required. Please sign in.",
                }
            )

        # Authorization errors (not retryable, user action needed)
        elif any(
            keyword in str(error).lower()
            for keyword in ["forbidden", "access denied", "permission"]
        ):
            error_info.update(
                {
                    "is_user_error": True,
                    "http_status": 403,
                    "user_message": "You don't have permission to perform this action.",
                }
            )

        # Validation errors (not retryable, user action needed)
        elif any(
            keyword in str(error).lower()
            for keyword in ["validation", "invalid input", "bad request"]
        ):
            error_info.update(
                {
                    "is_user_error": True,
                    "http_status": 400,
                    "user_message": "Invalid input. Please check your request and try again.",
                }
            )

        return error_info

    @staticmethod
    def get_user_friendly_message(error: Exception) -> str:
        """Get user-friendly error message"""
        error_info = ErrorHandler.classify_error(error)
        return error_info["user_message"]

    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if error is retryable"""
        error_info = ErrorHandler.classify_error(error)
        return error_info["is_retryable"]


# Specific resilience decorators for common services
def claude_resilience(func):
    """Combined resilience patterns for Claude API calls"""
    return circuit_breaker("claude_api")(
        resilient_retry(
            max_attempts=3,
            wait_min=1.0,
            wait_max=10.0,
            retry_exceptions=(ServiceUnavailableError,),
        )(func)
    )


def local_llm_resilience(func):
    """Combined resilience patterns for local LLM calls"""
    return circuit_breaker("local_llm")(
        resilient_retry(
            max_attempts=2,
            wait_min=0.5,
            wait_max=5.0,
            retry_exceptions=(ServiceUnavailableError,),
        )(func)
    )


def database_resilience(func):
    """Combined resilience patterns for database calls"""
    return circuit_breaker("database")(
        resilient_retry(
            max_attempts=3, wait_min=0.1, wait_max=2.0, retry_exceptions=(Exception,)
        )(func)
    )
