"""App configuration — env vars and constants for advanced_rag."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


class Config:
    # ── OpenAI ──────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    # ── Chroma persistence ───────────────────────────────────────────────────
    CHROMA_BASE_DIR: Path = Path(__file__).parent / ".chroma"

    # ── Chunking ─────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))

    # ── Retrieval ────────────────────────────────────────────────────────────
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "5"))

    # ── Reranking ────────────────────────────────────────────────────────────
    # Cross-encoder model for reranking retrieved chunks.
    # Set to "" or "none" to disable reranking.
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", "3"))

    # ── Hybrid search (BM25 + vector) ────────────────────────────────────────
    HYBRID_SEARCH_ENABLED: bool = os.getenv("HYBRID_SEARCH_ENABLED", "true").lower() == "true"
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT", "0.3"))
    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT", "0.7"))

    # ── Answer confidence thresholds ──────────────────────────────────────────
    CONFIDENCE_HIGH: float = 0.75
    CONFIDENCE_MEDIUM: float = 0.50
