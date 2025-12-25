"""
WeaktoStrong Data Analysis Runner
Output-based validation for "Vibe Coder" methodology
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
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DataValidation(BaseModel):
    """Single validation check for data analysis"""
    name: str
    type: str  # "variable_exists", "dataframe_shape", "value_check", "custom_check"
    variable: Optional[str] = None
    expected: Optional[Any] = None
    tolerance: Optional[float] = 0.001
    check_code: Optional[str] = None


class DataChallenge(BaseModel):
    """Data challenge configuration"""
    challenge_id: str
    initial_code: str = ""
    dataset_name: Optional[str] = None
    validations: List[DataValidation] = []
    timeout_seconds: int = 30


class DataExecutionResult(BaseModel):
    """Result of data analysis execution"""
    challenge_id: str
    user_id: str
    success: bool
    score: int
    max_score: int = 100
    execution_time_ms: int
    output: str
    errors: List[str] = []
    validations: List[Dict[str, Any]] = []
    variables_created: List[str] = []
    insights_found: bool = False


class DataRunner:
    """
    WeaktoStrong Data Analysis Runner
    
    Philosophy: Judge by OUTPUT, not by CODE
    - If final_df has the right shape → Pass
    - If result_value equals expected → Pass
    - If insights are extracted → Pass
    
    This enables "Vibe Coders" who use AI or messy code
    but still get the right analytical insights.
    """
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            self.image_name = "weak-to-strong/data-sandbox:latest"
            logger.info("DataRunner initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DataRunner: {e}")
            raise
    
    async def execute_data_challenge(
        self,
        user_id: str,
        code: str,
        challenge: DataChallenge
    ) -> DataExecutionResult:
        """
        Execute data analysis code in secure sandbox
        Focus on OUTPUT validation, not code style
        """
        start_time = time.time()
        
        logger.info(f"Executing data challenge {challenge.challenge_id} for user {user_id}")
        
        try:
            # Prepare the execution environment
            execution_config = self._prepare_execution_config(code, challenge)
            
            # Run in Docker sandbox
            container_result = await self._run_in_sandbox(execution_config)
            
            # Parse and validate results
            execution_time = int((time.time() - start_time) * 1000)
            
            result = self._process_sandbox_result(
                container_result, challenge, user_id, execution_time
            )
            
            # Apply WeaktoStrong scoring logic
            result = self._apply_vibe_coder_scoring(result, challenge)
            
            logger.info(f"Data challenge completed: {result.score}/{result.max_score}")
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Data challenge execution failed: {e}")
            
            return DataExecutionResult(
                challenge_id=challenge.challenge_id,
                user_id=user_id,
                success=False,
                score=0,
                execution_time_ms=execution_time,
                output="",
                errors=[f"Execution failed: {str(e)}"]
            )
    
    def _prepare_execution_config(self, user_code: str, challenge: DataChallenge) -> Dict:
        """
        Prepare execution configuration for sandbox
        Inject dataset loading and validation setup
        """
        
        # Build the complete execution script
        execution_script = []
        
        # Import required libraries
        execution_script.extend([
            "import pandas as pd",
            "import numpy as np", 
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "from sklearn.model_selection import train_test_split",
            "from sklearn.linear_model import LinearRegression",
            "from sklearn.metrics import mean_squared_error, r2_score",
            "import warnings",
            "warnings.filterwarnings('ignore')",
            ""
        ])
        
        # Load dataset if specified
        if challenge.dataset_name:
            execution_script.extend([
                f"# Load dataset: {challenge.dataset_name}",
                f"df = pd.read_csv('/datasets/{challenge.dataset_name}')",
                "print(f'Dataset loaded: {{df.shape}} rows, {{df.columns.tolist()}}')",
                ""
            ])
        
        # Add initial code if provided
        if challenge.initial_code:
            execution_script.extend([
                "# Initial setup code",
                challenge.initial_code,
                ""
            ])
        
        # Add user's analysis code
        execution_script.extend([
            "# User's data analysis code",
            user_code,
            ""
        ])
        
        # Add variable extraction for validation
        execution_script.extend([
            "# Extract variables for validation",
            "_extracted_vars = {}",
            "for var_name in list(globals().keys()):",
            "    if not var_name.startswith('_') and var_name not in ['pd', 'np', 'plt', 'sns']:",
            "        try:",
            "            _extracted_vars[var_name] = globals()[var_name]", 
            "        except:",
            "            pass",
            "",
            "print('VARIABLES_EXTRACTED:', list(_extracted_vars.keys()))"
        ])
        
        return {
            "type": "python",
            "code": "\n".join(execution_script),
            "dataset": challenge.dataset_name,
            "validations": [v.dict() for v in challenge.validations],
            "timeout": challenge.timeout_seconds
        }
    
    async def _run_in_sandbox(self, config: Dict) -> Dict:
        """
        Execute code in secure Docker sandbox
        Return parsed JSON results
        """
        
        try:
            # Create container configuration
            container_config = {
                "image": self.image_name,
                "command": ["python", "data-test-runner.py", json.dumps(config)],
                "mem_limit": "512m",
                "cpu_period": 100000,
                "cpu_quota": 50000,  # 0.5 CPU
                "network_mode": "none",
                "user": "sandbox",
                "security_opt": ["no-new-privileges:true"],
                "cap_drop": ["ALL"],
                "read_only": True,
                "tmpfs": {
                    "/tmp": "noexec,nosuid,size=100m",
                    "/workspace/temp": "noexec,nosuid,size=50m"
                },
                "remove": True,
                "stdout": True,
                "stderr": True
            }
            
            logger.info("Starting data analysis container...")
            
            # Run container
            container = self.docker_client.containers.run(**container_config)
            
            # Get output
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # Parse JSON result from test runner
            try:
                # Look for JSON output in logs
                json_start = logs.rfind('{')
                if json_start != -1:
                    json_content = logs[json_start:]
                    result = json.loads(json_content)
                    result["full_logs"] = logs
                    return result
                else:
                    return {
                        "error": "No JSON output found",
                        "passed": False,
                        "score": 0,
                        "full_logs": logs
                    }
                    
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse JSON output: {e}",
                    "passed": False,
                    "score": 0,
                    "full_logs": logs
                }
                
        except docker.errors.ContainerError as e:
            return {
                "error": f"Container execution failed: {e}",
                "passed": False,
                "score": 0,
                "full_logs": e.stderr.decode() if e.stderr else str(e)
            }
        except docker.errors.ImageNotFound:
            return {
                "error": f"Docker image not found: {self.image_name}",
                "passed": False,
                "score": 0,
                "full_logs": "Image not available"
            }
        except Exception as e:
            return {
                "error": f"Sandbox execution error: {e}",
                "passed": False,
                "score": 0,
                "full_logs": str(e)
            }
    
    def _process_sandbox_result(
        self, 
        container_result: Dict, 
        challenge: DataChallenge, 
        user_id: str, 
        execution_time: int
    ) -> DataExecutionResult:
        """
        Process raw sandbox results into structured execution result
        """
        
        # Extract variables created
        variables_created = []
        logs = container_result.get("full_logs", "")
        
        # Look for variable extraction output
        for line in logs.split('\n'):
            if line.startswith('VARIABLES_EXTRACTED:'):
                try:
                    var_list_str = line.replace('VARIABLES_EXTRACTED:', '').strip()
                    variables_created = eval(var_list_str)
                except:
                    pass
        
        # Check for common data science insights
        insights_found = self._detect_insights(logs, variables_created)
        
        return DataExecutionResult(
            challenge_id=challenge.challenge_id,
            user_id=user_id,
            success=container_result.get("passed", False),
            score=container_result.get("score", 0),
            execution_time_ms=execution_time,
            output=container_result.get("output", ""),
            errors=[container_result.get("error")] if container_result.get("error") else [],
            validations=container_result.get("validations", []),
            variables_created=variables_created,
            insights_found=insights_found
        )
    
    def _detect_insights(self, logs: str, variables: List[str]) -> bool:
        """
        Detect if meaningful data science insights were extracted
        WeaktoStrong philosophy: reward insight discovery
        """
        
        insight_indicators = [
            # Common result variables
            "correlation", "mean", "median", "std", "result",
            "summary", "insights", "conclusion", "findings",
            
            # DataFrame operations 
            "cleaned", "processed", "transformed", "merged",
            "grouped", "aggregated", "filtered",
            
            # ML indicators
            "model", "prediction", "accuracy", "score", "mse",
            "r2", "coefficients", "feature_importance"
        ]
        
        # Check variable names for insight indicators
        for var in variables:
            var_lower = var.lower()
            for indicator in insight_indicators:
                if indicator in var_lower:
                    return True
        
        # Check logs for analysis outputs
        logs_lower = logs.lower()
        analysis_patterns = [
            "correlation coefficient", "p-value", "r-squared",
            "mean:", "median:", "standard deviation",
            "null values", "missing data", "outliers",
            "accuracy:", "precision:", "recall:",
            "feature importance", "model score"
        ]
        
        for pattern in analysis_patterns:
            if pattern in logs_lower:
                return True
                
        return False
    
    def _apply_vibe_coder_scoring(
        self, 
        result: DataExecutionResult, 
        challenge: DataChallenge
    ) -> DataExecutionResult:
        """
        Apply WeaktoStrong "Vibe Coder" scoring methodology
        
        Philosophy: 
        - Reward correct outputs over clean code
        - Bonus points for insights discovery
        - Partial credit for attempting right approach
        """
        
        # Base score from validations
        base_score = result.score
        
        # Bonus for insights discovery
        if result.insights_found:
            insight_bonus = min(20, 100 - base_score)  # Up to 20 point bonus
            result.score += insight_bonus
            logger.info(f"Insights bonus applied: +{insight_bonus} points")
        
        # Bonus for creating expected variables
        expected_vars = ["result", "final_df", "summary", "model", "prediction"]
        vars_bonus = 0
        for expected_var in expected_vars:
            if any(expected_var in var.lower() for var in result.variables_created):
                vars_bonus += 5
        
        result.score = min(100, result.score + vars_bonus)
        
        # Ensure success flag matches score
        result.success = result.score >= 70  # Pass threshold for WeaktoStrong
        
        return result


# Global instance for dependency injection
_data_runner_instance = None

def get_data_runner() -> DataRunner:
    """Get or create DataRunner instance"""
    global _data_runner_instance
    if _data_runner_instance is None:
        _data_runner_instance = DataRunner()
    return _data_runner_instance