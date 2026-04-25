from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.websocket_manager import ConnectionManager


_loop: asyncio.AbstractEventLoop | None = None
_manager: ConnectionManager | None = None


def init_broadcaster(loop: asyncio.AbstractEventLoop, manager: ConnectionManager) -> None:
    global _loop, _manager
    _loop = loop
    _manager = manager


def publish(event: dict[str, Any]) -> None:
    """Publish from sync code into FastAPI loop (best-effort)."""
    if _loop is None or _manager is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(_manager.broadcast_json(event), _loop)
    except Exception:
        return


