# GCC Humanoid Etiquette Protocol Pack

## Product Summary

The **GCC Humanoid Etiquette Protocol Pack** is a sellable robotics protocol module for humanoid and social service robots operating in GCC hospitality, reception, majlis, mall concierge, and premium residential environments.

It provides a structured state-machine protocol that converts multimodal sensor input into prioritized, culturally aware robot behavior and standardized ROS 2 action outputs.

This is not a generic prompt. It is a buyer-facing protocol pack intended for robotics professionals who need a practical starting point for implementation, validation, and site adaptation.

## Intended Buyers

- Robotics integrators deploying humanoid or social robots in GCC venues
- Hospitality automation teams building concierge or service workflows
- Mall, hotel, and premium residential operators testing robot reception flows
- ROS 2 developers needing a structured behavior protocol to adapt to a robot stack

## Primary Use Case

A humanoid robot observes a room, detects guests, recognizes priority social cues, maintains respectful spacing, yields to higher-priority humans, and performs service actions such as greeting, escorting, and serving gahwa through ROS 2-compatible action commands.

## Core Design Principle

The protocol prioritizes:

1. Human safety
2. Hierarchical status and guest priority
3. GCC social etiquette
4. Task completion
5. Efficiency

Efficiency never overrides safety, seniority, personal-space handling, or human override commands.

## Included Deliverables

- `manifest.yaml` — product metadata and marketplace readiness notes
- `protocol.json` — complete structured state-machine logic schema
- `ros2_action_mapping.md` — ROS 2 action and service integration mapping
- `validation_checklist.md` — pre-sale and deployment-readiness QA checklist
- `integration_notes.md` — implementation guidance for robotics teams

## State-Machine Coverage

The protocol defines:

- State Zero: standby and observation mode
- Priority interrupts: elder/VIP entry, unsafe proximity, blocked route, prayer/quiet zone, operator override, audio distress signal
- Decision tree: gahwa serving workflow
- Multimodal sensor inputs: vision, lidar, audio, operator override
- ROS 2 outputs: navigation, speech, gesture, stop, yield, serve, and escalation actions

## What This Product Is

- A structured robotics behavior protocol pack
- A ROS 2-oriented action design reference
- A culturally aware decision schema for humanoid service robots
- A foundation for customer-specific deployment engineering

## What This Product Is Not

- It is not a certified safety system
- It is not a complete robot firmware package
- It is not a legal, religious, or etiquette authority
- It is not a replacement for local stakeholder validation
- It does not include robot-specific drivers, perception models, or hardware adapters

## Deployment Requirement

Before live use, the buyer must adapt the protocol to:

- Robot hardware limits
- Venue map and navigation stack
- Operator escalation policy
- Local cultural protocol preferences
- Safety and privacy requirements
- ROS 2 distribution and action interface names

## Commercial Status

Draft-ready for marketplace review. Pricing is intentionally not included until RoboMarket marketplace pricing rules are finalized.
