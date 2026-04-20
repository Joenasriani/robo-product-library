"""tests/test_retrieval.py — validate indexing and retrieval pipeline.

Uses FakeEmbeddings — no OpenAI API key required.
"""

import sys
from pathlib import Path

import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from langchain_core.documents import Document

_TEST_DOCS = [
    Document(
        page_content=(
            "RoboMarket is a B2B marketplace that connects buyers and sellers "
            "of industrial robots, cobots, and automation components."
        ),
        metadata={"source": "overview.txt", "page": -1, "chunk_index": 0},
    ),
    Document(
        page_content=(
            "The platform supports FANUC, KUKA, ABB, Yaskawa, and Universal Robots."
        ),
        metadata={"source": "overview.txt", "page": -1, "chunk_index": 1},
    ),
    Document(
        page_content=(
            "Suppliers must pass a three-stage verification: legal entity check, "
            "product authenticity audit, and reference customer validation."
        ),
        metadata={"source": "overview.txt", "page": -1, "chunk_index": 2},
    ),
    Document(
        page_content=(
            "RoboMarket charges a 1.5 to 3.5 percent transaction fee on completed orders."
        ),
        metadata={"source": "pricing.txt", "page": -1, "chunk_index": 0},
    ),
]


@pytest.fixture(scope="module")
def fake_embeddings():
    try:
        from langchain_community.embeddings.fake import FakeEmbeddings
    except ImportError:
        from langchain_core.embeddings.fake import FakeEmbeddings  # type: ignore
    return FakeEmbeddings(size=256)


@pytest.fixture(scope="module")
def chroma_store(tmp_path_factory, fake_embeddings):
    from langchain_chroma import Chroma

    persist_dir = tmp_path_factory.mktemp("chroma_simple") / "store"
    persist_dir.mkdir(parents=True, exist_ok=True)
    store = Chroma.from_documents(
        documents=_TEST_DOCS,
        embedding=fake_embeddings,
        persist_directory=str(persist_dir),
        collection_name="test_store",
    )
    return store, persist_dir


def test_index_creates_store(chroma_store) -> None:
    store, _ = chroma_store
    assert store is not None


def test_store_persists_to_disk(chroma_store) -> None:
    _, persist_dir = chroma_store
    assert persist_dir.exists()


def test_store_can_be_reloaded(chroma_store, fake_embeddings) -> None:
    from langchain_chroma import Chroma

    _, persist_dir = chroma_store
    reloaded = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=fake_embeddings,
        collection_name="test_store",
    )
    assert reloaded is not None


def test_retrieve_returns_results(chroma_store) -> None:
    store, _ = chroma_store
    results = store.similarity_search_with_relevance_scores("robot brands", k=2)
    assert len(results) > 0


def test_retrieve_returns_correct_k(chroma_store) -> None:
    store, _ = chroma_store
    results = store.similarity_search_with_relevance_scores("robots", k=3)
    assert len(results) <= 3


def test_result_contains_document_and_score(chroma_store) -> None:
    store, _ = chroma_store
    results = store.similarity_search_with_relevance_scores("marketplace", k=2)
    for doc, score in results:
        assert isinstance(doc, Document)
        assert isinstance(score, float)
        assert doc.page_content.strip()


def test_chunk_metadata_preserved(chroma_store) -> None:
    store, _ = chroma_store
    results = store.similarity_search_with_relevance_scores("transaction fee pricing", k=4)
    assert len(results) > 0
    sources = [doc.metadata.get("source") for doc, _ in results]
    assert any(s in ("overview.txt", "pricing.txt") for s in sources)


def test_retrieve_with_retriever_module(chroma_store) -> None:
    from retrieval.retriever import retrieve

    store, _ = chroma_store
    results = retrieve("FANUC KUKA ABB robot brands", store, k=2)
    assert len(results) > 0
    for doc, score in results:
        assert doc.page_content.strip()
        assert isinstance(score, float)
