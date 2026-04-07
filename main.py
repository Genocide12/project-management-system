#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Management System - Main Entry Point
Система управления проектами - Главная точка входа

Author: Genocide12
Version: 1.0.0
Date: 2025
"""

import sys
import logging
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from app.core.config import ConfigManager
from app.core.logging import setup_logging
from app.database.manager import DatabaseManager
from app.ui.main_window import MainWindow


def _configure_logging(config: dict) -> None:
    """Configure application logging."""
    try:
        setup_logging(config)
    except Exception as e:
        print(f"Warning: Failed to setup logging: {e}")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def _initialize_database(config_manager: ConfigManager) -> DatabaseManager:
    """Initialize database connection."""
    db_manager = DatabaseManager(config_manager)
    db_manager.initialize()
    return db_manager


def main() -> int:
    """
    Application main function.
    Главная функция приложения.
    """
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("Project Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Genocide12")

    config_manager = None
    db_manager = None

    try:
        config_manager = ConfigManager()
        config_manager.load_config()
        config = config_manager.get_config()

        _configure_logging(config)

        db_manager = _initialize_database(config_manager)

        window = MainWindow(config_manager, db_manager)
        window.show()

        return app.exec()

    except Exception as e:
        logging.error(f"Critical error during startup: {e}")
        logging.error(traceback.format_exc())

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Критическая ошибка")
        msg_box.setText("Произошла критическая ошибка при запуске приложения.")
        msg_box.setDetailedText(str(e))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        return 1

    finally:
        if db_manager:
            db_manager.close()


if __name__ == "__main__":
    sys.exit(main())