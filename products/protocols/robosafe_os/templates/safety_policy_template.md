# RoboSafeOS Facility Policy Template

Product: RoboSafeOS
Facility: {{facility_name}}
Facility type: {{facility_type}}
Robot type: {{robot_type}}
Country: {{country}}

## 1. Summary

This document organizes facility information for planning and review before a robotics project is implemented by a qualified vendor or integrator.

## 2. Facility zones

List each zone with access type, traffic level, risk level, and notes.

Required zone fields:

- zone_id
- name
- access_type
- traffic_level
- risk_level
- notes

## 3. Exclusion areas

List areas that require exclusion, special review, or site-specific approval before being included in a robotics project.

## 4. Traffic windows

Document peak and low-traffic periods. High-traffic windows should be reviewed carefully by the facility team and integrator.

## 5. Task schedule

Each task record should include:

- task_id
- task_name
- preferred time window
- zones involved
- whether staff review is required

## 6. Route documentation

Route records should be documented in `routing_rules.json` using `schemas/routing_rules.schema.json`.

## 7. Human review plan

Use `templates/human_override_plan_template.md` to document responsible roles, review points, and escalation contacts.

## 8. Incident records

Use `schemas/incident_log.schema.json` and `examples/hotel_service_robot/incident_log_template.csv` to set up the buyer incident log.

## 9. Review note

This template does not certify a deployment. The final pack must be reviewed by the facility operator, robot vendor, and qualified integrator before use in a physical site.
