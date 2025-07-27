# Multi-stage build for MCP Linux Debug Agent
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MCP_ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    htop \
    procps \
    psmisc \
    net-tools \
    systemd \
    sudo \
    vim \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
WORKDIR /app
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && \
    chown -R mcpuser:mcpuser /app

# Health check script
RUN echo '#!/bin/bash\necho "Health check starting..."\npython3 -c "import psutil; print(f\"CPU: {psutil.cpu_percent()}%\")"' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Switch to non-root user
USER mcpuser

# Expose ports for HTTP mode
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD /app/healthcheck.sh

# Default command
CMD ["python3", "main.py"]
