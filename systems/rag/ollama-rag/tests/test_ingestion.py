"""tests/test_ingestion.py — validate ingestion for ollama_rag."""

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
        "RoboMarket connects buyers and sellers of industrial robots.\n"
        "Cobots can work alongside humans safely.\n"
        "FANUC, KUKA, ABB, and Universal Robots are leading brands.\n" * 10
    )
    p = tmp_path / "kb.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_txt_ingest_produces_chunks(sample_txt): assert len(ingest(sample_txt)) > 0
def test_chunks_have_source_metadata(sample_txt):
    for c in ingest(sample_txt): assert c.metadata.get("source") == sample_txt.name
def test_chunks_have_chunk_index(sample_txt):
    chunks = ingest(sample_txt)
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))
def test_chunks_have_page_minus_one(sample_txt):
    for c in ingest(sample_txt): assert c.metadata.get("page") == -1
def test_chunk_content_non_empty(sample_txt):
    for c in ingest(sample_txt): assert c.page_content.strip()

def test_unsupported_extension_raises(tmp_path):
    bad = tmp_path / "data.csv"
    bad.write_text("a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest(bad)

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest(Path("/nonexistent/doc.txt"))

def test_sample_data_ingests():
    sample = _APP_DIR / "sample_data" / "robomarket_local_kb.txt"
    if not sample.exists():
        pytest.skip("sample_data/robomarket_local_kb.txt not found")
    chunks = ingest(sample)
    assert len(chunks) > 0
    assert any("RoboMarket" in c.page_content for c in chunks)
