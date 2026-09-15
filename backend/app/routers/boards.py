"""Boards router — CRUD for boards."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.engine import get_db
from app.db.models import BoardRow, CardLabelRow, CardRow, ColumnRow, LabelRow
from app.db.serializers import (
    board_to_pydantic,
    card_label_to_pydantic,
    card_to_pydantic,
    column_to_pydantic,
    label_to_pydantic,
)
from app.models import (
    Board,
    BoardCreate,
    BoardDetail,
    BoardUpdate,
    ErrorResponse,
)

router = APIRouter(tags=["Boards"])


@router.get("/boards", response_model=list[Board])
def list_boards(
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> list[Board]:
    boards = db.query(BoardRow).order_by(BoardRow.created_at.asc()).all()
    return [board_to_pydantic(b) for b in boards]


@router.post("/boards", response_model=Board, status_code=status.HTTP_201_CREATED)
def create_board(
    body: BoardCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Board:
    name = body.name.strip() if body.name else ""
    if not name:
        name = "Untitled board"

    board_id = str(uuid.uuid4())
    board = BoardRow(
        id=board_id,
        name=name,
        created_at=datetime.now(timezone.utc),
    )
    db.add(board)

    # Create three default columns
    for i, col_name in enumerate(["To Do", "In Progress", "Done"]):
        col = ColumnRow(
            id=str(uuid.uuid4()),
            board_id=board_id,
            name=col_name,
            position=i,
        )
        db.add(col)

    db.commit()
    db.refresh(board)
    return board_to_pydantic(board)


@router.get(
    "/boards/{boardId}",
    response_model=BoardDetail,
    responses={404: {"model": ErrorResponse}},
)
def get_board(
    boardId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> BoardDetail:
    board = db.get(BoardRow, boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    columns = (
        db.query(ColumnRow)
        .filter(ColumnRow.board_id == boardId)
        .order_by(ColumnRow.position.asc())
        .all()
    )
    column_ids = [c.id for c in columns]

    cards = (
        db.query(CardRow)
        .filter(CardRow.column_id.in_(column_ids))
        .order_by(CardRow.position.asc())
        .all()
        if column_ids
        else []
    )
    card_ids = [c.id for c in cards]

    labels = (
        db.query(LabelRow)
        .filter(LabelRow.board_id == boardId)
        .all()
    )

    card_labels = (
        db.query(CardLabelRow)
        .filter(CardLabelRow.card_id.in_(card_ids))
        .all()
        if card_ids
        else []
    )

    p_board = board_to_pydantic(board)
    return BoardDetail(
        id=p_board.id,
        name=p_board.name,
        created_at=p_board.created_at,
        columns=[column_to_pydantic(c) for c in columns],
        cards=[card_to_pydantic(c) for c in cards],
        labels=[label_to_pydantic(l) for l in labels],
        card_labels=[card_label_to_pydantic(cl) for cl in card_labels],
    )


@router.patch(
    "/boards/{boardId}",
    response_model=Board,
    responses={404: {"model": ErrorResponse}},
)
def update_board(
    boardId: str,
    body: BoardUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Board:
    board = db.get(BoardRow, boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if body.name is not None:
        board.name = body.name
        db.commit()
        db.refresh(board)

    return board_to_pydantic(board)


@router.delete(
    "/boards/{boardId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_board(
    boardId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    board = db.get(BoardRow, boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    db.delete(board)
    db.commit()
