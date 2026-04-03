# robo-output-format-lock

Category: control
Purpose: Lock the model into a required shape.

## What it does
- prevents format drift
- supports machine and human readability

## Common locked formats
- JSON
- YAML
- CSV rows
- markdown table
- numbered fields

## Pattern
Return output in exactly this format:
<format>

Do not add:
- explanation
- intro
- code fences
- extra notes
