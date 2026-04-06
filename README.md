# Consumer Finance Complaints Intelligence Platform

A portfolio-ready Analytics Engineering project that builds a batch pipeline for consumer finance complaint intelligence. The repository is structured to show how raw public data can be turned into reliable analytical marts using Python, DuckDB, dbt, Dagster, and CI automation. Phase 1 establishes a production-minded foundation and documentation; ingestion and transformation implementation are intentionally deferred to later phases.

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

## Current Project Status
- ✅ **Phase 1 complete:** repository scaffold, configs, CI, and baseline documentation/tests.
- ⏳ **Pending phases:** ingestion implementation, dbt models/tests, Dagster assets/jobs wiring, and production-grade data quality checks.
