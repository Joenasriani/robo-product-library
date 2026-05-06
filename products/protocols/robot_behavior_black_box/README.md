# Robot Behavior Black Box

A sellable robotics operations audit pack for documenting robot decisions, incidents, human overrides, and corrective-action recommendations.

## What this product does

Robot Behavior Black Box helps robotics operators and integrators structure post-event review data so teams can explain what happened during a robot task and decide what must be reviewed next.

It includes:

- Robot event schema
- Event log template
- Sample incident report
- Local validation tooling
- Local export-package builder

## Usage

1. Start from `templates/robot_event_log_template.json`.
2. Replace the sample event values with real event records supplied by the operator, integrator, or vendor platform.
3. Validate the record structure against `schemas/robot_event.schema.json`.
4. Use `examples/elevator_delay_incident_example.md` as a reporting pattern for incident review.
5. Treat root-cause notes and process updates as review recommendations until approved by the responsible human owner.

## Validate

```bash
python3 products/protocols/robot_behavior_black_box/tools/validate_product.py
```

## Build export package

```bash
python3 products/protocols/robot_behavior_black_box/tools/build_export_package.py
```

## Product limits

This pack structures review data. It does not prove legal liability, certify root cause, read proprietary robot logs without an adapter, or apply process changes without human review.
