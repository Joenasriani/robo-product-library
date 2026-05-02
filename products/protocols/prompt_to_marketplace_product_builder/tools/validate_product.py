#!/usr/bin/env python3
"""Validate Prompt-to-Marketplace Product Builder product files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/product_pack_model.md",
    "schemas/product_pack.schema.json",
    "schemas/listing_metadata.schema.json",
    "templates/protocol_pack_template/README.md",
    "templates/protocol_pack_template/manifest.yaml",
    "templates/protocol_pack_template/listing_metadata.json",
    "examples/humanoid_hospitality_protocol_pack_example.md",
    "deliverables/export_package_manifest.md",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(f"- {item}" for item in missing))

    listing = load_json(ROOT / "templates/protocol_pack_template/listing_metadata.json")
    for field in ["title", "slug", "summary", "category", "listing_status", "sales_mode", "price_aed"]:
        if field not in listing:
            raise SystemExit(f"listing_metadata.json missing field: {field}")

    product_schema = load_json(ROOT / "schemas/product_pack.schema.json")
    if "required" not in product_schema or "properties" not in product_schema:
        raise SystemExit("product_pack.schema.json must define required fields and properties")

    print("Prompt-to-Marketplace Product Builder validation passed.")


if __name__ == "__main__":
    main()
