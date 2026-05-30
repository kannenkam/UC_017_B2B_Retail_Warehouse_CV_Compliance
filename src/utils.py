# Shared logging metrics and general helper scripts
import logging
import sys
from pathlib import Path


def setup_production_logger(name: str = "Warehouse_Audit_System") -> logging.Logger:
    """Sets up a standardized, professional stream logger for the pipeline modules."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if initialized multiple times across modules
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Define a crisp corporate logging format
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Direct logs cleanly to the standard console output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def clear_local_directory(directory_path: Path):
    """Safely cleans up stale files within a directory without deleting the directory itself."""
    if directory_path.exists() and directory_path.is_dir():
        for item in directory_path.iterdir():
            if item.is_file():
                item.unlink()