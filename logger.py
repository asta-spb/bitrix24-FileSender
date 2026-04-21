import logging
import sys
from pathlib import Path

LOG_FILE = Path("bitrix_sender.log")
_FMT = "%(asctime)s [%(levelname)s] %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger("bitrix_sender")
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter

    # Console handler — respects verbose flag
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(_FMT, _DATE_FMT))

    # File handler — always DEBUG
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FMT, _DATE_FMT))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def get() -> logging.Logger:
    return logging.getLogger("bitrix_sender")
