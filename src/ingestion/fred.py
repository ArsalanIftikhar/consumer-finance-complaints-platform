"""FRED observations ingestion module for Phase 2."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
import requests
import yaml

from src.ingestion.metadata import append_ingestion_run_metadata
from src.ingestion.writers import write_dataframe_to_parquet
from src.utils.env import get_fred_api_key
from src.utils.logging import get_project_logger
from src.utils.paths import build_fred_bronze_path, get_ingestion_runs_log_path, get_repo_root

logger = get_project_logger(__name__)
FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


def _load_yaml_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as file_handle:
        loaded = yaml.safe_load(file_handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a mapping in config file: {path}")
    return loaded


def load_fred_ingestion_config() -> dict:
    config_path = get_repo_root() / "config" / "ingestion.yml"
    config = _load_yaml_file(config_path)
    fred_config = config.get("fred")
    if not isinstance(fred_config, dict):
        raise ValueError("Missing 'fred' section in config/ingestion.yml")

    required_keys = {
        "dataset_name",
        "output_format",
        "timeout_seconds",
        "file_type",
        "observation_start",
    }
    missing_keys = required_keys - set(fred_config)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing required fred config key(s): {missing}")
    return fred_config


def load_fred_series_config() -> list[dict]:
    series_config_path = get_repo_root() / "config" / "fred_series.yml"
    series_config = _load_yaml_file(series_config_path)
    series = series_config.get("series")
    if not isinstance(series, list) or not series:
        raise ValueError("config/fred_series.yml must define a non-empty 'series' list")
    return series


def build_fred_request_params(series_id: str, fred_config: dict, api_key: str) -> dict:
    return {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": fred_config["file_type"],
        "observation_start": fred_config["observation_start"],
    }


def fetch_fred_observations_json(
    series_id: str,
    fred_config: dict,
    api_key: str,
    session: requests.Session | None = None,
) -> dict:
    request_session = session or requests.Session()
    params = build_fred_request_params(series_id, fred_config, api_key)

    logger.info("Fetching FRED observations for series_id=%s", series_id)
    try:
        response = request_session.get(
            FRED_OBSERVATIONS_URL,
            params=params,
            timeout=int(fred_config["timeout_seconds"]),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch FRED observations for '{series_id}': {exc}") from exc

    payload = response.json()
    if "observations" not in payload:
        raise ValueError(f"Unexpected FRED payload for '{series_id}': missing observations field")
    return payload


def normalise_fred_observations(
    payload: dict,
    *,
    series_id: str,
    source_run_id: str,
    extracted_at_utc: str,
) -> pd.DataFrame:
    observations = payload.get("observations", [])
    if not observations:
        return pd.DataFrame(
            columns=["date", "value", "series_id", "source_run_id", "extracted_at_utc"]
        )

    dataframe = pd.DataFrame(observations)
    if "date" not in dataframe.columns or "value" not in dataframe.columns:
        raise ValueError(f"FRED observations for '{series_id}' must include date and value fields")

    dataframe = dataframe[["date", "value"]].copy()
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    dataframe["value"] = pd.to_numeric(dataframe["value"], errors="coerce")
    dataframe["series_id"] = series_id
    dataframe["source_run_id"] = source_run_id
    dataframe["extracted_at_utc"] = extracted_at_utc
    return dataframe


def run_fred_ingestion() -> None:
    api_key = get_fred_api_key()
    fred_config = load_fred_ingestion_config()
    series_items = load_fred_series_config()

    run_id = uuid4().hex
    extracted_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metadata_log_path = get_ingestion_runs_log_path()

    logger.info("Starting FRED ingestion run_id=%s for %s series", run_id, len(series_items))

    for series_item in series_items:
        series_id = series_item.get("code")
        if not series_id:
            raise ValueError("Each series entry in config/fred_series.yml must include 'code'")

        output_path = build_fred_bronze_path(series_id, filename=f"{series_id}_{run_id}.parquet")

        try:
            payload = fetch_fred_observations_json(series_id, fred_config, api_key)
            dataframe = normalise_fred_observations(
                payload,
                series_id=series_id,
                source_run_id=run_id,
                extracted_at_utc=extracted_at_utc,
            )
            written_path, row_count = write_dataframe_to_parquet(dataframe, output_path)

            append_ingestion_run_metadata(
                metadata_log_path,
                run_id=run_id,
                source_name="fred",
                dataset_name=fred_config["dataset_name"],
                status="success",
                extracted_at_utc=extracted_at_utc,
                row_count=row_count,
                output_path=str(written_path),
                file_format=fred_config["output_format"],
                notes=f"Series ingested: {series_id}",
                series_id=series_id,
            )
            logger.info(
                "FRED ingestion complete for series_id=%s rows=%s output=%s",
                series_id,
                row_count,
                written_path,
            )
        except Exception as exc:  # noqa: BLE001
            append_ingestion_run_metadata(
                metadata_log_path,
                run_id=run_id,
                source_name="fred",
                dataset_name=fred_config["dataset_name"],
                status="failed",
                extracted_at_utc=extracted_at_utc,
                row_count=None,
                output_path=str(output_path),
                file_format=fred_config["output_format"],
                notes=f"Series failed: {series_id}",
                error_message=str(exc),
                series_id=series_id,
            )
            logger.exception("FRED ingestion failed for series_id=%s", series_id)
            raise RuntimeError(f"FRED ingestion failed for series '{series_id}'") from exc

    logger.info("FRED ingestion run complete run_id=%s", run_id)


if __name__ == "__main__":
    run_fred_ingestion()
