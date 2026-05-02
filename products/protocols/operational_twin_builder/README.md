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
