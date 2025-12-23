# Data Science Sandbox for Jupyter + SQL challenges
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    postgresql-client \
    sqlite3 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash datauser && \
    mkdir -p /workspace /datasets && \
    chown -R datauser:datauser /workspace /datasets

# Install Python packages for data science
RUN pip install --no-cache-dir \
    jupyter==1.0.0 \
    jupyterlab==4.0.9 \
    notebook==7.0.6 \
    pandas==2.1.4 \
    numpy==1.25.2 \
    matplotlib==3.8.2 \
    seaborn==0.13.0 \
    scikit-learn==1.3.2 \
    scipy==1.11.4 \
    plotly==5.17.0 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    jupyter-client==8.6.0 \
    ipykernel==6.27.1 \
    nbformat==5.9.2 \
    nbconvert==7.12.0

# Install additional data tools
RUN pip install --no-cache-dir \
    openpyxl==3.1.2 \
    xlsxwriter==3.1.9 \
    beautifulsoup4==4.12.2 \
    requests==2.31.0 \
    lxml==4.9.3

# Set up Jupyter kernel
USER datauser
RUN python -m ipykernel install --user --name=python3

# Create workspace structure
WORKDIR /workspace
RUN mkdir -p notebooks data output

# Copy test runner script
COPY --chown=datauser:datauser data-test-runner.py /workspace/
COPY --chown=datauser:datauser sample_datasets/ /datasets/

# Set environment variables
ENV PYTHONPATH=/workspace
ENV JUPYTER_ENABLE_LAB=yes

# Security: Drop capabilities and set resource limits
USER datauser

# Default command
CMD ["python", "data-test-runner.py"]