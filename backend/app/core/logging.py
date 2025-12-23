"""
Structured logging configuration with correlation IDs
"""

import logging
import logging.config
import sys
import uuid
from contextvars import ContextVar

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings

# Context variable for request correlation ID
correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get or create a correlation ID for request tracing"""
    current_id = correlation_id.get()
    if current_id is None:
        current_id = str(uuid.uuid4())
        correlation_id.set(current_id)
    return current_id


def set_correlation_id(request_id: str) -> None:
    """Set correlation ID for current context"""
    correlation_id.set(request_id)


def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to all log messages"""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def add_timestamp(logger, method_name, event_dict):
    """Add timestamp to log messages"""
    import time

    event_dict["timestamp"] = time.time()
    return event_dict


def setup_logging():
    """Configure structured logging based on environment settings"""

    # Choose renderer based on format setting
    if settings.log_format.lower() == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_correlation_id,
            add_timestamp,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": renderer,
            },
        },
        "handlers": {
            "console": {
                "level": settings.log_level.upper(),
                "class": "logging.StreamHandler",
                "formatter": "structured",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": settings.log_level.upper(),
                "propagate": True,
            },
            # Reduce noise from third-party libraries
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING" if settings.is_production else "INFO",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    if name is None:
        name = __name__
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add structured logging to classes"""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


# Performance monitoring helpers
class PerformanceLogger:
    """Context manager for performance logging"""

    def __init__(self, operation: str, logger: structlog.stdlib.BoundLogger = None):
        self.operation = operation
        self.logger = logger or get_logger()
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.perf_counter()
        self.logger.info(f"Starting {self.operation}", operation=self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        duration = time.perf_counter() - self.start_time

        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation}",
                operation=self.operation,
                duration_seconds=round(duration, 3),
                status="success",
            )
        else:
            self.logger.error(
                f"Failed {self.operation}",
                operation=self.operation,
                duration_seconds=round(duration, 3),
                status="error",
                error_type=exc_type.__name__,
                error_message=str(exc_val),
            )


def log_performance(operation: str):
    """Decorator for performance logging"""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            with PerformanceLogger(f"{func.__name__}:{operation}", logger):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            with PerformanceLogger(f"{func.__name__}:{operation}", logger):
                return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Request logging for FastAPI
async def log_request_middleware(request, call_next):
    """Middleware to log all HTTP requests with timing"""
    import time

    # Generate correlation ID for this request
    request_id = str(uuid.uuid4())
    set_correlation_id(request_id)

    # Add correlation ID to request state
    request.state.correlation_id = request_id

    logger = get_logger("http")
    start_time = time.perf_counter()

    # Log incoming request
    logger.info(
        "HTTP request started",
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        # Log successful response
        logger.info(
            "HTTP request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=round(duration, 3),
            response_size=response.headers.get("content-length"),
        )

        return response

    except Exception as exc:
        duration = time.perf_counter() - start_time

        # Log error response
        logger.error(
            "HTTP request failed",
            method=request.method,
            path=request.url.path,
            duration_seconds=round(duration, 3),
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

        raise
