"""tests/test_retrieval.py — validate retrieval for ollama_rag (no Ollama needed)."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from langchain_core.documents import Document

_TEST_DOCS = [
    Document(page_content="Articulated robots have 4-6 joints for welding and assembly.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 0}),
    Document(page_content="Cobots comply with ISO/TS 15066 for safe human-robot collaboration.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 1}),
    Document(page_content="OPC UA is the recommended protocol for Industry 4.0 integrations.",
             metadata={"source": "kb.txt", "page": -1, "chunk_index": 2}),
    Document(page_content="FANUC, KUKA, ABB, Yaskawa, and Universal Robots are top brands.",
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
    persist_dir = tmp_path_factory.mktemp("chroma_ollama") / "store"
    persist_dir.mkdir(parents=True, exist_ok=True)
    store = Chroma.from_documents(
        documents=_TEST_DOCS, embedding=fake_embeddings,
        persist_directory=str(persist_dir), collection_name="test_ollama_rag",
    )
    return store, persist_dir


def test_store_created(chroma_store): assert chroma_store[0] is not None
def test_store_persists(chroma_store): assert chroma_store[1].exists()
def test_retrieve_returns_results(chroma_store):
    store, _ = chroma_store
    assert len(store.similarity_search_with_relevance_scores("robot brands", k=2)) > 0

def test_index_with_fake_embeddings(tmp_path, fake_embeddings):
    from retrieval.retriever import index
    import config as cfg
    original = cfg.Config.CHROMA_BASE_DIR
    cfg.Config.CHROMA_BASE_DIR = tmp_path / ".chroma"
    try:
        store = index([_TEST_DOCS[0]], "test-ollama-fake", embeddings=fake_embeddings)
        assert store is not None
    finally:
        cfg.Config.CHROMA_BASE_DIR = original

def test_retrieve_module_function(chroma_store):
    from retrieval.retriever import retrieve
    store, _ = chroma_store
    results = retrieve("industry 4.0 protocol", store, k=2)
    assert len(results) > 0
