# ==========================================
# Stage 1: Export locked requirements
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Export locked dependencies to a temporary requirements file
RUN uv export --frozen --no-dev -o requirements.txt

# ==========================================
# Stage 2: Minimal runtime environment
# ==========================================
FROM python:3.12-slim-bookworm

# Install curl for container health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy uv binary into runtime stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-privileged system user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install locked requirements into system Python
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Clean up uv binary and temporary files from final image
RUN rm /bin/uv /bin/uvx requirements.txt

# Copy application source code
COPY . .

# Prepare data directory permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch context to non-root user
USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Execute Uvicorn from system PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]