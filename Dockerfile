# ==========================================
# Stage 1: Build virtual environment
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# Install uv directly from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Explicitly set virtualenv destination and optimize compile step
ENV UV_PROJECT_ENVIRONMENT="/app/.venv" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency specification files first for optimal layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies without installing the project package itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY . .

# Final sync to install the project package into virtualenv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# Stage 2: Final minimal runtime
# ==========================================
FROM python:3.12-slim-bookworm

# Create a non-privileged system user and group
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Copy application code and virtual environment from builder stage with correct ownership
COPY --from=builder --chown=appuser:appuser /app /app

# Ensure application data directory exists and has correct permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch execution context to the non-root user
USER appuser

# Environment variables for unbuffered output and virtualenv PATH execution
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Expose standard FastAPI application port
EXPOSE 8000

# Start Uvicorn bound to all interfaces
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]