# Operational Twin Model

An operational twin is a structured planning representation of how a robot task should work inside a facility. It is not a physics simulation and does not control a robot.

## Core objects

| Object | Purpose |
|---|---|
| Zone | Physical or operational area where robot or human activity occurs. |
| Task node | A robot or human action within the workflow. |
| Human actor | Staff role responsible for approval, recovery, or escalation. |
| Escalation rule | What happens when a task cannot complete normally. |
| Failure branch | Anticipated operational exception and fallback path. |
| Safety owner | Human accountable for reviewing the twin before deployment. |

## Required review

Every operational twin must include:

1. Facility assumptions
2. Robot capability assumptions
3. Human intervention points
4. Escalation rules
5. Failure branches
6. Unresolved site questions
7. Safety owner approval status

## Example path

```text
Guest request -> front desk approval -> robot dispatch -> elevator access -> room arrival -> delivery confirmation -> return to dock
```

## Example failure branch

```text
Elevator unavailable -> wait timeout -> notify concierge -> retry once -> manual delivery fallback
```
