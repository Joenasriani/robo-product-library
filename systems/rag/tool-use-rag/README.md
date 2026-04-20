# tool-use-rag

> **Category:** RAG — Agentic &nbsp;|&nbsp; **Complexity:** ⭐⭐ Intermediate  
> **Stack:** Python · Streamlit · LangChain ReAct · Chroma · OpenAI

An agentic RAG application where an LLM agent autonomously decides when and how to invoke retrieval — iterating with refined queries until it has enough context to answer.

---

## What it does

`tool-use-rag` implements a **ReAct (Reason + Act) agent** loop:

```
Question → Agent thinks → Calls retrieve_documents tool (may repeat) → Synthesises grounded answer
```

Unlike a simple RAG chain, the agent can:
- Issue **multiple retrieval queries** with progressively refined terms
- Decide that **no retrieval is needed** for unanswerable questions
- Explicitly **cite sources** in its final answer

---

## Features

- 🧠 **ReAct agent loop** — LLM reasons before and after each retrieval step
- 🔁 **Multi-turn retrieval** — agent may call the retrieval tool multiple times per query
- 📄 **Multi-format document support** — PDF, TXT, Markdown
- 💾 **Persistent Chroma vector store** — resume any session by Store ID
- 🔗 **Source citations** — extracted from agent trace and displayed with score + excerpt
- 📊 **Confidence scoring** — `high / medium / low` derived from max retrieved score
- 🎨 **RoboMarket-themed Streamlit UI**

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Agent framework | LangChain ReAct agent |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | Chroma (persistent, on disk) |
| LLM | OpenAI `gpt-4o-mini` |

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

### Option A — Local

```bash
cd ai_products/rag/tool-use-rag

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

streamlit run app.py
```

### Option B — Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model for the agent |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `800` | Max characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Chunks retrieved per tool call |
| `AGENT_MAX_ITERATIONS` | `6` | Maximum ReAct loop iterations |

---

## Using the App

1. **Upload documents** — drag `.pdf`, `.txt`, or `.md` files into the uploader.
2. **Set a Store ID** and click **"Ingest & Index"**.
3. **Type a question** and click **"Ask Agent"** — the agent runs its ReAct loop, may call retrieval one or more times, and returns a grounded answer with source citations.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests do **not** require an OpenAI API key. Retrieval tests use `FakeEmbeddings`.

| Test file | What it validates |
|-----------|-------------------|
| `tests/test_smoke.py` | All modules importable, core functions callable |
| `tests/test_ingestion.py` | Chunking, metadata, error handling |
| `tests/test_retrieval.py` | Chroma indexing, retrieval, retrieval tool |

---

## Known Limitations

- Requires `OPENAI_API_KEY` at runtime.
- Long documents may require increasing `AGENT_MAX_ITERATIONS`.
- The ReAct agent can occasionally loop if the LLM produces malformed action strings; `handle_parsing_errors=True` mitigates this.

---

## License

MIT — see [LICENSE](../../../LICENSE) in the repository root.
