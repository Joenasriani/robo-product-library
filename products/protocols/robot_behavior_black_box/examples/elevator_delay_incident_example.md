# Service Access Delay — Example

## Event summary

A facility robot waited at a service access point longer than expected during a busy period. Staff completed the handoff manually after operator notification.

## Structured event fields

- Robot ID: `hotel-delivery-bot-01`
- Zone: `lobby_elevator_bank`
- Task state: `waiting_for_service_access`
- Review signal: `wait_time_exceeded_expected_threshold`
- Human override: `true`
- Outcome: staff completed handoff after delay
- Severity: `medium`

## Root-cause hypothesis

Service access wait handling was underspecified for peak activity conditions.

## Evidence needed

- Access policy
- Robot event log from the vendor platform
- Staff handoff notes
- Peak activity schedule

## Corrective action recommendations

1. Add a defined wait timeout.
2. Notify operator after threshold is exceeded.
3. Retry once before manual fallback.
4. Update the operating procedure with a peak-period exception path.

## Review status

This is an example report and must be replaced with site-specific evidence during real review.
