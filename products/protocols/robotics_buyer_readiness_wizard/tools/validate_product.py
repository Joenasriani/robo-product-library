#!/usr/bin/env python3
"""Validate Robotics Buyer Readiness Wizard product files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/readiness_model.md",
    "schemas/readiness_assessment.schema.json",
    "schemas/buyer_inquiry_packet.schema.json",
    "templates/hotel_readiness_assessment.json",
    "templates/warehouse_readiness_assessment.json",
    "examples/hotel_buyer_readiness_report.md",
    "deliverables/export_package_manifest.md",
]

REQUIRED_ASSESSMENT_FIELDS = [
    "facility_type",
    "robot_type",
    "zones",
    "human_traffic_patterns",
    "connectivity_status",
    "staff_support_model",
    "maintenance_capacity",
    "safety_review_owner",
    "budget_status",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(f"- {item}" for item in missing))

    for rel in ["templates/hotel_readiness_assessment.json", "templates/warehouse_readiness_assessment.json"]:
        data = load_json(ROOT / rel)
        absent = [field for field in REQUIRED_ASSESSMENT_FIELDS if field not in data]
        if absent:
            raise SystemExit(f"{rel} missing required fields: {', '.join(absent)}")
        if not isinstance(data.get("zones"), list) or not data["zones"]:
            raise SystemExit(f"{rel} must include at least one zone")

    schema = load_json(ROOT / "schemas/readiness_assessment.schema.json")
    if "required" not in schema or "properties" not in schema:
        raise SystemExit("readiness_assessment.schema.json must define required fields and properties")

    print("Robotics Buyer Readiness Wizard validation passed.")


if __name__ == "__main__":
    main()
