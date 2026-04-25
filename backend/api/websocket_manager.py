from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from fastapi import WebSocket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def _disconnect_async(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Best-effort sync disconnect so call sites don't need `await`.
        Safe to call from async contexts (schedules a task).
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self._disconnect_async(websocket))

    async def broadcast_json(self, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections)
        if not connections:
            return
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                await self._disconnect_async(ws)


# Shared singleton used by the API.
manager = ConnectionManager()

