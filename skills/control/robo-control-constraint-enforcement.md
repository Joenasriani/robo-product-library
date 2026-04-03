# robo-control-constraint-enforcement

Category: control
Purpose: Force hard boundaries.

## What it does
- preserves non-negotiable requirements
- protects product logic from drift

## Constraint examples
- do not rename endpoints
- do not change enums
- do not add fake features
- do not output markdown
- do not merge files

## Pattern
Non-negotiable constraints:
1. <constraint>
2. <constraint>
3. <constraint>

If any output violates a constraint, regenerate.
