# RoboSafeOS Deployment Workflow

## 1. Intake

Collect the facility type, robot type, zone list, restricted areas, traffic patterns, task schedule, operator contacts, and incident severity definitions.

Use:

- `schemas/intake.schema.json`
- `examples/hotel_service_robot/intake.json`

## 2. Zone review

Classify each zone by:

- public access
- staff-only access
- traffic level
- risk level
- operating time window
- notes for visitor or staff interaction

## 3. Routing rule drafting

Convert the zone review into structured routing rules.

Use:

- `schemas/routing_rules.schema.json`
- `examples/hotel_service_robot/routing_rules.json`

## 4. Human review plan

Document who reviews events, when review is required, and which facility role owns escalation.

Use:

- `templates/human_override_plan_template.md`

## 5. Incident log setup

Create the incident tracking sheet or database table from the included schema.

Use:

- `schemas/incident_log.schema.json`
- `examples/hotel_service_robot/incident_log_template.csv`

## 6. Buyer review demonstration

Open `simulation/browser_facility_demo.html` in a browser to show the operating idea visually.

The demo is explanatory only. It is not a certified physics simulator or live robot controller.

## 7. Integrator handoff

Share the final pack with the robot vendor or integrator. The integrator is responsible for translating the documented rules into the robot runtime, fleet platform, or middleware.

## 8. Site validation

Before any live deployment, the buyer and integrator must perform site-specific review, facility walk-through, operator training, and approval according to local requirements.
