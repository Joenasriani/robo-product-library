"""retrieval.retriever — Chroma-backed indexing and retrieval using Ollama embeddings."""

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

from config import Config

logger = logging.getLogger(__name__)


Chunk = tuple[Document, float]


def index(
    documents: list[Document],
    store_id: str,
    embeddings: Optional[Embeddings] = None,
) -> Chroma:
    """Embed documents and write into a persistent Chroma collection."""
    t0 = time.monotonic()
    persist_dir = _store_path(store_id)
    persist_dir.mkdir(parents=True, exist_ok=True)
    if embeddings is None:
        embeddings = _make_ollama_embeddings()
    try:
        store = Chroma.from_documents(
            documents=documents, embedding=embeddings,
            persist_directory=str(persist_dir), collection_name=store_id,
        )
    except Exception as exc:
        _log_error("indexing", str(exc), traceback.format_exc())
        raise
    duration_ms = int((time.monotonic() - t0) * 1000)
    logger.info(json.dumps({"status": "ok", "store_id": store_id, "vectors": len(documents), "ms": duration_ms}))
    return store


def load_store(store_id: str, embeddings: Optional[Embeddings] = None) -> Chroma:
    """Load an existing persistent Chroma store from disk."""
    persist_dir = _store_path(store_id)
    if not persist_dir.exists():
        raise FileNotFoundError(f"No Chroma store found for store_id='{store_id}'.")
    if embeddings is None:
        embeddings = _make_ollama_embeddings()
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings, collection_name=store_id,
    )


def retrieve(query: str, store: Chroma, k: int = Config.RETRIEVAL_K) -> list[Chunk]:
    """Retrieve the k most relevant chunks from store."""
    try:
        results: list[Chunk] = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as exc:
        _log_error("retrieval", str(exc), traceback.format_exc())
        raise
    top_score = results[0][1] if results else 0.0
    logger.info(json.dumps({"status": "ok", "chunks": len(results), "top_score": round(top_score, 4)}))
    return results


def store_exists(store_id: str) -> bool:
    try:
        return _store_path(store_id).exists()
    except ValueError:
        return False


def _store_path(store_id: str) -> Path:
    # Sanitize: use os.path.basename to strip directory separators, then strip any
    # remaining characters outside the allowed set (alphanumeric, hyphen, underscore).
    safe_id = os.path.basename(re.sub(r"[^A-Za-z0-9_\-]", "", store_id))
    if not safe_id or len(safe_id) > 128:
        raise ValueError(f"Invalid store_id '{store_id}'.")
    return Config.CHROMA_BASE_DIR.resolve() / safe_id


def _make_ollama_embeddings() -> Embeddings:
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(
        model=Config.OLLAMA_EMBED_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
    )


def _log_error(stage, message, tb):
    logger.error(json.dumps({"status": "error", "stage": stage, "message": message, "traceback": tb}))
