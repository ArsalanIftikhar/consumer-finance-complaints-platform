"""Append-only metadata logging for ingestion runs."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_ingestion_run_metadata(
    log_path: str | Path,
    *,
    run_id: str,
    source_name: str,
    dataset_name: str,
    status: str,
    row_count: int | None = None,
    output_path: str | None = None,
    file_format: str | None = None,
    notes: str | None = None,
    error_message: str | None = None,
    extracted_at_utc: str | None = None,
    **extra_fields: Any,
) -> dict[str, Any]:
    """Append one ingestion run record to a JSONL metadata log file."""
    metadata = {
        "run_id": run_id,
        "source_name": source_name,
        "dataset_name": dataset_name,
        "status": status,
        "extracted_at_utc": extracted_at_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "row_count": row_count,
        "output_path": output_path,
        "file_format": file_format,
        "notes": notes,
        "error_message": error_message,
    }
    metadata.update(extra_fields)

    destination = Path(log_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(metadata, default=str) + "\n")

    return metadata
