"""
Seed script for Cloud Track challenges  
Creates 15 cloud infrastructure challenges with AWS/LocalStack and Docker
"""

import asyncio

from app.core.database import get_db
from app.models.challenge import Challenge, ChallengeDifficulty, ChallengeTrack

CLOUD_CHALLENGES = [
    # BEGINNER: Basic Deployments (1-5)
    {
        "slug": "cloud-001-s3-bucket",
        "title": "Create and Configure S3 Bucket",
        "description": "Create an S3 bucket with proper permissions and upload a static website.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.CLOUD,
        "order_index": 1,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "30 minutes",
        "requirements": [
            {"id": "req1", "text": "Create S3 bucket with unique name", "points": 25},
            {
                "id": "req2",
                "text": "Configure bucket for static website hosting",
                "points": 25,
            },
            {
                "id": "req3",
                "text": "Upload index.html and error.html files",
                "points": 25,
            },
            {"id": "req4", "text": "Set proper bucket permissions", "points": 25},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use Terraform for infrastructure",
                "type": "technical",
            },
            {"id": "con2", "text": "Follow AWS naming conventions", "type": "business"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "S3 bucket exists",
                    "type": "resource_exists",
                    "resource_type": "aws_s3_bucket",
                },
                {
                    "name": "Website configuration",
                    "type": "aws_resource_exists",
                    "service": "s3",
                    "check": {"bucket_name": "my-static-website-bucket"},
                },
                {
                    "name": "Bucket policy configured",
                    "type": "resource_exists",
                    "resource_type": "aws_s3_bucket_policy",
                },
            ],
        },
        "hints": [
            "Use aws_s3_bucket resource in Terraform",
            "Enable website hosting with index_document and error_document",
            "Set bucket_acl to 'public-read' for static hosting",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-002-lambda-function",
        "title": "Deploy Lambda Function",
        "description": "Create and deploy a simple Lambda function that processes HTTP requests.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.CLOUD,
        "order_index": 2,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "40 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Create Lambda function with Python runtime",
                "points": 30,
            },
            {
                "id": "req2",
                "text": "Configure function to return JSON response",
                "points": 25,
            },
            {
                "id": "req3",
                "text": "Set up proper IAM role for execution",
                "points": 25,
            },
            {"id": "req4", "text": "Test function invocation", "points": 20},
        ],
        "constraints": [
            {"id": "con1", "text": "Use Python 3.11 runtime", "type": "technical"},
            {"id": "con2", "text": "Keep function under 1MB", "type": "performance"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "Lambda function exists",
                    "type": "resource_exists",
                    "resource_type": "aws_lambda_function",
                },
                {
                    "name": "Function accessible",
                    "type": "aws_resource_exists",
                    "service": "lambda",
                    "check": {"function_name": "hello-world-function"},
                },
                {
                    "name": "IAM role configured",
                    "type": "resource_exists",
                    "resource_type": "aws_iam_role",
                },
            ],
        },
        "hints": [
            "Use aws_lambda_function resource with filename or s3 source",
            "Create IAM role with lambda.amazonaws.com trust policy",
            "Attach AWSLambdaBasicExecutionRole policy for CloudWatch logs",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-003-api-gateway",
        "title": "API Gateway Integration",
        "description": "Set up API Gateway to expose Lambda function as REST API endpoint.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.CLOUD,
        "order_index": 3,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "45 minutes",
        "requirements": [
            {"id": "req1", "text": "Create API Gateway REST API", "points": 25},
            {"id": "req2", "text": "Configure resource and method", "points": 25},
            {"id": "req3", "text": "Integrate with Lambda function", "points": 30},
            {"id": "req4", "text": "Deploy API to stage", "points": 20},
        ],
        "constraints": [
            {"id": "con1", "text": "Use proxy integration", "type": "technical"},
            {"id": "con2", "text": "Enable CORS if needed", "type": "business"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "API Gateway exists",
                    "type": "resource_exists",
                    "resource_type": "aws_api_gateway_rest_api",
                },
                {
                    "name": "Lambda integration",
                    "type": "resource_exists",
                    "resource_type": "aws_api_gateway_integration",
                },
                {
                    "name": "API deployment",
                    "type": "resource_exists",
                    "resource_type": "aws_api_gateway_deployment",
                },
            ],
        },
        "hints": [
            "Create aws_api_gateway_rest_api resource first",
            "Use aws_api_gateway_resource for path, aws_api_gateway_method for HTTP method",
            "Configure aws_api_gateway_integration with lambda function URI",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-004-dynamodb-table",
        "title": "DynamoDB Table Setup",
        "description": "Create a DynamoDB table with proper indexing for a simple data application.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.CLOUD,
        "order_index": 4,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "35 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Create DynamoDB table with partition key",
                "points": 30,
            },
            {"id": "req2", "text": "Add Global Secondary Index (GSI)", "points": 30},
            {"id": "req3", "text": "Configure read/write capacity", "points": 20},
            {"id": "req4", "text": "Set up item TTL if applicable", "points": 20},
        ],
        "constraints": [
            {"id": "con1", "text": "Use on-demand billing mode", "type": "business"},
            {
                "id": "con2",
                "text": "Follow DynamoDB naming conventions",
                "type": "technical",
            },
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "DynamoDB table exists",
                    "type": "resource_exists",
                    "resource_type": "aws_dynamodb_table",
                },
                {
                    "name": "Table accessible",
                    "type": "aws_resource_exists",
                    "service": "dynamodb",
                    "check": {"table_name": "user-sessions"},
                },
                {
                    "name": "GSI configured",
                    "type": "resource_exists",
                    "resource_type": "aws_dynamodb_table",
                },
            ],
        },
        "hints": [
            "Use aws_dynamodb_table resource with hash_key (partition key)",
            "Add global_secondary_index block for GSI",
            "Set billing_mode to 'PAY_PER_REQUEST' for on-demand",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-005-docker-basics",
        "title": "Docker Container Deployment",
        "description": "Create a Dockerfile for a web application and deploy it locally.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.CLOUD,
        "order_index": 5,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "50 minutes",
        "requirements": [
            {"id": "req1", "text": "Write multi-stage Dockerfile", "points": 30},
            {"id": "req2", "text": "Configure application dependencies", "points": 25},
            {"id": "req3", "text": "Expose appropriate port", "points": 20},
            {"id": "req4", "text": "Optimize image size", "points": 25},
        ],
        "constraints": [
            {"id": "con1", "text": "Use Alpine Linux base image", "type": "technical"},
            {"id": "con2", "text": "Keep image under 100MB", "type": "performance"},
        ],
        "test_config": {
            "type": "docker",
            "files": [
                {
                    "path": "app.py",
                    "content": "from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef hello():\n    return 'Hello from Docker!'\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)",
                },
                {"path": "requirements.txt", "content": "Flask==2.3.3"},
            ],
            "ports": ["5000:5000"],
            "validations": [
                {"name": "Image builds successfully", "type": "image_exists"},
                {"name": "Container runs", "type": "container_running"},
                {"name": "Port accessible", "type": "port_accessible", "port": "5000"},
            ],
        },
        "hints": [
            "Start with python:3.11-alpine base image",
            "Copy requirements.txt first, then pip install (for layer caching)",
            "Use EXPOSE instruction to document port usage",
        ],
        "is_red_team": False,
    },
    # INTERMEDIATE: Infrastructure as Code (6-10)
    {
        "slug": "cloud-006-vpc-networking",
        "title": "VPC and Networking Setup",
        "description": "Create a VPC with subnets, internet gateway, and route tables.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.CLOUD,
        "order_index": 6,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "60 minutes",
        "requirements": [
            {"id": "req1", "text": "Create VPC with CIDR block", "points": 30},
            {"id": "req2", "text": "Set up public and private subnets", "points": 40},
            {
                "id": "req3",
                "text": "Configure internet gateway and NAT gateway",
                "points": 40,
            },
            {
                "id": "req4",
                "text": "Create route tables and associations",
                "points": 40,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use /24 subnets in different AZs",
                "type": "technical",
            },
            {"id": "con2", "text": "Follow AWS VPC best practices", "type": "business"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "VPC created",
                    "type": "resource_exists",
                    "resource_type": "aws_vpc",
                },
                {
                    "name": "Public subnet exists",
                    "type": "resource_exists",
                    "resource_type": "aws_subnet",
                },
                {
                    "name": "Internet gateway attached",
                    "type": "resource_exists",
                    "resource_type": "aws_internet_gateway",
                },
                {
                    "name": "Route tables configured",
                    "type": "resource_exists",
                    "resource_type": "aws_route_table",
                },
            ],
        },
        "hints": [
            "Start with aws_vpc resource using 10.0.0.0/16 CIDR",
            "Create subnets in different availability zones",
            "Attach internet gateway to VPC and create routes",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-007-ecs-deployment",
        "title": "ECS Container Deployment",
        "description": "Deploy a containerized application using Amazon ECS with Fargate.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.CLOUD,
        "order_index": 7,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "75 minutes",
        "requirements": [
            {"id": "req1", "text": "Create ECS cluster", "points": 30},
            {
                "id": "req2",
                "text": "Define task definition with container specs",
                "points": 40,
            },
            {
                "id": "req3",
                "text": "Set up ECS service with load balancer",
                "points": 50,
            },
            {"id": "req4", "text": "Configure auto-scaling", "points": 30},
        ],
        "constraints": [
            {"id": "con1", "text": "Use Fargate launch type", "type": "technical"},
            {"id": "con2", "text": "Implement health checks", "type": "business"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "ECS cluster exists",
                    "type": "resource_exists",
                    "resource_type": "aws_ecs_cluster",
                },
                {
                    "name": "Task definition created",
                    "type": "resource_exists",
                    "resource_type": "aws_ecs_task_definition",
                },
                {
                    "name": "ECS service running",
                    "type": "resource_exists",
                    "resource_type": "aws_ecs_service",
                },
            ],
        },
        "hints": [
            "Create aws_ecs_cluster with capacity_providers = ['FARGATE']",
            "Define container_definitions in JSON format",
            "Use aws_ecs_service with launch_type = 'FARGATE'",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-008-rds-database",
        "title": "RDS Database Setup",
        "description": "Set up RDS PostgreSQL instance with backup and security configuration.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.CLOUD,
        "order_index": 8,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "55 minutes",
        "requirements": [
            {"id": "req1", "text": "Create RDS PostgreSQL instance", "points": 40},
            {"id": "req2", "text": "Configure security groups", "points": 30},
            {"id": "req3", "text": "Set up automated backups", "points": 40},
            {"id": "req4", "text": "Enable encryption at rest", "points": 40},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use db.t3.micro instance class",
                "type": "business",
            },
            {"id": "con2", "text": "Place in private subnet", "type": "security"},
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "RDS instance exists",
                    "type": "resource_exists",
                    "resource_type": "aws_db_instance",
                },
                {
                    "name": "Security group configured",
                    "type": "resource_exists",
                    "resource_type": "aws_security_group",
                },
                {
                    "name": "Backup configured",
                    "type": "resource_exists",
                    "resource_type": "aws_db_instance",
                },
            ],
        },
        "hints": [
            "Use aws_db_instance with engine = 'postgres'",
            "Create security group allowing port 5432 from application",
            "Set backup_retention_period > 0 for automated backups",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-009-cloudformation",
        "title": "CloudFormation Stack",
        "description": "Create a CloudFormation template for a complete web application stack.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.CLOUD,
        "order_index": 9,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "80 minutes",
        "requirements": [
            {"id": "req1", "text": "Define parameters and outputs", "points": 30},
            {"id": "req2", "text": "Create resources with dependencies", "points": 50},
            {"id": "req3", "text": "Use conditions and mappings", "points": 40},
            {"id": "req4", "text": "Implement stack updates safely", "points": 30},
        ],
        "constraints": [
            {"id": "con1", "text": "Use YAML format", "type": "technical"},
            {"id": "con2", "text": "Include resource dependencies", "type": "business"},
        ],
        "test_config": {
            "type": "aws_cli",
            "commands": [
                "aws cloudformation create-stack --stack-name test-stack --template-body file://template.yaml",
                "aws cloudformation describe-stacks --stack-name test-stack",
                "aws cloudformation delete-stack --stack-name test-stack",
            ],
            "validations": [
                {
                    "name": "CloudFormation service available",
                    "type": "service_available",
                    "service": "cloudformation",
                }
            ],
        },
        "hints": [
            "Start with AWSTemplateFormatVersion: '2010-09-09'",
            "Use Ref and GetAtt functions for resource references",
            "Define DependsOn for explicit resource ordering",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-010-red-team-security",
        "title": "Red Team: AWS Security Assessment",
        "description": "Identify and fix security vulnerabilities in AWS infrastructure configuration.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.CLOUD,
        "order_index": 10,
        "points": 200,
        "model_tier": "haiku",
        "estimated_time": "70 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Identify overly permissive IAM policies",
                "points": 50,
            },
            {
                "id": "req2",
                "text": "Fix security group misconfigurations",
                "points": 50,
            },
            {"id": "req3", "text": "Implement least privilege access", "points": 50},
            {"id": "req4", "text": "Enable CloudTrail logging", "points": 50},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Maintain functional requirements",
                "type": "business",
            },
            {
                "id": "con2",
                "text": "Follow security best practices",
                "type": "security",
            },
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "IAM policies secured",
                    "type": "resource_exists",
                    "resource_type": "aws_iam_policy",
                },
                {
                    "name": "Security groups restricted",
                    "type": "resource_exists",
                    "resource_type": "aws_security_group",
                },
                {
                    "name": "CloudTrail enabled",
                    "type": "resource_exists",
                    "resource_type": "aws_cloudtrail",
                },
            ],
        },
        "hints": [
            "Look for policies with '*' permissions or 0.0.0.0/0 access",
            "Remove unnecessary administrative privileges",
            "Enable logging and monitoring for compliance",
        ],
        "is_red_team": True,
    },
    # ADVANCED: CI/CD & Monitoring (11-15)
    {
        "slug": "cloud-011-cicd-pipeline",
        "title": "CI/CD Pipeline with GitHub Actions",
        "description": "Build a complete CI/CD pipeline that deploys to AWS using GitHub Actions.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.CLOUD,
        "order_index": 11,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "90 minutes",
        "requirements": [
            {"id": "req1", "text": "Create GitHub Actions workflow", "points": 50},
            {
                "id": "req2",
                "text": "Implement testing and linting stages",
                "points": 50,
            },
            {
                "id": "req3",
                "text": "Configure deployment to staging and production",
                "points": 60,
            },
            {"id": "req4", "text": "Add rollback capabilities", "points": 40},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use infrastructure as code for deployments",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Implement approval gates for production",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "docker",
            "files": [
                {
                    "path": ".github/workflows/deploy.yml",
                    "content": "name: Deploy\non:\n  push:\n    branches: [main]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v3\n      - name: Test\n        run: echo 'Tests passed'",
                }
            ],
            "validations": [
                {"name": "Workflow file exists", "type": "image_exists"},
                {"name": "Multi-stage pipeline", "type": "container_running"},
            ],
        },
        "hints": [
            "Use GitHub Actions with aws-actions/configure-aws-credentials",
            "Implement separate jobs for test, build, and deploy",
            "Use environments for staging and production with protection rules",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-012-monitoring-observability",
        "title": "CloudWatch Monitoring Setup",
        "description": "Implement comprehensive monitoring and alerting for AWS infrastructure.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.CLOUD,
        "order_index": 12,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "85 minutes",
        "requirements": [
            {"id": "req1", "text": "Set up CloudWatch dashboards", "points": 40},
            {"id": "req2", "text": "Create custom metrics and alarms", "points": 50},
            {"id": "req3", "text": "Configure SNS notifications", "points": 50},
            {"id": "req4", "text": "Implement log aggregation", "points": 60},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use CloudWatch Insights for log analysis",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Set appropriate alarm thresholds",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "CloudWatch dashboard created",
                    "type": "resource_exists",
                    "resource_type": "aws_cloudwatch_dashboard",
                },
                {
                    "name": "Alarms configured",
                    "type": "resource_exists",
                    "resource_type": "aws_cloudwatch_metric_alarm",
                },
                {
                    "name": "SNS topic created",
                    "type": "resource_exists",
                    "resource_type": "aws_sns_topic",
                },
            ],
        },
        "hints": [
            "Use aws_cloudwatch_dashboard with JSON-formatted body",
            "Create alarms for CPU, memory, and custom application metrics",
            "Set up SNS topics for email/SMS notifications",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-013-kubernetes-deployment",
        "title": "Kubernetes Application Deployment",
        "description": "Deploy and manage a multi-service application on Kubernetes cluster.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.CLOUD,
        "order_index": 13,
        "points": 250,
        "model_tier": "sonnet",
        "estimated_time": "100 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Create Kubernetes manifests (Deployment, Service, Ingress)",
                "points": 60,
            },
            {"id": "req2", "text": "Configure ConfigMaps and Secrets", "points": 50},
            {
                "id": "req3",
                "text": "Implement health checks and resource limits",
                "points": 70,
            },
            {"id": "req4", "text": "Set up horizontal pod autoscaling", "points": 70},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use declarative YAML manifests",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Follow Kubernetes security best practices",
                "type": "security",
            },
        ],
        "test_config": {
            "type": "docker",
            "files": [
                {
                    "path": "deployment.yaml",
                    "content": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: app\nspec:\n  replicas: 2\n  selector:\n    matchLabels:\n      app: web\n  template:\n    metadata:\n      labels:\n        app: web\n    spec:\n      containers:\n      - name: web\n        image: nginx\n        ports:\n        - containerPort: 80",
                }
            ],
            "validations": [
                {"name": "Manifests created", "type": "image_exists"},
                {"name": "Deployment configured", "type": "container_running"},
            ],
        },
        "hints": [
            "Start with basic Deployment and Service manifests",
            "Use ConfigMaps for configuration, Secrets for sensitive data",
            "Add readiness and liveness probes for health checks",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-014-terraform-modules",
        "title": "Terraform Module Development",
        "description": "Create reusable Terraform modules for common infrastructure patterns.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.CLOUD,
        "order_index": 14,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "95 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Create module with input variables and outputs",
                "points": 50,
            },
            {
                "id": "req2",
                "text": "Implement data validation and defaults",
                "points": 40,
            },
            {"id": "req3", "text": "Add conditional resource creation", "points": 60},
            {"id": "req4", "text": "Write module documentation", "points": 50},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Follow Terraform module conventions",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Make modules reusable across environments",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "Module structure correct",
                    "type": "resource_exists",
                    "resource_type": "aws_vpc",
                },
                {
                    "name": "Variables defined",
                    "type": "resource_exists",
                    "resource_type": "aws_subnet",
                },
                {
                    "name": "Outputs configured",
                    "type": "resource_exists",
                    "resource_type": "aws_internet_gateway",
                },
            ],
        },
        "hints": [
            "Create separate files: main.tf, variables.tf, outputs.tf",
            "Use variable validation blocks for input checking",
            "Add count or for_each for conditional resources",
        ],
        "is_red_team": False,
    },
    {
        "slug": "cloud-015-red-team-infrastructure",
        "title": "Red Team: Infrastructure Attack Simulation",
        "description": "Simulate infrastructure attacks and implement defensive measures.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.CLOUD,
        "order_index": 15,
        "points": 250,
        "model_tier": "sonnet",
        "estimated_time": "110 minutes",
        "requirements": [
            {"id": "req1", "text": "Identify potential attack vectors", "points": 60},
            {"id": "req2", "text": "Implement network segmentation", "points": 70},
            {"id": "req3", "text": "Set up intrusion detection", "points": 60},
            {"id": "req4", "text": "Create incident response procedures", "points": 60},
        ],
        "constraints": [
            {"id": "con1", "text": "Maintain system availability", "type": "business"},
            {
                "id": "con2",
                "text": "Implement zero-trust principles",
                "type": "security",
            },
        ],
        "test_config": {
            "type": "terraform",
            "validations": [
                {
                    "name": "Network ACLs configured",
                    "type": "resource_exists",
                    "resource_type": "aws_network_acl",
                },
                {
                    "name": "WAF protection enabled",
                    "type": "resource_exists",
                    "resource_type": "aws_wafv2_web_acl",
                },
                {
                    "name": "GuardDuty enabled",
                    "type": "resource_exists",
                    "resource_type": "aws_guardduty_detector",
                },
            ],
        },
        "hints": [
            "Consider OWASP Top 10 for web applications",
            "Implement network segmentation with security groups",
            "Use AWS GuardDuty for threat detection",
        ],
        "is_red_team": True,
    },
]


async def seed_cloud_challenges():
    """Seed cloud infrastructure challenges to database"""

    async for db in get_db():
        try:
            for challenge_data in CLOUD_CHALLENGES:
                # Check if challenge already exists
                existing = await db.execute(
                    select(Challenge).where(Challenge.slug == challenge_data["slug"])
                )
                if existing.scalar_one_or_none():
                    print(
                        f"Challenge {challenge_data['slug']} already exists, skipping..."
                    )
                    continue

                # Create challenge
                challenge = Challenge(
                    slug=challenge_data["slug"],
                    title=challenge_data["title"],
                    description=challenge_data["description"],
                    difficulty=challenge_data["difficulty"],
                    track=challenge_data["track"],
                    order_index=challenge_data["order_index"],
                    points=challenge_data["points"],
                    model_tier=challenge_data["model_tier"],
                    estimated_time=challenge_data["estimated_time"],
                    requirements=challenge_data["requirements"],
                    constraints=challenge_data["constraints"],
                    test_config=challenge_data["test_config"],
                    hints=challenge_data["hints"],
                    is_red_team=challenge_data["is_red_team"],
                )

                db.add(challenge)
                print(f"Added challenge: {challenge_data['title']}")

            await db.commit()
            print(
                f"\n✅ Successfully seeded {len(CLOUD_CHALLENGES)} cloud infrastructure challenges!"
            )

        except Exception as e:
            await db.rollback()
            print(f"Error seeding challenges: {e}")
            raise

        break  # Only need first iteration


if __name__ == "__main__":
    asyncio.run(seed_cloud_challenges())
