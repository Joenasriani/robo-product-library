#!/usr/bin/env python3
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
    "templates/hotel_readiness_assessment.json",
    "examples/hotel_buyer_readiness_report.md",
    "tools/build_export_package.py",
    "deliverables/export_package_manifest.md",
]
REQUIRED_TEMPLATE_FIELDS = [
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


def main() -> None:
    missing = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(missing))
    data = json.loads((ROOT / "templates/hotel_readiness_assessment.json").read_text(encoding="utf-8"))
    missing_fields = [field for field in REQUIRED_TEMPLATE_FIELDS if field not in data]
    if missing_fields:
        raise SystemExit("Template missing fields: " + ", ".join(missing_fields))
    schema = json.loads((ROOT / "schemas/readiness_assessment.schema.json").read_text(encoding="utf-8"))
    if "required" not in schema or "properties" not in schema:
        raise SystemExit("Schema must define required fields and properties")
    print("Robotics Buyer Readiness Wizard validation passed.")


if __name__ == "__main__":
    main()
