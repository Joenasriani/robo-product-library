#!/usr/bin/env python3
"""Validate product-library sellability and functionality invariants.

This script is intentionally dependency-light. It does not require PyYAML.
It checks the repository as a product-delivery library, not as a marketplace app.

Validation focus:
- every manifest under products/ has a stable product id;
- product ids must be unique across products/;
- every manifest must sit beside a README.md;
- every manifest that references bundle.zip must have a bundle.zip file;
- every products/**/README.md should have a neighboring manifest.yaml unless it is a schema/docs file;
- product README status should not imply self-serve marketplace readiness.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "products"

ID_RE = re.compile(r"^id:\s*([^\n#]+)", re.MULTILINE)
STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.MULTILINE)

ALLOWED_README_WITHOUT_MANIFEST = {
    PRODUCTS / "README.md",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def manifest_id(path: Path) -> str | None:
    match = ID_RE.search(read_text(path))
    return match.group(1).strip().strip('"\'') if match else None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    manifests = sorted(PRODUCTS.glob("**/manifest.yaml"))
    ids: dict[str, list[Path]] = {}

    for manifest in manifests:
        product_id = manifest_id(manifest)
        rel = manifest.relative_to(ROOT)
        if not product_id:
            errors.append(f"{rel}: missing top-level id field")
            continue
        ids.setdefault(product_id, []).append(manifest)

        product_dir = manifest.parent
        readme = product_dir / "README.md"
        if not readme.exists():
            errors.append(f"{rel}: missing sibling README.md")

        text = read_text(manifest)
        if "bundle.zip" in text and not (product_dir / "bundle.zip").exists():
            errors.append(f"{rel}: references bundle.zip but no sibling bundle.zip exists")

    for product_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            locations = ", ".join(str(p.relative_to(ROOT)) for p in paths)
            errors.append(f"duplicate product id {product_id!r}: {locations}")

    for readme in sorted(PRODUCTS.glob("**/README.md")):
        if readme in ALLOWED_README_WITHOUT_MANIFEST:
            continue
        product_dir = readme.parent
        if not (product_dir / "manifest.yaml").exists():
            errors.append(f"{readme.relative_to(ROOT)}: README exists without sibling manifest.yaml")

        text = read_text(readme)
        status = STATUS_RE.search(text)
        if status:
            raw_status = status.group(1).strip().lower()
            if raw_status == "product-ready":
                warnings.append(
                    f"{readme.relative_to(ROOT)}: Status 'product-ready' is ambiguous; "
                    "prefer 'functional-package / inquiry-only' until checkout and auto-fulfillment exist"
                )
            if raw_status == "research-and-specification":
                errors.append(
                    f"{readme.relative_to(ROOT)}: README status conflicts with products/ sellable-SKU rule"
                )

    print("Product functionality validation")
    print(f"Manifests checked: {len(manifests)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}")

    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("\nErrors:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("\nPASS: product library invariants satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
