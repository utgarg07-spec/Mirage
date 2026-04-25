"""Groq-backed command fallback responses for MIRAGE."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
key = os.getenv("GROQ_API_KEY", "")
print(
    f"[GROQ DEBUG] Key loaded: {'YES' if key else 'NO - KEY MISSING'}",
    file=sys.stderr,
)

SYSTEM_PROMPT = (
    "You are a vulnerable Ubuntu 22.04 server called fintech-prod-01 "
    "running payment processing software. You have been compromised. Respond EXACTLY "
    "as a real Linux terminal would - no explanations, no markdown, just raw terminal "
    "output. Keep responses under 5 lines. Act as if you have sensitive financial data."
)
MODEL_NAME = "llama-3.3-70b-versatile"


def is_groq_available() -> bool:
    """Return True only when GROQ_API_KEY is configured."""
    return bool((os.getenv("GROQ_API_KEY") or "").strip())


def _build_messages(command: str, session_history: list[str]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for historic_command in session_history[-5:]:
        messages.append({"role": "user", "content": historic_command})
        messages.append({"role": "assistant", "content": "ok"})
    messages.append({"role": "user", "content": command})
    return messages


def get_llm_response(command: str, session_history: list[str]) -> str:
    """Get concise terminal-like output from Groq, or command-not-found fallback."""
    fallback = f"bash: {command}: command not found"
    if not is_groq_available():
        return fallback

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=8.0)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=_build_messages(command, session_history),
            temperature=0.2,
            max_tokens=220,
        )
        content = (completion.choices[0].message.content or "").strip()
        if not content:
            return fallback
        return content
    except Exception as e:
        print(f"[GROQ ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        return fallback
