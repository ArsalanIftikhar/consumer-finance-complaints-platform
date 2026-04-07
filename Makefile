.PHONY: install test lint format-check dagster-dev dbt-parse dbt-debug ingest-fred ingest-cfpb

install:
	python -m pip install -r requirements.txt

test:
	pytest

lint:
	ruff check .

format-check:
	ruff format --check .

dagster-dev:
	PYTHONPATH=. dagster dev -m src.orchestration.definitions

dbt-parse:
	dbt parse --project-dir dbt/complaints_ae --profiles-dir dbt/complaints_ae

dbt-debug:
	dbt debug --project-dir dbt/complaints_ae --profiles-dir dbt/complaints_ae

ingest-fred:
	PYTHONPATH=. python -m src.ingestion.fred

ingest-cfpb:
	@echo "Phase 2 foundation ready: CFPB ingestion HTTP step not implemented yet."
