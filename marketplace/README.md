# Marketplace

Marketplace-facing assets for protocol and agent product discovery, listing, and delivery.

## Structure

- [`protocols/`](./protocols/) — protocol catalog and storefront listings
- [`products/`](./products/) — long-form product page copy
- [`downloadables/`](./downloadables/) — packaged customer-deliverable bundles
- [`agents/`](./agents/) — marketplace listing assets for agent products
- [`protocol_product_api/`](./protocol_product_api/) — protocol product API backend assets
- [`agent_product_api/`](./agent_product_api/) — agent product API backend assets
- [`implementation/`](./implementation/) — implementation notes/spec assets

## Protocol Catalog Authority

- Storefront mapping/index: [`protocols/catalog.yaml`](./protocols/catalog.yaml)
- Canonical protocol definitions: `protocols/products/*/manifest.yaml` (outside this folder)

If listing metadata and canonical manifests differ, canonical manifests are authoritative.
See [`marketplace/protocols/README.md`](./protocols/README.md).
