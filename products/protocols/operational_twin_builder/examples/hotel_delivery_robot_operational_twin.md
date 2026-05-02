# Hotel Delivery Robot Operational Twin — Example

## Normal workflow

```text
request_received -> dispatch -> access_review -> delivery -> return_to_dock
```

## Human actors

- Front desk operator: confirms task eligibility.
- Concierge runner: handles fallback handoff.
- Operations manager: owns safety review.

## Failure branch

If the access route is unavailable, concierge handles manual handoff and the twin is updated after review.

## Review status

This example is ready for integrator review, not deployment certification.
