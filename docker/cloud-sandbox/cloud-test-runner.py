#!/usr/bin/env python3
"""
Cloud Infrastructure Test Runner for AWS/LocalStack challenges
Handles execution and validation of cloud infrastructure code
"""

import json
import sys
import os
import tempfile
import traceback
import subprocess
import boto3
import time
import yaml
from typing import Dict, List, Any
from pathlib import Path
import requests
from botocore.exceptions import ClientError


class CloudTestRunner:
    """Test runner for cloud infrastructure challenges"""
    
    def __init__(self):
        self.workspace = Path("/workspace")
        self.localstack_endpoint = "http://localstack:4566"
        self.aws_region = "us-east-1"
        self.results = []
        
        # Configure AWS clients for LocalStack
        self.aws_config = {
            'endpoint_url': self.localstack_endpoint,
            'aws_access_key_id': 'test',
            'aws_secret_access_key': 'test',
            'region_name': self.aws_region
        }
    
    def run_terraform_deployment(self, terraform_code: str, test_config: Dict) -> Dict:
        """Run Terraform deployment against LocalStack and validate"""
        
        result = {
            "type": "terraform",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "resources_created": [],
            "validations": []
        }
        
        try:
            # Create temporary terraform directory
            with tempfile.TemporaryDirectory() as temp_dir:
                tf_dir = Path(temp_dir)
                
                # Write terraform code
                tf_file = tf_dir / "main.tf"
                tf_file.write_text(terraform_code)
                
                # Write terraform providers configuration
                provider_config = """
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style          = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3         = "http://localstack:4566"
    lambda     = "http://localstack:4566"
    apigateway = "http://localstack:4566"
    dynamodb   = "http://localstack:4566"
    iam        = "http://localstack:4566"
    cloudwatch = "http://localstack:4566"
  }
}
"""
                
                providers_file = tf_dir / "providers.tf"
                providers_file.write_text(provider_config)
                
                # Initialize terraform
                init_result = subprocess.run(
                    ["terraform", "init"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if init_result.returncode != 0:
                    result["error"] = f"Terraform init failed: {init_result.stderr}"
                    return result
                
                # Plan terraform
                plan_result = subprocess.run(
                    ["terraform", "plan", "-out=tfplan"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if plan_result.returncode != 0:
                    result["error"] = f"Terraform plan failed: {plan_result.stderr}"
                    return result
                
                result["output"] += f"Plan output:\n{plan_result.stdout}\n"
                
                # Apply terraform
                apply_result = subprocess.run(
                    ["terraform", "apply", "-auto-approve", "tfplan"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if apply_result.returncode != 0:
                    result["error"] = f"Terraform apply failed: {apply_result.stderr}"
                    return result
                
                result["output"] += f"Apply output:\n{apply_result.stdout}\n"
                
                # Get terraform state
                state_result = subprocess.run(
                    ["terraform", "show", "-json"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if state_result.returncode == 0:
                    try:
                        state = json.loads(state_result.stdout)
                        resources = state.get("values", {}).get("root_module", {}).get("resources", [])
                        result["resources_created"] = [r.get("address") for r in resources]
                    except json.JSONDecodeError:
                        pass
                
                # Run validations
                validations = test_config.get('validations', [])
                passed_validations = 0
                
                for validation in validations:
                    validation_result = self._run_terraform_validation(validation, tf_dir)
                    result["validations"].append(validation_result)
                    if validation_result["passed"]:
                        passed_validations += 1
                
                # Cleanup: Destroy resources
                destroy_result = subprocess.run(
                    ["terraform", "destroy", "-auto-approve"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if destroy_result.returncode != 0:
                    result["output"] += f"Warning: Terraform destroy failed: {destroy_result.stderr}\n"
                
                # Calculate score
                if validations:
                    result["score"] = int((passed_validations / len(validations)) * 100)
                    result["passed"] = passed_validations == len(validations)
                else:
                    result["passed"] = len(result["resources_created"]) > 0
                    result["score"] = 100 if result["passed"] else 0
                
        except Exception as e:
            result["error"] = f"Terraform error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def run_aws_cli_commands(self, commands: List[str], test_config: Dict) -> Dict:
        """Run AWS CLI commands against LocalStack"""
        
        result = {
            "type": "aws_cli",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "command_results": [],
            "validations": []
        }
        
        try:
            # Set environment for LocalStack
            env = os.environ.copy()
            env.update({
                'AWS_ACCESS_KEY_ID': 'test',
                'AWS_SECRET_ACCESS_KEY': 'test',
                'AWS_DEFAULT_REGION': 'us-east-1',
                'AWS_ENDPOINT_URL': self.localstack_endpoint
            })
            
            # Execute each command
            for i, command in enumerate(commands):
                cmd_parts = command.split()
                if cmd_parts[0] == 'aws':
                    cmd_parts.extend(['--endpoint-url', self.localstack_endpoint])
                
                cmd_result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env=env
                )
                
                command_result = {
                    "command": command,
                    "returncode": cmd_result.returncode,
                    "stdout": cmd_result.stdout,
                    "stderr": cmd_result.stderr,
                    "passed": cmd_result.returncode == 0
                }
                
                result["command_results"].append(command_result)
                result["output"] += f"Command {i+1}: {command}\n"
                result["output"] += f"Output: {cmd_result.stdout}\n"
                if cmd_result.stderr:
                    result["output"] += f"Error: {cmd_result.stderr}\n"
                result["output"] += "---\n"
            
            # Run validations
            validations = test_config.get('validations', [])
            passed_validations = 0
            
            for validation in validations:
                validation_result = self._run_aws_validation(validation)
                result["validations"].append(validation_result)
                if validation_result["passed"]:
                    passed_validations += 1
            
            # Calculate score
            successful_commands = sum(1 for cr in result["command_results"] if cr["passed"])
            command_score = int((successful_commands / len(commands)) * 50) if commands else 0
            
            if validations:
                validation_score = int((passed_validations / len(validations)) * 50)
                result["score"] = command_score + validation_score
                result["passed"] = successful_commands == len(commands) and passed_validations == len(validations)
            else:
                result["score"] = command_score * 2
                result["passed"] = successful_commands == len(commands)
                
        except Exception as e:
            result["error"] = f"AWS CLI error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def run_docker_deployment(self, dockerfile_content: str, test_config: Dict) -> Dict:
        """Build and deploy Docker container"""
        
        result = {
            "type": "docker",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "image_id": "",
            "container_id": "",
            "validations": []
        }
        
        try:
            # Create temporary build context
            with tempfile.TemporaryDirectory() as temp_dir:
                build_dir = Path(temp_dir)
                
                # Write Dockerfile
                dockerfile = build_dir / "Dockerfile"
                dockerfile.write_text(dockerfile_content)
                
                # Copy any additional files if specified
                if 'files' in test_config:
                    for file_config in test_config['files']:
                        file_path = build_dir / file_config['path']
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(file_config['content'])
                
                # Build Docker image
                image_tag = f"test-image-{int(time.time())}"
                build_result = subprocess.run(
                    ["docker", "build", "-t", image_tag, "."],
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if build_result.returncode != 0:
                    result["error"] = f"Docker build failed: {build_result.stderr}"
                    return result
                
                result["output"] += f"Build output:\n{build_result.stdout}\n"
                
                # Get image ID
                inspect_result = subprocess.run(
                    ["docker", "inspect", "--format={{.Id}}", image_tag],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if inspect_result.returncode == 0:
                    result["image_id"] = inspect_result.stdout.strip()
                
                # Run container if specified
                if test_config.get('run_container', True):
                    run_cmd = ["docker", "run", "-d"]
                    
                    # Add port mappings if specified
                    if 'ports' in test_config:
                        for port_mapping in test_config['ports']:
                            run_cmd.extend(["-p", port_mapping])
                    
                    # Add environment variables if specified
                    if 'env' in test_config:
                        for env_var in test_config['env']:
                            run_cmd.extend(["-e", env_var])
                    
                    run_cmd.append(image_tag)
                    
                    # Add command if specified
                    if 'command' in test_config:
                        run_cmd.extend(test_config['command'])
                    
                    run_result = subprocess.run(
                        run_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if run_result.returncode == 0:
                        result["container_id"] = run_result.stdout.strip()
                        result["output"] += f"Container started: {result['container_id']}\n"
                        
                        # Wait a bit for container to start
                        time.sleep(2)
                    else:
                        result["error"] = f"Container run failed: {run_result.stderr}"
                        return result
                
                # Run validations
                validations = test_config.get('validations', [])
                passed_validations = 0
                
                for validation in validations:
                    validation_result = self._run_docker_validation(validation, image_tag, result["container_id"])
                    result["validations"].append(validation_result)
                    if validation_result["passed"]:
                        passed_validations += 1
                
                # Cleanup container
                if result["container_id"]:
                    subprocess.run(["docker", "stop", result["container_id"]], 
                                 capture_output=True, timeout=30)
                    subprocess.run(["docker", "rm", result["container_id"]], 
                                 capture_output=True, timeout=30)
                
                # Cleanup image
                subprocess.run(["docker", "rmi", image_tag], 
                             capture_output=True, timeout=30)
                
                # Calculate score
                if validations:
                    result["score"] = int((passed_validations / len(validations)) * 100)
                    result["passed"] = passed_validations == len(validations)
                else:
                    result["passed"] = bool(result["image_id"])
                    result["score"] = 100 if result["passed"] else 0
                
        except Exception as e:
            result["error"] = f"Docker error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def _run_terraform_validation(self, validation: Dict, tf_dir: Path) -> Dict:
        """Run validation check on Terraform deployment"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            
            if validation_type == "resource_exists":
                resource_type = validation["resource_type"]
                resource_name = validation.get("resource_name", "")
                
                # Check terraform state
                state_result = subprocess.run(
                    ["terraform", "state", "list"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if state_result.returncode == 0:
                    resources = state_result.stdout.strip().split('\n')
                    found = any(resource_type in resource and (not resource_name or resource_name in resource) 
                              for resource in resources if resource.strip())
                    
                    validation_result["passed"] = found
                    validation_result["message"] = f"Resource {resource_type} {'found' if found else 'not found'} in state"
                else:
                    validation_result["message"] = f"Failed to check terraform state: {state_result.stderr}"
            
            elif validation_type == "aws_resource_exists":
                service = validation["service"]
                resource_check = validation["check"]
                
                try:
                    if service == "s3":
                        s3 = boto3.client('s3', **self.aws_config)
                        bucket_name = resource_check["bucket_name"]
                        s3.head_bucket(Bucket=bucket_name)
                        validation_result["passed"] = True
                        validation_result["message"] = f"S3 bucket {bucket_name} exists"
                    
                    elif service == "lambda":
                        lambda_client = boto3.client('lambda', **self.aws_config)
                        function_name = resource_check["function_name"]
                        lambda_client.get_function(FunctionName=function_name)
                        validation_result["passed"] = True
                        validation_result["message"] = f"Lambda function {function_name} exists"
                    
                    elif service == "dynamodb":
                        dynamodb = boto3.client('dynamodb', **self.aws_config)
                        table_name = resource_check["table_name"]
                        dynamodb.describe_table(TableName=table_name)
                        validation_result["passed"] = True
                        validation_result["message"] = f"DynamoDB table {table_name} exists"
                        
                except ClientError as e:
                    validation_result["message"] = f"AWS resource check failed: {str(e)}"
                except Exception as e:
                    validation_result["message"] = f"Validation error: {str(e)}"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result
    
    def _run_aws_validation(self, validation: Dict) -> Dict:
        """Run validation check on AWS resources"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            service = validation.get("service", "")
            
            if validation_type == "service_available":
                # Check if LocalStack service is available
                try:
                    response = requests.get(f"{self.localstack_endpoint}/health", timeout=5)
                    health = response.json()
                    
                    service_status = health.get("services", {}).get(service, "unavailable")
                    validation_result["passed"] = service_status in ["available", "running"]
                    validation_result["message"] = f"Service {service} status: {service_status}"
                    
                except Exception as e:
                    validation_result["message"] = f"Health check failed: {str(e)}"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result
    
    def _run_docker_validation(self, validation: Dict, image_tag: str, container_id: str) -> Dict:
        """Run validation check on Docker deployment"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            
            if validation_type == "image_exists":
                inspect_result = subprocess.run(
                    ["docker", "inspect", image_tag],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                validation_result["passed"] = inspect_result.returncode == 0
                validation_result["message"] = f"Image {image_tag} {'exists' if validation_result['passed'] else 'does not exist'}"
            
            elif validation_type == "container_running" and container_id:
                ps_result = subprocess.run(
                    ["docker", "ps", "-q", "-f", f"id={container_id}"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                validation_result["passed"] = bool(ps_result.stdout.strip())
                validation_result["message"] = f"Container {'is running' if validation_result['passed'] else 'is not running'}"
            
            elif validation_type == "port_accessible":
                port = validation["port"]
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex(('localhost', int(port)))
                    sock.close()
                    
                    validation_result["passed"] = result == 0
                    validation_result["message"] = f"Port {port} {'is accessible' if validation_result['passed'] else 'is not accessible'}"
                    
                except Exception as e:
                    validation_result["message"] = f"Port check failed: {str(e)}"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result


def main():
    """Main test runner entry point"""
    
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No test configuration provided"}))
        sys.exit(1)
    
    try:
        test_config = json.loads(sys.argv[1])
        runner = CloudTestRunner()
        
        challenge_type = test_config.get("type", "terraform")
        code = test_config.get("code", "")
        
        if challenge_type == "terraform":
            result = runner.run_terraform_deployment(code, test_config)
        elif challenge_type == "aws_cli":
            commands = test_config.get("commands", [])
            result = runner.run_aws_cli_commands(commands, test_config)
        elif challenge_type == "docker":
            result = runner.run_docker_deployment(code, test_config)
        else:
            result = {
                "error": f"Unknown challenge type: {challenge_type}",
                "passed": False,
                "score": 0
            }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            "error": f"Test runner error: {str(e)}\n{traceback.format_exc()}",
            "passed": False,
            "score": 0
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()