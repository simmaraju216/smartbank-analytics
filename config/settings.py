import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load environment variables from .env
load_dotenv(PROJECT_ROOT / ".env")

# Project configuration
PROJECT_NAME = os.getenv("PROJECT_NAME", "SmartBankAnalytics")

RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

DATA_SIZE = int(os.getenv("DATA_SIZE", "10000"))

DUCKDB_PATH = Path(
    os.getenv("DUCKDB_PATH", "data/smartbank.duckdb")
)

# Convert relative database path to absolute path
if not DUCKDB_PATH.is_absolute():
    DUCKDB_PATH = PROJECT_ROOT / DUCKDB_PATH

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")