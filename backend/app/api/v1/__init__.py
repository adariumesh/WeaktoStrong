"""
API v1 routes
"""

from fastapi import APIRouter

from .ai import router as ai_router
from .auth import router as auth_router
from .certificates import router as certificates_router
from .challenges import router as challenges_router
from .payments import router as payments_router
from .progress import router as progress_router

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include challenge routes
api_router.include_router(challenges_router, prefix="", tags=["Challenges"])

# Include AI routes
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])

# Include progress routes
api_router.include_router(progress_router, prefix="/progress", tags=["Progress"])

# Include certificate routes
api_router.include_router(
    certificates_router, prefix="/certificates", tags=["Certificates"]
)

# Include payment routes
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
