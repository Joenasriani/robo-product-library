"""retrieval.retriever — Chroma-backed indexing and retrieval for rag_as_a_service."""

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
    embeddings: Optional[Embeddings] = None,
) -> Chroma:
    """Embed documents and write into a persistent Chroma collection."""
    t0 = time.monotonic()
    collection_name = _validate_store_id(store_id)
    persist_dir = _chroma_dir()
    if embeddings is None:
        embeddings = _make_embeddings()
    try:
        store = Chroma.from_documents(
            documents=documents, embedding=embeddings,
            persist_directory=str(persist_dir), collection_name=collection_name,
        )
    except Exception as exc:
        _log_error("indexing", str(exc), traceback.format_exc())
        raise
    duration_ms = int((time.monotonic() - t0) * 1000)
    logger.info(json.dumps({"status": "ok", "store_id": store_id, "vectors": len(documents), "ms": duration_ms}))
    return store


def load_store(store_id: str, embeddings: Optional[Embeddings] = None) -> Chroma:
    """Load an existing persistent Chroma store from disk."""
    collection_name = _validate_store_id(store_id)
    persist_dir = _chroma_dir()
    if embeddings is None:
        embeddings = _make_embeddings()
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings, collection_name=collection_name,
    )


def retrieve(query: str, store: Chroma, k: int = Config.RETRIEVAL_K) -> list[Chunk]:
    """Retrieve the k most relevant chunks."""
    try:
        results: list[Chunk] = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as exc:
        _log_error("retrieval", str(exc), traceback.format_exc())
        raise
    top_score = results[0][1] if results else 0.0
    logger.info(json.dumps({"status": "ok", "chunks": len(results), "top_score": round(top_score, 4)}))
    return results


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


def _make_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=Config.OPENAI_EMBEDDING_MODEL,
        openai_api_key=Config.OPENAI_API_KEY,
    )


def _log_error(stage, message, tb):
    logger.error(json.dumps({"status": "error", "stage": stage, "message": message, "traceback": tb}))
