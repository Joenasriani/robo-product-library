#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "robot-behavior-black-box-sample-export.zip"
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/event_log_model.md",
    "schemas/robot_event.schema.json",
    "templates/robot_event_log_template.json",
    "examples/elevator_delay_incident_example.md",
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
