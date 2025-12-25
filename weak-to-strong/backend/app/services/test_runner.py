"""
Test Runner Service
Manages Docker containers for secure code execution and testing
"""

import asyncio
import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import docker
import docker.errors
from docker.models.containers import Container
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TestResult(BaseModel):
    """Test execution result"""

    test_id: str
    challenge_id: str
    user_id: str
    code: str
    success: bool
    score: int = 0
    max_score: int = 0
    tests: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    metrics: Dict[str, Any] = {}
    execution_time_ms: int = 0
    timestamp: str
    container_logs: Optional[str] = None


class ContainerConfig(BaseModel):
    """Container configuration"""

    image: str = "weak-to-strong/web-sandbox:latest"
    memory_limit: str = "256m"
    cpu_limit: str = "0.5"
    timeout_seconds: int = 30
    network_mode: str = "none"  # No network access for security


class TestRunnerService:
    """
    Manages Docker containers for secure code execution
    """

    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

        self.active_containers: Dict[str, Container] = {}
        self.config = ContainerConfig()

    async def run_tests(
        self,
        challenge_id: str,
        user_id: str,
        code: str,
        test_config: Optional[Dict] = None,
    ) -> TestResult:
        """
        Execute code in a secure Docker container and return test results
        """
        test_id = f"{user_id}_{challenge_id}_{int(time.time())}"
        start_time = time.time()

        logger.info(f"Starting test execution: {test_id}")

        try:
            # Create temporary files for user code
            with tempfile.TemporaryDirectory() as temp_dir:
                code_file = Path(temp_dir) / "index.html"
                code_file.write_text(code)

                # Run container
                result = await self._run_container(
                    test_id=test_id,
                    code_file_path=str(code_file),
                    test_config=test_config,
                )

                execution_time = int((time.time() - start_time) * 1000)

                return TestResult(
                    test_id=test_id,
                    challenge_id=challenge_id,
                    user_id=user_id,
                    code=code,
                    success=result.get("success", False),
                    score=result.get("score", 0),
                    max_score=result.get("maxScore", 0),
                    tests=result.get("tests", []),
                    errors=result.get("errors", []),
                    metrics=result.get("metrics", {}),
                    execution_time_ms=execution_time,
                    timestamp=result.get("timestamp", ""),
                    container_logs=result.get("logs", ""),
                )

        except Exception as e:
            logger.error(f"Test execution failed for {test_id}: {e}")
            execution_time = int((time.time() - start_time) * 1000)

            return TestResult(
                test_id=test_id,
                challenge_id=challenge_id,
                user_id=user_id,
                code=code,
                success=False,
                score=0,
                max_score=0,
                tests=[],
                errors=[{"message": f"Execution error: {str(e)}", "type": "system"}],
                metrics={},
                execution_time_ms=execution_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

    async def _run_container(
        self, test_id: str, code_file_path: str, test_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run code in a Docker container with security restrictions
        """
        container = None

        try:
            # Container configuration
            container_config = {
                "image": self.config.image,
                "command": ["node", "test-runner.js", "/sandbox/user-code/index.html"],
                "volumes": {
                    code_file_path: {
                        "bind": "/sandbox/user-code/index.html",
                        "mode": "ro",  # Read-only
                    }
                },
                "mem_limit": self.config.memory_limit,
                "cpu_period": 100000,
                "cpu_quota": int(float(self.config.cpu_limit) * 100000),
                "network_mode": self.config.network_mode,
                "user": "sandbox:sandbox",  # Non-root user
                "security_opt": ["no-new-privileges:true"],
                "cap_drop": ["ALL"],  # Drop all capabilities
                "read_only": True,  # Read-only filesystem
                "tmpfs": {
                    "/tmp": "noexec,nosuid,size=100m",
                    "/sandbox/test-output": "noexec,nosuid,size=50m",
                },
                "remove": True,  # Auto-remove after completion
                "stdout": True,
                "stderr": True,
                "detach": False,
            }

            logger.info(f"Starting container for test {test_id}")

            # Run container with timeout
            container = self.docker_client.containers.run(**container_config)

            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")

            # Parse JSON output from test runner
            try:
                # Extract JSON from logs (test runner outputs JSON)
                json_start = logs.find("📄 Test Results:")
                if json_start != -1:
                    json_content = logs[json_start + len("📄 Test Results:") :].strip()
                    result = json.loads(json_content)
                else:
                    # Fallback: try to parse entire log as JSON
                    result = json.loads(logs)

                result["logs"] = logs
                return result

            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON output from container {test_id}")
                return {
                    "success": False,
                    "score": 0,
                    "maxScore": 0,
                    "tests": [],
                    "errors": [
                        {"message": "Could not parse test results", "type": "system"}
                    ],
                    "metrics": {},
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "logs": logs,
                }

        except docker.errors.ContainerError as e:
            logger.error(f"Container execution failed for {test_id}: {e}")
            return {
                "success": False,
                "score": 0,
                "maxScore": 0,
                "tests": [],
                "errors": [
                    {
                        "message": f"Container error: {e.stderr.decode() if e.stderr else str(e)}",
                        "type": "container",
                    }
                ],
                "metrics": {},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "logs": e.stderr.decode() if e.stderr else str(e),
            }

        except docker.errors.ImageNotFound:
            logger.error(f"Docker image not found: {self.config.image}")
            return {
                "success": False,
                "score": 0,
                "maxScore": 0,
                "tests": [],
                "errors": [
                    {"message": f"Test environment not available", "type": "system"}
                ],
                "metrics": {},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "logs": "Docker image not found",
            }

        except asyncio.TimeoutError:
            logger.warning(f"Container timeout for {test_id}")
            if container:
                try:
                    container.kill()
                except:
                    pass
            return {
                "success": False,
                "score": 0,
                "maxScore": 0,
                "tests": [],
                "errors": [{"message": "Test execution timeout", "type": "timeout"}],
                "metrics": {},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "logs": "Execution timed out",
            }

        except Exception as e:
            logger.error(f"Unexpected error running container {test_id}: {e}")
            return {
                "success": False,
                "score": 0,
                "maxScore": 0,
                "tests": [],
                "errors": [
                    {"message": f"Unexpected error: {str(e)}", "type": "system"}
                ],
                "metrics": {},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "logs": str(e),
            }

    def cleanup_container(self, container_id: str) -> None:
        """Clean up a specific container"""
        try:
            if container_id in self.active_containers:
                container = self.active_containers[container_id]
                container.kill()
                container.remove()
                del self.active_containers[container_id]
                logger.info(f"Cleaned up container {container_id}")
        except Exception as e:
            logger.error(f"Error cleaning up container {container_id}: {e}")

    def cleanup_all_containers(self) -> None:
        """Clean up all active containers"""
        for container_id in list(self.active_containers.keys()):
            self.cleanup_container(container_id)

    def get_container_stats(self) -> Dict[str, Any]:
        """Get statistics about container usage"""
        try:
            containers = self.docker_client.containers.list(
                filters={"label": "weak-to-strong"}
            )

            return {
                "active_containers": len(self.active_containers),
                "total_containers": len(containers),
                "docker_info": self.docker_client.info(),
            }
        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return {"error": str(e)}


# Lazy initialization to avoid Docker connection issues at startup
_test_runner_service = None


def get_test_runner_service():
    """Get or create test runner service instance"""
    global _test_runner_service
    if _test_runner_service is None:
        _test_runner_service = TestRunnerService()
    return _test_runner_service


# For backward compatibility
test_runner_service = None
