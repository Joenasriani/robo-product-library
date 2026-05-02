#!/usr/bin/env python3
"""Validate Robot Behavior Black Box product files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/event_log_model.md",
    "schemas/robot_event.schema.json",
    "schemas/incident_report.schema.json",
    "templates/robot_event_log_template.json",
    "templates/incident_report_template.md",
    "examples/elevator_delay_incident_example.md",
    "deliverables/export_package_manifest.md",
]

REQUIRED_EVENT_FIELDS = [
    "robot_id",
    "event_time",
    "zone",
    "task_state",
    "review_signal",
    "action_taken",
    "human_override",
    "outcome",
    "reviewer",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(f"- {item}" for item in missing))

    event = load_json(ROOT / "templates/robot_event_log_template.json")
    absent = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if absent:
        raise SystemExit("robot_event_log_template.json missing fields: " + ", ".join(absent))

    schema = load_json(ROOT / "schemas/robot_event.schema.json")
    if "required" not in schema or "properties" not in schema:
        raise SystemExit("robot_event.schema.json must define required fields and properties")

    print("Robot Behavior Black Box validation passed.")


if __name__ == "__main__":
    main()
