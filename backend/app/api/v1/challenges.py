"""
Challenge API endpoints
Handles challenge submission and test execution
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from app.core.deps import get_current_user
from app.models.user import User
from app.services.test_runner import TestResult, test_runner_service

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


class SubmissionRequest(BaseModel):
    """Challenge submission request"""

    challenge_id: str = Field(..., description="Challenge identifier")
    code: str = Field(..., description="User's code submission")
    language: str = Field(default="html", description="Programming language")
    test_config: dict[str, Any] | None = Field(
        default=None, description="Optional test configuration"
    )


class SubmissionResponse(BaseModel):
    """Challenge submission response"""

    submission_id: str
    challenge_id: str
    status: str = "submitted"  # submitted, running, completed, failed
    message: str = "Submission received and queued for testing"


@router.post("/challenges/{challenge_id}/submit", response_model=SubmissionResponse)
async def submit_challenge(
    challenge_id: str,
    submission: SubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """
    Submit code for a challenge and run tests
    """
    try:
        logger.info(
            f"Challenge submission received: {challenge_id} from user {current_user.id}"
        )

        # Validate challenge exists (you might want to check against a database)
        if not challenge_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge ID is required",
            )

        # Validate code submission
        if not submission.code or len(submission.code.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code submission cannot be empty",
            )

        # Check code length (prevent abuse)
        if len(submission.code) > 100000:  # 100KB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Code submission too large (max 100KB)",
            )

        # Run tests asynchronously
        test_result = await test_runner_service.run_tests(
            challenge_id=challenge_id,
            user_id=current_user.id,
            code=submission.code,
            test_config=submission.test_config,
        )

        # For now, return immediate results
        # In production, you might want to store these in a database
        return SubmissionResponse(
            submission_id=test_result.test_id,
            challenge_id=challenge_id,
            status="completed" if test_result.success else "failed",
            message=f"Tests completed: {test_result.score}/{test_result.max_score} passed",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting challenge {challenge_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your submission",
        )


@router.get("/challenges/{challenge_id}/results/{submission_id}")
async def get_submission_results(
    challenge_id: str,
    submission_id: str,
    current_user: User = Depends(get_current_user),
) -> TestResult:
    """
    Get test results for a specific submission
    """
    try:
        # In a real implementation, you would fetch this from a database
        # For now, we'll return a mock response or error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found. Use /submit endpoint for immediate results.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching results for {submission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching results",
        )


@router.post("/challenges/{challenge_id}/test", response_model=TestResult)
async def test_challenge_code(
    challenge_id: str,
    submission: SubmissionRequest,
    current_user: User = Depends(get_current_user),
) -> TestResult:
    """
    Test code for a challenge and return immediate results
    """
    try:
        logger.info(
            f"Challenge test requested: {challenge_id} from user {current_user.id}"
        )

        # Validate inputs
        if not challenge_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge ID is required",
            )

        if not submission.code or len(submission.code.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code submission cannot be empty",
            )

        # Check code length
        if len(submission.code) > 100000:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Code submission too large (max 100KB)",
            )

        # Run tests and return results immediately
        test_result = await test_runner_service.run_tests(
            challenge_id=challenge_id,
            user_id=current_user.id,
            code=submission.code,
            test_config=submission.test_config,
        )

        logger.info(
            f"Test completed for {challenge_id}: {test_result.score}/{test_result.max_score}"
        )
        return test_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing challenge {challenge_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while testing your code",
        )


@router.get("/test-runner/status")
async def get_test_runner_status(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get test runner service status and statistics
    """
    try:
        stats = test_runner_service.get_container_stats()
        return {
            "status": "healthy",
            "service": "test-runner",
            "stats": stats,
            "timestamp": "2024-12-21T12:00:00Z",
        }
    except Exception as e:
        logger.error(f"Error getting test runner status: {e}")
        return {
            "status": "error",
            "service": "test-runner",
            "error": str(e),
            "timestamp": "2024-12-21T12:00:00Z",
        }


@router.post("/test-runner/cleanup")
async def cleanup_test_containers(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Clean up test containers (admin only)
    """
    try:
        # In production, add admin role check
        test_runner_service.cleanup_all_containers()
        return {"message": "Container cleanup completed"}
    except Exception as e:
        logger.error(f"Error cleaning up containers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cleaning up containers",
        )
