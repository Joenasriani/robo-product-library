#!/usr/bin/env python3
"""Build a customer-facing ZIP export for Operational Twin Builder."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "operational-twin-builder-sample-export.zip"
INCLUDE = [
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


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for rel in INCLUDE:
            path = ROOT / rel
            if not path.exists():
                raise SystemExit(f"Cannot package missing file: {rel}")
            archive.write(path, rel)
    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
