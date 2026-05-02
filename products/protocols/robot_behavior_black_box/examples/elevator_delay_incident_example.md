# Elevator Delay Incident — Example

## Event summary

A hotel delivery robot waited at the lobby elevator bank longer than expected during a busy evening period. Staff completed the delivery manually after operator notification.

## Structured event fields

- Robot ID: `hotel-delivery-bot-01`
- Zone: `lobby_elevator_bank`
- Task state: `waiting_for_elevator`
- Review signal: `wait_time_exceeded_expected_threshold`
- Human override: `true`
- Outcome: staff completed delivery manually after delay
- Severity: `medium`

## Root-cause hypothesis

Elevator wait handling was underspecified for peak-hour conditions.

## Evidence needed

- Elevator access policy
- Robot event log from the vendor platform
- Staff handoff notes
- Peak traffic schedule

## Corrective action recommendations

1. Add a defined elevator-wait timeout.
2. Notify concierge after threshold is exceeded.
3. Retry once before manual fallback.
4. Update the delivery SOP with a peak-hour exception path.

## Review status

This is an example report and must be replaced with site-specific evidence during real review.
