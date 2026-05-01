# RoboSafeOS

Status: product-ready for inquiry-led sale

RoboSafeOS is a robotics deployment safety protocol pack for GCC facilities. It helps hotels, malls, hospitals, warehouses, and premium residential buildings document practical deployment boundaries before placing service robots in shared spaces.

This product sells the deployment brain, not the robot.

## Buyer problem

Many robotics buyers know they want robots, but they do not yet have a clear operating model for zones, visitor traffic, restricted areas, operator handoff, incident records, and deployment review.

## Included files

- `manifest.yaml` — product metadata and commercial constraints
- `RULES.yaml` — product truth rules and claim guardrails
- `docs/buyer_overview.md` — buyer-facing explanation
- `docs/deployment_workflow.md` — implementation workflow
- `docs/limitations.md` — explicit technical and commercial limits
- `schemas/intake.schema.json` — buyer intake schema
- `schemas/routing_rules.schema.json` — routing rules schema
- `schemas/incident_log.schema.json` — incident log schema
- `templates/safety_policy_template.md` — deterministic policy template
- `templates/human_override_plan_template.md` — deterministic override plan template
- `examples/hotel_service_robot/intake.json` — sample facility intake
- `examples/hotel_service_robot/routing_rules.json` — sample routing output
- `examples/hotel_service_robot/incident_log_template.csv` — sample incident log format
- `simulation/browser_facility_demo.html` — browser-based routing demo
- `deliverables/export_package_manifest.md` — buyer export package description

## What is real now

RoboSafeOS currently provides templates, schemas, examples, documentation, and a browser-based demonstration file that can be delivered to a buyer as an inquiry-led protocol pack.

## What requires integration later

- Live robot middleware connection
- Facility CAD/BIM import
- ROS2/Nav2 policy enforcement
- Isaac Sim, AirSim, or IR-SIM validation bridge
- Real-time fleet telemetry ingestion
- Automated PDF/ZIP generation inside RoboMarket checkout

## Demonstration note

The included HTML file is a browser-based facility routing demonstration. It is useful for explaining route restrictions, high-traffic zones, rerouting, and human review events. It is not a physics-accurate simulator and must not be sold as one.

## Inquiry instruction

For customization or deployment review, send an inquiry to `hello@robomarket.ae` and use this product name as the email subject:

`robosafe-os`
