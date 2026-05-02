#!/usr/bin/env python3
"""Build a customer-facing ZIP export for Robotics Buyer Readiness Wizard."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "robotics-buyer-readiness-wizard-sample-export.zip"
INCLUDE = [
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
