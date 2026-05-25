# LeaseSense Commands

Use these commands from the repository root.

## Run The App

```powershell
streamlit run app.py
```

## Run The API

```powershell
uvicorn leasesense.api.main:app --reload
```

## Run Tests

```powershell
pytest
```

## Compile Check

```powershell
python -m compileall app.py leasesense src tests
```

## Run Evals

```powershell
python -m leasesense.evals.runner path\to\lease.pdf --backend template
```

## Docker

```powershell
docker compose up --build
```

