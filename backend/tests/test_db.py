"""Tests for database engine, configuration, and persistence."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.engine import Base
from app.db.models import BoardRow, ColumnRow
from app.db.seed import seed_data


def test_database_persistence_across_sessions(tmp_path):
    """Test that data written to SQLite persists across independent sessions."""
    db_file = tmp_path / "test_persist.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Session 1: Seed data
    with Session() as session:
        seed_data(session)

    # Session 2: Read and verify data persists
    with Session() as session:
        boards = session.query(BoardRow).all()
        assert len(boards) == 2
        board_names = [b.name for b in boards]
        assert "Product Launch" in board_names
        assert "Bug Tracker" in board_names

        columns = session.query(ColumnRow).all()
        assert len(columns) == 6


def test_seed_data_is_idempotent_without_force(tmp_path):
    """Test that seed_data does not duplicate rows if data exists."""
    db_file = tmp_path / "test_idempotent.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        seed_data(session)
        # Calling again without force should be a no-op
        seed_data(session, force=False)
        boards = session.query(BoardRow).all()
        assert len(boards) == 2
