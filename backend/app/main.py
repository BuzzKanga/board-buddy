"""Board Buddy FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db.engine import Base, SessionLocal, engine
from app.db.seed import seed_data
from app.routers import auth, boards, cards, columns, labels

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and seed initial data if empty."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_data(db)
    yield


app = FastAPI(
    title="Board Buddy API",
    description="REST API for the Board Buddy kanban application.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — permissive for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(cards.router)
app.include_router(labels.router)

# ---------------------------------------------------------------------------
# Serve frontend SPA (only when the Docker-built static directory exists)
# ---------------------------------------------------------------------------
if STATIC_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=STATIC_DIR / "assets"),
        name="static_assets",
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve static files or fall back to index.html for SPA routing."""
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")

