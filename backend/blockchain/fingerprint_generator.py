"""Fingerprint and skill-level helpers for MIRAGE blockchain integration."""

from __future__ import annotations

import hashlib
import json


def generate_fingerprint(
    ip: str,
    command_sequence: list[str],
    timing_intervals: list[float] = None,
) -> str:
    """Build deterministic fingerprint from IP + command behavior features."""
    unique_commands = sorted(set(command_sequence))
    command_blob = " ".join(command_sequence).lower()

    technique = "generic"
    if any(token in command_blob for token in ("curl", "wget", "nc", "post", "scp")):
        technique = "exfiltration"
    elif any(token in command_blob for token in ("sudo", "su", "shadow", "uid=0")):
        technique = "privilege_escalation"
    elif any(token in command_blob for token in ("cat", "find", "grep", "ls")):
        technique = "collection"
    elif any(token in command_blob for token in ("ssh", "passwd", "password", "auth")):
        technique = "initial_access"
    elif any(token in command_blob for token in ("nmap", "ping", "traceroute", "whois")):
        technique = "reconnaissance"

    payload = {
        "ip": ip,
        "commands": unique_commands,
        "dominant_technique": technique,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"0x{digest}"


def calculate_skill_level(commands: list[str], stage_reached: str) -> int:
    """Estimate attacker skill level from reached stage."""
    from intelligence.mitre_predictor import MitrePredictor  # inline to avoid circular imports

    _ = MitrePredictor  # ensure import is used for linting and runtime linkage
    if stage_reached in ["collection", "exfiltration", "impact"]:
        return 3
    if stage_reached in ["execution", "privilege_escalation"]:
        return 2
    return 1
