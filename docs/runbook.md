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
make dbt-parse     # dbt parse --project-dir dbt/complaints_ae
make dbt-debug     # dbt debug --project-dir dbt/complaints_ae
make dagster-dev   # dagster dev
```

## Current Phase 1 Limitations
- Ingestion logic is not implemented yet.
- dbt project structure exists, but models/tests are pending.
- Dagster definitions are minimal and do not yet materialize assets.
- Data quality checks are limited to code linting and scaffold smoke tests.

## Troubleshooting
### `pytest` fails with missing scaffold paths
Ensure you are running commands from the repository root and that required directories were not removed.

### `ruff` command not found
Activate your virtual environment and rerun `make install`.

### `dbt` commands fail
Confirm dependencies were installed from `requirements.txt` and run commands from repo root.

### `dagster dev` startup errors
Check that your virtual environment is active and packages installed; Phase 1 only validates scaffold startup readiness.
