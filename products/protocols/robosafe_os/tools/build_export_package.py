#!/usr/bin/env python3
"""Build a deterministic sample buyer export package for RoboSafeOS."""
from __future__ import annotations

import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "hotel_service_robot"
DELIVERABLES_DIR = ROOT / "deliverables"
EXPORT_PATH = DELIVERABLES_DIR / "robosafe-os-sample-export.zip"

PACKAGE_FILES = [
    "README.md",
    "manifest.yaml",
    "RULES.yaml",
    "QA_REPORT.md",
    "docs/buyer_overview.md",
    "docs/deployment_workflow.md",
    "docs/limitations.md",
    "schemas/intake.schema.json",
    "schemas/routing_rules.schema.json",
    "schemas/incident_log.schema.json",
    "templates/safety_policy_template.md",
    "templates/human_review_plan_template.md",
    "examples/hotel_service_robot/intake.json",
    "examples/hotel_service_robot/routing_rules.json",
    "examples/hotel_service_robot/incident_log_template.csv",
    "examples/hotel_service_robot/generated_safety_policy.md",
    "examples/hotel_service_robot/generated_human_review_plan.md",
    "simulation/browser_facility_demo.html",
    "deliverables/export_package_manifest.md",
]


def load_intake() -> dict:
    return json.loads((EXAMPLE_DIR / "intake.json").read_text(encoding="utf-8"))


def load_routing() -> dict:
    return json.loads((EXAMPLE_DIR / "routing_rules.json").read_text(encoding="utf-8"))


def render_safety_policy() -> str:
    intake = load_intake()
    zones = "\n".join(
        f"- {zone['zone_id']}: {zone['name']} | access={zone['access_type']} | "
        f"traffic={zone['traffic_level']} | risk={zone['risk_level']} | notes={zone.get('notes', '')}"
        for zone in intake["zones"]
    )
    restricted = "\n".join(f"- {area}" for area in intake["restricted_areas"])
    traffic = "\n".join(
        f"- {item['time_window']}: {item['traffic_level']} traffic in {', '.join(item['affected_zones'])}"
        for item in intake["human_traffic_patterns"]
    )
    tasks = "\n".join(
        f"- {task['task_id']}: {task['task_name']} | window={task['preferred_time_window']} | "
        f"zones={', '.join(task['zones'])} | staff_review={task.get('requires_human_review', False)}"
        for task in intake["task_schedule"]
    )
    return f"""# RoboSafeOS Generated Facility Policy

Generated: {datetime.now(timezone.utc).isoformat()}
Facility: {intake.get('facility_name', 'Unnamed facility')}
Facility type: {intake['facility_type']}
Robot type: {intake['robot_type']}
Country: {intake.get('country', 'not specified')}

## 1. Facility zones

{zones}

## 2. Exclusion areas

{restricted}

## 3. Traffic windows

{traffic}

## 4. Task schedule

{tasks}

## 5. Package boundary

This document is generated from buyer-provided planning inputs. It is a review artifact for facility, vendor, and integrator discussion. It does not certify a physical deployment or replace site engineering review.
"""


def render_review_plan() -> str:
    intake = load_intake()
    routing = load_routing()
    rows = "\n".join(
        f"| {contact['role']} | {contact['contact_method']} | {contact.get('coverage_window', 'not specified')} | Review facility records and escalation notes. |"
        for contact in intake["escalation_contacts"]
    )
    conditions = "\n".join(f"- {condition}" for condition in routing["review_conditions"])
    return f"""# RoboSafeOS Generated Human Review Plan

Facility: {intake.get('facility_name', 'Unnamed facility')}
Facility type: {intake['facility_type']}
Robot type: {intake['robot_type']}

## 1. Review roles

| Role | Contact method | Coverage window | Responsibility |
| --- | --- | --- | --- |
{rows}

## 2. Review triggers

{conditions}

## 3. Scope note

This plan is a facility review artifact. It must be checked by the buyer, vendor, and qualified integrator before any physical site implementation.
"""


def ensure_generated_files() -> None:
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    (EXAMPLE_DIR / "generated_safety_policy.md").write_text(render_safety_policy(), encoding="utf-8")
    (EXAMPLE_DIR / "generated_human_review_plan.md").write_text(render_review_plan(), encoding="utf-8")


def validate_incident_csv() -> None:
    csv_path = EXAMPLE_DIR / "incident_log_template.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 2:
        raise RuntimeError("incident log CSV must include a header and one sample row")


def build_zip() -> None:
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(EXPORT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for relative_path in PACKAGE_FILES:
            source = ROOT / relative_path
            if not source.exists():
                raise FileNotFoundError(f"missing package file: {relative_path}")
            package.write(source, arcname=f"robosafe-os/{relative_path}")


def main() -> None:
    ensure_generated_files()
    validate_incident_csv()
    build_zip()
    print(f"Built {EXPORT_PATH}")


if __name__ == "__main__":
    main()
