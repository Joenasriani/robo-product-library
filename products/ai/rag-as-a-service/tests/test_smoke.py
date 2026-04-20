"""tests/test_smoke.py — smoke tests for rag_as_a_service."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def test_config_imports():
    from config import Config
    assert Config.OPENAI_MODEL
    assert Config.PORT > 0

def test_ingestion_imports():
    from ingestion.loader import ingest, ingest_text
    assert callable(ingest) and callable(ingest_text)

def test_retrieval_imports():
    from retrieval.retriever import index, load_store, retrieve, store_exists
    for fn in (index, load_store, retrieve, store_exists):
        assert callable(fn)

def test_generation_imports():
    from generation.chain import generate
    assert callable(generate)

def test_app_imports():
    import app as api_module
    assert hasattr(api_module, "app")

def test_health_endpoint_sync():
    """Ensure the health endpoint function is importable and returns correct structure."""
    import asyncio
    import app as api_module
    result = asyncio.run(api_module.health())
    assert result["status"] == "ok"
