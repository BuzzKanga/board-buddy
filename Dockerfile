# ===========================================================================
# Stage 1 — Build the frontend as a static SPA
# ===========================================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /build/frontend

# Install dependencies (cached unless package files change)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy source and build a plain SPA (no SSR / Nitro)
COPY frontend/ ./
ENV VITE_API_BASE_URL=""
RUN npx vite build --config vite.spa.config.ts

# ===========================================================================
# Stage 2 — Python backend + frontend static files
# ===========================================================================
FROM python:3.13-slim

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies (cached unless lock/toml change)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy backend source
COPY backend/app ./app

# Copy frontend build output into static/ (read by app/main.py)
COPY --from=frontend-builder /build/frontend/dist ./static

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
