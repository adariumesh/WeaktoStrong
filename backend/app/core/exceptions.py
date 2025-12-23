"""
Custom exception classes and global exception handlers
"""

from typing import Any

import structlog
from fastapi import HTTPException, Request
from fastapi.exceptions import ValidationException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.monitoring import track_error

logger = structlog.get_logger(__name__)


class BaseCustomException(Exception):
    """Base exception class for custom application exceptions"""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: dict[str, Any] = None,
        http_status: int = 500,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.http_status = http_status
        super().__init__(self.message)


class AuthenticationError(BaseCustomException):
    """Authentication-related errors"""

    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, http_status=401, **kwargs)


class AuthorizationError(BaseCustomException):
    """Authorization-related errors"""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, http_status=403, **kwargs)


class ValidationError(BaseCustomException):
    """Input validation errors"""

    def __init__(
        self,
        message: str = "Invalid input",
        field_errors: list[dict[str, str]] = None,
        **kwargs,
    ):
        self.field_errors = field_errors or []
        details = {"field_errors": self.field_errors}
        super().__init__(message, http_status=400, details=details, **kwargs)


class NotFoundError(BaseCustomException):
    """Resource not found errors"""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, http_status=404, **kwargs)


class ConflictError(BaseCustomException):
    """Resource conflict errors"""

    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(message, http_status=409, **kwargs)


class RateLimitError(BaseCustomException):
    """Rate limiting errors"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        **kwargs,
    ):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, http_status=429, details=details, **kwargs)


class ServiceUnavailableError(BaseCustomException):
    """External service unavailable errors"""

    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(message, http_status=503, **kwargs)


class BusinessLogicError(BaseCustomException):
    """Business logic validation errors"""

    def __init__(self, message: str = "Business rule violation", **kwargs):
        super().__init__(message, http_status=422, **kwargs)


class AIServiceError(BaseCustomException):
    """AI service specific errors"""

    def __init__(
        self,
        message: str = "AI service error",
        service_name: str = None,
        model_name: str = None,
        **kwargs,
    ):
        details = {"service_name": service_name, "model_name": model_name}
        super().__init__(message, http_status=503, details=details, **kwargs)


class TokenLimitError(RateLimitError):
    """Token usage limit exceeded"""

    def __init__(
        self,
        message: str = "Daily token limit exceeded",
        current_usage: int = None,
        limit: int = None,
        **kwargs,
    ):
        details = {"current_usage": current_usage, "limit": limit}
        super().__init__(message, details=details, **kwargs)


class PromptValidationError(ValidationError):
    """Anti-blind-prompting validation errors"""

    def __init__(
        self,
        message: str = "Prompt validation failed",
        validation_details: dict[str, Any] = None,
        **kwargs,
    ):
        details = {"validation_details": validation_details or {}}
        super().__init__(message, details=details, **kwargs)


def create_error_response(
    error: BaseCustomException, request: Request = None, include_details: bool = None
) -> JSONResponse:
    """Create standardized error response"""

    # Determine if we should include detailed error information
    if include_details is None:
        include_details = settings.debug or settings.is_development

    response_data = {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "type": error.__class__.__name__,
        }
    }

    # Add details in development or if explicitly requested
    if include_details and error.details:
        response_data["error"]["details"] = error.details

    # Add request context in development
    if include_details and request:
        response_data["error"]["request"] = {
            "method": request.method,
            "path": request.url.path,
            "correlation_id": getattr(request.state, "correlation_id", None),
        }

    return JSONResponse(status_code=error.http_status, content=response_data)


# Global exception handlers
async def custom_exception_handler(
    request: Request, exc: BaseCustomException
) -> JSONResponse:
    """Handler for custom application exceptions"""

    # Log the error
    logger.error(
        "Application exception occurred",
        error_code=exc.error_code,
        error_message=exc.message,
        error_type=exc.__class__.__name__,
        http_status=exc.http_status,
        request_method=request.method,
        request_path=request.url.path,
        details=exc.details,
    )

    # Track error metrics
    track_error(error_type=exc.__class__.__name__, endpoint=request.url.path)

    return create_error_response(exc, request)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI HTTP exceptions"""

    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        request_method=request.method,
        request_path=request.url.path,
    )

    track_error(error_type="HTTPException", endpoint=request.url.path)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "type": "HTTPException",
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Handler for Pydantic validation errors"""

    # Extract field errors
    field_errors = []
    for error in exc.errors():
        field_errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "Validation exception occurred",
        field_errors=field_errors,
        request_method=request.method,
        request_path=request.url.path,
    )

    track_error(error_type="ValidationException", endpoint=request.url.path)

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "type": "ValidationException",
                "details": {"field_errors": field_errors},
            }
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handler for SQLAlchemy database errors"""

    logger.error(
        "Database exception occurred",
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        request_method=request.method,
        request_path=request.url.path,
    )

    track_error(error_type=exc.__class__.__name__, endpoint=request.url.path)

    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "INTEGRITY_ERROR",
                    "message": "Data integrity violation",
                    "type": "IntegrityError",
                }
            },
        )

    # Generic database error
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed",
                "type": "SQLAlchemyError",
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected exceptions"""

    logger.error(
        "Unexpected exception occurred",
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        request_method=request.method,
        request_path=request.url.path,
        exc_info=True,  # Include stack trace
    )

    track_error(error_type=exc.__class__.__name__, endpoint=request.url.path)

    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal error occurred",
                    "type": "InternalServerError",
                }
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                    "type": exc.__class__.__name__,
                }
            },
        )


# Exception handler registry
EXCEPTION_HANDLERS = {
    BaseCustomException: custom_exception_handler,
    HTTPException: http_exception_handler,
    StarletteHTTPException: http_exception_handler,
    ValidationException: validation_exception_handler,
    SQLAlchemyError: sqlalchemy_exception_handler,
    Exception: generic_exception_handler,
}


def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)
