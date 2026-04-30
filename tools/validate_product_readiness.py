#!/usr/bin/env python3
"""Validate RoboMarket product readiness metadata.

This script is dependency-free. It performs repository-level checks that prevent
catalog drift and false product-readiness claims.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products" / "catalog.yaml"
AUDIT_JSON_PATH = ROOT / "shared" / "docs" / "audits" / "product_sellability_audit.json"

VALID_STATUSES = {
    "ready-to-list",
    "ready_to_list",
    "inquiry-only",
    "inquiry_only",
    "manual-fulfillment",
    "manual_fulfillment",
    "internal-only",
    "internal_only",
    "needs-review",
    "needs_review",
}

REQUIRED_MANIFEST_FIELDS = {
    "id",
    "slug",
    "name",
    "version",
    "category",
    "status",
    "sales_mode",
    "deliverable_type",
    "fulfillment_method",
    "deliverables",
}

PROTOCOL_REQUIRED_DOCS = (
    "docs/setup.md",
    "docs/compatibility.md",
    "docs/deliverables.md",
    "docs/support.md",
)

PROTOCOL_REQUIRED_TESTS = (
    "tests/acceptance_criteria.yaml",
    "tests/qa_checklist.md",
)

PROHIBITED_PHRASES = (
    "fully autonomous deployment",
    "guaranteed compliance",
    "legal certainty",
    "medical certainty",
    "replaces human staff",
    "instant checkout",
    "buy now",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def top_level_yaml_value(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        value = value[1:-1]
    return value or None


def has_top_level_key(text: str, key: str) -> bool:
    return re.search(rf"^{re.escape(key)}:\s*", text, re.MULTILINE) is not None


def parse_catalog() -> list[dict[str, str]]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Missing catalog: {CATALOG_PATH.relative_to(ROOT)}")

    entries: list[dict[str, str]] = []
    current_group = ""
    current: dict[str, str] | None = None

    for raw_line in read_text(CATALOG_PATH).splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_group = line[:-1]
            continue
        if line.startswith("- id:"):
            if current:
                entries.append(current)
            current = {"group": current_group, "id": line.split(":", 1)[1].strip()}
            continue
        if current is not None and line.startswith("  ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key] = value.strip()

    if current:
        entries.append(current)

    return entries


def audit_entries() -> dict[str, dict]:
    if not AUDIT_JSON_PATH.exists():
        return {}
    data = json.loads(read_text(AUDIT_JSON_PATH))
    return {item.get("slug") or item.get("id"): item for item in data if isinstance(item, dict)}


def validate_catalog_entry(entry: dict[str, str], audit_by_slug: dict[str, dict], errors: list[str]) -> None:
    entry_id = entry.get("id", "<missing-id>")
    manifest_rel = entry.get("manifest")
    readme_rel = entry.get("readme")

    if not manifest_rel:
        errors.append(f"{entry_id}: missing manifest path in catalog")
        return
    if not readme_rel:
        errors.append(f"{entry_id}: missing readme path in catalog")
        return

    manifest_path = ROOT / manifest_rel
    readme_path = ROOT / readme_rel

    if not manifest_path.exists():
        errors.append(f"{entry_id}: manifest does not exist: {manifest_rel}")
        return
    if not readme_path.exists():
        errors.append(f"{entry_id}: README does not exist: {readme_rel}")
        return

    manifest_text = read_text(manifest_path)
    readme_text = read_text(readme_path)
    combined_text = f"{manifest_text}\n{readme_text}".lower()

    for field in REQUIRED_MANIFEST_FIELDS:
        if not has_top_level_key(manifest_text, field):
            errors.append(f"{entry_id}: manifest missing required field `{field}` in {manifest_rel}")

    manifest_id = top_level_yaml_value(manifest_text, "id")
    if manifest_id != entry_id:
        errors.append(f"{entry_id}: catalog id does not match manifest id `{manifest_id}`")

    status = top_level_yaml_value(manifest_text, "status")
    if not status:
        errors.append(f"{entry_id}: manifest missing status")
    elif status not in VALID_STATUSES:
        errors.append(f"{entry_id}: unsupported status `{status}`")

    if status in {"ready-to-list", "ready_to_list"} and "checkout" not in manifest_text.lower():
        errors.append(f"{entry_id}: ready-to-list requires explicit checkout/delivery evidence")

    for phrase in PROHIBITED_PHRASES:
        if phrase in combined_text:
            errors.append(f"{entry_id}: prohibited phrase found: `{phrase}`")

    parent = manifest_path.parent
    if "/protocols/" in manifest_rel:
        for rel in PROTOCOL_REQUIRED_DOCS:
            if not (parent / rel).exists():
                errors.append(f"{entry_id}: missing protocol doc {parent.joinpath(rel).relative_to(ROOT)}")
        for rel in PROTOCOL_REQUIRED_TESTS:
            if not (parent / rel).exists():
                errors.append(f"{entry_id}: missing protocol QA file {parent.joinpath(rel).relative_to(ROOT)}")

    slug = top_level_yaml_value(manifest_text, "slug")
    if entry_id not in audit_by_slug and slug not in audit_by_slug:
        errors.append(f"{entry_id}: missing from machine-readable audit JSON")


def main() -> int:
    errors: list[str] = []

    try:
        catalog_entries = parse_catalog()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not catalog_entries:
        print("ERROR: products/catalog.yaml has no product entries", file=sys.stderr)
        return 1

    audit_by_slug = audit_entries()

    for entry in catalog_entries:
        validate_catalog_entry(entry, audit_by_slug, errors)

    if errors:
        print("Product readiness validation failed:\n", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Product readiness validation passed for {len(catalog_entries)} catalog entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
