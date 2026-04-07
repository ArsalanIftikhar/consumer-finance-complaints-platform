# Runbook

## Prerequisites
- Python 3.11
- `pip` available in shell
- Local clone of this repository

## Environment Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Copy environment template and configure values:
   ```bash
   cp .env.example .env
   ```

## Install Dependencies
```bash
make install
```

## Expected Environment Variables
- `FRED_API_KEY`
- `DUCKDB_PATH`
- `CFPB_BASE_URL`

See `.env.example` for default scaffold values.

## Common Commands
```bash
make lint          # ruff check .
make test          # pytest
make ingest-fred   # run FRED ingestion
make ingest-cfpb   # run CFPB ingestion
make dbt-parse     # dbt parse with project/profiles in dbt/complaints_ae
make dbt-debug     # dbt debug with project/profiles in dbt/complaints_ae
make dagster-dev   # dagster dev with src.orchestration.definitions
```

## FRED Ingestion
- Ensure `FRED_API_KEY` is set in `.env`.
- Run:
  ```bash
  make ingest-fred
  ```
- Outputs are written to `data/bronze/fred/<series_id>/` as one Parquet file per series per run.
- Metadata is appended to `logs/ingestion_runs.jsonl`.

## CFPB Ingestion
- Run:
  ```bash
  make ingest-cfpb
  ```
- Uses `CFPB_BASE_URL` from `.env` when set; otherwise uses configured/default project URL.
- Writes one raw Parquet file per run to `data/bronze/cfpb_complaints/`.
- Assumes a JSON response containing records as a top-level list or under `hits`, `complaints`, `data`, or `results`.

## Current Limitations
- dbt project structure exists, but models/tests are pending.
- Dagster definitions are minimal and do not yet materialize assets.
- Data quality checks are still limited to baseline linting/tests.

## Troubleshooting
### `pytest` fails with missing scaffold paths
Ensure you are running commands from the repository root and that required directories were not removed.

### `ruff` command not found
Activate your virtual environment and rerun `make install`.

### `dbt` commands fail
Confirm dependencies were installed from `requirements.txt` and run commands from repo root.

### `dagster dev` startup errors
Check that your virtual environment is active and packages installed; Phase 1 only validates scaffold startup readiness.

## dbt Profile Note
This repository includes a local `dbt/complaints_ae/profiles.yml` configured for DuckDB. The `make dbt-parse` and `make dbt-debug` targets already point dbt to that profiles directory, so no global `~/.dbt/profiles.yml` is required for this scaffold.
