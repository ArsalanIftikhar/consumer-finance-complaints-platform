from pathlib import Path

import yaml


def test_ingestion_config_has_required_fred_keys() -> None:
    config_path = Path("config/ingestion.yml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    assert "fred" in config
    fred = config["fred"]
    required_keys = [
        "dataset_name",
        "output_format",
        "timeout_seconds",
        "file_type",
        "observation_start",
    ]
    for key in required_keys:
        assert key in fred


def test_fred_series_config_has_series_codes() -> None:
    series_path = Path("config/fred_series.yml")
    series_config = yaml.safe_load(series_path.read_text(encoding="utf-8"))

    assert "series" in series_config
    assert isinstance(series_config["series"], list)
    assert series_config["series"]
    assert all("code" in item and item["code"] for item in series_config["series"])
