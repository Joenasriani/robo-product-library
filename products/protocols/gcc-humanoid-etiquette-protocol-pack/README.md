# GCC Humanoid Etiquette Protocol Pack

Status: product-ready for inquiry-led marketplace review

The GCC Humanoid Etiquette Protocol Pack is a self-contained mini product folder for robotics professionals building humanoid or social service robot behavior in GCC hospitality, majlis, mall concierge, reception, and premium residential contexts.

This product sells a structured behavior protocol pack, not a robot, not firmware, and not a certified safety system.

## Buyer problem

Humanoid service robots in GCC environments need more than generic greeting logic. They need safe spatial behavior, operator override, elder or VIP priority handling, quiet/privacy zone handling, culturally reviewed speech and gesture choices, and clear integration boundaries.

## Included files

- `manifest.yaml` — product metadata and commercial constraints
- `protocol.json` — state-machine protocol with State Zero, priority interrupts, and gahwa service decision tree
- `ros2_action_mapping.md` — suggested ROS 2 action/service mapping
- `integration_notes.md` — implementation guidance for robotics teams
- `validation_checklist.md` — product and deployment-readiness checklist

## What is real now

This mini product currently provides a structured protocol, integration reference, validation checklist, and marketplace-ready metadata. It can be reviewed and sold later as an inquiry-led downloadable protocol pack once marketplace fulfillment rules are finalized.

## Usage

A robotics integrator can use this pack as follows:

1. Read `manifest.yaml` to confirm buyer fit, limitations, and delivery boundary.
2. Load or inspect `protocol.json` as the source behavior schema.
3. Map protocol actions to robot-specific ROS 2 actions/services using `ros2_action_mapping.md`.
4. Adapt speech, gesture, priority handling, and privacy behavior to the venue.
5. Run the checks in `validation_checklist.md` before live deployment.

## Core behavior coverage

- State Zero standby/observation mode
- Human safety priority interrupt
- Operator override interrupt
- Elder/VIP/priority guest interrupt
- Privacy or quiet-zone interrupt
- Gahwa service decision tree
- Confidence-based escalation to human handoff
- ROS 2-oriented action output contract

## What requires integration later

- Robot-specific drivers
- Perception models
- Navigation and map binding
- Speech/TTS localization
- Gesture library binding
- Manipulator or tray handover adapter
- Operator dashboard integration
- Site-specific safety and cultural review

## Operational boundary

This mini-repo is operational as a protocol package and integration reference. It is not operational as a live robot controller, certified safety layer, legal compliance product, or fully automated deployment system.

## Inquiry instruction

For customization or deployment review, send an inquiry to `hello@robomarket.ae` and use this product name as the email subject:

`GCC Humanoid Etiquette Protocol Pack`
