import pandas as pd

from src.ingestion.fred import normalise_fred_observations


def test_normalise_fred_observations_returns_dataframe_with_required_columns() -> None:
    payload = {
        "observations": [
            {"date": "2024-01-01", "value": "3.7"},
            {"date": "2024-02-01", "value": "3.8"},
        ]
    }

    result = normalise_fred_observations(
        payload,
        series_id="UNRATE",
        source_run_id="run_123",
        extracted_at_utc="2026-04-07T00:00:00+00:00",
    )

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [
        "date",
        "value",
        "series_id",
        "source_run_id",
        "extracted_at_utc",
    ]
    assert len(result) == 2
    assert result["series_id"].eq("UNRATE").all()
    assert result["source_run_id"].eq("run_123").all()


def test_normalise_fred_observations_handles_empty_payload() -> None:
    payload = {"observations": []}

    result = normalise_fred_observations(
        payload,
        series_id="UNRATE",
        source_run_id="run_456",
        extracted_at_utc="2026-04-07T00:00:00+00:00",
    )

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == [
        "date",
        "value",
        "series_id",
        "source_run_id",
        "extracted_at_utc",
    ]
