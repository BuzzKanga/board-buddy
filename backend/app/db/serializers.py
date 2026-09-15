"""Serializers converting SQLAlchemy ORM rows to Pydantic domain models."""

from __future__ import annotations

from datetime import datetime, timezone

from app.db.models import BoardRow, CardLabelRow, CardRow, ColumnRow, LabelRow
from app.models import Board, Card, CardLabel, Column, Label, Priority


def ensure_utc(dt: datetime | None) -> datetime | None:
    """Ensure a datetime object has UTC timezone information."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def board_to_pydantic(row: BoardRow) -> Board:
    return Board(
        id=row.id,
        name=row.name,
        created_at=ensure_utc(row.created_at),
    )


def column_to_pydantic(row: ColumnRow) -> Column:
    return Column(
        id=row.id,
        board_id=row.board_id,
        name=row.name,
        position=row.position,
    )


def card_to_pydantic(row: CardRow) -> Card:
    return Card(
        id=row.id,
        column_id=row.column_id,
        title=row.title,
        description=row.description,
        assignee_name=row.assignee_name,
        assignee_color=row.assignee_color,
        due_date=row.due_date,
        priority=Priority(row.priority),
        position=row.position,
        created_at=ensure_utc(row.created_at),
        updated_at=ensure_utc(row.updated_at),
    )


def label_to_pydantic(row: LabelRow) -> Label:
    return Label(
        id=row.id,
        board_id=row.board_id,
        name=row.name,
        color=row.color,
    )


def card_label_to_pydantic(row: CardLabelRow) -> CardLabel:
    return CardLabel(
        card_id=row.card_id,
        label_id=row.label_id,
    )
