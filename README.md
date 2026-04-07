# Consumer Finance Complaints Intelligence Platform

A portfolio-ready Analytics Engineering project that builds a batch pipeline for consumer finance complaint intelligence. The repository is structured to show how raw public data can be turned into reliable analytical marts using Python, DuckDB, dbt, Dagster, and CI automation.

## Business Problem
Consumer finance teams often have complaint data available, but struggle to consistently track trends, service levels, and risk concentration over time. This project creates a repeatable analytics foundation to transform complaint records and macro context into decision-ready monthly marts.

## Target Stakeholders
- Operations leaders monitoring complaint volume and resolution performance
- Risk and compliance teams tracking issue concentration and emerging hotspots
- Analytics engineers and data teams responsible for reliable batch pipelines

## Decisions Enabled
- Which products/issues show increasing complaint risk month over month
- Whether response timeliness is improving or degrading across periods
- How macro conditions may align with shifts in complaint patterns

## Stack
- **Python** for ingestion orchestration and utility scripts
- **DuckDB** as local analytical warehouse engine
- **dbt (dbt-duckdb)** for modeled transformations and marts
- **Dagster** for orchestration definitions and job execution
- **GitHub Actions** for CI checks (lint + tests)
- **Parquet** for bronze raw-data persistence

## High-Level Architecture
- Land raw CFPB and FRED extracts into Parquet bronze folders
- Standardize and model data into DuckDB using dbt (silver/gold layering)
- Orchestrate pipeline steps with Dagster
- Enforce baseline quality through CI linting and scaffold smoke tests

## Repository Structure (Summary)
- `src/`: Python packages for ingestion, orchestration, and utilities
- `config/`: ingestion and source configuration files
- `dbt/complaints_ae/`: dbt project root (to be implemented in later phases)
- `data/`: bronze, warehouse, and export storage locations
- `docs/`: project brief, architecture, source, mart, and runbook docs
- `.github/workflows/ci.yml`: CI workflow for lint/test checks

## Local Setup
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:
   ```bash
   make install
   ```
3. Copy `.env.example` to `.env` and fill required values.
4. Validate scaffold:
   ```bash
   make lint
   make test
   ```
5. Run ingestion commands:
   ```bash
   make ingest-fred
   make ingest-cfpb
   ```

## FRED Ingestion Notes
- `FRED_API_KEY` is required in your `.env` file.
- `make ingest-fred` fetches configured FRED series and writes one Parquet file per series per run under `data/bronze/fred/<series_id>/`.
- Run metadata is appended to `logs/ingestion_runs.jsonl`.

## CFPB Ingestion Notes
- `make ingest-cfpb` uses the CFPB export endpoint in CSV mode (`format=csv`, `field=all`, `no_aggs=true`).
- `CFPB_BASE_URL` is optional; when not set, ingestion uses the default project export URL.
- Query window defaults are config-driven (`cfpb.date_received_min`) with `date_received_max` set to the current UTC date at runtime.
- Raw output is written to `data/bronze/cfpb_complaints/` as one Parquet file per run.
- `cfpb.size` controls max records per request (default `250000` if not set).

## Current Project Status
- ✅ **Phase 1 complete:** repository scaffold, configs, CI, and baseline documentation/tests.
- ✅ **Phase 2 (partial):** FRED ingestion implemented with bronze Parquet outputs and ingestion metadata logging.
- ✅ **Phase 2 (partial):** CFPB ingestion added for raw bronze landing with metadata logging.
- ⏳ **Pending phases:** dbt models/tests, Dagster assets/jobs wiring, and production-grade data quality checks.
