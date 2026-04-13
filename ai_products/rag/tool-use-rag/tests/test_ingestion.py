"""tests/test_ingestion.py — validate ingestion pipeline for tool_use_rag."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from ingestion.loader import ingest


@pytest.fixture()
def sample_txt(tmp_path):
    content = (
        "RoboMarket is a B2B marketplace for industrial robots.\n"
        "It supports FANUC, KUKA, ABB, and Universal Robots.\n"
        "Suppliers must pass a three-stage verification process.\n" * 10
    )
    p = tmp_path / "test_doc.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_txt_ingest_produces_chunks(sample_txt):
    assert len(ingest(sample_txt)) > 0


def test_txt_chunks_have_source_metadata(sample_txt):
    chunks = ingest(sample_txt)
    for chunk in chunks:
        assert chunk.metadata.get("source") == sample_txt.name


def test_txt_chunks_have_chunk_index(sample_txt):
    chunks = ingest(sample_txt)
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))


def test_txt_chunks_have_page_minus_one(sample_txt):
    for chunk in ingest(sample_txt):
        assert chunk.metadata.get("page") == -1


def test_chunk_content_non_empty(sample_txt):
    for chunk in ingest(sample_txt):
        assert chunk.page_content.strip()


def test_unsupported_extension_raises(tmp_path):
    bad = tmp_path / "data.csv"
    bad.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest(bad)


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest(Path("/nonexistent/doc.txt"))


def test_sample_data_ingests():
    sample = _APP_DIR / "sample_data" / "robomarket_faq.txt"
    if not sample.exists():
        pytest.skip("sample_data/robomarket_faq.txt not found")
    chunks = ingest(sample)
    assert len(chunks) > 0
    assert any("RoboMarket" in c.page_content for c in chunks)
