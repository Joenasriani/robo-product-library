#!/usr/bin/env python3
"""Validate RoboMarket catalog canonical truth, schema consistency, and no hardcoded seeds.

Checks:
1. products/protocols/index.yaml — every manifest exists; status/sales_mode are valid.
2. marketplace/protocols/listings/index.json — every listing exists; status/sales_mode valid;
   canonical_manifest references (if present) resolve.
3. marketplace/protocols/catalog.yaml — every manifest and listing path exists.
4. systems/agents/index.yaml — every listing path exists.
5. marketplace/agents/listings/index.json — every listing exists; status/sales_mode valid.
6. marketplace/agents/catalog.yaml — every listing and source folder exists.
7. Runtime db.py files contain no hardcoded seed data.

Exit 0 on success, exit 1 if any errors found.
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALID_PROTOCOL_STATUSES = {"inquiry_only", "non_commercial"}
VALID_AGENT_STATUSES = {"inquiry_only", "non_commercial"}
VALID_SALES_MODES = {"inquiry_only", "non_commercial"}

errors = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"ERROR: {msg}")


def check_exists(path: Path, context: str) -> bool:
    if not path.exists():
        err(f"{context}: not found: {path.relative_to(REPO_ROOT)}")
        return False
    return True


# ── 1. Protocol manifest index ────────────────────────────────────────────────
protocol_index_path = REPO_ROOT / "products" / "protocols" / "index.yaml"
if check_exists(protocol_index_path, "Protocol manifest index"):
    with open(protocol_index_path) as f:
        protocol_index = yaml.safe_load(f)
    for rel_path in protocol_index.get("products", []):
        mpath = REPO_ROOT / rel_path
        if not check_exists(mpath, f"Protocol manifest {rel_path}"):
            continue
        with open(mpath) as mf:
            manifest = yaml.safe_load(mf)
        status = manifest.get("status")
        sales_mode = manifest.get("sales_mode")
        if status not in VALID_PROTOCOL_STATUSES:
            err(f"{rel_path}: invalid status '{status}' — must be one of {sorted(VALID_PROTOCOL_STATUSES)}")
        if sales_mode is not None and sales_mode not in VALID_SALES_MODES:
            err(f"{rel_path}: invalid sales_mode '{sales_mode}' — must be one of {sorted(VALID_SALES_MODES)}")

# ── 2. Protocol listings index ────────────────────────────────────────────────
proto_listings_index = REPO_ROOT / "marketplace" / "protocols" / "listings" / "index.json"
if check_exists(proto_listings_index, "Protocol listings index"):
    with open(proto_listings_index) as f:
        listing_paths = json.load(f)
    for rel_path in listing_paths:
        lpath = REPO_ROOT / rel_path
        if not check_exists(lpath, f"Protocol listing {rel_path}"):
            continue
        with open(lpath) as lf:
            listing = json.load(lf)
        status = listing.get("status")
        sales_mode = listing.get("sales_mode")
        if status not in VALID_PROTOCOL_STATUSES:
            err(f"{rel_path}: invalid status '{status}' — must be one of {sorted(VALID_PROTOCOL_STATUSES)}")
        if sales_mode not in VALID_SALES_MODES:
            err(f"{rel_path}: invalid sales_mode '{sales_mode}' — must be one of {sorted(VALID_SALES_MODES)}")
        canonical_manifest = listing.get("canonical_manifest")
        if canonical_manifest and not (REPO_ROOT / canonical_manifest).exists():
            err(f"{rel_path}: canonical_manifest '{canonical_manifest}' not found")

# ── 3. Protocol catalog ───────────────────────────────────────────────────────
proto_catalog_path = REPO_ROOT / "marketplace" / "protocols" / "catalog.yaml"
if check_exists(proto_catalog_path, "Protocol catalog"):
    with open(proto_catalog_path) as f:
        proto_catalog = yaml.safe_load(f)
    for entry in proto_catalog.get("protocol_products", []):
        for key in ("manifest", "listing"):
            val = entry.get(key)
            if val and not (REPO_ROOT / val).exists():
                err(f"marketplace/protocols/catalog.yaml entry '{entry.get('id')}': {key} '{val}' not found")

# ── 4. Agent index ────────────────────────────────────────────────────────────
agents_index_path = REPO_ROOT / "systems" / "agents" / "index.yaml"
if check_exists(agents_index_path, "Agents index"):
    with open(agents_index_path) as f:
        agents_index = yaml.safe_load(f)
    for rel_path in agents_index.get("agents", []):
        check_exists(REPO_ROOT / rel_path, f"Agent listing {rel_path}")

# ── 5. Agent listings index ───────────────────────────────────────────────────
agent_listings_index = REPO_ROOT / "marketplace" / "agents" / "listings" / "index.json"
if check_exists(agent_listings_index, "Agent listings index"):
    with open(agent_listings_index) as f:
        agent_listing_paths = json.load(f)
    for rel_path in agent_listing_paths:
        lpath = REPO_ROOT / rel_path
        if not check_exists(lpath, f"Agent listing {rel_path}"):
            continue
        with open(lpath) as lf:
            listing = json.load(lf)
        status = listing.get("status")
        sales_mode = listing.get("sales_mode")
        if status not in VALID_AGENT_STATUSES:
            err(f"{rel_path}: invalid status '{status}' — must be one of {sorted(VALID_AGENT_STATUSES)}")
        if sales_mode not in VALID_SALES_MODES:
            err(f"{rel_path}: invalid sales_mode '{sales_mode}' — must be one of {sorted(VALID_SALES_MODES)}")

# ── 6. Agent catalog ──────────────────────────────────────────────────────────
agent_catalog_path = REPO_ROOT / "marketplace" / "agents" / "catalog.yaml"
if check_exists(agent_catalog_path, "Agent catalog"):
    with open(agent_catalog_path) as f:
        agent_catalog = yaml.safe_load(f)
    for entry in agent_catalog.get("agent_products", []):
        listing_rel = entry.get("listing")
        if listing_rel and not (REPO_ROOT / listing_rel).exists():
            err(f"marketplace/agents/catalog.yaml entry '{entry.get('id')}': listing '{listing_rel}' not found")
        source_rel = entry.get("source")
        if source_rel and not (REPO_ROOT / source_rel).exists():
            err(f"marketplace/agents/catalog.yaml entry '{entry.get('id')}': source '{source_rel}' not found")

# ── 7. No hardcoded seed data in runtime db.py files ─────────────────────────
# Detect the presence of the removed _seed_products function or known hardcoded
# product slug strings that were part of the old seed arrays.
SEED_PATTERNS = [
    "def _seed_products",
    "gcc-royal-protocol-pack",
    "gcc-hotel-concierge-protocol",
]
runtime_db_files = [
    REPO_ROOT / "systems" / "agents" / "protocol_marketplace_agent" / "src" / "db.py",
    REPO_ROOT / "systems" / "agents" / "ai_agent_download_center" / "src" / "db.py",
]
for db_path in runtime_db_files:
    if not db_path.exists():
        continue
    content = db_path.read_text()
    for pattern in SEED_PATTERNS:
        if pattern in content:
            err(f"{db_path.relative_to(REPO_ROOT)}: contains hardcoded seed pattern '{pattern}'")

# ── 8. Product standard validation (/products) ───────────────────────────────
products_catalog_path = REPO_ROOT / "products" / "catalog.yaml"
if check_exists(products_catalog_path, "Products catalog"):
    with open(products_catalog_path) as f:
        products_catalog = yaml.safe_load(f) or {}

    for section in ("protocol_products", "ai_products"):
        for item in products_catalog.get(section, []):
            product_id = item.get("id")
            manifest_rel = item.get("manifest")
            bundle_rel = item.get("bundle")
            readme_rel = item.get("readme")

            if not manifest_rel:
                err(f"products/catalog.yaml section '{section}' item '{product_id}': missing manifest")
                continue

            manifest_path = REPO_ROOT / manifest_rel
            if not check_exists(manifest_path, f"products/catalog.yaml manifest for '{product_id}'"):
                continue

            if bundle_rel:
                check_exists(REPO_ROOT / bundle_rel, f"products/catalog.yaml bundle for '{product_id}'")
            if readme_rel:
                rpath = REPO_ROOT / readme_rel
                if check_exists(rpath, f"products/catalog.yaml readme for '{product_id}'"):
                    rtxt = rpath.read_text(encoding="utf-8", errors="ignore")
                    if "## Usage" not in rtxt and "## Sellable Package Usage" not in rtxt:
                        err(f"{readme_rel}: missing Usage instructions section")

            manifest = yaml.safe_load(manifest_path.read_text()) or {}
            for field in ("id", "slug", "name", "version"):
                if not manifest.get(field):
                    err(f"{manifest_rel}: missing required field '{field}'")

            status = manifest.get("status")
            sales_mode = manifest.get("sales_mode")
            if status not in VALID_PROTOCOL_STATUSES:
                err(f"{manifest_rel}: invalid status '{status}' — must be one of {sorted(VALID_PROTOCOL_STATUSES)}")
            if sales_mode not in VALID_SALES_MODES:
                err(f"{manifest_rel}: invalid sales_mode '{sales_mode}' — must be one of {sorted(VALID_SALES_MODES)}")

# ── Result ────────────────────────────────────────────────────────────────────
if errors:
    print(f"\n{len(errors)} validation error(s) found.")
    sys.exit(1)
else:
    print("All catalog validations passed.")
    sys.exit(0)
