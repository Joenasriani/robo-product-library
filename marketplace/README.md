# Marketplace

Marketplace-facing assets for protocol and agent product discovery, listing, and delivery.

## Structure

- [`protocols/`](./protocols/) — protocol catalog and storefront listings
- [`agents/`](./agents/) — marketplace listing assets for agent products
- (moved to `/plans/`) product-page drafts, API plans, and implementation notes

## Protocol Catalog Authority

- Storefront mapping/index: [`protocols/catalog.yaml`](./protocols/catalog.yaml)
- Canonical protocol definitions: `products/protocols/*/manifest.yaml` (outside this folder)

If listing metadata and canonical manifests differ, canonical manifests are authoritative.
See [`marketplace/protocols/README.md`](./protocols/README.md).
