"""Boards router — CRUD for boards."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app import store
from app.auth import get_current_user
from app.models import (
    Board,
    BoardCreate,
    BoardDetail,
    BoardUpdate,
    CardLabel,
    Column,
    ErrorResponse,
)

router = APIRouter(tags=["Boards"])


@router.get("/boards", response_model=list[Board])
def list_boards(_user: str = Depends(get_current_user)) -> list[Board]:
    return sorted(store.boards.values(), key=lambda b: b.created_at)


@router.post("/boards", response_model=Board, status_code=status.HTTP_201_CREATED)
def create_board(
    body: BoardCreate,
    _user: str = Depends(get_current_user),
) -> Board:
    name = body.name.strip() if body.name else ""
    if not name:
        name = "Untitled board"

    board = Board(
        id=str(uuid.uuid4()),
        name=name,
        created_at=datetime.now(timezone.utc),
    )
    store.boards[board.id] = board

    # Create three default columns
    for i, col_name in enumerate(["To Do", "In Progress", "Done"]):
        col = Column(
            id=str(uuid.uuid4()),
            board_id=board.id,
            name=col_name,
            position=i,
        )
        store.columns[col.id] = col

    return board


@router.get(
    "/boards/{boardId}",
    response_model=BoardDetail,
    responses={404: {"model": ErrorResponse}},
)
def get_board(
    boardId: str,
    _user: str = Depends(get_current_user),
) -> BoardDetail:
    board = store.boards.get(boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    board_columns = sorted(
        [c for c in store.columns.values() if c.board_id == boardId],
        key=lambda c: c.position,
    )
    column_ids = {c.id for c in board_columns}
    board_cards = sorted(
        [c for c in store.cards.values() if c.column_id in column_ids],
        key=lambda c: c.position,
    )
    board_labels = [l for l in store.labels.values() if l.board_id == boardId]
    card_ids = {c.id for c in board_cards}
    board_card_labels = [
        cl for cl in store.card_labels
        if cl.card_id in card_ids
    ]

    return BoardDetail(
        id=board.id,
        name=board.name,
        created_at=board.created_at,
        columns=board_columns,
        cards=board_cards,
        labels=board_labels,
        card_labels=board_card_labels,
    )


@router.patch(
    "/boards/{boardId}",
    response_model=Board,
    responses={404: {"model": ErrorResponse}},
)
def update_board(
    boardId: str,
    body: BoardUpdate,
    _user: str = Depends(get_current_user),
) -> Board:
    board = store.boards.get(boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if body.name is not None:
        board = board.model_copy(update={"name": body.name})
        store.boards[boardId] = board

    return board


@router.delete(
    "/boards/{boardId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_board(
    boardId: str,
    _user: str = Depends(get_current_user),
) -> None:
    board = store.boards.pop(boardId, None)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Cascade: delete columns, cards, labels, and card-label associations
    col_ids = [c.id for c in store.columns.values() if c.board_id == boardId]
    for cid in col_ids:
        del store.columns[cid]

    card_ids = [c.id for c in store.cards.values() if c.column_id in set(col_ids)]
    for cid in card_ids:
        del store.cards[cid]

    label_ids = [l.id for l in store.labels.values() if l.board_id == boardId]
    for lid in label_ids:
        del store.labels[lid]

    card_id_set = set(card_ids)
    label_id_set = set(label_ids)
    store.card_labels[:] = [
        cl for cl in store.card_labels
        if cl.card_id not in card_id_set and cl.label_id not in label_id_set
    ]
