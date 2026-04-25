"""Generate realistic staged honey files using Groq, with cache."""

from __future__ import annotations

from .groq_handler import get_llm_response


_HONEY_FILE_CACHE: dict[str, str] = {}


def generate_honey_file(filename: str, stage: str) -> str:
    """Generate and cache believable file content for a filename."""
    if filename in _HONEY_FILE_CACHE:
        return _HONEY_FILE_CACHE[filename]

    prompt = (
        "Generate realistic fake file contents for a FinTech payment processor server.\n"
        f"File: {filename}. Attack stage context: {stage}.\n"
        "Return ONLY the raw file contents, no explanation. Make it look like real\n"
        "sensitive financial data that an attacker would want to steal."
    )
    content = get_llm_response(prompt, [])
    if not content or "command not found" in content:
        content = (
            f"# {filename}\n"
            "# MIRAGE generated placeholder\n"
            "record_id,amount,currency,status\n"
            "MIR-001,12990.44,USD,settled\n"
        )

    _HONEY_FILE_CACHE[filename] = content
    return content
