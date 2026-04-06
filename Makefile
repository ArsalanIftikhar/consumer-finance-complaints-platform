.PHONY: install test lint format-check dagster-dev dbt-parse dbt-debug

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	ruff check .

format-check:
	ruff format --check .

dagster-dev:
	dagster dev

dbt-parse:
	dbt parse --project-dir dbt/complaints_ae

dbt-debug:
	dbt debug --project-dir dbt/complaints_ae
