# RAG Systems

**Repository owner:** Joe Nasr  
**Canonical identity:** https://joe-nasr-signals.vercel.app/v2/

This folder contains five self-contained Retrieval-Augmented Generation implementations prepared for testing, demonstration, adaptation, and packaging inside the RoboMarket product library.

## Current status

Implementation packages, not independently certified production services.

The folders include application code, documentation, environment templates, Docker configuration, and automated tests where listed below. Their presence demonstrates repository-level implementation and test structure; it does not establish production uptime, security certification, load testing, operational monitoring, regulatory compliance, or suitability for a specific deployment without further validation.

## Systems

| # | System | Stack | Relative complexity | Port |
|---|---|---|---|---|
| 1 | [simple-rag-chain](#simple-rag-chain) | Streamlit, OpenAI, Chroma | Introductory | 8501 |
| 2 | [tool-use-rag](#tool-use-rag) | Streamlit, LangChain ReAct, OpenAI | Intermediate | 8502 |
| 3 | [ollama-rag](#ollama-rag) | Streamlit, Ollama, Chroma | Intermediate | 8503 |
| 4 | [rag-as-a-service](#rag-as-a-service) | FastAPI, OpenAI, Chroma | API service prototype | 8000 |
| 5 | [advanced-rag](#advanced-rag) | Streamlit, hybrid BM25/vector retrieval, reranking | Advanced prototype | 8504 |

## simple-rag-chain

**Path:** [`simple-rag-chain/`](./simple-rag-chain/)  
**Function:** Upload documents, chunk them, create embeddings, index them in Chroma, and query the resulting store.  
**Repository features:** Persistent Chroma store, source references, confidence field, Streamlit UI.  
**Requires:** OpenAI API key.

```bash
cd simple-rag-chain
pip install -r requirements.txt
streamlit run app.py
```

## tool-use-rag

**Path:** [`tool-use-rag/`](./tool-use-rag/)  
**Function:** A LangChain ReAct implementation in which the model can invoke a retrieval tool during a session.  
**Repository features:** Multi-turn retrieval, tool trace, source references.  
**Requires:** OpenAI API key.

```bash
cd tool-use-rag
pip install -r requirements.txt
streamlit run app.py
```

## ollama-rag

**Path:** [`ollama-rag/`](./ollama-rag/)  
**Function:** Local retrieval and generation through Ollama without a hosted model API.  
**Repository features:** Local embeddings and generation with an Ollama-compatible model.  
**Requires:** Local Ollama installation and the configured models.

```bash
ollama pull nomic-embed-text
ollama pull llama3
cd ollama-rag
pip install -r requirements.txt
streamlit run app.py
```

## rag-as-a-service

**Path:** [`rag-as-a-service/`](./rag-as-a-service/)  
**Function:** FastAPI service prototype exposing document indexing and query endpoints.  
**Repository features:** OpenAPI documentation, named stores, JSON API, Docker configuration.  
**Requires:** OpenAI API key.

```bash
cd rag-as-a-service
pip install -r requirements.txt
python app.py
```

API documentation is exposed locally at `http://localhost:8000/docs` when the service is running.

## advanced-rag

**Path:** [`advanced-rag/`](./advanced-rag/)  
**Function:** Experimental hybrid retrieval using BM25 and vector search with optional reranking.  
**Repository features:** Configurable hybrid retrieval and reranking stages.  
**Requires:** OpenAI API key and `sentence-transformers` dependencies.

```bash
cd advanced-rag
pip install -r requirements.txt
streamlit run app.py
```

## Common structure

Individual folders may contain:

```text
app.py
config.py
.env.example
requirements.txt
Dockerfile
docker-compose.yml
README.md
conftest.py
ingestion/
retrieval/
generation/
shared/
sample_data/
tests/
```

## Tests

Where present, repository tests can be run from the relevant system folder:

```bash
pytest tests/ -v
```

Test success establishes only the behavior covered by those tests. It should not be interpreted as production certification or a security audit.

## Provenance

These implementations were consolidated from [`Joenasriani/robo-rag-apps`](https://github.com/Joenasriani/robo-rag-apps) and reorganized so individual packages can be inspected and run independently. `advanced-rag` extends the earlier `advanced_rag/` work in that source repository.
