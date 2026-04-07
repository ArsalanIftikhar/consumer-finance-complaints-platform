"""Shared data writers for ingestion pipelines."""

from pathlib import Path

import pandas as pd


def write_dataframe_to_parquet(df: pd.DataFrame, output_path: str | Path) -> tuple[Path, int]:
    """Write a dataframe to Parquet and return output path with row count."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path, len(df)
