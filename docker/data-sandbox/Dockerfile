# WeaktoStrong Data Science Sandbox - Optimized for Speed
FROM python:3.10-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -s /bin/bash sandbox && \
    mkdir -p /workspace /datasets && \
    chown -R sandbox:sandbox /workspace /datasets

# Install core data science packages in single layer for optimization
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pandas==2.1.4 \
    numpy==1.25.2 \
    scikit-learn==1.3.2 \
    matplotlib==3.8.2 \
    pytest==7.4.3 \
    seaborn==0.13.0 \
    scipy==1.11.4

# Set up workspace structure
WORKDIR /workspace
USER sandbox
RUN mkdir -p data output temp

# Copy test runner script
COPY --chown=sandbox:sandbox data-test-runner.py /workspace/

# Copy sample datasets if they exist
COPY --chown=sandbox:sandbox sample_datasets/ /datasets/

# Set environment variables for optimal performance
ENV PYTHONPATH=/workspace \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    NUMEXPR_MAX_THREADS=1

# Default command
CMD ["python", "data-test-runner.py"]