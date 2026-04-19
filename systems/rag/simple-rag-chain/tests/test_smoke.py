"""tests/test_smoke.py — smoke tests for simple_rag_chain.

Verifies that all key modules can be imported and core functions are callable.
No API keys or external services required.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def test_config_imports() -> None:
    from config import Config
    assert Config.OPENAI_MODEL is not None
    assert Config.CHUNK_SIZE > 0
    assert Config.RETRIEVAL_K > 0


def test_ingestion_loader_imports() -> None:
    from ingestion.loader import ingest
    assert callable(ingest)


def test_retrieval_retriever_imports() -> None:
    from retrieval.retriever import index, load_store, retrieve, store_exists
    assert callable(index)
    assert callable(load_store)
    assert callable(retrieve)
    assert callable(store_exists)


def test_generation_chain_imports() -> None:
    from generation.chain import generate
    assert callable(generate)


def test_shared_theme_imports() -> None:
    from shared.ui.theme import apply_theme, status_badge, TOKENS
    assert callable(apply_theme)
    assert callable(status_badge)
    assert isinstance(TOKENS, dict)
    assert "accent" in TOKENS


def test_status_badge_returns_html() -> None:
    from shared.ui.theme import status_badge
    for state in ("idle", "ingesting", "indexing", "querying", "error", "success"):
        result = status_badge(state, state.upper())
        assert isinstance(result, str)
        assert "<span" in result
