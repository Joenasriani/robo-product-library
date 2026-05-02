#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/event_log_model.md",
    "schemas/robot_event.schema.json",
    "templates/robot_event_log_template.json",
    "examples/elevator_delay_incident_example.md",
    "tools/build_export_package.py",
    "deliverables/export_package_manifest.md",
]
FIELDS = ["robot_id", "event_time", "zone", "task_state", "review_signal", "action_taken", "human_override", "outcome", "reviewer"]
missing = [f for f in FILES if not (ROOT / f).exists()]
if missing:
    raise SystemExit("Missing:\n" + "\n".join(missing))
event = json.loads((ROOT / "templates/robot_event_log_template.json").read_text(encoding="utf-8"))
absent = [field for field in FIELDS if field not in event]
if absent:
    raise SystemExit("Template missing fields: " + ", ".join(absent))
print("Robot Behavior Black Box validation passed.")
