# robo-prompt-few-shot-learning

Category: core
Purpose: Improve output quality by giving examples.

## What it does
- shows the model what good output looks like
- stabilizes style and format
- improves classification and transformation tasks

## Use when
- output format matters
- labels matter
- tone consistency matters
- the task is easy to show by example

## Pattern
Instruction
Example 1 input
Example 1 output
Example 2 input
Example 2 output
Now solve:
<new input>

## Benefits
- reduces guesswork
- improves format adherence
- lowers randomness

## Risks
- weak examples create weak outputs
- examples can bias wrong behavior
