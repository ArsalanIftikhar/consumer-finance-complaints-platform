"""Environment variable helpers for ingestion tasks."""

import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env_var(name: str) -> str:
    """Return an environment variable value or raise a readable error."""
    value = os.getenv(name)
    if value:
        return value
    raise ValueError(
        f"Missing required environment variable '{name}'. "
        "Set it in your environment or .env file."
    )


def get_fred_api_key() -> str:
    """Return FRED API key from environment."""
    return get_required_env_var("FRED_API_KEY")


def get_duckdb_path() -> str:
    """Return DuckDB path from environment."""
    return get_required_env_var("DUCKDB_PATH")
