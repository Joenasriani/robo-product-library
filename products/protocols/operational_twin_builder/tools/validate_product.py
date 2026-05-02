#!/usr/bin/env python3
"""Validate Operational Twin Builder product files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/operational_twin_model.md",
    "schemas/operational_twin.schema.json",
    "schemas/task_node.schema.json",
    "templates/hotel_delivery_robot_twin.yaml",
    "templates/warehouse_amr_twin.yaml",
    "examples/hotel_delivery_robot_operational_twin.md",
    "deliverables/export_package_manifest.md",
]

REQUIRED_TEMPLATE_MARKERS = [
    "facility_type:",
    "robot_type:",
    "zones:",
    "task_nodes:",
    "human_actor_roles:",
    "escalation_rules:",
    "failure_branches:",
    "safety_owner:",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(f"- {item}" for item in missing))

    for rel in ["templates/hotel_delivery_robot_twin.yaml", "templates/warehouse_amr_twin.yaml"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        absent = [marker for marker in REQUIRED_TEMPLATE_MARKERS if marker not in text]
        if absent:
            raise SystemExit(f"{rel} missing required markers: {', '.join(absent)}")

    schema = load_json(ROOT / "schemas/operational_twin.schema.json")
    if "required" not in schema or "properties" not in schema:
        raise SystemExit("operational_twin.schema.json must define required fields and properties")

    print("Operational Twin Builder validation passed.")


if __name__ == "__main__":
    main()
