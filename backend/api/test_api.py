from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

import websockets


BASE = "http://127.0.0.1:8000"
WS = "ws://127.0.0.1:8000/ws"


def _get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def _ws_sniff(seconds: int = 8) -> None:
    print(f"[TEST] connecting websocket {WS}")
    async with websockets.connect(WS, open_timeout=6) as ws:
        start = time.time()
        while time.time() - start < seconds:
            try:
                msg = await ws.recv()
                print(f"[WS] {msg}")
            except Exception:
                break


def main() -> None:
    try:
        print("[TEST] GET /health")
        print(json.dumps(_get("/health"), indent=2))
        print("[TEST] GET /sessions?limit=3")
        print(json.dumps(_get("/sessions?limit=3"), indent=2))
        print("[TEST] tip: run an SSH attacker while ws sniffing to see events.")
    except urllib.error.URLError as e:
        print(f"[TEST] API not reachable: {e}")


if __name__ == "__main__":
    main()

