"""retrieval.retriever — Hybrid search (BM25 + vector) + cross-encoder reranking.

Pipeline:
  1. Vector similarity search (Chroma) retrieves candidate chunks.
  2. BM25 keyword search fuses additional signal (if HYBRID_SEARCH_ENABLED).
  3. Scores are fused using configurable weights.
  4. A cross-encoder model re-ranks the fused results (requires sentence-transformers).
  5. Top RERANK_TOP_K chunks are returned.
"""

import json
import logging
import os
import re
import time
import traceback
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from config import Config

logger = logging.getLogger(__name__)


Chunk = tuple[Document, float]


def index(
    documents: list[Document],
    store_id: str,
    embedding_model: Optional[str] = None,
    embeddings: Optional[Embeddings] = None,
) -> Chroma:
    """Embed documents and write into a persistent Chroma collection."""
    t0 = time.monotonic()
    collection_name = _validate_store_id(store_id)
    persist_dir = _chroma_dir()
    if embeddings is None:
        embeddings = _make_embeddings(embedding_model)
    try:
        store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=str(persist_dir),
            collection_name=collection_name,
        )
    except Exception as exc:
        _log_error("indexing", str(exc), traceback.format_exc())
        raise
    duration_ms = int((time.monotonic() - t0) * 1000)
    logger.info(json.dumps({"status": "ok", "store_id": store_id, "vectors": len(documents), "ms": duration_ms}))
    return store


def load_store(store_id: str, embedding_model: Optional[str] = None) -> Chroma:
    """Load an existing persistent Chroma store from disk."""
    collection_name = _validate_store_id(store_id)
    persist_dir = _chroma_dir()
    embeddings = _make_embeddings(embedding_model)
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
        collection_name=collection_name,
    )


def retrieve(
    query: str,
    store: Chroma,
    k: int = Config.RETRIEVAL_K,
    rerank: bool = True,
    hybrid: bool = Config.HYBRID_SEARCH_ENABLED,
) -> list[Chunk]:
    """Retrieve with optional hybrid search and cross-encoder reranking.

    Args:
        query:  User query.
        store:  Loaded Chroma store.
        k:      Number of initial candidates to retrieve.
        rerank: Apply cross-encoder reranking (requires sentence-transformers).
        hybrid: Enable BM25 + vector fusion.
    """
    t0 = time.monotonic()

    try:
        vector_results: list[Chunk] = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as exc:
        _log_error("retrieval", str(exc), traceback.format_exc())
        raise

    if not vector_results:
        return []

    candidates = list(vector_results)

    if hybrid:
        try:
            candidates = _hybrid_fusion(query, candidates, k)
        except Exception:
            logger.warning("BM25 hybrid fusion failed — falling back to vector-only results.")

    if rerank and Config.RERANK_MODEL and Config.RERANK_MODEL.lower() != "none":
        try:
            candidates = _rerank(query, candidates, Config.RERANK_TOP_K)
        except Exception:
            logger.warning("Reranking failed — returning un-reranked results.")
            candidates = candidates[:Config.RERANK_TOP_K]
    else:
        candidates = candidates[:Config.RERANK_TOP_K]

    duration_ms = int((time.monotonic() - t0) * 1000)
    top_score = candidates[0][1] if candidates else 0.0
    logger.info(json.dumps({
        "status": "ok", "chunks": len(candidates),
        "top_score": round(top_score, 4), "ms": duration_ms,
    }))
    return candidates


def store_exists(store_id: str) -> bool:
    """Return True if a Chroma collection indexed under store_id has documents."""
    try:
        collection_name = _validate_store_id(store_id)
        persist_dir = _chroma_dir()
        if not persist_dir.exists():
            return False
        import chromadb
        client = chromadb.PersistentClient(path=str(persist_dir))
        names = [c.name for c in client.list_collections()]
        return collection_name in names
    except Exception:
        return False


def _hybrid_fusion(query: str, vector_results: list[Chunk], k: int) -> list[Chunk]:
    """Fuse BM25 and vector scores using configurable weights."""
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        return vector_results

    docs = [chunk for chunk, _ in vector_results]
    tokenized_corpus = [doc.page_content.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query.lower().split())

    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    fused: list[Chunk] = []
    for i, (doc, vec_score) in enumerate(vector_results):
        bm25_score = bm25_scores[i] / max_bm25
        fused_score = Config.VECTOR_WEIGHT * vec_score + Config.BM25_WEIGHT * bm25_score
        fused.append((doc, fused_score))

    fused.sort(key=lambda x: x[1], reverse=True)
    return fused[:k]


def _rerank(query: str, candidates: list[Chunk], top_k: int) -> list[Chunk]:
    """Apply cross-encoder reranking and return top_k results."""
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(Config.RERANK_MODEL)
    pairs = [(query, doc.page_content) for doc, _ in candidates]
    scores = model.predict(pairs)

    reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [(chunk, float(score)) for (chunk, _), score in reranked[:top_k]]


def _validate_store_id(store_id: str) -> str:
    """Validate and return a safe store_id used only as a Chroma collection name."""
    import os as _os
    safe_id = _os.path.basename(re.sub(r"[^A-Za-z0-9_\-]", "", store_id))
    if not safe_id or len(safe_id) > 128:
        raise ValueError(f"Invalid store_id '{store_id}'.")
    return safe_id


def _chroma_dir() -> Path:
    """Return the fixed Chroma persist directory — not derived from user input."""
    path = Config.CHROMA_BASE_DIR.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _make_embeddings(model: Optional[str] = None) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=model or Config.OPENAI_EMBEDDING_MODEL,
        openai_api_key=Config.OPENAI_API_KEY,
    )


def _log_error(stage, message, tb):
    logger.error(json.dumps({"status": "error", "stage": stage, "message": message, "traceback": tb}))
