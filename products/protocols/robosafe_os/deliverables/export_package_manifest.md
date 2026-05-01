# RoboSafeOS Export Package Manifest

This file describes the buyer package assembled after inquiry review.

## Core package

- `README.md`
- `manifest.yaml`
- `RULES.yaml`
- `docs/buyer_overview.md`
- `docs/deployment_workflow.md`
- `docs/limitations.md`
- `schemas/intake.schema.json`
- `schemas/routing_rules.schema.json`
- `schemas/incident_log.schema.json`
- `templates/safety_policy_template.md`
- `templates/human_override_plan_template.md`
- `examples/hotel_service_robot/intake.json`
- `examples/hotel_service_robot/routing_rules.json`
- `examples/hotel_service_robot/incident_log_template.csv`
- `simulation/browser_facility_demo.html`

## Buyer-specific package after inquiry

A customized buyer package may include:

- completed intake JSON
- facility policy document generated from the template
- route documentation JSON
- incident log CSV template
- human review plan
- browser demo configured to reflect the buyer facility at a high level

## Not included

- live robot connection
- certified simulator
- regulatory approval
- site engineering approval
- payment checkout flow
- automated PDF or ZIP generation inside RoboMarket

## Packaging note

This product is structured as a self-contained product folder. It should be treated as a mini-repository inside `products/protocols/robosafe_os/`.
