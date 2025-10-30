# Container-based Testing for Bit Buddy
# Run complete test suites without any local dependencies

FROM python:3.11-slim as base

# Set up working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install testing dependencies
RUN pip install pytest pytest-asyncio pytest-cov pytest-benchmark \
    black isort flake8 mypy bandit safety

# Install AI dependencies (CPU versions)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install sentence-transformers chromadb

# Copy source code
COPY . .

# Create test data directory
RUN mkdir -p /app/test-data

# === UNIT TESTING IMAGE ===
FROM base as unit-tests

RUN echo "Running unit tests..." && \
    python test_runner.py --unit --verbose

# === INTEGRATION TESTING IMAGE ===  
FROM base as integration-tests

# Create test workspace
RUN mkdir -p /app/test-workspace/{buddy,watch,models} && \
    echo "Test document about AI and machine learning" > /app/test-workspace/watch/ai.txt && \
    echo "Python code example" > /app/test-workspace/watch/code.py && \
    echo "Project management notes" > /app/test-workspace/watch/notes.md && \
    echo "Data analysis results" > /app/test-workspace/watch/data.csv

ENV TEST_WORKSPACE=/app/test-workspace

RUN echo "Running integration tests..." && \
    python test_runner.py --integration --verbose

# === PERFORMANCE TESTING IMAGE ===
FROM base as performance-tests  

# Create large test dataset
RUN mkdir -p /app/perf-data && \
    for i in $(seq 1 1000); do \
        echo "Performance test file $i with content about various topics including AI, programming, and project management" > /app/perf-data/file_$i.txt; \
    done

ENV TEST_DATA_DIR=/app/perf-data

RUN echo "Running performance tests..." && \
    python test_runner.py --performance --verbose

# === MESH NETWORKING TEST IMAGE ===
FROM base as mesh-tests

EXPOSE 8000-8010

# Create multiple buddy configurations
RUN mkdir -p /app/buddy-{1,2,3}/{buddy,watch} && \
    echo "Buddy 1 test files" > /app/buddy-1/watch/test1.txt && \
    echo "Buddy 2 test files" > /app/buddy-2/watch/test2.txt && \
    echo "Buddy 3 test files" > /app/buddy-3/watch/test3.txt

COPY docker-mesh-test.sh /app/
RUN chmod +x /app/docker-mesh-test.sh

CMD ["./docker-mesh-test.sh"]

# === SECURITY TESTING IMAGE ===
FROM base as security-tests

RUN echo "Running security scans..." && \
    bandit -r . -f json -o bandit-report.json && \
    safety check --json --output safety-report.json && \
    echo "Security scans completed"

# === ALL-IN-ONE TESTING IMAGE ===
FROM base as all-tests

# Run comprehensive test suite
RUN echo "Running comprehensive test suite..." && \
    python test_runner.py --all --verbose

# Create final report
RUN echo "# Bit Buddy Test Report" > /app/test-report.md && \
    echo "Generated: $(date)" >> /app/test-report.md && \
    echo "" >> /app/test-report.md && \
    echo "✅ All tests completed successfully in containerized environment" >> /app/test-report.md && \
    echo "🐳 No local dependencies required" >> /app/test-report.md

CMD ["cat", "/app/test-report.md"]

# === DEVELOPMENT IMAGE ===
FROM base as development

# Install additional development tools
RUN pip install jupyter notebook ipython

# Create development workspace  
RUN mkdir -p /app/dev-workspace/{buddies,test-files,debug-logs}

# Set up development environment
ENV PYTHONPATH=/app
ENV BUDDY_DEV_MODE=true

# Expose ports for development servers
EXPOSE 8000 8001 8002 8003 8888

# Default command for development
CMD ["bash"]