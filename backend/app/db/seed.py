"""Seed data initialization for Board Buddy database."""

from __future__ import annotations

from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from app.db.models import BoardRow, CardLabelRow, CardRow, ColumnRow, LabelRow
from app.models import Priority


def seed_data(db: Session, force: bool = False) -> None:
    """Populate database with demo data if empty or forced."""
    if not force:
        has_boards = db.query(BoardRow).first() is not None
        if has_boards:
            return

    # Clear existing data if forced
    if force:
        db.query(CardLabelRow).delete()
        db.query(CardRow).delete()
        db.query(ColumnRow).delete()
        db.query(LabelRow).delete()
        db.query(BoardRow).delete()
        db.commit()

    ts = datetime(2026, 9, 12, 1, 0, 0, tzinfo=timezone.utc)

    # ── Board 1: Product Launch ─────────────────────────────────────
    b1 = BoardRow(id="board-1", name="Product Launch", created_at=ts)
    db.add(b1)

    cols_b1 = [
        ColumnRow(id="col-1", board_id=b1.id, name="To Do", position=0),
        ColumnRow(id="col-2", board_id=b1.id, name="In Progress", position=1),
        ColumnRow(id="col-3", board_id=b1.id, name="Done", position=2),
    ]
    for c in cols_b1:
        db.add(c)

    # ── Board 2: Bug Tracker ────────────────────────────────────────
    b2 = BoardRow(id="board-2", name="Bug Tracker", created_at=ts)
    db.add(b2)

    cols_b2 = [
        ColumnRow(id="col-4", board_id=b2.id, name="To Do", position=0),
        ColumnRow(id="col-5", board_id=b2.id, name="In Progress", position=1),
        ColumnRow(id="col-6", board_id=b2.id, name="Done", position=2),
    ]
    for c in cols_b2:
        db.add(c)

    # ── Cards for Board 1 ──────────────────────────────────────────
    card_defs_b1 = [
        {
            "id": "card-1", "column_id": "col-1", "title": "Draft landing page copy",
            "description": "Short punchy hero and three benefits.",
            "assignee_name": "Alice", "assignee_color": "#0f766e",
            "due_date": date(2026, 9, 18), "priority": Priority.high.value, "position": 0,
        },
        {
            "id": "card-2", "column_id": "col-1", "title": "Design email template",
            "description": "Responsive HTML email for launch announcement.",
            "assignee_name": "Bob", "assignee_color": "#7c3aed",
            "due_date": date(2026, 9, 20), "priority": Priority.medium.value, "position": 1,
        },
        {
            "id": "card-3", "column_id": "col-2", "title": "Set up CI/CD pipeline",
            "description": "GitHub Actions workflow for staging deploys.",
            "assignee_name": "Charlie", "assignee_color": "#dc2626",
            "due_date": date(2026, 9, 16), "priority": Priority.high.value, "position": 0,
        },
        {
            "id": "card-4", "column_id": "col-3", "title": "Create logo variants",
            "description": "Dark, light, and monochrome versions.",
            "assignee_name": "Alice", "assignee_color": "#0f766e",
            "due_date": None, "priority": Priority.low.value, "position": 0,
        },
    ]

    for d in card_defs_b1:
        db.add(CardRow(**d, created_at=ts, updated_at=ts))

    # ── Cards for Board 2 ──────────────────────────────────────────
    card_defs_b2 = [
        {
            "id": "card-5", "column_id": "col-4", "title": "Login page 500 error",
            "description": "Intermittent server error on /login when session expired.",
            "assignee_name": "Diana", "assignee_color": "#ea580c",
            "due_date": date(2026, 9, 15), "priority": Priority.high.value, "position": 0,
        },
        {
            "id": "card-6", "column_id": "col-4", "title": "Dashboard chart tooltip cut off",
            "description": "Tooltip overflows container on narrow viewports.",
            "assignee_name": None, "assignee_color": None,
            "due_date": None, "priority": Priority.low.value, "position": 1,
        },
        {
            "id": "card-7", "column_id": "col-5", "title": "Fix password reset flow",
            "description": "Token expiry not checked correctly.",
            "assignee_name": "Bob", "assignee_color": "#7c3aed",
            "due_date": date(2026, 9, 17), "priority": Priority.medium.value, "position": 0,
        },
        {
            "id": "card-8", "column_id": "col-6", "title": "Update API rate limiter",
            "description": "Switched to sliding window algorithm.",
            "assignee_name": "Charlie", "assignee_color": "#dc2626",
            "due_date": None, "priority": Priority.medium.value, "position": 0,
        },
    ]

    for d in card_defs_b2:
        db.add(CardRow(**d, created_at=ts, updated_at=ts))

    # ── Labels ─────────────────────────────────────────────────────
    label_defs = [
        {"id": "lbl-1", "board_id": "board-1", "name": "Feature", "color": "#3b82f6"},
        {"id": "lbl-2", "board_id": "board-1", "name": "Design", "color": "#a855f7"},
        {"id": "lbl-3", "board_id": "board-1", "name": "Urgent", "color": "#ef4444"},
        {"id": "lbl-4", "board_id": "board-2", "name": "Bug", "color": "#ef4444"},
        {"id": "lbl-5", "board_id": "board-2", "name": "Backend", "color": "#22c55e"},
    ]
    for d in label_defs:
        db.add(LabelRow(**d))

    # ── Card ↔ Label associations ──────────────────────────────────
    card_label_defs = [
        ("card-1", "lbl-1"),
        ("card-1", "lbl-3"),
        ("card-2", "lbl-2"),
        ("card-3", "lbl-1"),
        ("card-5", "lbl-4"),
        ("card-5", "lbl-5"),
        ("card-7", "lbl-4"),
        ("card-8", "lbl-5"),
    ]
    for cid, lid in card_label_defs:
        db.add(CardLabelRow(card_id=cid, label_id=lid))

    db.commit()
