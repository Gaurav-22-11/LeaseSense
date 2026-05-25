from __future__ import annotations

import tempfile
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

import streamlit as st

from leasesense.config import settings
from leasesense.embeddings import get_embedder
from leasesense.feedback import save_feedback
from leasesense.ingestion.pipeline import LeaseIngestionPipeline
from leasesense.rag import answer_question
from leasesense.vector_store import LeaseVectorStore


st.set_page_config(
    page_title="LeaseSense",
    page_icon="LS",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ls-bg: #f7f7f4;
          --ls-panel: #ffffff;
          --ls-ink: #151515;
          --ls-muted: #686963;
          --ls-line: #dfddd4;
          --ls-accent: #256d5a;
          --ls-soft: #edf5f1;
          --ls-warn: #b35c00;
          --ls-risk: #b42318;
        }
        .stApp { background: var(--ls-bg); color: var(--ls-ink); }
        [data-testid="stSidebar"] { background: #efeee8; border-right: 1px solid var(--ls-line); }
        h1, h2, h3 { letter-spacing: 0; }
        .hero {
          padding: 1.25rem 0 0.5rem 0;
          border-bottom: 1px solid var(--ls-line);
          margin-bottom: 1.25rem;
        }
        .hero h1 {
          font-size: 2.2rem;
          line-height: 1.05;
          margin: 0 0 0.4rem 0;
        }
        .hero p { color: var(--ls-muted); font-size: 1.02rem; margin: 0; max-width: 760px; }
        .disclaimer {
          border-left: 4px solid var(--ls-warn);
          background: #fff8ed;
          padding: 0.8rem 1rem;
          margin: 0.8rem 0 1rem 0;
          font-size: 0.92rem;
          color: #4a3320;
        }
        .metric-band {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.75rem;
          margin: 1rem 0;
        }
        .metric-tile {
          background: var(--ls-panel);
          border: 1px solid var(--ls-line);
          border-radius: 8px;
          padding: 0.9rem;
        }
        .metric-tile strong { display: block; font-size: 1.45rem; }
        .metric-tile span { color: var(--ls-muted); font-size: 0.86rem; }
        .risk-low, .risk-medium, .risk-high {
          border-radius: 999px;
          padding: 0.18rem 0.55rem;
          font-size: 0.78rem;
          font-weight: 700;
        }
        .risk-low { background: #e8f5ed; color: #17633a; }
        .risk-medium { background: #fff4df; color: #875000; }
        .risk-high { background: #fde8e7; color: var(--ls-risk); }
        .evidence {
          border: 1px solid var(--ls-line);
          border-radius: 8px;
          padding: 0.8rem;
          background: var(--ls-panel);
          margin-bottom: 0.7rem;
        }
        .evidence small { color: var(--ls-muted); }
        .tag-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.25rem 0 0.55rem 0; }
        .meta-tag {
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          border: 1px solid var(--ls-line);
          background: var(--ls-soft);
          color: #1f4f43;
          padding: 0.12rem 0.5rem;
          font-size: 0.75rem;
          font-weight: 700;
        }
        .section-list {
          border: 1px solid var(--ls-line);
          border-radius: 8px;
          background: var(--ls-panel);
          padding: 0.75rem;
          margin-bottom: 0.65rem;
        }
        div.stButton > button {
          border-radius: 8px;
          border: 1px solid var(--ls-line);
        }
        div.stButton > button[kind="primary"] {
          background: var(--ls-accent);
          border-color: var(--ls-accent);
        }
        @media (max-width: 800px) {
          .metric-band { grid-template-columns: 1fr; }
          .hero h1 { font-size: 1.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def cached_embedder():
    return get_embedder(settings.embedding_model)


def get_vector_store():
    return LeaseVectorStore(settings.qdrant_path, settings.collection_name)


def initialize_state() -> None:
    defaults = {
        "lease_id": None,
        "lease_text": "",
        "chunks": [],
        "risks": [],
        "last_answer": None,
        "llm_backend": settings.llm_backend,
        "section_filter": "All sections",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def process_upload(uploaded_file) -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=settings.upload_dir) as tmp:
        tmp.write(uploaded_file.getbuffer())
        pdf_path = Path(tmp.name)

    embedder = cached_embedder()
    if embedder.using_fallback:
        st.warning(
            "The BGE sentence-transformers model is not available locally, so LeaseSense is using a deterministic local fallback embedder for this session. Retrieval quality may be lower."
        )
    pipeline = LeaseIngestionPipeline(embedder=embedder, vector_store=get_vector_store())
    result = pipeline.ingest_pdf(pdf_path=pdf_path, lease_id=pdf_path.stem)

    st.session_state.lease_id = result.lease_id
    st.session_state.lease_text = result.parsed.text
    st.session_state.chunks = result.chunks
    st.session_state.risks = result.risks
    st.session_state.last_answer = None


def render_risk_radar() -> None:
    risks = st.session_state.risks
    if not risks:
        st.info("Upload a lease to generate the risk radar.")
        return

    st.subheader("Risk Radar")
    for item in risks:
        css = f"risk-{item.level.value}"
        st.markdown(
            f"**{item.name}** &nbsp; <span class='{css}'>{item.level.value.upper()}</span>",
            unsafe_allow_html=True,
        )
        st.caption(item.summary)
        if item.evidence:
            with st.expander("Evidence"):
                for evidence in item.evidence:
                    st.write(evidence)


def render_metrics() -> None:
    text = st.session_state.lease_text
    chunks = st.session_state.chunks
    high_risks = sum(1 for risk in st.session_state.risks if risk.level.value == "high")
    sections = {chunk.section for chunk in chunks if getattr(chunk, "section", "")}
    st.markdown(
        f"""
        <div class="metric-band">
          <div class="metric-tile"><strong>{len(text.split()):,}</strong><span>Words parsed</span></div>
          <div class="metric-tile"><strong>{len(chunks):,}</strong><span>Evidence chunks indexed</span></div>
          <div class="metric-tile"><strong>{len(sections):,}</strong><span>Clause sections detected</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if high_risks:
        st.caption(f"{high_risks} high-risk flags detected in the risk radar.")


def section_options() -> list[str]:
    sections = sorted({chunk.section for chunk in st.session_state.chunks if getattr(chunk, "section", "")})
    return ["All sections", *sections]


def render_evidence_dashboard() -> None:
    chunks = st.session_state.chunks
    if not chunks:
        return

    st.subheader("Evidence Dashboard")
    counts = Counter(chunk.section for chunk in chunks)
    cols = st.columns(min(4, max(1, len(counts))))
    for col, (section, count) in zip(cols, counts.most_common()):
        col.markdown(
            f"""
            <div class="section-list">
              <strong>{escape(section)}</strong><br>
              <span>{count} chunks</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    grouped: dict[str, list] = defaultdict(list)
    for chunk in chunks:
        grouped[chunk.section].append(chunk)

    selected = st.selectbox("Browse indexed section", ["All sections", *sorted(grouped)], key="browse_section")
    visible_sections = sorted(grouped) if selected == "All sections" else [selected]
    for section in visible_sections:
        with st.expander(f"{section} ({len(grouped[section])} chunks)"):
            for chunk in grouped[section][:8]:
                tags = ", ".join(tag.replace("_", " ").title() for tag in chunk.risk_tags) or "No risk tag"
                st.caption(f"Chunk {chunk.index} | {chunk.clause_type.replace('_', ' ').title()} | {tags}")
                st.write(chunk.text[:900])


def render_answer() -> None:
    answer = st.session_state.last_answer
    if not answer:
        return

    st.subheader("LeaseSense Answer")
    st.markdown(answer.answer_markdown)

    st.subheader("Retrieved Evidence")
    for idx, evidence in enumerate(answer.evidence, start=1):
        safe_text = escape(evidence.text)
        safe_section = escape(evidence.section)
        safe_clause_type = escape(evidence.clause_type.replace("_", " ").title())
        tags = "".join(
            f"<span class='meta-tag'>{escape(tag.replace('_', ' ').title())}</span>"
            for tag in evidence.risk_tags
        )
        st.markdown(
            f"""
            <div class="evidence">
              <div class="tag-row">
                <span class="meta-tag">{safe_section}</span>
                <span class="meta-tag">{safe_clause_type}</span>
                {tags}
              </div>
              <small>Evidence {idx} · score {evidence.score:.3f}</small>
              <p>{safe_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("Was this useful?")
    cols = st.columns(3)
    feedback_options = ["Helpful", "Confusing", "Risk seems wrong"]
    for col, option in zip(cols, feedback_options):
        if col.button(option, use_container_width=True):
            save_feedback(
                lease_id=st.session_state.lease_id or "unknown",
                question=answer.question,
                feedback=option,
                answer=answer.answer_markdown,
            )
            st.toast(f"Feedback saved: {option}")


def render_answer_card() -> None:
    answer = st.session_state.last_answer
    if not answer:
        st.info("Ask a question to generate an answer with cited lease evidence.")
        return

    st.subheader("LeaseSense Answer")
    st.markdown(answer.answer_markdown)

    st.subheader("Retrieved Evidence")
    for idx, evidence in enumerate(answer.evidence, start=1):
        safe_text = escape(evidence.text)
        safe_section = escape(evidence.section)
        safe_clause_type = escape(evidence.clause_type.replace("_", " ").title())
        tags = "".join(
            f"<span class='meta-tag'>{escape(tag.replace('_', ' ').title())}</span>"
            for tag in evidence.risk_tags
        )
        st.markdown(
            f"""
            <div class="evidence">
              <div class="tag-row">
                <span class="meta-tag">{safe_section}</span>
                <span class="meta-tag">{safe_clause_type}</span>
                {tags}
              </div>
              <small>Evidence {idx} - score {evidence.score:.3f}</small>
              <p>{safe_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("Was this useful?")
    cols = st.columns(3)
    feedback_options = ["Helpful", "Confusing", "Risk seems wrong"]
    for col, option in zip(cols, feedback_options):
        if col.button(option, use_container_width=True):
            save_feedback(
                lease_id=st.session_state.lease_id or "unknown",
                question=answer.question,
                feedback=option,
                answer=answer.answer_markdown,
            )
            st.toast(f"Feedback saved: {option}")


def main() -> None:
    inject_styles()
    initialize_state()

    st.markdown(
        """
        <div class="hero">
          <h1>LeaseSense</h1>
          <p>Upload a lease, ask practical renter questions, and see the exact clauses behind each answer.</p>
        </div>
        <div class="disclaimer">
          LeaseSense is not legal advice. It is an educational tool that can help you spot issues to discuss with a qualified professional.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Lease Intake")
        backend_options = ["template", "ollama", "llama_cpp", "transformers"]
        selected_backend = st.selectbox(
            "Answer backend",
            backend_options,
            index=backend_options.index(st.session_state.llm_backend)
            if st.session_state.llm_backend in backend_options
            else 0,
            help="Template is deterministic and fully offline. The others use local model runtimes.",
        )
        st.session_state.llm_backend = selected_backend
        st.caption(f"Active backend: {selected_backend}")

        uploaded_file = st.file_uploader("Upload lease PDF", type=["pdf"])
        if uploaded_file and st.button("Analyze Lease", type="primary", use_container_width=True):
            with st.spinner("Parsing, chunking, embedding, and indexing your lease..."):
                try:
                    process_upload(uploaded_file)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.success("Lease indexed locally.")

    if st.session_state.lease_text:
        render_metrics()
    else:
        st.info("Start by uploading a lease PDF in the sidebar.")

    ask_tab, risk_tab, evidence_tab, parsed_tab = st.tabs(
        ["Ask", "Risk Radar", "Evidence Dashboard", "Parsed Lease"]
    )

    with ask_tab:
        section_filter = st.selectbox(
            "Limit retrieval to section",
            section_options(),
            disabled=not bool(st.session_state.lease_id),
            help="Use this to ask questions against a specific lease section.",
        )
        st.session_state.section_filter = section_filter

        question = st.text_input(
            "Ask a lease question",
            placeholder="Example: Can my landlord charge me for breaking the lease early?",
            disabled=not bool(st.session_state.lease_id),
        )
        ask = st.button("Ask LeaseSense", type="primary", disabled=not question or not st.session_state.lease_id)

        if ask:
            with st.spinner("Retrieving lease evidence and drafting a plain-English answer..."):
                try:
                    result = answer_question(
                        question=question,
                        lease_id=st.session_state.lease_id,
                        embedder=cached_embedder(),
                        vector_store=get_vector_store(),
                        detected_risks=st.session_state.risks,
                        llm_backend=st.session_state.llm_backend,
                        section=None
                        if st.session_state.section_filter == "All sections"
                        else st.session_state.section_filter,
                    )
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.session_state.last_answer = result

        render_answer_card()

    with risk_tab:
        render_risk_radar()

    with evidence_tab:
        render_evidence_dashboard()

    with parsed_tab:
        if st.session_state.lease_text:
            st.markdown(st.session_state.lease_text[: settings.preview_char_limit])
        else:
            st.info("Upload and analyze a lease to inspect parsed text.")


if __name__ == "__main__":
    main()
