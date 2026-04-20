# simple-rag-chain

> **Category:** RAG — Basic &nbsp;|&nbsp; **Complexity:** ⭐ Beginner  
> **Stack:** Python · Streamlit · LangChain · Chroma · OpenAI

Upload documents, index them into a local vector store, and ask questions answered grounded in your content — with traceable source citations.

---

## What it does

`simple-rag-chain` is a foundational RAG application demonstrating the complete pipeline:

```
Upload → Ingest → Chunk → Embed → Index → Retrieve → Generate → Cite
```

Everything runs locally on your machine. The only external service is the OpenAI API (embeddings + chat completion). The vector index persists on disk across restarts.

---

## Features

- 📄 **Multi-format document support** — PDF, plain text (`.txt`), Markdown (`.md`)
- 🔍 **Persistent Chroma vector store** — survives process restarts; resume any session by Store ID
- 🤖 **Grounded answers** — LLM is constrained to retrieved context only; no hallucination
- 🔗 **Source citations** — every answer includes traceable excerpts from original documents
- 📊 **Confidence scoring** — `high / medium / low` based on top retrieval relevance score
- 🎨 **RoboMarket-themed Streamlit UI** — dark-mode, branded design system

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | Chroma (persistent, on disk) |
| LLM | OpenAI `gpt-4o-mini` |
| RAG framework | LangChain (LCEL chain) |

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

### Option A — Local (recommended for development)

```bash
# 1. Navigate to this product folder
cd ai_products/rag/simple-rag-chain

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Open .env and set OPENAI_API_KEY=sk-...

# 5. Run
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Option B — Docker

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

docker compose up --build
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat completion model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `800` | Max characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between adjacent chunks |
| `RETRIEVAL_K` | `4` | Number of chunks to retrieve per query |

---

## Using the App

1. **Upload documents** — drag `.pdf`, `.txt`, or `.md` files into the file uploader.
2. **Optionally set a Store ID** — name the collection. Using the same ID on restart reuses the existing index (no re-ingestion needed).
3. **Click "Ingest & Index"** — files are chunked and embedded. Status shows `INGESTING → INDEXING → INDEXED`.
4. **Type a question** in the query box.
5. **Click "Ask"** — the app retrieves the most relevant chunks, generates a grounded answer, and displays it alongside source citations.

### Persistent Store

The Chroma vector store is saved under `.chroma/<store_id>/` relative to this folder. On restart, enter the same Store ID to reuse the index without re-ingesting.

---

## Running Tests

```bash
# From this product directory
pytest tests/ -v
```

Tests do **not** require an OpenAI API key. Retrieval tests use `FakeEmbeddings` from `langchain-community`.

| Test file | What it validates |
|-----------|-------------------|
| `tests/test_smoke.py` | All key modules import and core functions are callable |
| `tests/test_ingestion.py` | `.txt`/`.md` ingestion: chunk count, metadata, error handling |
| `tests/test_retrieval.py` | Chroma indexing, persistence, reload, retrieval results, metadata |

---

## Answer Schema

```json
{
  "answer": "...",
  "sources": [
    {
      "document": "filename.pdf",
      "page_or_chunk": 2,
      "score": 0.87,
      "excerpt": "first 220 characters of the chunk..."
    }
  ],
  "confidence": "high | medium | low",
  "retrieved_chunks": 4
}
```

**Confidence** is derived from the top retrieval relevance score:

| Score | Confidence |
|-------|------------|
| ≥ 0.75 | high |
| ≥ 0.50 | medium |
| < 0.50 | low |

---

## Chunking Strategy

| Parameter | Default | Override |
|-----------|---------|---------|
| Splitter | `RecursiveCharacterTextSplitter` | — |
| `chunk_size` | 800 chars | `CHUNK_SIZE` env var |
| `chunk_overlap` | 150 chars | `CHUNK_OVERLAP` env var |

---

## Deploy

### Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3. Set `OPENAI_API_KEY` as a secret in the Streamlit Cloud dashboard.
4. Set the main file path to `app.py`.

### Docker (production)

```bash
docker build -t simple-rag-chain .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... simple-rag-chain
```

---

## Known Limitations

- **No cross-session deduplication**: Re-ingesting the same file into the same store adds duplicate vectors. Clear `.chroma/<store_id>/` to start fresh.
- **PDF page metadata**: Complex or scanned PDFs may produce inaccurate page assignments.
- **No API authentication**: The Streamlit app has no built-in auth. Add a reverse proxy or use Streamlit's built-in auth for production.

---

## License

MIT — see [LICENSE](../../../LICENSE) in the repository root.
