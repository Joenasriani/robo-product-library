"""tests/test_smoke.py — smoke tests for advanced_rag."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def test_config_imports():
    from config import Config
    assert Config.OPENAI_MODEL
    assert Config.RERANK_TOP_K > 0
    assert 0 < Config.BM25_WEIGHT < 1
    assert 0 < Config.VECTOR_WEIGHT < 1

def test_ingestion_imports():
    from ingestion.loader import ingest
    assert callable(ingest)

def test_retrieval_imports():
    from retrieval.retriever import index, load_store, retrieve, store_exists
    for fn in (index, load_store, retrieve, store_exists):
        assert callable(fn)

def test_generation_imports():
    from generation.chain import generate
    assert callable(generate)

def test_shared_theme_imports():
    from shared.ui.theme import apply_theme, status_badge, TOKENS
    assert callable(apply_theme)
    assert callable(status_badge)
    assert "accent" in TOKENS
