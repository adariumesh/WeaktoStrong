"""
Monitoring and observability setup with Sentry and metrics
"""

import logging
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

import sentry_sdk
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

AI_REQUEST_COUNT = Counter(
    "ai_requests_total", "Total AI requests", ["model", "tier", "status"]
)

AI_REQUEST_DURATION = Histogram(
    "ai_request_duration_seconds", "AI request duration in seconds", ["model", "tier"]
)

TOKEN_USAGE = Counter(
    "ai_tokens_used_total", "Total AI tokens used", ["model", "user_tier"]
)

ACTIVE_CONNECTIONS = Gauge("active_database_connections", "Active database connections")

ERROR_COUNT = Counter(
    "application_errors_total", "Total application errors", ["error_type", "endpoint"]
)


def setup_sentry():
    """Configure Sentry for error tracking"""
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured, skipping Sentry setup")
        return

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=settings.version,
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
            RedisIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=1.0 if settings.is_development else 0.1,
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        debug=settings.debug,
    )

    logger.info("Sentry initialized", environment=settings.environment)


def setup_metrics():
    """Setup metrics collection"""
    if settings.enable_metrics:
        logger.info("Metrics collection enabled", port=settings.metrics_port)
    else:
        logger.info("Metrics collection disabled")


def track_request_metrics(
    method: str, endpoint: str, status_code: int, duration: float
):
    """Track HTTP request metrics"""
    if settings.enable_metrics:
        REQUEST_COUNT.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def track_ai_metrics(
    model: str,
    tier: str,
    status: str,
    duration: float,
    tokens_used: int = 0,
    user_tier: str = "free",
):
    """Track AI request metrics"""
    if settings.enable_metrics:
        AI_REQUEST_COUNT.labels(model=model, tier=tier, status=status).inc()

        AI_REQUEST_DURATION.labels(model=model, tier=tier).observe(duration)

        if tokens_used > 0:
            TOKEN_USAGE.labels(model=model, user_tier=user_tier).inc(tokens_used)


def track_error(error_type: str, endpoint: str = "unknown"):
    """Track application errors"""
    if settings.enable_metrics:
        ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint).inc()


def get_metrics():
    """Get Prometheus metrics for /metrics endpoint"""
    return generate_latest()


class MetricsMiddleware:
    """Middleware for tracking HTTP request metrics"""

    def __init__(self):
        self.logger = get_logger("metrics")

    async def __call__(self, request, call_next):
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time

            # Track successful request
            track_request_metrics(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )

            return response

        except Exception as exc:
            duration = time.perf_counter() - start_time

            # Track error
            track_request_metrics(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration,
            )

            track_error(error_type=type(exc).__name__, endpoint=request.url.path)

            # Re-raise exception
            raise


def monitor_ai_request(model: str, tier: str, user_tier: str = "free"):
    """Decorator for monitoring AI requests"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start_time

                # Extract tokens used if available
                tokens_used = 0
                if isinstance(result, dict) and "tokens_used" in result:
                    tokens_used = result["tokens_used"]

                track_ai_metrics(
                    model=model,
                    tier=tier,
                    status="success",
                    duration=duration,
                    tokens_used=tokens_used,
                    user_tier=user_tier,
                )

                return result

            except Exception:
                duration = time.perf_counter() - start_time
                track_ai_metrics(
                    model=model,
                    tier=tier,
                    status="error",
                    duration=duration,
                    user_tier=user_tier,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time

                tokens_used = 0
                if isinstance(result, dict) and "tokens_used" in result:
                    tokens_used = result["tokens_used"]

                track_ai_metrics(
                    model=model,
                    tier=tier,
                    status="success",
                    duration=duration,
                    tokens_used=tokens_used,
                    user_tier=user_tier,
                )

                return result

            except Exception:
                duration = time.perf_counter() - start_time
                track_ai_metrics(
                    model=model,
                    tier=tier,
                    status="error",
                    duration=duration,
                    user_tier=user_tier,
                )
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@asynccontextmanager
async def monitor_database_connections(engine):
    """Context manager to monitor database connection pool"""
    if settings.enable_metrics:
        try:
            # Get connection pool info
            pool = engine.pool
            ACTIVE_CONNECTIONS.set(pool.checkedout())
            yield
        finally:
            if hasattr(engine, "pool"):
                ACTIVE_CONNECTIONS.set(engine.pool.checkedout())
    else:
        yield


class HealthChecker:
    """Health check utilities"""

    def __init__(self):
        self.logger = get_logger("health")

    async def check_database(self, engine) -> dict[str, Any]:
        """Check database connectivity"""
        try:
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            return {"status": "healthy", "details": "Database connection successful"}
        except Exception as e:
            self.logger.error("Database health check failed", error=str(e))
            return {"status": "unhealthy", "details": f"Database error: {e!s}"}

    async def check_redis(self, redis_client) -> dict[str, Any]:
        """Check Redis connectivity"""
        try:
            await redis_client.ping()
            return {"status": "healthy", "details": "Redis connection successful"}
        except Exception as e:
            self.logger.error("Redis health check failed", error=str(e))
            return {"status": "unhealthy", "details": f"Redis error: {e!s}"}

    async def check_ai_services(self) -> dict[str, Any]:
        """Check AI services availability"""
        checks = {}

        # Check local LLM
        try:
            from app.core.ai.local_llm import local_llm_service

            local_healthy = await local_llm_service.health_check()
            checks["local_llm"] = {
                "status": "healthy" if local_healthy else "unhealthy",
                "details": "Local LLM service check",
            }
        except Exception as e:
            checks["local_llm"] = {
                "status": "unhealthy",
                "details": f"Local LLM error: {e!s}",
            }

        # Check Claude API
        try:
            from app.core.ai.claude_client import claude_service

            claude_healthy = await claude_service.health_check()
            checks["claude"] = {
                "status": "healthy" if claude_healthy else "unhealthy",
                "details": "Claude API service check",
            }
        except Exception as e:
            checks["claude"] = {
                "status": "unhealthy",
                "details": f"Claude API error: {e!s}",
            }

        return checks

    async def comprehensive_health_check(
        self, engine, redis_client=None
    ) -> dict[str, Any]:
        """Run all health checks"""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.version,
            "environment": settings.environment,
            "checks": {},
        }

        # Database check
        db_health = await self.check_database(engine)
        health_status["checks"]["database"] = db_health

        # Redis check
        if redis_client:
            redis_health = await self.check_redis(redis_client)
            health_status["checks"]["redis"] = redis_health

        # AI services check
        ai_health = await self.check_ai_services()
        health_status["checks"]["ai_services"] = ai_health

        # Overall status
        all_healthy = all(
            check.get("status") == "healthy"
            for service_checks in health_status["checks"].values()
            for check in (
                service_checks
                if isinstance(service_checks, dict) and "status" in service_checks
                else service_checks.values() if isinstance(service_checks, dict) else []
            )
        )

        if not all_healthy:
            health_status["status"] = "unhealthy"

        return health_status


# Global health checker instance
health_checker = HealthChecker()
