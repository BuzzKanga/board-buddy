"""Columns router — create, update, delete columns."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import store
from app.auth import get_current_user
from app.models import Column, ColumnCreate, ColumnUpdate, ErrorResponse

router = APIRouter(tags=["Columns"])


def _sibling_columns(board_id: str) -> list[Column]:
    """Return columns for a board sorted by position."""
    return sorted(
        [c for c in store.columns.values() if c.board_id == board_id],
        key=lambda c: c.position,
    )


def _reindex_columns(board_id: str) -> None:
    """Re-index positions 0..n for columns of a board."""
    for i, col in enumerate(_sibling_columns(board_id)):
        updated = col.model_copy(update={"position": i})
        store.columns[col.id] = updated


@router.post(
    "/boards/{boardId}/columns",
    response_model=Column,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
def create_column(
    boardId: str,
    body: ColumnCreate,
    _user: str = Depends(get_current_user),
) -> Column:
    if boardId not in store.boards:
        raise HTTPException(status_code=404, detail="Board not found")

    name = body.name.strip() if body.name else ""
    if not name:
        name = "New column"

    siblings = _sibling_columns(boardId)
    position = len(siblings)

    col = Column(
        id=str(uuid.uuid4()),
        board_id=boardId,
        name=name,
        position=position,
    )
    store.columns[col.id] = col
    return col


@router.patch(
    "/columns/{columnId}",
    response_model=Column,
    responses={404: {"model": ErrorResponse}},
)
def update_column(
    columnId: str,
    body: ColumnUpdate,
    _user: str = Depends(get_current_user),
) -> Column:
    col = store.columns.get(columnId)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    updates: dict = {}
    if body.name is not None:
        updates["name"] = body.name

    if body.position is not None and body.position != col.position:
        board_id = col.board_id
        siblings = _sibling_columns(board_id)
        new_pos = min(body.position, len(siblings) - 1)

        # Remove from current position and insert at new
        ordered = [c for c in siblings if c.id != columnId]
        updated_col = col.model_copy(update={**updates, "position": new_pos})
        ordered.insert(new_pos, updated_col)

        for i, c in enumerate(ordered):
            store.columns[c.id] = c.model_copy(update={"position": i})

        return store.columns[columnId]

    if updates:
        col = col.model_copy(update=updates)
        store.columns[columnId] = col

    return col


@router.delete(
    "/columns/{columnId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_column(
    columnId: str,
    _user: str = Depends(get_current_user),
) -> None:
    col = store.columns.pop(columnId, None)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    # Delete cards in this column and their label associations
    card_ids = [c.id for c in store.cards.values() if c.column_id == columnId]
    for cid in card_ids:
        del store.cards[cid]

    card_id_set = set(card_ids)
    store.card_labels[:] = [
        cl for cl in store.card_labels if cl.card_id not in card_id_set
    ]

    # Reindex remaining sibling columns
    _reindex_columns(col.board_id)
