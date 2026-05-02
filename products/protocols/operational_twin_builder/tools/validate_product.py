#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/operational_twin_model.md",
    "schemas/operational_twin.schema.json",
    "templates/hotel_delivery_robot_twin.yaml",
    "examples/hotel_delivery_robot_operational_twin.md",
    "tools/build_export_package.py",
    "deliverables/export_package_manifest.md",
]
MARKERS = ["facility_type:", "robot_type:", "zones:", "task_nodes:", "escalation_rules:", "failure_branches:", "safety_owner:"]

missing = [f for f in FILES if not (ROOT / f).exists()]
if missing:
    raise SystemExit("Missing:\n" + "\n".join(missing))
text = (ROOT / "templates/hotel_delivery_robot_twin.yaml").read_text(encoding="utf-8")
absent = [m for m in MARKERS if m not in text]
if absent:
    raise SystemExit("Missing markers: " + ", ".join(absent))
print("Operational Twin Builder validation passed.")
