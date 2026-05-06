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

## Usage

1. Copy one of the assessment templates from `templates/`.
2. Replace the sample facility and robot assumptions with buyer-provided information.
3. Validate the completed assessment against `schemas/readiness_assessment.schema.json`.
4. Use `schemas/buyer_inquiry_packet.schema.json` to prepare a structured buyer handoff packet.
5. Review the output with a qualified robotics integrator, facility operator, and safety owner before any deployment decision.

This product is intended for readiness assessment and buyer qualification. It is not a certified safety approval or final vendor-selection system.

## How to validate

```bash
python3 products/protocols/robotics_buyer_readiness_wizard/tools/validate_product.py
```

## How to build the export package

```bash
python3 products/protocols/robotics_buyer_readiness_wizard/tools/build_export_package.py
```

## Product limits

This product does not certify a facility, select a final robot vendor, guarantee deployment success, or replace a qualified robotics integrator. It is a structured readiness and buyer-intake pack.
