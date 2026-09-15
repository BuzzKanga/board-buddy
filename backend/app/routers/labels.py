"""Labels router — CRUD for labels and card↔label associations."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.engine import get_db
from app.db.models import BoardRow, CardLabelRow, CardRow, LabelRow
from app.db.serializers import label_to_pydantic
from app.models import ErrorResponse, Label, LabelCreate

router = APIRouter(tags=["Labels"])


# ── Label CRUD ──────────────────────────────────────────────────────────


@router.post(
    "/boards/{boardId}/labels",
    response_model=Label,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
def create_label(
    boardId: str,
    body: LabelCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Label:
    board = db.get(BoardRow, boardId)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    label = LabelRow(
        id=str(uuid.uuid4()),
        board_id=boardId,
        name=body.name,
        color=body.color,
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label_to_pydantic(label)


@router.delete(
    "/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_label(
    labelId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    label = db.get(LabelRow, labelId)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    db.delete(label)
    db.commit()


# ── Card ↔ Label ────────────────────────────────────────────────────────


@router.put(
    "/cards/{cardId}/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def attach_label_to_card(
    cardId: str,
    labelId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    card = db.get(CardRow, cardId)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    label = db.get(LabelRow, labelId)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    # Idempotent — don't add if already attached
    existing = (
        db.query(CardLabelRow)
        .filter(CardLabelRow.card_id == cardId, CardLabelRow.label_id == labelId)
        .first()
    )
    if not existing:
        assoc = CardLabelRow(card_id=cardId, label_id=labelId)
        db.add(assoc)
        db.commit()


@router.delete(
    "/cards/{cardId}/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def remove_label_from_card(
    cardId: str,
    labelId: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    card = db.get(CardRow, cardId)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    label = db.get(LabelRow, labelId)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    assoc = (
        db.query(CardLabelRow)
        .filter(CardLabelRow.card_id == cardId, CardLabelRow.label_id == labelId)
        .first()
    )
    if assoc:
        db.delete(assoc)
        db.commit()
