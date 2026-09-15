"""Columns router — create, update, delete columns."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.engine import get_db
from app.db.models import BoardRow, ColumnRow
from app.db.serializers import column_to_pydantic
from app.models import Column, ColumnCreate, ColumnUpdate, ErrorResponse

router = APIRouter(tags=["Columns"])


def _sibling_columns(db: Session, board_id: str) -> list[ColumnRow]:
    """Return columns for a board sorted by position."""
    return (
        db.query(ColumnRow)
        .filter(ColumnRow.board_id == board_id)
        .order_by(ColumnRow.position.asc())
        .all()
    )


def _reindex_columns(db: Session, board_id: str) -> None:
    """Re-index positions 0..n for columns of a board."""
    for i, col in enumerate(_sibling_columns(db, board_id)):
        col.position = i
    db.flush()


@router.post(
    "/boards/{boardId}/columns",
    response_model=Column,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
def create_column(
    boardId: str,
    body: ColumnCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Column:
    board = db.get(BoardRow, boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    name = body.name.strip() if body.name else ""
    if not name:
        name = "New column"

    siblings = _sibling_columns(db, boardId)
    position = len(siblings)

    col = ColumnRow(
        id=str(uuid.uuid4()),
        board_id=boardId,
        name=name,
        position=position,
    )
    db.add(col)
    db.commit()
    db.refresh(col)
    return column_to_pydantic(col)


@router.patch(
    "/columns/{columnId}",
    response_model=Column,
    responses={404: {"model": ErrorResponse}},
)
def update_column(
    columnId: str,
    body: ColumnUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Column:
    col = db.get(ColumnRow, columnId)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    if body.name is not None:
        col.name = body.name

    if body.position is not None and body.position != col.position:
        board_id = col.board_id
        siblings = _sibling_columns(db, board_id)
        new_pos = min(body.position, len(siblings) - 1)

        ordered = [c for c in siblings if c.id != columnId]
        ordered.insert(new_pos, col)

        for i, c in enumerate(ordered):
            c.position = i

    db.commit()
    db.refresh(col)
    return column_to_pydantic(col)


@router.delete(
    "/columns/{columnId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_column(
    columnId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    col = db.get(ColumnRow, columnId)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    board_id = col.board_id
    db.delete(col)
    db.flush()

    _reindex_columns(db, board_id)
    db.commit()
