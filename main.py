#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Management System - Main Entry Point
Система управления проектами - Главная точка входа

Author: Genocide12
Version: 1.0.0
Date: 2025

This is the main entry point for the Project Management System.
Это главная точка входа в систему управления проектами.
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import application modules
try:
    from app.core.application import ProjectManagerApp
    from app.core.config import Config, ConfigManager
    from app.core.logger import setup_logging
    from app.database.connection import DatabaseManager
    from app.utils.system_check import SystemChecker
    from app.utils.splash import SplashScreenManager
except ImportError as e:
    print(f"Critical import error: {e}")
    print("Please ensure all required dependencies are installed.")
    sys.exit(1)


def main():
    """
    Application main function
    Главная функция приложения
    """
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print("Ошибка: Требуется Python 3.8 или выше.")
        sys.exit(1)

    # Create QApplication
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Project Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Genocide12")

    try:
        # Initialize configuration
        config_manager = ConfigManager()
        config_manager.load_config()

        # Setup logging
        setup_logging(config_manager.get_config())

        # Initialize database
        db_manager = DatabaseManager(config_manager)
        db_manager.initialize()

        # Create main application
        main_app = ProjectManagerApp(config_manager, db_manager)
        main_app.show()

        # Run application
        return app.exec()

    except Exception as e:
        logging.error(f"Critical error during application startup: {str(e)}")
        logging.error(traceback.format_exc())

        # Show error dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Критическая ошибка")
        msg_box.setText("Произошла критическая ошибка при запуске приложения.")
        msg_box.setDetailedText(str(e))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)