# Operational Twin Model

An operational twin is a structured planning representation of how a robot task should work inside a facility. It is not a physics simulation and does not operate a robot.

## Core objects

- Zone: physical or operational area.
- Task node: robot or human action in the workflow.
- Human actor: staff role responsible for approval, recovery, or escalation.
- Escalation rule: what happens when a task cannot complete normally.
- Failure branch: anticipated exception and fallback path.
- Safety owner: human accountable for reviewing the model before deployment.

## Required review

Every operational twin must include facility assumptions, robot capability assumptions, human intervention points, escalation rules, failure branches, unresolved site questions, and safety owner approval status.
