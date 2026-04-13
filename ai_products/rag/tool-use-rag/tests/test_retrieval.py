"""tests/test_retrieval.py — validate retrieval and tool for tool_use_rag."""

import sys
from pathlib import Path
import pytest

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from langchain_core.documents import Document

_TEST_DOCS = [
    Document(page_content="RoboMarket is a B2B marketplace for industrial robots.",
             metadata={"source": "faq.txt", "page": -1, "chunk_index": 0}),
    Document(page_content="FANUC, KUKA, ABB, and Universal Robots are available.",
             metadata={"source": "faq.txt", "page": -1, "chunk_index": 1}),
    Document(page_content="Transaction fees range from 1.5% to 3.5%.",
             metadata={"source": "faq.txt", "page": -1, "chunk_index": 2}),
    Document(page_content="Suppliers undergo a three-stage verification process.",
             metadata={"source": "faq.txt", "page": -1, "chunk_index": 3}),
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
    persist_dir = tmp_path_factory.mktemp("chroma_tool_use") / "store"
    persist_dir.mkdir(parents=True, exist_ok=True)
    store = Chroma.from_documents(
        documents=_TEST_DOCS, embedding=fake_embeddings,
        persist_directory=str(persist_dir), collection_name="test_tool_use",
    )
    return store, persist_dir


def test_index_creates_store(chroma_store):
    assert chroma_store[0] is not None


def test_store_persists_to_disk(chroma_store):
    assert chroma_store[1].exists()


def test_retrieve_returns_results(chroma_store):
    store, _ = chroma_store
    assert len(store.similarity_search_with_relevance_scores("robot brands", k=2)) > 0


def test_result_has_document_and_score(chroma_store):
    store, _ = chroma_store
    for doc, score in store.similarity_search_with_relevance_scores("fees", k=2):
        assert isinstance(doc, Document)
        assert isinstance(score, float)
        assert doc.page_content.strip()


def test_retrieve_module_function(chroma_store):
    from retrieval.retriever import retrieve
    store, _ = chroma_store
    results = retrieve("transaction fees", store, k=2)
    assert len(results) > 0


def test_make_retrieval_tool_returns_string(chroma_store):
    from retrieval.retriever import make_retrieval_tool
    store, _ = chroma_store
    tool = make_retrieval_tool(store, k=2)
    result = tool.run("verification process")
    assert isinstance(result, str) and len(result) > 0
