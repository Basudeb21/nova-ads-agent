
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


# ==========================================
# PROJECT ROOT
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]


# ==========================================
# ENVIRONMENT
# ==========================================

load_dotenv(ROOT_DIR / ".env")


# ==========================================
# APPLICATION
# ==========================================

APP_NAME = os.getenv(
    "APP_NAME",
    "NOVA ADS STUDIO",
)

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
)

DEBUG = os.getenv(
    "DEBUG",
    "false",
).lower() in ("true", "1", "yes")


# ==========================================
# DATABASE
# ==========================================

DB_HOST = os.getenv("DB_HOST", "localhost")

DB_PORT = int(
    os.getenv("DB_PORT", "3306")
)

DB_NAME = os.getenv(
    "DB_NAME",
    "nova_ads",
)

DB_USERNAME = os.getenv(
    "DB_USERNAME",
    "",
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    "",
)

DB_CHARSET = os.getenv(
    "DB_CHARSET",
    "utf8mb4",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
).strip()

if not DATABASE_URL:
    if not DB_USERNAME or not DB_PASSWORD:
        raise RuntimeError(
            "Configure DATABASE_URL or DB_USERNAME and DB_PASSWORD in .env"
        )

    DATABASE_URL = (
        "mysql+pymysql://"
        f"{quote_plus(DB_USERNAME)}:"
        f"{quote_plus(DB_PASSWORD)}@"
        f"{DB_HOST}:{DB_PORT}/"
        f"{DB_NAME}?charset={DB_CHARSET}"
    )


# ==========================================
# LOGGING
# ==========================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

LOG_FILE_NAME = os.getenv(
    "LOG_FILE_NAME",
    "nova_ads_studio.log",
)

LOG_MAX_SIZE = int(
    os.getenv("LOG_MAX_SIZE", "10485760")
)

LOG_BACKUP_COUNT = int(
    os.getenv("LOG_BACKUP_COUNT", "5")
)


# ==========================================
# STORAGE PATHS
# ==========================================

STORAGE_NAME = os.getenv(
    "STORAGE_DIR",
    "storage",
)

INPUT_NAME = os.getenv(
    "INPUT_DIR",
    "input",
)

LOG_NAME = os.getenv(
    "LOG_DIR",
    "logs",
)

STORAGE_DIR = ROOT_DIR / STORAGE_NAME

INPUT_DIR = STORAGE_DIR / INPUT_NAME

LOG_DIR = STORAGE_DIR / LOG_NAME


# ==========================================
# DIRECTORY INITIALIZATION
# ==========================================

STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# REDIS CONFIGURATION
# ============================================================

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

REDIS_SOCKET_TIMEOUT = float(
    os.getenv("REDIS_SOCKET_TIMEOUT", "5")
)

REDIS_CONNECT_TIMEOUT = float(
    os.getenv("REDIS_CONNECT_TIMEOUT", "5")
)

# ============================================================
# INTAKE SESSION CONFIGURATION
# ============================================================

INTAKE_SESSION_TTL_SECONDS = int(
    os.getenv("INTAKE_SESSION_TTL_SECONDS", "86400")
)