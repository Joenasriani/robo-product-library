# robo-output-validation-loop

Category: control
Purpose: Validate output and retry on failure.

## What it does
- catches malformed output
- improves production reliability
- supports self-correction

## Loop
1. generate
2. validate
3. identify mismatch
4. retry with correction instruction
5. stop only when valid

## Example correction instruction
Your last answer failed validation.
Fix only the following:
- missing field: score
- invalid enum: recommended_action
Return corrected output only.
