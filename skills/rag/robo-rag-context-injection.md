# robo-rag-context-injection

Category: rag
Purpose: Inject retrieved context into the prompt safely.

## What it does
- supplies relevant source material
- improves factuality
- narrows answer scope

## Pattern
Context:
<retrieved excerpts>

Instruction:
Answer only using the context above.
If missing, say what is missing.
