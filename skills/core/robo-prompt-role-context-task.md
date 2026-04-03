# robo-prompt-role-context-task

Category: core
Purpose: Structure prompts using role, context, and task separation.

## What it does
- clarifies model behavior
- reduces ambiguity
- improves consistency across runs

## Pattern
Role:
<who the model is>

Context:
<what environment, constraints, and facts apply>

Task:
<what must be done>

Output:
<required format>

## Use when
- building reusable prompts
- giving a model domain identity
- separating facts from instructions

## Example skeleton
Role:
You are a GCC tender evaluation engine.

Context:
The user provides tender text from GCC procurement environments.
Focus on commercial fit, risk, and action recommendation.

Task:
Analyze the tender and return structured output.

Output:
Return one valid JSON object.

## Reuse in agents
- tender analysis
- outreach generation
- protocol creation
- report writing
