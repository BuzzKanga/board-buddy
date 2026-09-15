"""SQLAlchemy ORM models for Board Buddy."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.engine import Base
from app.models import Priority


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BoardRow(Base):
    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    columns: Mapped[list[ColumnRow]] = relationship(
        "ColumnRow",
        back_populates="board",
        cascade="all, delete-orphan",
        order_by="ColumnRow.position",
    )
    labels: Mapped[list[LabelRow]] = relationship(
        "LabelRow",
        back_populates="board",
        cascade="all, delete-orphan",
    )


class ColumnRow(Base):
    __tablename__ = "columns"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    board_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    board: Mapped[BoardRow] = relationship("BoardRow", back_populates="columns")
    cards: Mapped[list[CardRow]] = relationship(
        "CardRow",
        back_populates="column",
        cascade="all, delete-orphan",
        order_by="CardRow.position",
    )


class CardRow(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    column_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assignee_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assignee_color: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default=Priority.medium.value)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    column: Mapped[ColumnRow] = relationship("ColumnRow", back_populates="cards")
    card_labels: Mapped[list[CardLabelRow]] = relationship(
        "CardLabelRow",
        back_populates="card",
        cascade="all, delete-orphan",
    )


class LabelRow(Base):
    __tablename__ = "labels"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    board_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(32), nullable=False)

    board: Mapped[BoardRow] = relationship("BoardRow", back_populates="labels")
    card_labels: Mapped[list[CardLabelRow]] = relationship(
        "CardLabelRow",
        back_populates="label",
        cascade="all, delete-orphan",
    )


class CardLabelRow(Base):
    __tablename__ = "card_labels"

    card_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True
    )
    label_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True
    )

    card: Mapped[CardRow] = relationship("CardRow", back_populates="card_labels")
    label: Mapped[LabelRow] = relationship("LabelRow", back_populates="card_labels")
