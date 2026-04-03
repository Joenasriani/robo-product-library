# robo-control-self-check-loop

Category: control
Purpose: Make the model review its own result before finalizing.

## What it does
- detects obvious contradictions
- improves completeness
- reduces instruction misses

## Pattern
Before finalizing:
- check every instruction one by one
- verify output format
- verify required fields
- fix any mismatch
- only then return final answer

## Best for
- code generation
- file formatting
- contract-sensitive outputs
- spec generation
