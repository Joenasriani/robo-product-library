"""retrieval.retriever — Chroma-backed indexing and retrieval.

Each store is persisted on disk under:
  <app_root>/.chroma/<store_id>/
"""

import json
import logging
import os
import re
import time
import traceback
from pathlib import Path
from typing import Optional, Union

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import Config

logger = logging.getLogger(__name__)


Chunk = tuple[Document, float]


def index(
    documents: list[Document],
    store_id: str,
    embedding_model: Optional[str] = None,
) -> Chroma:
    """Embed documents and write them into a persistent Chroma collection."""
    t0 = time.monotonic()
    persist_dir = _store_path(store_id)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = _make_embeddings(embedding_model)

    try:
        store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=str(persist_dir),
            collection_name=store_id,
        )
    except Exception as exc:
        _log_error("indexing", str(exc), traceback.format_exc())
        raise

    duration_ms = int((time.monotonic() - t0) * 1000)
    _log_indexing(store_id, len(documents), duration_ms)
    return store


def load_store(
    store_id: str,
    embedding_model: Optional[str] = None,
) -> Chroma:
    """Load an existing persistent Chroma store from disk."""
    persist_dir = _store_path(store_id)
    if not persist_dir.exists():
        raise FileNotFoundError(
            f"No Chroma store found for store_id='{store_id}' at {persist_dir}."
        )
    embeddings = _make_embeddings(embedding_model)
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
        collection_name=store_id,
    )


def retrieve(
    query: str,
    store: Chroma,
    k: int = Config.RETRIEVAL_K,
) -> list[Chunk]:
    """Retrieve the k most relevant chunks from store for query."""
    try:
        results: list[Chunk] = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as exc:
        _log_error("retrieval", str(exc), traceback.format_exc())
        raise

    top_score = results[0][1] if results else 0.0
    _log_retrieval(len(results), top_score)
    return results


def store_exists(store_id: str) -> bool:
    """Return True if a persisted Chroma store exists for store_id."""
    try:
        return _store_path(store_id).exists()
    except ValueError:
        return False


def _store_path(store_id: str) -> Path:
    # Sanitize: use os.path.basename to strip directory separators, then strip any
    # remaining characters outside the allowed set (alphanumeric, hyphen, underscore).
    safe_id = os.path.basename(re.sub(r"[^A-Za-z0-9_\-]", "", store_id))
    if not safe_id or len(safe_id) > 128:
        raise ValueError(
            f"Invalid store_id '{store_id}'. "
            "Use only letters, digits, hyphens, and underscores (max 128 chars)."
        )
    return Config.CHROMA_BASE_DIR.resolve() / safe_id


def _make_embeddings(model: Optional[str] = None) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=model or Config.OPENAI_EMBEDDING_MODEL,
        openai_api_key=Config.OPENAI_API_KEY,
    )


def _log_indexing(store_id, vectors_written, duration_ms):
    logger.info(json.dumps({
        "status": "ok", "store_id": store_id,
        "vectors_written": vectors_written, "duration_ms": duration_ms,
    }))


def _log_retrieval(chunks_returned, top_score):
    logger.info(json.dumps({
        "status": "ok", "chunks_returned": chunks_returned,
        "top_score": round(top_score, 4),
    }))


def _log_error(stage, message, tb):
    logger.error(json.dumps({"status": "error", "stage": stage, "message": message, "traceback": tb}))
