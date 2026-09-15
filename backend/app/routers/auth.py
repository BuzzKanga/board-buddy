"""Auth router — BYPASSED for now, will be re-added with database backend."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

# No endpoints while auth is bypassed.
# Register and login will be re-added when the backend switches to a database.
