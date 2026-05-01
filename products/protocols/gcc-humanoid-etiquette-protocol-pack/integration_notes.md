# Integration Notes

## Recommended Implementation Pattern

Use this pack as a behavior-policy layer above the robot navigation, perception, speech, gesture, and manipulation systems.

Suggested architecture:

1. Sensor adapters publish normalized perception events.
2. Protocol engine evaluates priority interrupts before normal task logic.
3. State machine selects the next behavior state.
4. ROS 2 adapter converts protocol actions into robot-specific action/service calls.
5. Operator dashboard receives handoff and uncertainty events.

## Minimal Runtime Components

- ROS 2 node for protocol orchestration
- Perception event normalizer
- Venue semantic map with greeting, yield, service, and return poses
- Action adapter for navigation
- Action adapter for speech
- Action adapter for gestures or face expression
- Optional manipulator/tray service adapter for `ServeItem`
- Operator override service

## Suggested Event Shape

```json
{
  "event_id": "evt_001",
  "timestamp": "2026-05-01T00:00:00Z",
  "source": "vision|lidar|audio|operator_override",
  "type": "human_presence|priority_guest|blocked_path|stop_command|privacy_zone|serve_request",
  "confidence": 0.92,
  "payload": {
    "zone_id": "majlis_entrance",
    "track_id": "anonymous_track_12",
    "distance_m": 1.8
  }
}
```

## Safety Handling

All autonomous service states must be preempted by safety interrupts. A robot should not continue a greeting, service, or escort action if lidar, vision, audio, or operator input indicates unsafe motion, blocked path, distress, or social/privacy conflict.

## Cultural Adaptation Handling

The pack avoids hardcoded identity assumptions. Priority guest and elder handling should be configured through venue-approved tags, operator confirmation, or locally validated perception rules.

The buyer should review:

- Greeting text
- Gesture selection
- Gender-sensitive interaction rules if required by the venue
- Quiet-zone behavior
- VIP/elder priority policy
- Service order expectations

## Privacy Handling

Avoid identity recognition by default. Use anonymous tracks, operator tags, or explicit venue-approved classification only. Do not store raw face, audio, or identity data unless the deployment owner has approved the full data policy.

## Extension Points

Robotics teams can extend the protocol with:

- Venue-specific priority classes
- Additional service workflows
- Multilingual text keys
- Robot-specific gesture libraries
- Queue-management logic
- Simulation replay tests
- Audit logging

## Buyer Implementation Boundary

The downloadable pack gives the buyer the structured protocol and integration contract. The buyer still needs robot-specific engineering before live deployment.
