#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "prompt-to-marketplace-product-builder-sample-export.zip"
FILES = [
    "README.md",
    "RULES.yaml",
    "manifest.yaml",
    "docs/product_pack_model.md",
    "schemas/product_pack.schema.json",
    "templates/protocol_pack_template/manifest.yaml",
    "examples/humanoid_hospitality_protocol_pack_example.md",
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
