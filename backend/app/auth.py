"""Authentication helpers — BYPASSED for now, will be re-added with database backend."""

from __future__ import annotations


def get_current_user() -> str:
    """FastAPI dependency — returns a hardcoded username while auth is bypassed."""
    return "anonymous"
