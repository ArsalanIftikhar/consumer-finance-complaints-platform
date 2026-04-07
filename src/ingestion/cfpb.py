"""CFPB complaints raw ingestion module for Phase 2."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from uuid import uuid4

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

from src.ingestion.metadata import append_ingestion_run_metadata
from src.ingestion.writers import write_dataframe_to_parquet
from src.utils.logging import get_project_logger
from src.utils.paths import build_cfpb_bronze_path, get_ingestion_runs_log_path, get_repo_root

logger = get_project_logger(__name__)
DEFAULT_CFPB_BASE_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
DEFAULT_DATE_RECEIVED_MIN = "2011-12-01"
DEFAULT_PAGE_SIZE = 250000
DEFAULT_SORT = "date_received_desc"


def _load_yaml_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as file_handle:
        loaded = yaml.safe_load(file_handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a mapping in config file: {path}")
    return loaded


def load_cfpb_ingestion_config() -> dict:
    config_path = get_repo_root() / "config" / "ingestion.yml"
    config = _load_yaml_file(config_path)
    cfpb_config = config.get("cfpb")
    if not isinstance(cfpb_config, dict):
        raise ValueError("Missing 'cfpb' section in config/ingestion.yml")

    required_keys = {"dataset_name", "output_format", "timeout_seconds", "mode"}
    missing_keys = required_keys - set(cfpb_config)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing required cfpb config key(s): {missing}")
    return cfpb_config


def resolve_cfpb_source_url(cfpb_config: dict) -> str:
    load_dotenv()
    return (
        os.getenv("CFPB_BASE_URL")
        or cfpb_config.get("base_url")
        or DEFAULT_CFPB_BASE_URL
    )


def build_cfpb_query_params(cfpb_config: dict) -> dict[str, str | int]:
    date_received_max = datetime.now(timezone.utc).date().isoformat()
    return {
        "format": "csv",
        "field": "all",
        "no_aggs": "true",
        "date_received_min": cfpb_config.get("date_received_min", DEFAULT_DATE_RECEIVED_MIN),
        "date_received_max": date_received_max,
        "size": int(cfpb_config.get("size", DEFAULT_PAGE_SIZE)),
        "sort": cfpb_config.get("sort", DEFAULT_SORT),
    }


def fetch_cfpb_csv(source_url: str, params: dict[str, str | int], timeout_seconds: int) -> str:
    logger.info("Fetching CFPB complaints CSV from %s", source_url)
    logger.info("Using CFPB query params: %s", params)
    try:
        response = requests.get(source_url, params=params, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch CFPB complaints CSV export: {exc}") from exc

    if not response.text.strip():
        raise ValueError("CFPB CSV export returned an empty response body")

    return response.text


def _to_snake_case(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    return re.sub(r"_+", "_", normalized).lower()


def normalise_cfpb_csv(csv_text: str, *, source_run_id: str, extracted_at_utc: str) -> pd.DataFrame:
    try:
        dataframe = pd.read_csv(StringIO(csv_text))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Failed to parse CFPB CSV response: {exc}") from exc

    if dataframe.empty:
        raise ValueError("CFPB CSV export returned zero records")

    dataframe.columns = [_to_snake_case(column) for column in dataframe.columns]
    dataframe["source_run_id"] = source_run_id
    dataframe["extracted_at_utc"] = extracted_at_utc
    return dataframe


def run_cfpb_ingestion() -> None:
    cfpb_config = load_cfpb_ingestion_config()
    source_url = resolve_cfpb_source_url(cfpb_config)
    query_params = build_cfpb_query_params(cfpb_config)

    run_id = uuid4().hex
    extracted_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_path = build_cfpb_bronze_path(filename=f"cfpb_complaints_{run_id}.parquet")
    metadata_log_path = get_ingestion_runs_log_path()

    logger.info("Starting CFPB ingestion run_id=%s", run_id)
    try:
        csv_text = fetch_cfpb_csv(source_url, query_params, int(cfpb_config["timeout_seconds"]))
        dataframe = normalise_cfpb_csv(
            csv_text,
            source_run_id=run_id,
            extracted_at_utc=extracted_at_utc,
        )
        written_path, row_count = write_dataframe_to_parquet(dataframe, output_path)
        append_ingestion_run_metadata(
            metadata_log_path,
            run_id=run_id,
            source_name="cfpb",
            dataset_name=cfpb_config["dataset_name"],
            status="success",
            extracted_at_utc=extracted_at_utc,
            row_count=row_count,
            output_path=str(written_path),
            file_format=cfpb_config["output_format"],
            notes=(
                "CFPB CSV export mode. "
                f"date_received_min={query_params['date_received_min']} "
                f"date_received_max={query_params['date_received_max']} "
                f"size={query_params['size']}"
            ),
        )
        logger.info("CFPB ingestion complete rows=%s output=%s", row_count, written_path)
    except Exception as exc:  # noqa: BLE001
        append_ingestion_run_metadata(
            metadata_log_path,
            run_id=run_id,
            source_name="cfpb",
            dataset_name=cfpb_config["dataset_name"],
            status="failed",
            extracted_at_utc=extracted_at_utc,
            row_count=None,
            output_path=str(output_path),
            file_format=cfpb_config["output_format"],
            notes="CFPB CSV export mode",
            error_message=str(exc),
        )
        logger.exception("CFPB ingestion failed run_id=%s", run_id)
        raise RuntimeError(
            "CFPB ingestion failed. Check logs/ingestion_runs.jsonl for details."
        ) from exc


if __name__ == "__main__":
    run_cfpb_ingestion()
