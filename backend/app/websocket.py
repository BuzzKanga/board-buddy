"""WebSocket broadcast hub for real-time board sync."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections grouped by board_id.

    - Board-scoped connections: keyed by board_id string
    - Global connections (board list): keyed by the sentinel "_global"
    """

    GLOBAL_KEY = "_global"

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, key: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(key, set()).add(ws)

    def disconnect(self, key: str, ws: WebSocket) -> None:
        conns = self._connections.get(key)
        if conns:
            conns.discard(ws)
            if not conns:
                del self._connections[key]

    async def broadcast(self, key: str, data: dict[str, Any]) -> None:
        """Send a JSON message to all connections on *key*."""
        conns = self._connections.get(key)
        if not conns:
            return
        message = json.dumps(data)
        # Send to all; remove broken connections
        broken: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                broken.append(ws)
        for ws in broken:
            conns.discard(ws)


manager = ConnectionManager()


def _get_board_id_for_column(column_id: str) -> str | None:
    """Look up the board_id that owns a column."""
    from app.db.engine import SessionLocal
    from app.db.models import ColumnRow

    with SessionLocal() as db:
        col = db.get(ColumnRow, column_id)
        return col.board_id if col else None


def _get_board_id_for_card(card_id: str) -> str | None:
    """Look up the board_id that owns a card (via its column)."""
    from app.db.engine import SessionLocal
    from app.db.models import CardRow

    with SessionLocal() as db:
        card = db.get(CardRow, card_id)
        if not card:
            return None
        return _get_board_id_for_column(card.column_id)


def _get_board_id_for_label(label_id: str) -> str | None:
    """Look up the board_id that owns a label."""
    from app.db.engine import SessionLocal
    from app.db.models import LabelRow

    with SessionLocal() as db:
        label = db.get(LabelRow, label_id)
        return label.board_id if label else None


async def notify_board_changed(board_id: str) -> None:
    """Broadcast a board_changed event to all clients watching this board."""
    await manager.broadcast(board_id, {"type": "board_changed", "board_id": board_id})


async def notify_boards_changed() -> None:
    """Broadcast a boards_changed event to all clients on the global channel."""
    await manager.broadcast(
        ConnectionManager.GLOBAL_KEY, {"type": "boards_changed"}
    )


def fire_board_changed(board_id: str) -> None:
    """Schedule a board_changed notification from sync code (routers)."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(notify_board_changed(board_id))
    except RuntimeError:
        pass  # No running loop — e.g. during tests


def fire_boards_changed() -> None:
    """Schedule a boards_changed notification from sync code (routers)."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(notify_boards_changed())
    except RuntimeError:
        pass


# ── WebSocket endpoints ────────────────────────────────────────────────


@router.websocket("/ws/boards/{boardId}")
async def ws_board(ws: WebSocket, boardId: str) -> None:
    """Per-board WebSocket — clients receive board_changed events."""
    await manager.connect(boardId, ws)
    try:
        while True:
            # Keep the connection alive; ignore any client messages
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(boardId, ws)


@router.websocket("/ws/boards")
async def ws_boards_global(ws: WebSocket) -> None:
    """Global WebSocket — clients receive boards_changed events."""
    await manager.connect(ConnectionManager.GLOBAL_KEY, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ConnectionManager.GLOBAL_KEY, ws)
