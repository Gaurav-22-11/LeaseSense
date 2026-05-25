.PHONY: run api test compile eval docker

run:
	streamlit run app.py

api:
	uvicorn leasesense.api.main:app --reload

test:
	pytest

compile:
	python -m compileall app.py leasesense src tests

eval:
	python -m leasesense.evals.runner "$(PDF)" --backend template

docker:
	docker compose up --build

