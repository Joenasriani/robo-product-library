#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/product_pack_model.md",
    "schemas/product_pack.schema.json",
    "templates/protocol_pack_template/manifest.yaml",
    "examples/humanoid_hospitality_protocol_pack_example.md",
    "tools/build_export_package.py",
    "deliverables/export_package_manifest.md",
]
missing = [f for f in FILES if not (ROOT / f).exists()]
if missing:
    raise SystemExit("Missing:\n" + "\n".join(missing))
schema = json.loads((ROOT / "schemas/product_pack.schema.json").read_text(encoding="utf-8"))
if "required" not in schema or "properties" not in schema:
    raise SystemExit("Schema must define required fields and properties")
print("Prompt-to-Marketplace Product Builder validation passed.")
