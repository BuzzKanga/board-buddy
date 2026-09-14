"""Cards router — create, update/move, delete cards."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app import store
from app.auth import get_current_user
from app.models import Card, CardCreate, CardUpdate, ErrorResponse, Priority

router = APIRouter(tags=["Cards"])


def _cards_in_column(column_id: str) -> list[Card]:
    """Return cards in a column sorted by position."""
    return sorted(
        [c for c in store.cards.values() if c.column_id == column_id],
        key=lambda c: c.position,
    )


def _reindex_cards(column_id: str) -> None:
    """Re-index positions 0..n for cards in a column."""
    for i, card in enumerate(_cards_in_column(column_id)):
        store.cards[card.id] = card.model_copy(update={"position": i})


@router.post(
    "/columns/{columnId}/cards",
    response_model=Card,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
def create_card(
    columnId: str,
    body: CardCreate,
    _user: str = Depends(get_current_user),
) -> Card:
    if columnId not in store.columns:
        raise HTTPException(status_code=404, detail="Column not found")

    title = (body.title or "").strip()
    if not title:
        title = "Untitled card"

    now = datetime.now(timezone.utc)
    siblings = _cards_in_column(columnId)

    card = Card(
        id=str(uuid.uuid4()),
        column_id=columnId,
        title=title,
        description=body.description or "",
        assignee_name=body.assignee_name,
        assignee_color=body.assignee_color,
        due_date=body.due_date,
        priority=body.priority or Priority.medium,
        position=len(siblings),
        created_at=now,
        updated_at=now,
    )
    store.cards[card.id] = card
    return card


@router.patch(
    "/cards/{cardId}",
    response_model=Card,
    responses={404: {"model": ErrorResponse}},
)
def update_card(
    cardId: str,
    body: CardUpdate,
    _user: str = Depends(get_current_user),
) -> Card:
    card = store.cards.get(cardId)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    now = datetime.now(timezone.utc)

    # Collect simple field updates
    field_updates: dict = {"updated_at": now}
    for field in ("title", "description", "assignee_name", "assignee_color", "due_date", "priority"):
        value = getattr(body, field, None)
        if value is not None:
            field_updates[field] = value

    # Handle move / reorder
    target_column_id = body.column_id if body.column_id is not None else card.column_id
    target_position = body.position

    if target_column_id not in store.columns:
        raise HTTPException(status_code=404, detail="Target column not found")

    moving = target_column_id != card.column_id or target_position is not None

    if moving:
        old_column_id = card.column_id

        # Remove card from old column
        old_siblings = [c for c in _cards_in_column(old_column_id) if c.id != cardId]
        for i, c in enumerate(old_siblings):
            store.cards[c.id] = c.model_copy(update={"position": i})

        # Determine target position in new column
        new_siblings = [c for c in _cards_in_column(target_column_id) if c.id != cardId]
        if target_position is None:
            target_position = len(new_siblings)
        else:
            target_position = min(target_position, len(new_siblings))

        field_updates["column_id"] = target_column_id
        field_updates["position"] = target_position

        # Update the card
        card = card.model_copy(update=field_updates)
        store.cards[cardId] = card

        # Insert into new column and reindex
        new_siblings.insert(target_position, card)
        for i, c in enumerate(new_siblings):
            store.cards[c.id] = c.model_copy(update={"position": i})
    else:
        card = card.model_copy(update=field_updates)
        store.cards[cardId] = card

    return store.cards[cardId]


@router.delete(
    "/cards/{cardId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_card(
    cardId: str,
    _user: str = Depends(get_current_user),
) -> None:
    card = store.cards.pop(cardId, None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Remove label associations
    store.card_labels[:] = [
        cl for cl in store.card_labels if cl.card_id != cardId
    ]

    # Reindex remaining cards in the column
    _reindex_cards(card.column_id)
