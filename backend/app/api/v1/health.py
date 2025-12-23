"""
Health check endpoints for monitoring and observability
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, get_db
from app.core.monitoring import CONTENT_TYPE_LATEST, get_metrics, health_checker

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint
    Returns the overall health status of all services
    """
    health_status = await health_checker.comprehensive_health_check(engine)

    # Set HTTP status based on health
    status_code = 200 if health_status["status"] == "healthy" else 503

    return Response(
        content=health_status, status_code=status_code, media_type="application/json"
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - checks if the application is ready to serve traffic
    Used by Kubernetes readiness probes
    """
    return {"status": "ready", "timestamp": health_checker.time.time()}


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe - basic check that the application is running
    Used by Kubernetes liveness probes
    """
    return {"status": "alive", "timestamp": health_checker.time.time()}


@router.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Check database connectivity specifically"""
    db_health = await health_checker.check_database(engine)
    status_code = 200 if db_health["status"] == "healthy" else 503

    return Response(
        content=db_health, status_code=status_code, media_type="application/json"
    )


@router.get("/health/ai")
async def ai_services_health_check():
    """Check AI services availability"""
    ai_health = await health_checker.check_ai_services()

    # Check if any service is unhealthy
    all_healthy = all(
        service.get("status") == "healthy" for service in ai_health.values()
    )

    status_code = 200 if all_healthy else 503

    return Response(
        content=ai_health, status_code=status_code, media_type="application/json"
    )


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus format for scraping
    """
    if not settings.enable_metrics:
        return Response(
            content="Metrics collection is disabled",
            status_code=404,
            media_type="text/plain",
        )

    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@router.get("/info")
async def application_info():
    """
    Application information endpoint
    Returns basic app information and configuration
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "debug": settings.debug,
        "features": {
            "metrics_enabled": settings.enable_metrics,
            "sentry_enabled": bool(settings.sentry_dsn),
            "prompt_validation": settings.enable_prompt_validation,
            "docker_enabled": settings.docker_enabled,
        },
        "limits": {
            "free_tier_tokens": settings.free_tier_daily_tokens,
            "pro_tier_tokens": settings.pro_tier_daily_tokens,
            "team_tier_tokens": settings.team_tier_daily_tokens,
            "max_tokens_per_request": settings.ai_max_tokens_per_request,
        },
    }
