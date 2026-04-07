#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration module.
Модуль конфигурации логирования.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Setup application logging with file and console handlers.
    Настройка логирования приложения с обработчиками файла и консоли.
    
    Args:
        config: Application configuration dictionary.
    """
    log_level = logging.INFO
    log_file = "logs/app.log"
    max_bytes = 10 * 1024 * 1024  # 10 MB
    backup_count = 5

    if config:
        app_config = config.get("application", {})
        log_level_str = app_config.get("log_level", "INFO")
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        log_file = app_config.get("log_file_path", "logs/app.log")
        max_bytes = app_config.get("log_max_size_mb", 10) * 1024 * 1024
        backup_count = app_config.get("log_backup_count", 5)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
        file_logger = logging.getLogger(__name__)
        file_logger.warning(f"File logging disabled: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    Получить экземпляр логгера с указанным именем.
    
    Args:
        name: Logger name (usually __name__).
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
