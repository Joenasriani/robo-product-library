# advanced-rag

> **Category:** RAG — Advanced &nbsp;|&nbsp; **Complexity:** ⭐⭐⭐ Advanced  
> **Stack:** Python · Streamlit · LangChain · Chroma · OpenAI · Sentence Transformers · BM25

An advanced RAG application combining **hybrid search** (BM25 + vector) with **cross-encoder reranking** for significantly higher retrieval precision compared to basic vector search.

---

## What it does

`advanced-rag` augments the standard RAG pipeline with two key enhancements:

```
Upload → Ingest (small chunks) → Embed → Index
                                         ↓
Query → Vector Search (k=5)  →  BM25 Fusion  →  Cross-Encoder Rerank (top 3)  →  Generate
```

### Why this matters
- **BM25 hybrid fusion** captures exact keyword matches that semantic search can miss.
- **Cross-encoder reranking** re-reads each `(query, chunk)` pair jointly for much higher precision than bi-encoder cosine similarity.
- **Smaller chunks** (600 chars vs 800) improve per-chunk coherence for reranking.

---

## Features

- 🔍 **Hybrid search** — weighted BM25 + vector score fusion
- 🏆 **Cross-encoder reranking** — `ms-marco-MiniLM-L-6-v2` by default
- 📄 **Multi-format** — PDF, TXT, Markdown
- ⚙️ **Configurable pipeline** — toggle hybrid and reranking independently via UI
- 💾 **Persistent Chroma store**
- 🔗 **Source citations** with post-rerank confidence scores
- 🎨 **RoboMarket-themed Streamlit UI**

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | Chroma (persistent) |
| Keyword search | `rank-bm25` (BM25Okapi) |
| Reranking | `sentence-transformers` CrossEncoder |
| LLM | OpenAI `gpt-4o-mini` |

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- The `sentence-transformers` reranking model is downloaded automatically on first use (~90 MB).

---

## Setup

### Option A — Local

```bash
cd ai_products/rag/advanced-rag

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
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `600` | Max chars per chunk (smaller for reranking precision) |
| `CHUNK_OVERLAP` | `120` | Overlap between chunks |
| `RETRIEVAL_K` | `5` | Initial candidates from vector search |
| `RERANK_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model |
| `RERANK_TOP_K` | `3` | Chunks passed to generation after reranking |
| `HYBRID_SEARCH_ENABLED` | `true` | Enable BM25 + vector fusion |
| `BM25_WEIGHT` | `0.3` | BM25 score weight in fusion |
| `VECTOR_WEIGHT` | `0.7` | Vector score weight in fusion |

---

## Running Tests

```bash
pytest tests/ -v
```

| Test file | What it validates |
|-----------|-------------------|
| `tests/test_smoke.py` | Config, module imports, theme |
| `tests/test_ingestion.py` | Chunking, metadata, error handling |
| `tests/test_retrieval.py` | Retrieval without rerank, hybrid fusion, store persistence |

> **Note:** The `test_index_with_fake_embeddings` test requires an `OPENAI_API_KEY` for the default embedding path. Use the `embeddings` parameter override for offline testing.

---

## Architecture Notes

### Hybrid Fusion
BM25 scores are normalised to [0, 1] and combined with vector scores:
```
fused_score = VECTOR_WEIGHT × vector_score + BM25_WEIGHT × bm25_score
```

### Cross-Encoder Reranking
The cross-encoder reads each `(query, passage)` pair and produces a relevance score. Unlike bi-encoder similarity, it can use the full attention mechanism between query and document tokens.

### Degradation Gracefully
If `rank-bm25` or `sentence-transformers` are unavailable, the pipeline falls back to vector-only results without crashing.

---

## Known Gaps / Future Work

- **Parent document retriever**: index small chunks, retrieve larger parent passages.
- **Query reformulation**: use the LLM to expand or re-phrase the query before retrieval.
- **Multi-query retrieval**: generate multiple query variants and merge results.
- **Streaming answers**: add async generation with token streaming to the UI.

---

## License

MIT — see [LICENSE](../../../LICENSE) in the repository root.
