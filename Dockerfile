# ==========================================
# Stage 1: Export locked dependencies with uv
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary directly from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export frozen dependencies to a standard requirements.txt
RUN uv export --frozen --no-dev -o requirements.txt

# ==========================================
# Stage 2: Minimal runtime
# ==========================================
FROM python:3.12-slim-bookworm

# Create non-privileged system user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install locked dependencies into system Python using uv
RUN uv pip install --system --frozen --no-dev -r pyproject.toml

# Copy remaining app source code
COPY . .
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]