# Validation Checklist

## Product-Readiness Checks

- [ ] Product has a standalone folder under `products/protocols/`.
- [ ] Product has a manifest with clear buyer, use case, deliverables, limitations, and commercial status.
- [ ] Product does not claim certification, legal approval, religious authority, or guaranteed deployment compatibility.
- [ ] Product has a structured protocol file that can be reviewed by robotics developers.
- [ ] Product includes integration notes and ROS 2 action mapping.
- [ ] Pricing is not invented inside the repo.

## Technical Validation

- [ ] `protocol.json` is valid JSON.
- [ ] Every state has a clear description.
- [ ] State Zero is explicitly defined.
- [ ] Priority interrupts have ordered priority values.
- [ ] Human safety outranks all service actions.
- [ ] Operator override can stop or redirect robot behavior.
- [ ] Gahwa service flow has acceptance, decline, blocked-path, and uncertainty branches.
- [ ] Low-confidence sensor cases route to `HUMAN_HANDOFF`.
- [ ] ROS 2 action names are mapped to suggested interfaces.

## Deployment Validation

- [ ] Venue map has safe greeting, service, yield, and return poses.
- [ ] Robot can stop safely at low speed near humans.
- [ ] Robot can maintain minimum social distance thresholds.
- [ ] Robot can detect blocked route or unsafe approach conditions.
- [ ] Operator can pause, resume, and force human handoff.
- [ ] Text-to-speech content is reviewed by the venue owner.
- [ ] Gesture library is reviewed for cultural appropriateness.
- [ ] Privacy-sensitive perception features are disabled unless explicitly approved.

## Simulation Validation

- [ ] Test elder/VIP entry while robot is in service flow.
- [ ] Test blocked path during gahwa approach.
- [ ] Test human entering safety radius.
- [ ] Test audio stop command.
- [ ] Test privacy/quiet zone behavior.
- [ ] Test low-confidence recipient ranking.
- [ ] Test handover failure.
- [ ] Test successful return to State Zero.

## Sale Boundary

This product can be listed as a downloadable protocol pack only if the listing clearly states that it is a structured implementation reference and not a turnkey certified robot safety system.
