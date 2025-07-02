FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ssh \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 spatium \
    && useradd --uid 1000 --gid spatium --shell /bin/bash --create-home spatium

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv && \
    uv venv && \
    uv sync --frozen

# Copy application code
COPY spatium/ ./spatium/
COPY README.md ./

# Change ownership to non-root user
RUN chown -R spatium:spatium /app

# Switch to non-root user
USER spatium

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uv", "run", "uvicorn", "spatium.main:app", "--host", "0.0.0.0", "--port", "8000"]
