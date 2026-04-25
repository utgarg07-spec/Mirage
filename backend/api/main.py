from __future__ import annotations

import asyncio
import os
import sys
import threading
import traceback
from contextlib import suppress
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.event_broadcaster import init_broadcaster
from api.websocket_manager import manager
from blockchain.web3_handler import Web3Handler
from honeypot.server import start_server
from honeypot.session_logger import get_session, get_sessions
from intelligence.mitre_predictor import MitrePredictor

app = FastAPI(title="MIRAGE API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

honeypot_thread: threading.Thread = threading.Thread()


def _commands_only(session: dict[str, Any] | None) -> list[str]:
    if not session:
        return []
    commands_run = session.get("commands_run") or []
    commands: list[str] = []
    for entry in commands_run:
        cmd = (entry or {}).get("command")
        if isinstance(cmd, str) and cmd and cmd != "__error__":
            commands.append(cmd)
    return commands


@app.on_event("startup")
async def startup():
    try:
        print("[MIRAGE] Starting up...")

        # Step 1 - Web3
        app.state.web3 = Web3Handler()
        print("[MIRAGE] Web3 initialized")

        # Step 2 - MITRE Predictor
        app.state.predictor = MitrePredictor()
        print("[MIRAGE] MITRE predictor initialized")

        # Step 3 - Event broadcaster
        loop = asyncio.get_running_loop()
        init_broadcaster(loop, manager)
        print("[MIRAGE] Event broadcaster initialized")

        # Step 4 - Start honeypot thread
        global honeypot_thread
        t = threading.Thread(target=start_server, daemon=True)
        t.start()
        honeypot_thread = t
        print("[MIRAGE] All systems started")

    except Exception as e:
        print(f"[MIRAGE STARTUP ERROR] {e}")
        traceback.print_exc()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "honeypot_thread_alive": True,
        "web3_available": app.state.web3.available,
        "web3_reason": "",
        "mitre_stages": ["reconnaissance", "initial_access", "execution", 
                         "privilege_escalation", "collection", 
                         "exfiltration", "impact"]
    }


@app.get("/sessions")
def list_sessions(limit: int = 100, offset: int = 0, active_only: bool | None = None) -> dict[str, Any]:
    return {"sessions": get_sessions(limit=limit, offset=offset, active_only=active_only)}


@app.get("/sessions/{session_id}")
def session_detail(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session


@app.get("/sessions/{session_id}/prediction")
def session_prediction(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    commands = _commands_only(session)
    return app.state.predictor.predict(commands)


@app.post("/sessions/{session_id}/register")
def register_session_threat(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    commands = _commands_only(session)
    pred = app.state.predictor.predict(commands)

    stage = pred.get("current_stage", "reconnaissance")
    skill_level = int(pred.get("skill_level", 1))
    ip = session.get("ip_address") or "unknown"

    result = app.state.web3.register_threat(ip, commands, stage, skill_level)
    payload: dict[str, Any] = {"prediction": pred, "blockchain": result}
    return payload


@app.get("/blockchain/status")
def blockchain_status() -> dict[str, Any]:
    return {"available": bool(getattr(app.state.web3, "available", False)), "reason": getattr(app.state.web3, "reason", "")}


@app.get("/blockchain/threats")
def blockchain_threats() -> dict[str, Any]:
    return {"threats": app.state.web3.get_all_threats()}


@app.get("/blockchain/threats/count")
async def blockchain_threat_count():
    return {"count": app.state.web3.get_threat_count()}


@app.get("/blockchain/check/{fingerprint_hex}")
def blockchain_check(fingerprint_hex: str) -> dict[str, Any]:
    return app.state.web3.check_threat(fingerprint_hex)


@app.post("/blockchain/alert")
def blockchain_alert(payload: dict[str, Any]) -> dict[str, Any]:
    fingerprint = str(payload.get("fingerprint", "")).strip()
    message = str(payload.get("message", "")).strip()
    if not fingerprint or not message:
        raise HTTPException(status_code=400, detail="fingerprint and message required")
    return app.state.web3.broadcast_alert(fingerprint, message)


@app.get("/forensics/{session_id}")
def forensics_report(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    commands = _commands_only(session)
    pred = app.state.predictor.predict(commands)

    return {
        "session": {
            "session_id": session.get("session_id"),
            "ip_address": session.get("ip_address"),
            "username_tried": session.get("username_tried"),
            "password_tried": session.get("password_tried"),
            "start_time": session.get("start_time"),
            "end_time": session.get("end_time"),
            "is_active": session.get("is_active"),
        },
        "command_count": len(commands),
        "mitre": pred,
        "honey_files": pred.get("honey_files", []),
        "technique_tags": pred.get("technique_tags", []),
        "last_commands": commands[-10:],
        "web3": {"available": bool(getattr(app.state.web3, "available", False)), "reason": getattr(app.state.web3, "reason", "")},
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial snapshot for UI hydration.
        await websocket.send_json({"type": "initial_state", "data": {"sessions": get_sessions(limit=50, offset=0)}})
        while True:
            try:
                # Wait for any message from client (ping), timeout after 30s
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text('{"type":"ping"}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

