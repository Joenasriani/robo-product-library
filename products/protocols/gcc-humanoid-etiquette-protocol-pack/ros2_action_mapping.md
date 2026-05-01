# ROS 2 Action Mapping

## Purpose

This file maps the GCC Humanoid Etiquette Protocol Pack to ROS 2-compatible actions and services. It is written as an integration reference for robotics developers, not as a claim that every robot exposes these exact interfaces out of the box.

## Recommended Namespace

`/humanoid_etiquette`

## Core Interfaces

| Protocol Output | Suggested ROS 2 Interface | Purpose | Required Adapter Work |
|---|---|---|---|
| `NavigateToPose` | `nav2_msgs/action/NavigateToPose` | Move to greeting, service, or yield pose | Map semantic poses to coordinates |
| `FollowWaypoints` | `nav2_msgs/action/FollowWaypoints` | Execute escort or multi-guest service path | Venue map and waypoint planner required |
| `Speak` | `robot_interfaces/action/Speak` | Deliver localized greeting, offer, and escalation messages | Connect to robot TTS stack |
| `PlayGesture` | `robot_interfaces/action/PlayGesture` | Trigger respectful greeting, offer, idle, and yield gestures | Map gesture names to robot motion library |
| `SetFaceExpression` | `robot_interfaces/action/SetFaceExpression` | Set neutral, welcoming, low-attention, or handoff expression | Requires robot display/face API |
| `ServeItem` | `robot_interfaces/action/ServeItem` | Controlled item handover for gahwa cup or tray item | Requires manipulator or tray handover adapter |
| `StopMotion` | `robot_interfaces/srv/StopMotion` | Immediate controlled stop for safety or override | Must connect to motion controller stop service |
| `YieldPath` | `robot_interfaces/action/YieldPath` | Move aside while preserving social clearance | Requires local planner and safe-side logic |
| `RequestHumanAssistance` | `robot_interfaces/srv/RequestHumanAssistance` | Escalate ambiguous, unsafe, or etiquette-sensitive cases | Connect to operator dashboard or alerting system |

## Message Key Examples

The protocol intentionally uses `text_key` values instead of hardcoded phrases so the buyer can localize Arabic, English, or bilingual output.

Suggested keys:

- `formal_welcome`
- `priority_guest_greeting`
- `gahwa_offer_formal`
- `safety_pause_polite`
- `operator_override_acknowledged`
- `human_assistance_requested`
- `minimal_or_silent_mode`

## Integration Flow

1. Parse `protocol.json` into the robot behavior engine.
2. Bind each protocol output action to a robot-specific ROS 2 action or service.
3. Connect perception events from vision, lidar, audio, and operator controls.
4. Validate interrupt priority order before enabling autonomous service behavior.
5. Run the validation checklist in simulation and in a controlled venue test.

## Implementation Boundary

This pack does not include robot drivers, perception models, motion planners, or manipulator control software. The buyer or integrator must provide the robot-specific adapter layer.
