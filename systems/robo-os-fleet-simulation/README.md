# ROBO-OS Fleet Simulation

Browser-based robotics fleet simulation system for demonstrating fleet operations, mission dispatch, route planning, facility-map interaction, and exception handling.

## Status

- Type: runtime/internal demonstration system
- Commercial status: not sold directly as a universal machine-control product
- Live machine integration: not included in the base demo
- Certification status: not included

## What this system does

- Simulates a facility map with zones, static obstacles, temporary blockers, and human hazard zones.
- Simulates multiple robot models using public specification snapshots.
- Demonstrates mission creation, task queueing, capability matching, route planning, and event logging.
- Demonstrates rule-based exception behavior such as battery checks, active fault checks, human hazard halts, and proximity checks.
- Supports interactive demo controls: inspect map elements, click-to-create missions, add blockers, add human hazards, drag idle robots, clear map edits, and export logs.

## What this system does not claim

- It does not operate live machines by default.
- It does not include a live ROS 2, Open-RMF, Nav2, or manufacturer API bridge.
- It is not a certified industrial deployment package.
- It is not a plug-and-play integration for all AMRs, AGVs, humanoids, or industrial machines.

## Intended use

This system is intended as the base demonstration engine for custom digital twin and fleet simulation services. It can be adapted to a buyer's facility, machines, workflows, task logic, and operational rules after technical discovery.

## Entry point

Open `index.html` directly in a browser.

## Related sellable service

See:

- `products/custom-robot-fleet-digital-twin-service/`
- `marketplace/listings/custom-robot-fleet-digital-twin-service.yaml`
