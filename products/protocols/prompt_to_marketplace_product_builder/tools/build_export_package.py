#!/usr/bin/env python3
"""Build a customer-facing ZIP export for Prompt-to-Marketplace Product Builder."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "prompt-to-marketplace-product-builder-sample-export.zip"
INCLUDE = [
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
