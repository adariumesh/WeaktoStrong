# Cloud Infrastructure Sandbox for AWS/LocalStack challenges
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws/

# Install Terraform
RUN wget -O terraform.zip https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip && \
    unzip terraform.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform.zip

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Create non-root user for security
RUN useradd -m -s /bin/bash clouduser && \
    usermod -aG docker clouduser && \
    mkdir -p /workspace /infra && \
    chown -R clouduser:clouduser /workspace /infra

# Install Python packages for cloud automation
RUN pip install --no-cache-dir \
    boto3==1.34.0 \
    localstack-client==2.5 \
    awscli-local==0.21 \
    docker==6.1.3 \
    pyyaml==6.0.1 \
    jinja2==3.1.2 \
    requests==2.31.0

# Install LocalStack CLI
RUN pip install --no-cache-dir localstack==3.0.2

# Set up workspace
USER clouduser
WORKDIR /workspace
RUN mkdir -p terraform ansible scripts outputs

# Copy test runner and templates
COPY --chown=clouduser:clouduser cloud-test-runner.py /workspace/
COPY --chown=clouduser:clouduser terraform_templates/ /workspace/terraform/
COPY --chown=clouduser:clouduser aws_policies/ /workspace/policies/

# Set environment variables for LocalStack
ENV AWS_ACCESS_KEY_ID=test
ENV AWS_SECRET_ACCESS_KEY=test
ENV AWS_DEFAULT_REGION=us-east-1
ENV LOCALSTACK_HOST=localstack

# Security: Resource limits will be set by Docker
USER clouduser

# Default command
CMD ["python", "cloud-test-runner.py"]