# Project Brief

## Problem Statement
Consumer complaint data is high volume and publicly available, but organizations often lack a clean, reproducible analytics pipeline that converts raw records into trusted monthly decision-support datasets.

## Business Context
Financial-services operations and risk teams need consistent trend views across products, issues, response performance, and external macro context. Without engineered datasets, analysis is ad hoc, slow to refresh, and hard to trust.

## Users / Stakeholders
- Complaint operations managers
- Risk and compliance analysts
- Data and analytics engineering teams
- Hiring managers evaluating analytics engineering execution quality

## Key Decisions Enabled
- Where complaint pressure is rising and which product/issue areas require intervention
- Whether service-level outcomes are improving over time
- How external macro signals align with complaint pattern shifts

## Project Goals
- Establish a production-minded repository and operating model for batch analytics
- Define clear source, architecture, and mart contracts before implementation
- Prepare a maintainable path for Python ingestion, DuckDB storage, dbt marts, and Dagster orchestration
- Demonstrate disciplined scope control and engineering documentation quality

## Explicit Non-Goals (Phase 1)
- Implementing ingestion or transformation logic
- Building dashboards or BI delivery artifacts
- Adding ML/NLP models or cloud infrastructure
- Introducing tools beyond the agreed stack

## Why This Signals Analytics Engineering Capability
This project demonstrates core Analytics Engineering behaviors: translating business questions into mart contracts, choosing appropriate tooling for reproducible batch workflows, structuring repositories for maintainability, and setting CI/documentation standards before feature buildout.
