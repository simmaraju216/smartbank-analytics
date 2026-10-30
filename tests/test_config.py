
from pathlib import Path

from config.settings import (
    PROJECT_ROOT,
    PROJECT_NAME,
    RANDOM_SEED,
    DATA_SIZE,
    DUCKDB_PATH,
    LOG_LEVEL
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_project_name():
    assert PROJECT_NAME == "SmartBankAnalytics"


def test_random_seed():
    assert isinstance(RANDOM_SEED, int)
    assert RANDOM_SEED >= 0


def test_data_size():
    assert isinstance(DATA_SIZE, int)
    assert DATA_SIZE > 0


def test_duckdb_path():
    assert isinstance(DUCKDB_PATH, Path)
    assert DUCKDB_PATH.is_absolute()
    assert DUCKDB_PATH == PROJECT_ROOT / "data" / "smartbank.duckdb"


def test_log_level():
    assert LOG_LEVEL in {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    }
