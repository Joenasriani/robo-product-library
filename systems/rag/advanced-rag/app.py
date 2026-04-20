"""advanced_rag — Streamlit entry point.

Advanced RAG features:
  - Hybrid search (BM25 + vector)
  - Cross-encoder reranking
  - Smaller, more precise chunks

Run:
    streamlit run app.py

Requires:
    OPENAI_API_KEY set in .env (see .env.example)
"""

import sys
import tempfile
import traceback
from pathlib import Path

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from config import Config
from generation.chain import generate
from ingestion.loader import ingest
from retrieval.retriever import index as index_docs
from retrieval.retriever import load_store, retrieve, store_exists
from shared.ui.theme import apply_theme, status_badge

st.set_page_config(
    page_title="Advanced RAG — RoboMarket",
    page_icon="🔬",
    layout="wide",
)
apply_theme()


def _init_state() -> None:
    defaults = {
        "store_id": "advanced_rag_default",
        "status": "idle",
        "store": None,
        "last_answer": None,
        "rerank_enabled": True,
        "hybrid_enabled": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


def _validate_api_key() -> bool:
    if not Config.OPENAI_API_KEY:
        st.error(
            "⚠️ **OPENAI_API_KEY** is not set. "
            "Copy `.env.example` to `.env` and add your key, then restart."
        )
        return False
    return True


st.markdown("# 🔬 Advanced RAG")
st.markdown(
    "Hybrid search (BM25 + vector) combined with cross-encoder **reranking** for "
    "higher precision retrieval."
)

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown("### 📥 Ingest Documents")

    uploaded_files = st.file_uploader(
        "Upload one or more documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    store_id_input = st.text_input(
        "Store ID",
        value=st.session_state["store_id"],
    )

    ingest_btn = st.button(
        "⚡ Ingest & Index",
        use_container_width=True,
        disabled=not uploaded_files,
    )

    if ingest_btn:
        if not _validate_api_key():
            st.rerun()

        store_id = store_id_input.strip() or "advanced_rag_default"
        st.session_state["store_id"] = store_id
        all_chunks = []

        with st.spinner("Ingesting…"):
            st.session_state["status"] = "ingesting"
            for uploaded_file in uploaded_files:
                suffix = Path(uploaded_file.name).suffix.lower()
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = Path(tmp.name)
                    chunks = ingest(tmp_path)
                    for c in chunks:
                        c.metadata["source"] = uploaded_file.name
                    all_chunks.extend(chunks)
                    tmp_path.unlink(missing_ok=True)
                except Exception as exc:
                    st.error(f"❌ {uploaded_file.name}: {exc}")

        if all_chunks:
            with st.spinner("Embedding…"):
                st.session_state["status"] = "indexing"
                try:
                    store = index_docs(all_chunks, store_id)
                    st.session_state["store"] = store
                    st.session_state["status"] = "success"
                    st.success(f"✅ Indexed **{len(all_chunks)}** chunks into `{store_id}`")
                except Exception as exc:
                    st.error(f"❌ Indexing failed: {exc}")
                    st.session_state["status"] = "error"

    st.markdown("---")
    st.markdown("### ⚙️ Retrieval Settings")

    rerank = st.toggle("Cross-encoder reranking", value=True)
    hybrid = st.toggle("Hybrid search (BM25 + vector)", value=True)

    if rerank:
        st.markdown(
            f"<small style='color:#8888AA;'>Model: <code>{Config.RERANK_MODEL}</code></small>",
            unsafe_allow_html=True,
        )
    st.markdown(
        f"<small style='color:#8888AA;'>Retrieve k={Config.RETRIEVAL_K} → re-rank to top {Config.RERANK_TOP_K}</small>",
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("### 🔍 Ask a Question")
    query = st.text_area(
        "Your question",
        placeholder="Which safety standards apply to collaborative robots?",
        height=100,
    )

    ask_btn = st.button(
        "🔎 Ask (Advanced RAG)",
        use_container_width=True,
        disabled=not query,
    )

    if ask_btn:
        if not _validate_api_key():
            st.rerun()
        if st.session_state["store"] is None:
            if store_exists(st.session_state["store_id"]):
                try:
                    st.session_state["store"] = load_store(st.session_state["store_id"])
                except Exception as exc:
                    st.error(f"❌ {exc}")
                    st.stop()
            else:
                st.warning("⚠️ Ingest or load a store first.")
                st.stop()

        with st.spinner("Retrieving (hybrid + rerank)…"):
            try:
                chunks = retrieve(
                    query,
                    st.session_state["store"],
                    k=Config.RETRIEVAL_K,
                    rerank=rerank,
                    hybrid=hybrid,
                )
                answer = generate(query, chunks)
                st.session_state["last_answer"] = answer
            except Exception as exc:
                st.error(f"❌ {exc}")
                st.session_state["status"] = "error"
                st.stop()

    if st.session_state["last_answer"]:
        ans = st.session_state["last_answer"]
        conf_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(ans["confidence"], "⚪")

        st.markdown("#### Answer")
        st.markdown(ans["answer"])
        st.markdown(
            f"**Confidence:** {conf_color} {ans['confidence'].capitalize()} &nbsp;|&nbsp; "
            f"**Chunks (post-rerank):** {ans['retrieved_chunks']}"
        )

        if ans["sources"]:
            st.markdown("#### Sources")
            for src in ans["sources"]:
                loc = src["page_or_chunk"]
                loc_label = f"page {loc}" if loc >= 0 else f"chunk {abs(loc)}"
                with st.expander(
                    f"📄 {src['document']} — {loc_label} (score: {src['score']:.4f})"
                ):
                    st.markdown(f"*{src['excerpt']}*")
