# robo-prompt-structured-json-output

Category: core
Purpose: Force reliable structured JSON output from an LLM.

## What it does
- Locks output to one JSON object
- Reduces formatting drift
- Improves downstream parsing reliability

## Use when
- building APIs
- generating configs
- returning machine-readable output
- creating agent responses consumed by code

## Prompt pattern
Role:
You are a structured output engine.

Rules:
- Return only valid JSON
- No markdown
- No code fences
- No commentary
- Follow the schema exactly

Schema:
{
  "field_1": "string",
  "field_2": ["string"],
  "field_3": 0
}

Task:
<insert task>

## Inputs
- task
- schema
- constraints

## Outputs
- valid JSON object only

## Failure modes
- adds commentary
- wraps in markdown
- returns invalid keys
- returns malformed JSON

## Hardening
- repeat "Return only valid JSON"
- provide exact schema
- reject extra keys
- add validation loop after generation

## Reuse in agents
- tender analyzer
- protocol generators
- internal admin tools
- entitlement systems
