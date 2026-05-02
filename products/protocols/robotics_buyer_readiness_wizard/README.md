# Robotics Buyer Readiness Wizard

A sellable robotics buyer-readiness assessment pack for facilities evaluating whether they are ready to purchase and deploy robots.

## What this product does

It gives robotics buyers, facility teams, and RoboMarket intake operators a structured way to assess deployment readiness before a robot purchase discussion becomes serious.

It includes:

- Facility intake schema
- Robot category readiness questions
- Working assessment templates
- Buyer inquiry packet schema
- Sample readiness report
- Local validation tooling
- Local export-package builder

## Primary users

- Hotels considering delivery, concierge, cleaning, or reception robots
- Malls considering cleaning, patrol, or wayfinding robots
- Warehouses considering AMR deployment
- Hospitals considering delivery or service robots
- Premium residential buildings considering concierge or delivery robots
- RoboMarket.ae buyer intake operators

## Delivered files

- `manifest.yaml` — commercial/product metadata
- `RULES.yaml` — product truth and usage rules
- `docs/readiness_model.md` — assessment model
- `schemas/readiness_assessment.schema.json` — required assessment fields
- `schemas/buyer_inquiry_packet.schema.json` — handoff packet fields
- `templates/hotel_readiness_assessment.json` — working hotel template
- `templates/warehouse_readiness_assessment.json` — working warehouse template
- `examples/hotel_buyer_readiness_report.md` — sample output report
- `tools/validate_product.py` — validates required files and JSON templates
- `tools/build_export_package.py` — builds the customer export ZIP
- `deliverables/export_package_manifest.md` — documents package contents

## How to validate

From the repository root:

```bash
python3 products/protocols/robotics_buyer_readiness_wizard/tools/validate_product.py
```

## How to build the export package

From the repository root:

```bash
python3 products/protocols/robotics_buyer_readiness_wizard/tools/build_export_package.py
```

The builder writes:

```text
deliverables/robotics-buyer-readiness-wizard-sample-export.zip
```

## Product limits

This product does not certify a facility, select a final robot vendor, guarantee deployment success, or replace a qualified robotics integrator. It is a structured readiness and buyer-intake pack.
