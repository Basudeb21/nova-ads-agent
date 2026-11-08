
import logging
import logging.handlers

from app.core.config import (
    LOG_DIR,
    LOG_LEVEL,
    LOG_FILE_NAME,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT,
)


LOG_FILE = LOG_DIR / LOG_FILE_NAME

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:

    root_logger = logging.getLogger()

    root_logger.setLevel(
        getattr(logging, LOG_LEVEL, logging.INFO)
    )

    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
