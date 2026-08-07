# ==========================================
# Stage 1: Dependency resolution stage
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary directly from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# ==========================================
# Stage 2: Final minimal runtime
# ==========================================
FROM python:3.12-slim-bookworm

# Copy uv binary into runtime stage so we can install into system Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-privileged system user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Copy dependency files from builder
COPY --from=builder /app/pyproject.toml /app/uv.lock ./

# Install locked production dependencies directly into system Python
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --system

# Remove uv binary from final image now that dependencies are installed
RUN rm /bin/uv /bin/uvx

# Copy remaining application source code
COPY . .

# Ensure data directory exists with non-root ownership
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start Uvicorn directly from system PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]