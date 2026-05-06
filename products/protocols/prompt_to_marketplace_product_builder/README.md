# Prompt-to-Marketplace Product Builder

A sellable product-packaging framework for turning a rough robotics, AI, automation, or protocol idea into a structured downloadable SKU folder.

## What this product does

It helps creators and marketplace operators package product ideas into clear, auditable, buyer-ready product folders without inventing unsupported claims.

It includes:

- Product pack schema
- Protocol pack template
- Example product pack
- Product truth rules
- Local validation tooling
- Local export-package builder

## Usage

1. Start from `templates/protocol_pack_template/manifest.yaml`.
2. Replace the sample product idea, buyer, use case, deliverables, limitations, and commercial status with real creator-supplied information.
3. Check the product structure against `schemas/product_pack.schema.json`.
4. Confirm every listed deliverable exists before marking the product ready for marketplace review.
5. Keep unknown prices, certifications, compatibility, and deployment proof unset until evidence exists.

## Validate

```bash
python3 products/protocols/prompt_to_marketplace_product_builder/tools/validate_product.py
```

## Build export package

```bash
python3 products/protocols/prompt_to_marketplace_product_builder/tools/build_export_package.py
```

## Product limits

This framework creates a sellable product structure. It does not create real technical deliverables unless the creator supplies or builds them. It does not invent pricing, certifications, compatibility, or deployment proof.
