# Multi-stage build for MCP Weather Server
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DOCKER_CONTAINER=true

# Install system dependencies including psutil for health checks
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and logs directory with proper permissions
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psutil

# Create non-root user for security BEFORE copying files
RUN useradd --create-home --shell /bin/bash app

# Create directories with proper ownership
RUN mkdir -p /app/logs /app/scripts && \
    chown -R app:app /app

# Copy application code
COPY . .

# Ensure scripts are executable and fix ownership
RUN chmod +x /app/scripts/*.py 2>/dev/null || true && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Health check script
RUN echo '#!/bin/bash\necho "Health check starting..."\npython -c "import sys; print(\"Python is working\"); sys.exit(0)"' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/healthcheck.sh

# Default command (can be overridden)
CMD ["python", "-u", "weather_server.py"]
# Multi-stage build for MCP Weather Server
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DOCKER_CONTAINER=true

# Install system dependencies including psutil for health checks
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and logs directory
WORKDIR /app
RUN mkdir -p /app/logs /app/scripts

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psutil

# Copy application code
COPY . .

# Ensure scripts are executable
RUN chmod +x /app/scripts/*.py || true

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check script
RUN echo '#!/bin/bash\necho "Health check starting..."\npython -c "import sys; print(\"Python is working\"); sys.exit(0)"' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/healthcheck.sh

# Default command (can be overridden)
CMD ["python", "-u", "weather_server.py"]
# Multi-stage build for MCP Weather Server
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DOCKER_CONTAINER=true

# Install system dependencies including psutil for health checks
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and logs directory
WORKDIR /app
RUN mkdir -p /app/logs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psutil

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check script
RUN echo '#!/bin/bash\necho "Health check starting..."\npython -c "import sys; print(\"Python is working\"); sys.exit(0)"' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/healthcheck.sh

# Default command (can be overridden)
CMD ["python", "-u", "weather_server.py"]
# Multi-stage build for MCP Weather Server
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "weather_server.py"]
