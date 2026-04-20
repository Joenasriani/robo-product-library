"""tests/test_smoke.py — smoke tests for tool_use_rag."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def test_config_imports():
    from config import Config
    assert Config.OPENAI_MODEL
    assert Config.AGENT_MAX_ITERATIONS > 0


def test_ingestion_imports():
    from ingestion.loader import ingest
    assert callable(ingest)


def test_retrieval_imports():
    from retrieval.retriever import index, load_store, retrieve, store_exists, make_retrieval_tool
    for fn in (index, load_store, retrieve, store_exists, make_retrieval_tool):
        assert callable(fn)


def test_generation_imports():
    from generation.chain import run_agent
    assert callable(run_agent)


def test_shared_theme_imports():
    from shared.ui.theme import apply_theme, status_badge, TOKENS
    assert callable(apply_theme)
    assert callable(status_badge)
    assert "accent" in TOKENS


def test_status_badge_returns_html():
    from shared.ui.theme import status_badge
    for state in ("idle", "success", "error"):
        result = status_badge(state)
        assert "<span" in result
