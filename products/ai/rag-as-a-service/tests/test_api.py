"""tests/test_api.py — FastAPI endpoint tests for rag_as_a_service.

Uses FakeEmbeddings and mocked LLM — no API key required.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import app as api_module


@pytest.fixture()
def fake_embeddings():
    try:
        from langchain_community.embeddings.fake import FakeEmbeddings
    except ImportError:
        from langchain_core.embeddings.fake import FakeEmbeddings
    return FakeEmbeddings(size=256)


@pytest.mark.asyncio
async def test_health_endpoint():
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_query_unknown_store_returns_404():
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://test") as client:
        resp = await client.post(
            "/query",
            json={"store_id": "nonexistent-store-xyz", "query": "test query"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_index_without_api_key_returns_503(monkeypatch):
    import config as cfg
    monkeypatch.setattr(cfg.Config, "ACTIVE_AI_API_KEY", "")
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://test") as client:
        resp = await client.post(
            "/index",
            json={"store_id": "test-store", "documents": ["Some document text."]},
        )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_index_mismatched_source_names_returns_422(monkeypatch):
    import config as cfg
    monkeypatch.setattr(cfg.Config, "ACTIVE_AI_API_KEY", "sk-test")
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://test") as client:
        resp = await client.post(
            "/index",
            json={
                "store_id": "test-store",
                "documents": ["Doc 1", "Doc 2"],
                "source_names": ["only_one.txt"],
            },
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_index_and_query_end_to_end(tmp_path, fake_embeddings, monkeypatch):
    """Full end-to-end: index a document, then query it."""
    import config as cfg
    monkeypatch.setattr(cfg.Config, "ACTIVE_AI_API_KEY", "sk-test")
    monkeypatch.setattr(cfg.Config, "CHROMA_BASE_DIR", tmp_path / ".chroma")

    from httpx import ASGITransport, AsyncClient

    with patch("retrieval.retriever._make_embeddings", return_value=fake_embeddings), \
         patch("app.generate") as mock_generate:

        mock_generate.return_value = {
            "answer": "The API uses OAuth 2.0.",
            "sources": [{
                "document": "inline_doc.txt", "page_or_chunk": 0,
                "score": 0.85, "excerpt": "OAuth 2.0 authentication.",
            }],
            "confidence": "high",
            "retrieved_chunks": 1,
        }

        async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://test") as client:
            idx_resp = await client.post(
                "/index",
                json={
                    "store_id": "e2e-test-store",
                    "documents": ["OAuth 2.0 is used for authentication. Rate limits are 1000 per minute. " * 5],
                    "source_names": ["inline_doc.txt"],
                },
            )
            assert idx_resp.status_code == 201, idx_resp.text
            assert idx_resp.json()["chunks_indexed"] > 0

            q_resp = await client.post(
                "/query",
                json={"store_id": "e2e-test-store", "query": "How does authentication work?"},
            )
            assert q_resp.status_code == 200, q_resp.text
            body = q_resp.json()
            assert body["answer"]
            assert body["confidence"] in ("high", "medium", "low")
