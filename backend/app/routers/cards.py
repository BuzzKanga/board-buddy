"""Cards router — create, update/move, delete cards."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.engine import get_db
from app.db.models import CardRow, ColumnRow
from app.db.serializers import card_to_pydantic
from app.models import Card, CardCreate, CardUpdate, ErrorResponse, Priority

router = APIRouter(tags=["Cards"])


def _cards_in_column(db: Session, column_id: str) -> list[CardRow]:
    """Return cards in a column sorted by position."""
    return (
        db.query(CardRow)
        .filter(CardRow.column_id == column_id)
        .order_by(CardRow.position.asc())
        .all()
    )


def _reindex_cards(db: Session, column_id: str) -> None:
    """Re-index positions 0..n for cards in a column."""
    for i, card in enumerate(_cards_in_column(db, column_id)):
        card.position = i
    db.flush()


@router.post(
    "/columns/{columnId}/cards",
    response_model=Card,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
def create_card(
    columnId: str,
    body: CardCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Card:
    col = db.get(ColumnRow, columnId)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    title = (body.title or "").strip()
    if not title:
        title = "Untitled card"

    now = datetime.now(timezone.utc)
    siblings = _cards_in_column(db, columnId)

    priority_val = body.priority.value if body.priority else Priority.medium.value

    card = CardRow(
        id=str(uuid.uuid4()),
        column_id=columnId,
        title=title,
        description=body.description or "",
        assignee_name=body.assignee_name,
        assignee_color=body.assignee_color,
        due_date=body.due_date,
        priority=priority_val,
        position=len(siblings),
        created_at=now,
        updated_at=now,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card_to_pydantic(card)


@router.patch(
    "/cards/{cardId}",
    response_model=Card,
    responses={404: {"model": ErrorResponse}},
)
def update_card(
    cardId: str,
    body: CardUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Card:
    card = db.get(CardRow, cardId)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    now = datetime.now(timezone.utc)
    card.updated_at = now

    for field in ("title", "description", "assignee_name", "assignee_color", "due_date"):
        val = getattr(body, field, None)
        if val is not None:
            setattr(card, field, val)

    if body.priority is not None:
        card.priority = body.priority.value

    # Handle move / reorder
    target_column_id = body.column_id if body.column_id is not None else card.column_id
    target_position = body.position

    target_col = db.get(ColumnRow, target_column_id)
    if not target_col:
        raise HTTPException(status_code=404, detail="Target column not found")

    moving = target_column_id != card.column_id or target_position is not None

    if moving:
        old_column_id = card.column_id

        # Remove card from old column
        old_siblings = [c for c in _cards_in_column(db, old_column_id) if c.id != cardId]
        for i, c in enumerate(old_siblings):
            c.position = i

        # Determine target position in new column
        new_siblings = [c for c in _cards_in_column(db, target_column_id) if c.id != cardId]
        if target_position is None:
            target_position = len(new_siblings)
        else:
            target_position = min(target_position, len(new_siblings))

        card.column_id = target_column_id
        card.position = target_position

        new_siblings.insert(target_position, card)
        for i, c in enumerate(new_siblings):
            c.position = i

    db.commit()
    db.refresh(card)
    return card_to_pydantic(card)


@router.delete(
    "/cards/{cardId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_card(
    cardId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    card = db.get(CardRow, cardId)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    col_id = card.column_id
    db.delete(card)
    db.flush()

    _reindex_cards(db, col_id)
    db.commit()
