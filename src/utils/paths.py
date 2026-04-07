"""Path utilities for ingestion outputs and run metadata."""

from pathlib import Path

PROJECT_ROOT_MARKERS = ("pyproject.toml", ".git")


def get_repo_root(start_path: Path | None = None) -> Path:
    """Resolve the repository root by searching parent directories."""
    current = (start_path or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        if any((directory / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            return directory

    raise FileNotFoundError(
        "Could not determine repository root. Expected one of: "
        f"{', '.join(PROJECT_ROOT_MARKERS)}"
    )


def build_cfpb_bronze_path(filename: str = "cfpb_complaints.parquet") -> Path:
    """Build the bronze output path for CFPB complaints data."""
    return get_repo_root() / "data" / "bronze" / "cfpb_complaints" / filename


def build_fred_bronze_path(series_id: str, filename: str | None = None) -> Path:
    """Build the bronze output path for a FRED series."""
    output_name = filename or f"{series_id}.parquet"
    return get_repo_root() / "data" / "bronze" / "fred" / series_id / output_name


def get_ingestion_runs_log_path() -> Path:
    """Path to append-only ingestion run metadata log."""
    return get_repo_root() / "logs" / "ingestion_runs.jsonl"
