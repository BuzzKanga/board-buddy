"""Board Buddy FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, boards, cards, columns, labels
from app.store import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed the in-memory store on startup."""
    seed_data()
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
