# Architecture

## Architecture Overview
The platform follows a layered batch architecture: raw source extracts land in Parquet bronze storage, curated relational models are built in DuckDB, and business-facing marts are produced with dbt. Dagster defines orchestration entry points, while GitHub Actions enforces baseline code quality in CI.

## Data Layering: Bronze / Silver / Gold
- **Bronze (raw Parquet):** immutable-ish source-aligned extracts from CFPB and FRED.
- **Silver (standardized):** cleaned, typed, and conformed intermediate models suitable for reuse.
- **Gold (marts):** monthly business-facing tables aligned to operational/risk decisions.

Phase 1 defines the structure and contracts for these layers; implementation is deferred.

## Tool Roles
- **Python:** source retrieval and file-level processing orchestration (future phases).
- **DuckDB:** local analytical compute/storage target for modeled data.
- **dbt:** transformation framework for layered SQL models, tests, and documentation.
- **Dagster:** orchestration definitions to run pipeline steps on schedule or on demand.
- **GitHub Actions:** automated lint/test checks to maintain repository quality.

## Why Parquet Bronze Is Included
Parquet provides efficient columnar storage, fast local reads, and strong interoperability across Python and DuckDB. Using Parquet in bronze also separates source landing from warehouse modeling, improving recoverability and reproducibility.

## Batch / Incremental-Batch Rationale
Complaint intelligence use cases are typically trend-oriented and tolerate scheduled refreshes better than streaming complexity. A batch-first design minimizes operational overhead while still supporting incremental extension in later phases.

## Observability and Quality Approach (This Repo)
Phase 1 includes foundational quality controls: pinned dependencies, linting, CI execution, and scaffold integrity tests. Later phases will extend this with data tests, run logging, and pipeline-level operational checks.
