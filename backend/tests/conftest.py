"""Shared test fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import seed_data


@pytest.fixture(autouse=True)
def reset_store():
    """Re-seed the store before every test for isolation."""
    seed_data()
    yield


@pytest.fixture()
def client():
    """FastAPI test client."""
    return TestClient(app)
