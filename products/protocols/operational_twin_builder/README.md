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

It is delivered as a functional product pack with schemas, templates, examples, validation tooling, and a local ZIP export builder.

## Primary users

- Robotics integrators
- Facility automation consultants
- Hotel, mall, warehouse, hospital, retail, and premium residential operations teams
- Smart-building planners

## Delivered files

- `manifest.yaml`
- `RULES.yaml`
- `docs/operational_twin_model.md`
- `schemas/operational_twin.schema.json`
- `schemas/task_node.schema.json`
- `templates/hotel_delivery_robot_twin.yaml`
- `templates/warehouse_amr_twin.yaml`
- `examples/hotel_delivery_robot_operational_twin.md`
- `tools/validate_product.py`
- `tools/build_export_package.py`
- `deliverables/export_package_manifest.md`

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
