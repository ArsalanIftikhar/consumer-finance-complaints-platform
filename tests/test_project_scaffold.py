from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


EXPECTED_ROOT_FILES = [
    "README.md",
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "pyproject.toml",
    "Makefile",
]

EXPECTED_DIRECTORIES = [
    "docs",
    "diagrams",
    "config",
    "data/bronze/cfpb_complaints",
    "data/bronze/fred",
    "data/warehouse",
    "data/exports",
    "logs",
    "src/ingestion",
    "src/utils",
    "src/orchestration",
    "dbt/complaints_ae",
    "tests",
    ".github/workflows",
]


def test_expected_root_files_exist() -> None:
    missing = [path for path in EXPECTED_ROOT_FILES if not (ROOT / path).is_file()]
    assert not missing, f"Missing expected root files: {missing}"


def test_expected_scaffold_directories_exist() -> None:
    missing = [path for path in EXPECTED_DIRECTORIES if not (ROOT / path).is_dir()]
    assert not missing, f"Missing expected scaffold directories: {missing}"
