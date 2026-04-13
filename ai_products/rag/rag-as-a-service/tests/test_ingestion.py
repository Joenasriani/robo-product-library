"""tests/test_ingestion.py — validate ingestion pipeline for rag_as_a_service."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from ingestion.loader import ingest, ingest_text


@pytest.fixture()
def sample_txt(tmp_path):
    content = (
        "RoboMarket API provides programmatic access to product listings.\n"
        "Authentication uses OAuth 2.0 bearer tokens.\n"
        "Rate limits: 1,000 requests per minute for standard plans.\n" * 10
    )
    p = tmp_path / "api_docs.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_file_ingest_produces_chunks(sample_txt):
    assert len(ingest(sample_txt)) > 0

def test_file_chunks_have_source_metadata(sample_txt):
    for c in ingest(sample_txt):
        assert c.metadata.get("source") == sample_txt.name

def test_file_chunks_have_chunk_index(sample_txt):
    chunks = ingest(sample_txt)
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))

def test_file_chunks_have_page_minus_one(sample_txt):
    for c in ingest(sample_txt):
        assert c.metadata.get("page") == -1

def test_chunk_content_non_empty(sample_txt):
    for c in ingest(sample_txt):
        assert c.page_content.strip()

def test_unsupported_extension_raises(tmp_path):
    bad = tmp_path / "data.json"
    bad.write_text('{"key": "value"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest(bad)

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest(Path("/nonexistent/doc.txt"))

def test_ingest_text_produces_chunks():
    text = (
        "The RoboMarket API supports OAuth 2.0. "
        "Rate limits apply per plan tier. "
    ) * 30
    chunks = ingest_text(text, "inline_doc.txt")
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata.get("source") == "inline_doc.txt"
        assert chunk.metadata.get("page") == -1
        assert "chunk_index" in chunk.metadata

def test_ingest_text_chunk_indices_sequential():
    text = "word " * 1000
    chunks = ingest_text(text, "big_doc.txt")
    indices = [c.metadata["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))

def test_sample_data_ingests():
    sample = _APP_DIR / "sample_data" / "robomarket_api_docs.txt"
    if not sample.exists():
        pytest.skip("sample_data/robomarket_api_docs.txt not found")
    chunks = ingest(sample)
    assert len(chunks) > 0
    assert any("RoboMarket" in c.page_content for c in chunks)
