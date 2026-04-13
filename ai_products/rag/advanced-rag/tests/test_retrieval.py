"""tests/test_retrieval.py — validate retrieval for advanced_rag (no API key needed)."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from langchain_core.documents import Document

_TEST_DOCS = [
    Document(page_content="Articulated robots are used for welding and assembly.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 0}),
    Document(page_content="Cobots comply with ISO/TS 15066 for safe human-robot collaboration.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 1}),
    Document(page_content="FANUC, KUKA, ABB, and Universal Robots are top brands.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 2}),
    Document(page_content="RoboMarket charges 1.5-3.5 percent transaction fees.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 3}),
]


@pytest.fixture(scope="module")
def fake_embeddings():
    try:
        from langchain_community.embeddings.fake import FakeEmbeddings
    except ImportError:
        from langchain_core.embeddings.fake import FakeEmbeddings
    return FakeEmbeddings(size=256)


@pytest.fixture(scope="module")
def chroma_store(tmp_path_factory, fake_embeddings):
    from langchain_chroma import Chroma
    persist_dir = tmp_path_factory.mktemp("chroma_adv") / "store"
    persist_dir.mkdir(parents=True, exist_ok=True)
    store = Chroma.from_documents(
        documents=_TEST_DOCS, embedding=fake_embeddings,
        persist_directory=str(persist_dir), collection_name="test_advanced",
    )
    return store, persist_dir


def test_store_created(chroma_store): assert chroma_store[0] is not None
def test_store_persists(chroma_store): assert chroma_store[1].exists()

def test_retrieve_no_rerank_no_hybrid(chroma_store):
    from retrieval.retriever import retrieve
    store, _ = chroma_store
    results = retrieve("robot brands", store, k=3, rerank=False, hybrid=False)
    assert len(results) > 0

def test_retrieve_hybrid_only(chroma_store):
    from retrieval.retriever import retrieve
    store, _ = chroma_store
    results = retrieve("cobots safety", store, k=3, rerank=False, hybrid=True)
    assert len(results) > 0

def test_index_with_fake_embeddings(tmp_path, fake_embeddings):
    from retrieval.retriever import index
    import config as cfg
    original = cfg.Config.CHROMA_BASE_DIR
    cfg.Config.CHROMA_BASE_DIR = tmp_path / ".chroma"
    try:
        store = index([_TEST_DOCS[0]], "adv-test-fake", embeddings=fake_embeddings)
        assert store is not None
    finally:
        cfg.Config.CHROMA_BASE_DIR = original
