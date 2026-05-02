#!/usr/bin/env python3
"""Validate Robo Product Library marketplace listing readiness.

This script validates readiness for later marketplace listing, not payment
checkout, Stripe fulfillment, or live robot deployment.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products" / "catalog.yaml"

REQUIRED_MANIFEST_FIELDS = {
    "id",
    "slug",
    "name",
    "version",
    "deliverable_type",
}

REQUIRED_LISTING_FIELDS = {
    "status",
    "sales_mode",
    "fulfillment_method",
    "customer_receives",
    "limitations",
}

COMMERCIAL_BOUNDARY_FIELDS = {
    "commercial_status",
    "commercial_status_note",
    "commercial_tier",
}

ALLOWED_LISTING_STATUSES = {
    "ready_for_marketplace_listing_review",
    "staged_downloadable_package_review",
    "needs_manual_review",
}

ALLOWED_SALES_MODES = {
    "inquiry_only",
    "manual-fulfillment",
    "manual_fulfillment",
    "buy_now_future",
    "staged_downloadable_package_review",
}

PAYMENT_CLAIM_PATTERNS = [
    re.compile(r"checkout\s+is\s+live", re.IGNORECASE),
    re.compile(r"stripe\s+checkout\s+is\s+live", re.IGNORECASE),
    re.compile(r"automated\s+file\s+delivery\s+is\s+active", re.IGNORECASE),
    re.compile(r"instant\s+download\s+is\s+active", re.IGNORECASE),
]

FORBIDDEN_ROBOTICS_OVERCLAIMS = [
    re.compile(r"certified\s+safety\s+system", re.IGNORECASE),
    re.compile(r"legal\s+compliance\s+guaranteed", re.IGNORECASE),
    re.compile(r"official\s+royal\s+protocol", re.IGNORECASE),
    re.compile(r"provides\s+medical\s+advice", re.IGNORECASE),
]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def catalog_products(catalog: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    products: list[tuple[str, dict[str, Any]]] = []
    for section in ("protocol_products", "ai_products", "downloadable_products"):
        for entry in catalog.get(section, []) or []:
            products.append((section, entry))
    return products


def read_text_if_exists(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def validate_entry(section: str, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    product_id = entry.get("id", "<missing id>")

    listing_status = entry.get("listing_status")
    if listing_status not in ALLOWED_LISTING_STATUSES:
        errors.append(f"{product_id}: listing_status must be one of {sorted(ALLOWED_LISTING_STATUSES)}")

    manifest_rel = entry.get("manifest")
    readme_rel = entry.get("readme")
    if not manifest_rel:
        errors.append(f"{product_id}: missing manifest path")
        return errors
    if not readme_rel:
        errors.append(f"{product_id}: missing readme path")
        return errors

    manifest_path = ROOT / manifest_rel
    readme_path = ROOT / readme_rel

    if not manifest_path.exists():
        errors.append(f"{product_id}: manifest does not exist at {manifest_rel}")
        return errors
    if not readme_path.exists():
        errors.append(f"{product_id}: README does not exist at {readme_rel}")
        return errors

    manifest = load_yaml(manifest_path)
    missing_manifest = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing_manifest:
        errors.append(f"{product_id}: manifest missing required fields {missing_manifest}")

    missing_listing = sorted(REQUIRED_LISTING_FIELDS - set(manifest))
    if missing_listing:
        errors.append(f"{product_id}: manifest missing listing fields {missing_listing}")

    if not (COMMERCIAL_BOUNDARY_FIELDS & set(manifest)):
        errors.append(
            f"{product_id}: manifest needs one commercial boundary field: "
            f"{sorted(COMMERCIAL_BOUNDARY_FIELDS)}"
        )

    sales_mode = manifest.get("sales_mode")
    if sales_mode not in ALLOWED_SALES_MODES:
        errors.append(f"{product_id}: unsupported sales_mode {sales_mode!r}")

    price = manifest.get("price_aed")
    if sales_mode in {"inquiry_only", "manual-fulfillment", "manual_fulfillment"}:
        # Pricing may be visible for later listing/inquiry, but must not imply checkout exists.
        if price is not None and not isinstance(price, (int, float)):
            errors.append(f"{product_id}: price_aed must be numeric or null")
    elif sales_mode == "buy_now_future" and price is None:
        errors.append(f"{product_id}: buy_now_future products need an intended price_aed or needs_manual_review")

    has_bundle = bool(entry.get("bundle"))
    has_deliverable_manifest = bool(entry.get("deliverable_manifest"))
    has_customer_receives = bool(manifest.get("customer_receives"))
    if not (has_bundle or has_deliverable_manifest or has_customer_receives):
        errors.append(f"{product_id}: needs bundle, deliverable_manifest, or customer_receives")

    for key in ("bundle", "deliverable_manifest"):
        rel = entry.get(key)
        if rel:
            path = ROOT / rel
            if not path.exists():
                errors.append(f"{product_id}: {key} path does not exist at {rel}")

    readme_text = read_text_if_exists(readme_path)
    if not re.search(r"^##\s+Usage\b", readme_text, flags=re.MULTILINE | re.IGNORECASE):
        errors.append(f"{product_id}: README must include a ## Usage section")

    combined_text = readme_text + "\n" + read_text_if_exists(manifest_path)
    for pattern in PAYMENT_CLAIM_PATTERNS:
        if pattern.search(combined_text):
            errors.append(f"{product_id}: contains payment/fulfillment claim matching {pattern.pattern!r}")
    for pattern in FORBIDDEN_ROBOTICS_OVERCLAIMS:
        if pattern.search(combined_text):
            errors.append(f"{product_id}: contains robotics overclaim matching {pattern.pattern!r}")

    return errors


def main() -> int:
    catalog = load_yaml(CATALOG_PATH)
    all_errors: list[str] = []
    products = catalog_products(catalog)

    if not products:
        all_errors.append("No products found in products/catalog.yaml")

    for section, entry in products:
        all_errors.extend(validate_entry(section, entry))

    if all_errors:
        print("Product listing readiness validation failed:\n")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"Product listing readiness validation passed for {len(products)} catalog entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
