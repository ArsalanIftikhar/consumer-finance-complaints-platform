# Data Sources

## CFPB Consumer Complaints Source (Primary)
CFPB provides complaint records through a public API endpoint suitable for historical batch extraction. It is the core fact source for complaint volume, product/issue patterns, company response behavior, and timeliness metrics.

### Likely High-Value CFPB Fields / Entities
- Complaint identifiers and submission/response dates
- Product and sub-product
- Issue and sub-issue
- Company and company response attributes
- Timely response indicator and consumer dispute indicator
- State and channel metadata

## FRED Macroeconomic Source (Enrichment)
FRED provides macroeconomic time series for contextual enrichment of complaint trends. Phase 1 configuration includes unemployment rate (UNRATE), federal funds rate (FEDFUNDS), and CPI (CPIAUCSL).

### Likely High-Value FRED Fields / Entities
- Series ID and human-readable label
- Observation date (monthly granularity target)
- Observed value

## Practical Access / Setup Notes
- CFPB base URL is documented in `.env.example`.
- FRED access uses an API key in `.env.example`.
- Source-specific behavior (e.g., frequency, output format, mode) is controlled via `config/ingestion.yml` and `config/fred_series.yml`.

## Why a Third Enrichment Source Is Excluded in v1
v1 intentionally limits scope to one primary operational source (CFPB) plus one macro source (FRED) to keep ingestion/transformation complexity manageable and demonstrate disciplined delivery. Additional enrichment sources can be added once baseline pipeline reliability is established.
