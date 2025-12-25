"""
WeaktoStrong Execution Service
Unified service for executing challenges across different tracks (Web, Data, Cloud)
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.challenge import Challenge, Track
from app.models.user import User
from app.services.test_runner import (
    TestRunnerService,
    TestResult,
    get_test_runner_service,
)
from app.services.runners.data_runner import (
    DataRunner,
    DataChallenge,
    DataValidation,
    DataExecutionResult,
    get_data_runner,
)

logger = logging.getLogger(__name__)


class ExecutionRequest(BaseModel):
    """Universal execution request for any challenge type"""

    challenge_id: str = Field(..., description="Challenge identifier")
    user_id: str = Field(..., description="User identifier")
    code: str = Field(..., description="User's code submission")
    language: Optional[str] = Field(default=None, description="Programming language")
    test_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional test configuration"
    )


class ExecutionResult(BaseModel):
    """Universal execution result for any challenge type"""

    challenge_id: str
    user_id: str
    track_type: str  # "web", "data", "cloud"
    success: bool
    score: int
    max_score: int = 100
    execution_time_ms: int
    output: str
    errors: list[str] = []
    test_details: Dict[str, Any] = {}
    validation_results: list[Dict[str, Any]] = []
    insights_found: Optional[bool] = None  # Data analysis specific


class ExecutionService:
    """
    Unified execution service for all WeaktoStrong challenge tracks

    Handles:
    - Web Development challenges (HTML/CSS/JS) via TestRunnerService
    - Data Analysis challenges (Python/Pandas/ML) via DataRunner
    - Cloud Infrastructure challenges (Terraform/AWS) via CloudRunner (future)
    """

    def __init__(self):
        # Initialize track-specific runners
        self.web_runner: Optional[TestRunnerService] = None
        self.data_runner: Optional[DataRunner] = None
        # self.cloud_runner: Optional[CloudRunner] = None  # Future implementation

        logger.info("ExecutionService initialized")

    async def execute_challenge(
        self, request: ExecutionRequest, db: AsyncSession
    ) -> ExecutionResult:
        """
        Execute a challenge submission using the appropriate runner for the track type
        """
        logger.info(
            f"Executing challenge {request.challenge_id} for user {request.user_id}"
        )

        try:
            # Fetch challenge from database to determine track type
            challenge = await self._get_challenge_with_track(request.challenge_id, db)
            if not challenge:
                raise ValueError(f"Challenge {request.challenge_id} not found")

            track_name = challenge.track.name
            logger.info(f"Challenge track: {track_name}")

            # Route to appropriate execution engine based on track
            if track_name == "Data Analysis":
                result = await self._execute_data_challenge(request, challenge)
            elif track_name == "Web Development":
                result = await self._execute_web_challenge(request, challenge)
            elif track_name == "Cloud Infrastructure":
                result = await self._execute_cloud_challenge(request, challenge)
            else:
                raise ValueError(f"Unsupported track type: {track_name}")

            logger.info(f"Execution completed: {result.score}/{result.max_score}")
            return result

        except Exception as e:
            logger.error(f"Challenge execution failed: {e}")
            return ExecutionResult(
                challenge_id=request.challenge_id,
                user_id=request.user_id,
                track_type="unknown",
                success=False,
                score=0,
                execution_time_ms=0,
                output="",
                errors=[f"Execution failed: {str(e)}"],
            )

    async def _get_challenge_with_track(
        self, challenge_id: str, db: AsyncSession
    ) -> Optional[Challenge]:
        """Fetch challenge with track information"""
        try:
            # Support both UUID and string challenge IDs
            if challenge_id.count("-") == 4:  # Likely a UUID
                challenge_uuid = UUID(challenge_id)
                stmt = (
                    select(Challenge).join(Track).where(Challenge.id == challenge_uuid)
                )
            else:
                # Try by title or slug (for legacy support)
                stmt = (
                    select(Challenge)
                    .join(Track)
                    .where(Challenge.title.ilike(f"%{challenge_id}%"))
                )

            result = await db.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching challenge {challenge_id}: {e}")
            return None

    async def _execute_data_challenge(
        self, request: ExecutionRequest, challenge: Challenge
    ) -> ExecutionResult:
        """Execute a Data Analysis challenge using DataRunner"""

        # Initialize data runner if needed
        if self.data_runner is None:
            self.data_runner = get_data_runner()

        # Convert challenge validation_rules to DataChallenge format
        validation_rules = challenge.validation_rules or {}

        # Create DataValidation objects from validation_rules JSON
        validations = []
        for validation_data in validation_rules.get("validations", []):
            validations.append(DataValidation(**validation_data))

        # Create DataChallenge object
        data_challenge = DataChallenge(
            challenge_id=request.challenge_id,
            dataset_name=validation_rules.get("dataset"),
            validations=validations,
            timeout_seconds=(
                challenge.estimated_time_minutes * 60
                if challenge.estimated_time_minutes
                else 300
            ),
        )

        # Execute the challenge
        data_result = await self.data_runner.execute_data_challenge(
            user_id=request.user_id, code=request.code, challenge=data_challenge
        )

        # Convert DataExecutionResult to universal ExecutionResult
        return ExecutionResult(
            challenge_id=request.challenge_id,
            user_id=request.user_id,
            track_type="data",
            success=data_result.success,
            score=data_result.score,
            max_score=data_result.max_score,
            execution_time_ms=data_result.execution_time_ms,
            output=data_result.output,
            errors=data_result.errors,
            test_details={
                "variables_created": data_result.variables_created,
                "validations": data_result.validations,
            },
            validation_results=data_result.validations,
            insights_found=data_result.insights_found,
        )

    async def _execute_web_challenge(
        self, request: ExecutionRequest, challenge: Challenge
    ) -> ExecutionResult:
        """Execute a Web Development challenge using TestRunnerService"""

        # Initialize web runner if needed
        if self.web_runner is None:
            self.web_runner = get_test_runner_service()

        # Execute using existing test runner
        web_result = await self.web_runner.run_tests(
            challenge_id=request.challenge_id,
            user_id=request.user_id,
            code=request.code,
            test_config=request.test_config,
        )

        # Convert TestResult to universal ExecutionResult
        return ExecutionResult(
            challenge_id=request.challenge_id,
            user_id=request.user_id,
            track_type="web",
            success=web_result.success,
            score=web_result.score,
            max_score=web_result.max_score,
            execution_time_ms=web_result.execution_time_ms,
            output=web_result.container_logs or "",
            errors=[error.get("message", "") for error in web_result.errors],
            test_details={"tests": web_result.tests, "metrics": web_result.metrics},
            validation_results=web_result.tests,
        )

    async def _execute_cloud_challenge(
        self, request: ExecutionRequest, challenge: Challenge
    ) -> ExecutionResult:
        """Execute a Cloud Infrastructure challenge (placeholder for future implementation)"""

        logger.warning("Cloud challenge execution not yet implemented")

        return ExecutionResult(
            challenge_id=request.challenge_id,
            user_id=request.user_id,
            track_type="cloud",
            success=False,
            score=0,
            execution_time_ms=0,
            output="",
            errors=["Cloud challenge execution not yet implemented"],
        )

    async def get_execution_status(self) -> Dict[str, Any]:
        """Get status of all execution engines"""

        status = {
            "service": "execution_service",
            "timestamp": "2024-12-24",
            "runners": {},
        }

        # Web runner status
        try:
            if self.web_runner is None:
                self.web_runner = get_test_runner_service()
            web_stats = self.web_runner.get_container_stats()
            status["runners"]["web"] = {"status": "healthy", "stats": web_stats}
        except Exception as e:
            status["runners"]["web"] = {"status": "error", "error": str(e)}

        # Data runner status
        try:
            if self.data_runner is None:
                self.data_runner = get_data_runner()
            status["runners"]["data"] = {
                "status": "healthy",
                "image": "weak-to-strong/data-sandbox:latest",
            }
        except Exception as e:
            status["runners"]["data"] = {"status": "error", "error": str(e)}

        # Cloud runner status (placeholder)
        status["runners"]["cloud"] = {"status": "not_implemented"}

        return status


# Global instance for dependency injection
_execution_service_instance = None


def get_execution_service() -> ExecutionService:
    """Get or create ExecutionService instance"""
    global _execution_service_instance
    if _execution_service_instance is None:
        _execution_service_instance = ExecutionService()
    return _execution_service_instance
