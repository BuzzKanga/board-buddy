"""Labels router — CRUD for labels and card↔label associations."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import store
from app.auth import get_current_user
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
    _user: str = Depends(get_current_user),
) -> Label:
    if boardId not in store.boards:
        raise HTTPException(status_code=404, detail="Board not found")

    label = Label(
        id=str(uuid.uuid4()),
        board_id=boardId,
        name=body.name,
        color=body.color,
    )
    store.labels[label.id] = label
    return label


@router.delete(
    "/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_label(
    labelId: str,
    _user: str = Depends(get_current_user),
) -> None:
    label = store.labels.pop(labelId, None)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    # Remove all associations with this label
    store.card_labels[:] = [
        cl for cl in store.card_labels if cl.label_id != labelId
    ]


# ── Card ↔ Label ────────────────────────────────────────────────────────


@router.put(
    "/cards/{cardId}/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def attach_label_to_card(
    cardId: str,
    labelId: str,
    _user: str = Depends(get_current_user),
) -> None:
    if cardId not in store.cards:
        raise HTTPException(status_code=404, detail="Card not found")
    if labelId not in store.labels:
        raise HTTPException(status_code=404, detail="Label not found")

    # Idempotent — don't add if already attached
    already = any(
        cl.card_id == cardId and cl.label_id == labelId
        for cl in store.card_labels
    )
    if not already:
        from app.models import CardLabel
        store.card_labels.append(CardLabel(card_id=cardId, label_id=labelId))


@router.delete(
    "/cards/{cardId}/labels/{labelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def remove_label_from_card(
    cardId: str,
    labelId: str,
    _user: str = Depends(get_current_user),
) -> None:
    if cardId not in store.cards:
        raise HTTPException(status_code=404, detail="Card not found")
    if labelId not in store.labels:
        raise HTTPException(status_code=404, detail="Label not found")

    store.card_labels[:] = [
        cl for cl in store.card_labels
        if not (cl.card_id == cardId and cl.label_id == labelId)
    ]
