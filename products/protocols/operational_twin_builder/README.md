# Operational Twin Builder

A sellable robotics deployment-planning product for modeling a facility operation before robots are deployed.

## What this product does

Operational Twin Builder helps robotics integrators and facility teams convert a target deployment into a structured operational twin:

- facility zones
- robot tasks
- human actors
- escalation rules
- failure branches
- safety owners
- deployment assumptions

## Usage

1. Start from `templates/hotel_delivery_robot_twin.yaml` or create a new twin using `schemas/operational_twin.schema.json`.
2. Replace sample zones, task nodes, actors, escalation rules, failure branches, assumptions, and unresolved questions with site-specific information.
3. Review every human intervention point and escalation path with the facility operations owner.
4. Validate the product folder before delivery using the validation command below.
5. Use the generated package as a planning artifact for integrator review, not as a certified simulation or live robot controller.

## Validate

```bash
python3 products/protocols/operational_twin_builder/tools/validate_product.py
```

## Build export package

```bash
python3 products/protocols/operational_twin_builder/tools/build_export_package.py
```

## Product limits

This product is a planning and documentation framework. It does not control robots, simulate physics, certify site safety, or replace integrator review.
