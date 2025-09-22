#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Management System - Main Entry Point
Комплексная система управления проектами

Author: Genocide12
Version: 1.0.0
Date: 2024

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


class InitializationThread(QThread):
    """
    Background thread for application initialization
    Фоновый поток для инициализации приложения
    """
    progress_updated = pyqtSignal(int, str)
    initialization_complete = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.config_manager = None
        self.db_manager = None
        
    def run(self):
        """
        Initialize application components
        Инициализация компонентов приложения
        """
        try:
            # Step 1: Check system requirements
            self.progress_updated.emit(10, "Checking system requirements...")
            system_checker = SystemChecker()
            if not system_checker.check_all():
                self.initialization_complete.emit(False, "System requirements check failed")
                return
                
            # Step 2: Load configuration
            self.progress_updated.emit(25, "Loading configuration...")
            self.config_manager = ConfigManager()
            self.config_manager.load_config()
            
            # Step 3: Setup logging
            self.progress_updated.emit(40, "Setting up logging system...")
            setup_logging(self.config_manager.get_config())
            
            # Step 4: Initialize database
            self.progress_updated.emit(55, "Initializing database...")
            self.db_manager = DatabaseManager()
            self.db_manager.initialize()
            
            # Step 5: Check database integrity
            self.progress_updated.emit(70, "Verifying database integrity...")
            self.db_manager.verify_integrity()
            
            # Step 6: Load user preferences
            self.progress_updated.emit(85, "Loading user preferences...")
            self.config_manager.load_user_preferences()
            
            # Step 7: Complete initialization
            self.progress_updated.emit(100, "Initialization complete")
            self.initialization_complete.emit(True, "Application initialized successfully")
            
        except Exception as e:
            logging.error(f"Initialization failed: {str(e)}")
            logging.error(traceback.format_exc())
            self.initialization_complete.emit(False, f"Initialization failed: {str(e)}")


class ApplicationLauncher:
    """
    Main application launcher with splash screen and initialization
    Основной запускатель приложения с экраном загрузки и инициализацией
    """
    
    def __init__(self):
        self.app = None
        self.splash = None
        self.main_app = None
        self.init_thread = None
        
    def setup_qt_application(self):
        """
        Setup Qt application with proper attributes
        Настройка Qt приложения с необходимыми атрибутами
        """
        # Set application attributes before creating QApplication
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Create application instance
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("Project Management System")
        self.app.setApplicationVersion("1.0.0")
        self.app.setApplicationDisplayName("Система управления проектами")
        self.app.setOrganizationName("Genocide12")
        self.app.setOrganizationDomain("github.com/Genocide12")
        
        # Set application icon
        icon_path = project_root / "resources" / "icons" / "app_icon.ico"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
            
        # Set application font
        font = QFont("Segoe UI", 9)
        self.app.setFont(font)
        
        # Set application style
        self.app.setStyle("Fusion")
        
    def create_splash_screen(self):
        """
        Create and show splash screen
        Создание и отображение экрана загрузки
        """
        splash_manager = SplashScreenManager()
        self.splash = splash_manager.create_splash()
        
        if self.splash:
            self.splash.show()
            self.splash.showMessage(
                "Загрузка системы управления проектами...",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                Qt.GlobalColor.white
            )
            
    def start_initialization(self):
        """
        Start background initialization thread
        Запуск фонового потока инициализации
        """
        self.init_thread = InitializationThread()
        self.init_thread.progress_updated.connect(self.update_splash_message)
        self.init_thread.initialization_complete.connect(self.on_initialization_complete)
        self.init_thread.start()
        
    def update_splash_message(self, progress, message):
        """
        Update splash screen with progress information
        Обновление экрана загрузки информацией о прогрессе
        """
        if self.splash:
            russian_message = self.translate_message(message)
            self.splash.showMessage(
                f"{russian_message} ({progress}%)",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                Qt.GlobalColor.white
            )
            
    def translate_message(self, message):
        """
        Translate initialization messages to Russian
        Перевод сообщений инициализации на русский язык
        """
        translations = {
            "Checking system requirements...": "Проверка системных требований...",
            "Loading configuration...": "Загрузка конфигурации...",
            "Setting up logging system...": "Настройка системы журналирования...",
            "Initializing database...": "Инициализация базы данных...",
            "Verifying database integrity...": "Проверка целостности базы данных...",
            "Loading user preferences...": "Загрузка пользовательских настроек...",
            "Initialization complete": "Инициализация завершена"
        }
        return translations.get(message, message)
        
    def on_initialization_complete(self, success, message):
        """
        Handle initialization completion
        Обработка завершения инициализации
        """
        if success:
            self.launch_main_application()
        else:
            self.show_error_and_exit(f"Ошибка инициализации: {message}")
            
    def launch_main_application(self):
        """
        Launch the main application window
        Запуск главного окна приложения
        """
        try:
            # Hide splash screen
            if self.splash:
                self.splash.close()
                
            # Create main application
            self.main_app = ProjectManagerApp(
                config_manager=self.init_thread.config_manager,
                db_manager=self.init_thread.db_manager
            )
            
            # Show main window
            self.main_app.show()
            
            # Setup application exit handling
            self.app.aboutToQuit.connect(self.cleanup)
            
        except Exception as e:
            logging.error(f"Failed to launch main application: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error_and_exit(f"Не удалось запустить главное окно: {str(e)}")
            
    def show_error_and_exit(self, error_message):
        """
        Show error message and exit application
        Отображение сообщения об ошибке и выход из приложения
        """
        if self.splash:
            self.splash.close()
            
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Критическая ошибка")
        msg_box.setText("Произошла критическая ошибка при запуске приложения.")
        msg_box.setDetailedText(error_message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        sys.exit(1)
        
    def cleanup(self):
        """
        Cleanup resources before application exit
        Очистка ресурсов перед выходом из приложения
        """
        try:
            if self.init_thread and self.init_thread.db_manager:
                self.init_thread.db_manager.close()
                
            if self.main_app:
                self.main_app.cleanup()
                
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
            
    def run(self):
        """
        Main application entry point
        Главная точка входа приложения
        """
        try:
            # Setup Qt application
            self.setup_qt_application()
            
            # Create splash screen
            self.create_splash_screen()
            
            # Start initialization
            self.start_initialization()
            
            # Run application event loop
            return self.app.exec()
            
        except Exception as e:
            print(f"Critical error during application startup: {str(e)}")
            print(traceback.format_exc())
            return 1


def setup_error_handling():
    """
    Setup global error handling
    Настройка глобальной обработки ошибок
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logging.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
    sys.excepthook = handle_exception


def check_python_version():
    """
    Check if Python version meets requirements
    Проверка соответствия версии Python требованиям
    """
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print("Ошибка: Требуется Python 3.8 или выше.")
        sys.exit(1)


def main():
    """
    Application main function
    Главная функция приложения
    """
    # Check Python version
    check_python_version()
    
    # Setup error handling
    setup_error_handling()
    
    # Create and run application launcher
    launcher = ApplicationLauncher()
    exit_code = launcher.run()
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
