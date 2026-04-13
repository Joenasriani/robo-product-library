# RAG Products — AI Product Library

> **Folder:** `ai_products/rag/`  
> **Category:** Retrieval-Augmented Generation (RAG)

Five production-ready RAG applications for the RoboMarket platform — from a simple chain to an advanced hybrid pipeline. Each product is self-contained, fully documented, and includes tests, Docker support, and `.env.example`.

---

## Products

| # | Product | Stack | Complexity | Port |
|---|---------|-------|------------|------|
| 1 | [simple-rag-chain](#simple-rag-chain) | Streamlit · OpenAI · Chroma | ⭐ Beginner | 8501 |
| 2 | [tool-use-rag](#tool-use-rag) | Streamlit · LangChain ReAct · OpenAI | ⭐⭐ Intermediate | 8502 |
| 3 | [ollama-rag](#ollama-rag) | Streamlit · Ollama · Chroma | ⭐⭐ Intermediate | 8503 |
| 4 | [rag-as-a-service](#rag-as-a-service) | FastAPI · OpenAI · Chroma | ⭐⭐⭐ Advanced | 8000 |
| 5 | [advanced-rag](#advanced-rag) | Streamlit · Hybrid BM25+Vector · Reranking | ⭐⭐⭐ Advanced | 8504 |

---

## simple-rag-chain

**Path:** [`simple-rag-chain/`](./simple-rag-chain/)  
**What it does:** The foundational RAG app. Upload documents → chunk → embed → index into Chroma → ask questions.  
**Key features:** Persistent Chroma store, source citations, confidence scoring, Streamlit UI.  
**Requires:** OpenAI API key.

```bash
cd simple-rag-chain && pip install -r requirements.txt && streamlit run app.py
```

---

## tool-use-rag

**Path:** [`tool-use-rag/`](./tool-use-rag/)  
**What it does:** An agentic RAG app using the LangChain ReAct framework. The LLM agent autonomously decides when and how to call the retrieval tool — issuing multiple queries if needed.  
**Key features:** Multi-turn retrieval, ReAct loop, tool-use trace, source citations.  
**Requires:** OpenAI API key.

```bash
cd tool-use-rag && pip install -r requirements.txt && streamlit run app.py
```

---

## ollama-rag

**Path:** [`ollama-rag/`](./ollama-rag/)  
**What it does:** A fully local RAG app — no cloud API keys. Embeddings and generation run via Ollama on your machine.  
**Key features:** 100% local, privacy-first, supports any Ollama-compatible model.  
**Requires:** Ollama running with `nomic-embed-text` and `llama3` pulled.

```bash
ollama pull nomic-embed-text && ollama pull llama3
cd ollama-rag && pip install -r requirements.txt && streamlit run app.py
```

---

## rag-as-a-service

**Path:** [`rag-as-a-service/`](./rag-as-a-service/)  
**What it does:** A production-grade RAG microservice exposing a REST API (FastAPI). Index documents and query them programmatically via `POST /index` and `POST /query`.  
**Key features:** OpenAPI docs at `/docs`, multiple named stores, JSON API, Docker-ready.  
**Requires:** OpenAI API key.

```bash
cd rag-as-a-service && pip install -r requirements.txt && python app.py
# API docs: http://localhost:8000/docs
```

---

## advanced-rag

**Path:** [`advanced-rag/`](./advanced-rag/)  
**What it does:** Advanced RAG with hybrid search (BM25 + vector fusion) and cross-encoder reranking for significantly higher retrieval precision.  
**Key features:** Configurable pipeline (toggle hybrid/rerank independently), degradation-graceful, smaller chunks for reranking precision.  
**Requires:** OpenAI API key + `sentence-transformers` (downloaded automatically on first use).

```bash
cd advanced-rag && pip install -r requirements.txt && streamlit run app.py
```

---

## Common Structure

Each product folder follows this layout:

```
<product-name>/
├── app.py                 # Entrypoint (Streamlit or FastAPI)
├── config.py              # Configuration (env vars, safe defaults)
├── .env.example           # Environment variable template
├── requirements.txt       # Pinned/constrained dependencies
├── Dockerfile
├── docker-compose.yml
├── README.md              # Product documentation
├── conftest.py            # pytest path setup
├── ingestion/
│   ├── __init__.py
│   └── loader.py          # Document loading and chunking
├── retrieval/
│   ├── __init__.py
│   └── retriever.py       # Chroma indexing and retrieval
├── generation/
│   ├── __init__.py
│   └── chain.py           # LLM chain / agent
├── shared/
│   └── ui/
│       └── theme.py       # RoboMarket design system (Streamlit apps)
├── sample_data/           # Sample documents for testing
└── tests/
    ├── test_smoke.py      # Import and callable checks (no API key needed)
    ├── test_ingestion.py  # Ingestion pipeline tests
    └── test_retrieval.py  # Retrieval pipeline tests (FakeEmbeddings)
```

---

## Running Tests

From any product directory:

```bash
cd ai_products/rag/<product>
pip install -r requirements.txt
pytest tests/ -v
```

> All test suites run without an OpenAI API key (retrieval tests use `FakeEmbeddings`).

---

## Source

Products ported from [`Joenasriani/robo-rag-apps`](https://github.com/Joenasriani/robo-rag-apps), refactored to be self-contained and sell-ready:
- Each product bundles its `shared/ui` dependency.
- `app.py` sys.path is self-referential (no monorepo parent needed).
- All products have smoke tests, ingestion tests, and retrieval tests.
- `advanced-rag` was created as a new product based on the `advanced_rag/` folder stub in the source repo.
