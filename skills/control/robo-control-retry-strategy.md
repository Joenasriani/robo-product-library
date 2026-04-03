# robo-control-retry-strategy

Category: control
Purpose: Define how to recover from bad generations.

## Retry types
- format retry
- schema retry
- missing field retry
- instruction compliance retry
- partial completion retry

## Recommended logic
Retry 1:
- restate missing rule

Retry 2:
- narrow output scope

Retry 3:
- force exact structure

If still failing:
- return partial result + explicit gap
