"""Pydantic models for Board Buddy API."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ───────────────────────────────────────────────────────────────


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ── Domain models ───────────────────────────────────────────────────────


class Board(BaseModel):
    id: str
    name: str
    created_at: datetime


class Column(BaseModel):
    id: str
    board_id: str
    name: str
    position: int = Field(ge=0)


class Card(BaseModel):
    id: str
    column_id: str
    title: str
    description: str
    assignee_name: Optional[str] = None
    assignee_color: Optional[str] = None
    due_date: Optional[date] = None
    priority: Priority
    position: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class Label(BaseModel):
    id: str
    board_id: str
    name: str
    color: str


class CardLabel(BaseModel):
    card_id: str
    label_id: str


class BoardDetail(BaseModel):
    id: str
    name: str
    created_at: datetime
    columns: list[Column]
    cards: list[Card]
    labels: list[Label]
    card_labels: list[CardLabel]


# ── Request / response bodies ───────────────────────────────────────────


class BoardCreate(BaseModel):
    name: str = ""


class BoardUpdate(BaseModel):
    name: Optional[str] = None


class ColumnCreate(BaseModel):
    name: str = ""


class ColumnUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = Field(default=None, ge=0)


class CardCreate(BaseModel):
    title: Optional[str] = None
    description: str = ""
    assignee_name: Optional[str] = None
    assignee_color: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[Priority] = None


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    assignee_color: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[Priority] = None
    column_id: Optional[str] = None
    position: Optional[int] = Field(default=None, ge=0)


class LabelCreate(BaseModel):
    name: str
    color: str


class ErrorResponse(BaseModel):
    message: str


# ── Auth models ─────────────────────────────────────────────────────────


class User(BaseModel):
    id: str
    username: str
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
