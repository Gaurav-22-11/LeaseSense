# LeaseSense Portfolio Case Study

## One-Line Pitch

LeaseSense is a local-first AI lease analysis system that helps renters ask questions about lease PDFs, retrieve clause-level evidence, and identify lease risks without paid APIs.

## Resume Summary

Built LeaseSense, a local-first RAG application for lease analysis using Streamlit, Docling, Qdrant, sentence-transformers, and pluggable local LLM backends. The system parses lease PDFs, classifies clauses by section, supports metadata-filtered retrieval, generates plain-English answers with cited evidence, flags rule-based renter risks, and includes tests, evals, Docker, FastAPI, and CI-ready project structure.

## Resume Bullets

- Built a local-first RAG system for lease PDF analysis with Docling parsing, semantic chunking, BGE embeddings, Qdrant vector search, and cited answer generation.
- Implemented clause intelligence that labels chunks by lease section and powers section-aware retrieval filters and an evidence dashboard.
- Designed pluggable local generation backends supporting deterministic offline answers, Ollama, llama.cpp GGUF models, and Hugging Face Transformers.
- Added a rule-based risk radar for joint liability, subleasing restrictions, occupancy limits, deposits, unauthorized occupants, and early termination.
- Added production-oriented project infrastructure including FastAPI service entrypoint, Docker setup, eval harness, unit tests, and GitHub Actions CI.

## Interview Talking Points

- Why local-first matters: lease data is sensitive, so the MVP avoids paid/cloud APIs by default.
- Why the template backend exists: it makes demos deterministic, cheap, testable, and runnable on low-storage machines.
- Why metadata-aware retrieval matters: filtering by lease section improves explainability and lets users inspect the evidence space.
- Why evals are included: RAG projects need measurable retrieval and answer quality, not only a chat interface.
- Main tradeoff: rule-based risk detection is explainable but should be expanded with labeled clauses before production legal-adjacent use.

## Demo Script

1. Start the app with `streamlit run app.py`.
2. Upload a lease PDF.
3. Show the metrics: parsed words, indexed chunks, detected sections.
4. Open `Risk Radar` and explain the detected renter risks.
5. Open `Evidence Dashboard` and show clause grouping by section.
6. Go to `Ask`, select a section filter such as `Subleasing and Assignment`.
7. Ask: `Can my landlord charge me for subleasing?`
8. Show the answer sections and retrieved evidence cards.
9. Mention the local-first backend selector and optional model providers.
10. Close with tests/evals/API/Docker/CI as engineering polish.

## Suggested GitHub Description

Local-first AI lease analysis MVP for renters: Docling PDF parsing, Qdrant RAG, clause metadata, risk radar, pluggable local LLM backends, Streamlit UI, FastAPI, evals, tests, Docker, and CI.

## Suggested Tags

`rag` `streamlit` `qdrant` `docling` `sentence-transformers` `local-ai` `fastapi` `legal-tech` `portfolio-project`

