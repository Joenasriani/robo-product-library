#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "robot-behavior-black-box-sample-export.zip"
INCLUDE = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/event_log_model.md",
    "schemas/robot_event.schema.json",
    "schemas/incident_report.schema.json",
    "templates/robot_event_log_template.json",
    "templates/incident_report_template.md",
    "examples/elevator_delay_incident_example.md",
    "deliverables/export_package_manifest.md",
]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for rel in INCLUDE:
            path = ROOT / rel
            if not path.exists():
                raise SystemExit(f"Missing file: {rel}")
            archive.write(path, rel)
    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
