# rag-as-a-service

> **Category:** RAG — API Service &nbsp;|&nbsp; **Complexity:** ⭐⭐⭐ Advanced  
> **Stack:** Python · FastAPI · LangChain · Chroma · OpenAI

A production-grade **RAG microservice** exposing a REST API. Index documents and query them programmatically via simple HTTP endpoints — no UI required. Suitable for integration with any application or platform.

---

## What it does

`rag-as-a-service` wraps the full RAG pipeline in a FastAPI application:

```
POST /index  →  chunk + embed documents  →  store in Chroma
POST /query  →  retrieve + generate  →  grounded JSON answer
GET  /health →  service health check
```

---

## Features

- 🚀 **REST API** — clean JSON interface over FastAPI
- 📝 **Auto-generated OpenAPI docs** — interactive Swagger UI at `/docs`
- 📄 **Plain-text document ingestion** — send document text directly in request body
- 💾 **Named persistent stores** — manage multiple independent Chroma collections via `store_id`
- 🔗 **Source citations** — every answer includes source excerpts with relevance scores
- 📊 **Confidence scoring** — `high / medium / low`
- 🐳 **Docker-ready** — single `docker compose up` to deploy

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| API framework | FastAPI |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | Chroma (persistent, on disk) |
| LLM | OpenAI `gpt-4o-mini` |
| RAG framework | LangChain (LCEL chain) |
| Schema validation | Pydantic v2 |

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

### Option A — Local

```bash
cd ai_products/rag/rag-as-a-service

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

python app.py
# or: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
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
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat completion model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `800` | Max characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Chunks per query |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |

---

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "robomarket-rag-api"}
```

### Index Documents

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "my-kb",
    "documents": ["RoboMarket is a B2B marketplace for industrial robots and cobots. ..."],
    "source_names": ["overview.txt"]
  }'
```

Response (201 Created):
```json
{
  "store_id": "my-kb",
  "chunks_indexed": 12,
  "message": "Successfully indexed 12 chunks into store 'my-kb'."
}
```

### Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "my-kb",
    "query": "What robot brands are available?",
    "k": 4
  }'
```

Response (200 OK):
```json
{
  "store_id": "my-kb",
  "query": "What robot brands are available?",
  "answer": "RoboMarket offers FANUC, KUKA, ABB, Yaskawa, and Universal Robots...",
  "sources": [{"document": "overview.txt", "page_or_chunk": 2, "score": 0.87, "excerpt": "..."}],
  "confidence": "high",
  "retrieved_chunks": 4
}
```

### Interactive Docs

Navigate to **http://localhost:8000/docs** for the Swagger UI with full endpoint documentation.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests do **not** require a real OpenAI API key. API tests use `FakeEmbeddings` and mock the LLM.

| Test file | What it validates |
|-----------|-------------------|
| `tests/test_smoke.py` | All modules importable, core functions callable, health endpoint |
| `tests/test_ingestion.py` | File and text ingestion, metadata, error handling |
| `tests/test_api.py` | FastAPI endpoints: health, 404, 503, 422, end-to-end index+query |

---

## Error Responses

| Status | Trigger |
|--------|---------|
| 422 | Invalid `store_id` pattern, mismatched `source_names`, empty documents |
| 404 | Query against a non-existent store |
| 503 | `OPENAI_API_KEY` not configured |
| 500 | Indexing or generation failure |

---

## Known Limitations

- **No authentication** — add an API gateway or middleware for production.
- **No cross-store deduplication** — re-indexing the same documents adds duplicate vectors. Delete `.chroma/<store_id>/` to reset a store.
- **In-process Chroma** — for high-concurrency deployments, consider using Chroma's HTTP client pointing at a separate Chroma server container.

---

## License

MIT — see [LICENSE](../../../LICENSE) in the repository root.


## Sellable Package Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` using `.env.example` (set `OPENAI_API_KEY`).
3. Start API: `python app.py`
4. Health check: `GET /health`
5. Index docs: `POST /index`
6. Query docs: `POST /query`

### Example

```bash
curl -X POST http://localhost:8000/index \
  -H 'content-type: application/json' \
  -d '{"store_id":"demo","documents":["RoboMarket offers protocol packs."]}'
```
