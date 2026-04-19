"""tests/test_ingestion.py — validate ingestion for advanced_rag."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from ingestion.loader import ingest


@pytest.fixture()
def sample_txt(tmp_path):
    content = "RoboMarket is a B2B marketplace for industrial robots. " * 40
    p = tmp_path / "doc.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_ingest_produces_chunks(sample_txt):
    assert len(ingest(sample_txt)) > 0

def test_chunks_have_source(sample_txt):
    for c in ingest(sample_txt):
        assert c.metadata.get("source") == sample_txt.name

def test_chunks_have_chunk_index(sample_txt):
    chunks = ingest(sample_txt)
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))

def test_unsupported_extension_raises(tmp_path):
    bad = tmp_path / "data.csv"
    bad.write_text("a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest(bad)

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest(Path("/nonexistent/doc.txt"))
