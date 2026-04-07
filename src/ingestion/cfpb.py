"""CFPB complaints raw ingestion module for Phase 2."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
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


def fetch_cfpb_payload(source_url: str, timeout_seconds: int) -> dict | list:
    logger.info("Fetching CFPB complaints from %s", source_url)
    try:
        response = requests.get(source_url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch CFPB complaints data: {exc}") from exc

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type and "text/json" not in content_type:
        raise ValueError(
            "CFPB source returned a non-JSON response. "
            f"Received content-type: {content_type or 'unknown'}"
        )
    return response.json()


def _extract_records(payload: dict | list) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]

    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get("hits"), list):
        rows: list[dict] = []
        for item in payload["hits"]:
            if isinstance(item, dict):
                if isinstance(item.get("_source"), dict):
                    rows.append(item["_source"])
                else:
                    rows.append(item)
        return rows

    for key in ("complaints", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]

    return []


def _to_snake_case(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    return re.sub(r"_+", "_", normalized).lower()


def normalise_cfpb_payload(
    payload: dict | list,
    *,
    source_run_id: str,
    extracted_at_utc: str,
) -> pd.DataFrame:
    records = _extract_records(payload)
    if not records:
        raise ValueError(
            "CFPB response did not contain any complaint records. "
            "Expected a list payload or a dict with hits/complaints/data/results."
        )

    dataframe = pd.DataFrame(records)
    dataframe.columns = [_to_snake_case(column) for column in dataframe.columns]
    dataframe["source_run_id"] = source_run_id
    dataframe["extracted_at_utc"] = extracted_at_utc
    return dataframe


def run_cfpb_ingestion() -> None:
    cfpb_config = load_cfpb_ingestion_config()
    source_url = resolve_cfpb_source_url(cfpb_config)

    run_id = uuid4().hex
    extracted_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_path = build_cfpb_bronze_path(filename=f"cfpb_complaints_{run_id}.parquet")
    metadata_log_path = get_ingestion_runs_log_path()

    logger.info("Starting CFPB ingestion run_id=%s", run_id)
    try:
        payload = fetch_cfpb_payload(source_url, int(cfpb_config["timeout_seconds"]))
        dataframe = normalise_cfpb_payload(
            payload,
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
            notes=f"CFPB mode: {cfpb_config['mode']}",
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
            notes=f"CFPB mode: {cfpb_config['mode']}",
            error_message=str(exc),
        )
        logger.exception("CFPB ingestion failed run_id=%s", run_id)
        raise RuntimeError(
            "CFPB ingestion failed. Check logs/ingestion_runs.jsonl for details."
        ) from exc


if __name__ == "__main__":
    run_cfpb_ingestion()
