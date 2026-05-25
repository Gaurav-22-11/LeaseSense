# LeaseSense Demo Script

Use this script for a short screen recording or live portfolio walkthrough.

## 30-Second Version

LeaseSense is a local-first AI lease analysis tool for renters. I upload a lease PDF, the app parses and chunks it, labels clauses by section, stores embeddings in local Qdrant, and lets me ask questions with cited evidence. It also includes a risk radar for common renter issues and a section-aware evidence dashboard. The project is designed like a production MVP with pluggable model backends, FastAPI, Docker, tests, evals, and CI.

## 2-Minute Walkthrough

1. Open the Streamlit app.
2. Point out the backend selector. Use `template` for a no-model offline demo.
3. Upload and analyze a lease PDF.
4. Show the metric tiles.
5. Open `Risk Radar`.
6. Explain that risk findings are rule-based and evidence-backed.
7. Open `Evidence Dashboard`.
8. Show sections like `Rent and Payments`, `Security Deposit`, or `Subleasing and Assignment`.
9. Open `Ask`.
10. Select a section filter.
11. Ask a renter question.
12. Show the required answer sections:
    - Plain English Explanation
    - Relevant Lease Evidence
    - Risk Level
    - Suggested Next Steps
13. Show retrieved evidence cards with section/type tags.
14. Mention FastAPI, Docker, evals, and tests.

## Screenshot Checklist

- Sidebar with backend selector and upload
- Metrics after lease ingestion
- Ask tab with an answer and evidence cards
- Risk Radar tab
- Evidence Dashboard tab
- Parsed Lease tab

