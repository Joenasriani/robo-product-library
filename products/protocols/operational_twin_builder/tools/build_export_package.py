#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "operational-twin-builder-sample-export.zip"
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/operational_twin_model.md",
    "schemas/operational_twin.schema.json",
    "templates/hotel_delivery_robot_twin.yaml",
    "examples/hotel_delivery_robot_operational_twin.md",
    "deliverables/export_package_manifest.md",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(OUT, "w", ZIP_DEFLATED) as zf:
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            raise SystemExit(f"Missing: {rel}")
        zf.write(p, rel)
print(OUT)
