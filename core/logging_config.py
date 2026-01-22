"""
CHAIRMAN - Logging Configuration Module

This module sets up comprehensive logging for the application.
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LogConfig


def setup_logging() -> logging.Logger:
    """
    Configure and return the application logger.

    This sets up:
    - Console logging for development
    - Rotating file logging for production
    - Proper formatting and log levels

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    LogConfig.LOG_DIR.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("chairman")
    logger.setLevel(getattr(logging, LogConfig.LOG_LEVEL))

    # Avoid adding handlers multiple times if already configured
    if logger.handlers:
        return logger

    # Create formatters
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)

    # Console handler (for development/debugging)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating, for production)
    try:
        file_handler = RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.LOG_MAX_BYTES,
            backupCount=LogConfig.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, log to console and continue
        logger.warning(f"Could not set up file logging: {e}")

    logger.info(f"Logging initialized - Log file: {LogConfig.LOG_FILE}")

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Optional name for the logger (typically __name__)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"chairman.{name}")
    return logging.getLogger("chairman")
