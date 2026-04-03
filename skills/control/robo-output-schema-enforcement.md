# robo-output-schema-enforcement

Category: control
Purpose: Enforce fixed output fields and types.

## What it does
- aligns output with expected schema
- supports validators and downstream automation

## Best practice
- specify required keys
- specify allowed enums
- specify min/max ranges
- reject extra keys if strictness matters

## Example
Allowed values:
- recommended_action: pursue | review | skip
- risk_level: low | medium | high

Required:
- summary
- key_requirements
- score
- reasoning
