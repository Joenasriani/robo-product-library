"""App configuration — env vars and constants for rag_as_a_service."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


class Config:
    # ── AI provider (BYOK-first with OPENAI_* backward compatibility) ─────
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai").strip().lower()
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", os.getenv("OPENAI_BASE_URL", "")).strip()
    AI_MODEL: str = os.getenv("AI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()
    AI_EMBEDDING_MODEL: str = os.getenv(
        "AI_EMBEDDING_MODEL",
        os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    ).strip()

    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").strip().lower() == "true"
    DEMO_AI_API_KEY: str = os.getenv("DEMO_AI_API_KEY", "").strip()

    _BYOK_AI_API_KEY: str = os.getenv("AI_API_KEY", "").strip() or os.getenv(
        "OPENAI_API_KEY", ""
    ).strip()
    ACTIVE_AI_API_KEY: str = _BYOK_AI_API_KEY or (
        DEMO_AI_API_KEY if DEMO_MODE else ""
    )
    DEMO_KEY_ACTIVE: bool = bool(DEMO_MODE and not _BYOK_AI_API_KEY and DEMO_AI_API_KEY)

    DEMO_MODE_WARNING: str = (
        "Demo key mode is active. This key is evaluation-only, may be rate-limited "
        "or revoked at any time, and is not intended for production use. "
        "For production, set your own AI_API_KEY."
    )

    # Backward-compatible aliases for existing OPENAI_* usage.
    OPENAI_API_KEY: str = ACTIVE_AI_API_KEY
    OPENAI_MODEL: str = AI_MODEL
    OPENAI_EMBEDDING_MODEL: str = AI_EMBEDDING_MODEL

    # ── Chroma persistence ───────────────────────────────────────────────────
    CHROMA_BASE_DIR: Path = Path(__file__).parent / ".chroma"

    # ── Chunking ─────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # ── Retrieval ────────────────────────────────────────────────────────────
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "4"))

    # ── Server ───────────────────────────────────────────────────────────────
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # ── Answer confidence thresholds ──────────────────────────────────────────
    CONFIDENCE_HIGH: float = 0.75
    CONFIDENCE_MEDIUM: float = 0.50

    @classmethod
    def warnings(cls) -> list[str]:
        warnings: list[str] = []
        if cls.DEMO_KEY_ACTIVE:
            warnings.append(cls.DEMO_MODE_WARNING)
        elif cls.DEMO_MODE and not cls.ACTIVE_AI_API_KEY:
            warnings.append(
                "DEMO_MODE=true but no key is available. Set AI_API_KEY (preferred) "
                "or DEMO_AI_API_KEY for evaluation."
            )
        return warnings
