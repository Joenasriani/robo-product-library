# ollama-rag

> **Category:** RAG — Local / Privacy-First &nbsp;|&nbsp; **Complexity:** ⭐⭐ Intermediate  
> **Stack:** Python · Streamlit · LangChain · Chroma · Ollama (no cloud APIs)

A fully local RAG application using [Ollama](https://ollama.com) for both embeddings and language generation — no OpenAI or other cloud API keys required.

---

## What it does

`ollama-rag` runs the complete RAG pipeline entirely on your hardware:

```
Upload → Ingest → Chunk → Embed (Ollama) → Index (Chroma) → Retrieve → Generate (Ollama LLM)
```

All data stays on your machine. Ideal for privacy-sensitive use cases, offline environments, and organisations that cannot use cloud APIs.

---

## Features

- 🔒 **100% local** — no external API keys, no data leaves your machine
- 🦙 **Ollama-powered** — embeddings via `nomic-embed-text`, generation via `llama3` (or any Ollama model)
- 📄 **Multi-format** — PDF, TXT, Markdown
- 💾 **Persistent Chroma store** — survives restarts
- 🔗 **Source citations** — grounded answers with traceable excerpts
- 🎨 **RoboMarket-themed Streamlit UI**

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Embeddings | Ollama `nomic-embed-text` |
| Vector store | Chroma (persistent, on disk) |
| LLM | Ollama `llama3` |
| RAG framework | LangChain (LCEL chain) |

---

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running

Pull the required models before first run:

```bash
ollama pull nomic-embed-text
ollama pull llama3
```

---

## Setup

### Option A — Local

```bash
cd ai_products/rag/ollama-rag

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env if using non-default Ollama URL or models

# Start Ollama (if not already running)
ollama serve

streamlit run app.py
```

### Option B — Docker

```bash
# 1. Ensure Ollama is running on your host machine
# 2. Build and start the container
docker compose up --build
```

> ℹ️ The Docker Compose file configures `host.docker.internal` so the container can reach Ollama on your host.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model (must be pulled) |
| `OLLAMA_LLM_MODEL` | `llama3` | LLM for generation (must be pulled) |
| `CHUNK_SIZE` | `800` | Max characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Chunks to retrieve per query |

---

## Running Tests

```bash
pytest tests/ -v
```

Tests do **not** require Ollama to be running. Retrieval tests use `FakeEmbeddings`. The generation module is not tested end-to-end (it requires a live Ollama instance), but imports are validated by the smoke test.

| Test file | What it validates |
|-----------|-------------------|
| `tests/test_smoke.py` | All modules importable, core functions callable |
| `tests/test_ingestion.py` | Chunking, metadata, error handling |
| `tests/test_retrieval.py` | Chroma indexing, retrieval, embeddings override |

---

## Performance Notes

- **Embedding speed** depends on your hardware. On a modern CPU: ~50–200 tokens/sec.
- GPU acceleration (via CUDA or Metal) significantly improves throughput.
- `nomic-embed-text` produces 768-dim embeddings; `llama3` (8B) requires ~5 GB RAM.

---

## Known Limitations

- Requires Ollama to be running and models pulled before ingestion or querying.
- The Docker container uses `host.docker.internal` to reach Ollama on the host — works on macOS and Windows; on Linux, add `--add-host=host.docker.internal:host-gateway` or use the host network.
- No API authentication. Add a reverse proxy for production deployments.

---

## License

MIT — see [LICENSE](../../../LICENSE) in the repository root.
