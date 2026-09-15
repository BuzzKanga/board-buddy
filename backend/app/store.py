"""In-memory data store and seed data for Board Buddy."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.models import (
    Board,
    Card,
    CardLabel,
    Column,
    Label,
    Priority,
)

# ── Global stores (dictionaries keyed by id) ───────────────────────────

boards: dict[str, Board] = {}
columns: dict[str, Column] = {}
cards: dict[str, Card] = {}
labels: dict[str, Label] = {}
card_labels: list[CardLabel] = []



def _now() -> datetime:
    return datetime.now(timezone.utc)


def clear() -> None:
    """Wipe all data — used by tests."""
    boards.clear()
    columns.clear()
    cards.clear()
    labels.clear()
    card_labels.clear()


def seed_data() -> None:
    """Populate stores with demo data."""
    clear()


    ts = datetime(2026, 9, 12, 1, 0, 0, tzinfo=timezone.utc)

    # ── Board 1: Product Launch ─────────────────────────────────────
    b1 = Board(id="board-1", name="Product Launch", created_at=ts)
    boards[b1.id] = b1

    cols_b1 = [
        Column(id="col-1", board_id=b1.id, name="To Do", position=0),
        Column(id="col-2", board_id=b1.id, name="In Progress", position=1),
        Column(id="col-3", board_id=b1.id, name="Done", position=2),
    ]
    for c in cols_b1:
        columns[c.id] = c

    # ── Board 2: Bug Tracker ────────────────────────────────────────
    b2 = Board(id="board-2", name="Bug Tracker", created_at=ts)
    boards[b2.id] = b2

    cols_b2 = [
        Column(id="col-4", board_id=b2.id, name="To Do", position=0),
        Column(id="col-5", board_id=b2.id, name="In Progress", position=1),
        Column(id="col-6", board_id=b2.id, name="Done", position=2),
    ]
    for c in cols_b2:
        columns[c.id] = c

    # ── Cards for Board 1 ──────────────────────────────────────────
    card_defs_b1 = [
        {
            "id": "card-1", "column_id": "col-1", "title": "Draft landing page copy",
            "description": "Short punchy hero and three benefits.",
            "assignee_name": "Alice", "assignee_color": "#0f766e",
            "due_date": date(2026, 9, 18), "priority": Priority.high, "position": 0,
        },
        {
            "id": "card-2", "column_id": "col-1", "title": "Design email template",
            "description": "Responsive HTML email for launch announcement.",
            "assignee_name": "Bob", "assignee_color": "#7c3aed",
            "due_date": date(2026, 9, 20), "priority": Priority.medium, "position": 1,
        },
        {
            "id": "card-3", "column_id": "col-2", "title": "Set up CI/CD pipeline",
            "description": "GitHub Actions workflow for staging deploys.",
            "assignee_name": "Charlie", "assignee_color": "#dc2626",
            "due_date": date(2026, 9, 16), "priority": Priority.high, "position": 0,
        },
        {
            "id": "card-4", "column_id": "col-3", "title": "Create logo variants",
            "description": "Dark, light, and monochrome versions.",
            "assignee_name": "Alice", "assignee_color": "#0f766e",
            "due_date": None, "priority": Priority.low, "position": 0,
        },
    ]

    for d in card_defs_b1:
        cards[d["id"]] = Card(**d, created_at=ts, updated_at=ts)

    # ── Cards for Board 2 ──────────────────────────────────────────
    card_defs_b2 = [
        {
            "id": "card-5", "column_id": "col-4", "title": "Login page 500 error",
            "description": "Intermittent server error on /login when session expired.",
            "assignee_name": "Diana", "assignee_color": "#ea580c",
            "due_date": date(2026, 9, 15), "priority": Priority.high, "position": 0,
        },
        {
            "id": "card-6", "column_id": "col-4", "title": "Dashboard chart tooltip cut off",
            "description": "Tooltip overflows container on narrow viewports.",
            "assignee_name": None, "assignee_color": None,
            "due_date": None, "priority": Priority.low, "position": 1,
        },
        {
            "id": "card-7", "column_id": "col-5", "title": "Fix password reset flow",
            "description": "Token expiry not checked correctly.",
            "assignee_name": "Bob", "assignee_color": "#7c3aed",
            "due_date": date(2026, 9, 17), "priority": Priority.medium, "position": 0,
        },
        {
            "id": "card-8", "column_id": "col-6", "title": "Update API rate limiter",
            "description": "Switched to sliding window algorithm.",
            "assignee_name": "Charlie", "assignee_color": "#dc2626",
            "due_date": None, "priority": Priority.medium, "position": 0,
        },
    ]

    for d in card_defs_b2:
        cards[d["id"]] = Card(**d, created_at=ts, updated_at=ts)

    # ── Labels ─────────────────────────────────────────────────────
    label_defs = [
        {"id": "lbl-1", "board_id": "board-1", "name": "Feature", "color": "#3b82f6"},
        {"id": "lbl-2", "board_id": "board-1", "name": "Design", "color": "#a855f7"},
        {"id": "lbl-3", "board_id": "board-1", "name": "Urgent", "color": "#ef4444"},
        {"id": "lbl-4", "board_id": "board-2", "name": "Bug", "color": "#ef4444"},
        {"id": "lbl-5", "board_id": "board-2", "name": "Backend", "color": "#22c55e"},
    ]
    for d in label_defs:
        labels[d["id"]] = Label(**d)

    # ── Card ↔ Label associations ──────────────────────────────────
    card_labels.extend([
        CardLabel(card_id="card-1", label_id="lbl-1"),
        CardLabel(card_id="card-1", label_id="lbl-3"),
        CardLabel(card_id="card-2", label_id="lbl-2"),
        CardLabel(card_id="card-3", label_id="lbl-1"),
        CardLabel(card_id="card-5", label_id="lbl-4"),
        CardLabel(card_id="card-5", label_id="lbl-5"),
        CardLabel(card_id="card-7", label_id="lbl-4"),
        CardLabel(card_id="card-8", label_id="lbl-5"),
    ])
