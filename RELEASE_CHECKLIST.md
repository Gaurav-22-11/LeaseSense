# Release Checklist

Use this before sharing LeaseSense publicly.

## Local Checks

- [ ] `python -m compileall app.py leasesense src tests`
- [ ] `pytest`
- [ ] `streamlit run app.py`
- [ ] Upload a lease PDF and confirm sections populate
- [ ] Ask a question with `LLM_BACKEND=template`
- [ ] Confirm Risk Radar tab loads
- [ ] Confirm Evidence Dashboard tab groups chunks

## GitHub Checks

- [ ] Initialize Git repository if needed
- [ ] Commit source files, docs, tests, Docker, CI
- [ ] Exclude `data/`, `.venv/`, `.env`, and runtime cache files
- [ ] Push to GitHub
- [ ] Confirm GitHub Actions CI passes
- [ ] Add screenshots to `docs/screenshots/`
- [ ] Add repository topics

## Portfolio Checks

- [ ] Add project link to resume or portfolio
- [ ] Use the resume bullets in `PORTFOLIO.md`
- [ ] Record a 60-120 second walkthrough
- [ ] Mention local-first privacy, section-aware retrieval, evals, and tests

