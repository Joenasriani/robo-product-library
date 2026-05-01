#!/usr/bin/env python3
"""Local validation for the RoboSafeOS mini product repository.

This script intentionally uses only the Python standard library so a robotics
integrator or IT buyer can run it without installing project dependencies.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
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
    "tools/build_export_package.py",
    "tools/validate_product.py",
    "deliverables/export_package_manifest.md",
]

REQUIRED_INTAKE_FIELDS = {
    "facility_type",
    "robot_type",
    "zones",
    "restricted_areas",
    "human_traffic_patterns",
    "task_schedule",
    "escalation_contacts",
    "incident_severity_levels",
}

REQUIRED_ROUTING_FIELDS = {
    "facility_type",
    "robot_type",
    "zones",
    "allowed_routes",
    "restricted_routes",
    "review_conditions",
}

INCIDENT_HEADERS = [
    "incident_id",
    "timestamp",
    "robot_id",
    "zone",
    "task_id",
    "severity",
    "trigger",
    "human_involved",
    "review_used",
    "resolution",
    "evidence_notes",
    "follow_up_required",
    "follow_up_owner",
    "closed_at",
]

REQUIRED_DISCLOSURES = [
    "not a physics simulator",
    "does not ship a certified robot controller",
    "does not claim iso",
    "does not connect directly to robots without custom integration",
]

BANNED_AFFIRMATIVE_CLAIMS = [
    "guaranteed compliance",
    "iso certified product",
    "live robot control included",
    "certified safety runtime included",
]


def fail(message: str) -> None:
    print(f"RoboSafeOS validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {relative_path}: {exc}")


def assert_non_empty(relative_path: str) -> None:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing required file: {relative_path}")
    if path.stat().st_size == 0:
        fail(f"empty required file: {relative_path}")


def validate_required_files() -> None:
    for relative_path in REQUIRED_FILES:
        assert_non_empty(relative_path)


def validate_json_files() -> None:
    for relative_path in [
        "schemas/intake.schema.json",
        "schemas/routing_rules.schema.json",
        "schemas/incident_log.schema.json",
        "examples/hotel_service_robot/intake.json",
        "examples/hotel_service_robot/routing_rules.json",
    ]:
        load_json(relative_path)


def validate_examples() -> None:
    intake = load_json("examples/hotel_service_robot/intake.json")
    routing = load_json("examples/hotel_service_robot/routing_rules.json")

    missing_intake = REQUIRED_INTAKE_FIELDS.difference(intake)
    if missing_intake:
        fail(f"sample intake missing fields: {sorted(missing_intake)}")

    missing_routing = REQUIRED_ROUTING_FIELDS.difference(routing)
    if missing_routing:
        fail(f"sample routing missing fields: {sorted(missing_routing)}")

    zone_ids = {zone["zone_id"] for zone in intake.get("zones", []) if "zone_id" in zone}
    if not zone_ids:
        fail("sample intake has no zones")

    routing_zone_ids = {zone["zone_id"] for zone in routing.get("zones", []) if "zone_id" in zone}
    unknown_routing_zones = routing_zone_ids.difference(zone_ids)
    if unknown_routing_zones:
        fail(f"routing references zones missing from intake: {sorted(unknown_routing_zones)}")

    for route in routing.get("allowed_routes", []):
        for key in ("from_zone", "to_zone"):
            if route.get(key) not in zone_ids:
                fail(f"allowed route {route.get('route_id')} references missing {key}: {route.get(key)}")


def validate_incident_csv() -> None:
    path = ROOT / "examples/hotel_service_robot/incident_log_template.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration:
            fail("incident CSV is empty")
    if headers != INCIDENT_HEADERS:
        fail(f"incident CSV headers mismatch: {headers}")


def validate_html_demo() -> None:
    html = (ROOT / "simulation/browser_facility_demo.html").read_text(encoding="utf-8")
    for token in ["<!doctype html>", "function playDemo()", "function pauseDemo()", "function resetDemo()"]:
        if token not in html:
            fail(f"browser demo missing token: {token}")
    if "not a physics simulator" not in html:
        fail("browser demo does not disclose simulator limitation")


def validate_truth_boundaries() -> None:
    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "RULES.yaml", "docs/limitations.md", "manifest.yaml"]
    ).lower()
    for disclosure in REQUIRED_DISCLOSURES:
        if disclosure not in combined:
            fail(f"missing required disclosure: {disclosure}")
    for phrase in BANNED_AFFIRMATIVE_CLAIMS:
        if phrase in combined:
            fail(f"truth-boundary violation phrase found: {phrase}")


def main() -> None:
    validate_required_files()
    validate_json_files()
    validate_examples()
    validate_incident_csv()
    validate_html_demo()
    validate_truth_boundaries()
    print("RoboSafeOS validation passed")


if __name__ == "__main__":
    main()
