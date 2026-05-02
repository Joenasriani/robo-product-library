# Hotel Delivery Robot Operational Twin — Example

## Normal workflow

```text
Guest request received -> robot dispatch -> elevator access -> room delivery -> return to dock
```

## Human actors

- Front desk operator: confirms task eligibility and dispatch.
- Concierge runner: handles failed delivery or elevator timeout.
- Operations manager: owns safety review and SOP approval.

## Key failure branches

| Failure | Trigger | Fallback |
|---|---|---|
| Elevator unavailable | Wait exceeds 180 seconds | Notify concierge runner and retry once |
| Guest unavailable | No confirmation within 240 seconds | Return item to front desk |
| Corridor blocked | Route blocked by crowd or object | Wait 60 seconds, then return to lobby |

## Open questions

- Is elevator access controlled by API, card, or staff?
- Are guest corridors covered by reliable Wi-Fi?
- Which items are allowed for robot delivery?

## Review status

This twin is ready for integrator review, not deployment certification.
