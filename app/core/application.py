#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application Class
Основной класс приложения

This module contains the main application class that manages the overall
application lifecycle, window management, and core functionality.

Этот модуль содержит основной класс приложения, который управляет общим
жизненным циклом приложения, управлением окон и основной функциональностью.
"""

import sys
import logging
import traceback
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QSystemTrayIcon, 
    QMenu, QVBoxLayout, QWidget, QSplitter, QStatusBar,
    QMenuBar, QToolBar, QDockWidget, QTabWidget
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSettings, QSize, QPoint,
    QTranslator, QLocale, QLibraryInfo
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QAction, QKeySequence, QFont, QPalette,
    QColor, QCloseEvent, QShowEvent, QResizeEvent
)

# Import application modules
from app.core.config import ConfigManager
from app.database.connection import DatabaseManager
from app.ui.main_window import MainWindow
from app.ui.login_window import LoginWindow
from app.ui.splash_screen import SplashScreen
from app.utils.theme_manager import ThemeManager
from app.utils.notification_manager import NotificationManager
from app.utils.session_manager import SessionManager
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.report_service import ReportService


class ProjectManagerApp(QMainWindow):
    """
    Main application class for the Project Management System
    Основной класс приложения для системы управления проектами
    """
    
    # Custom signals
    user_logged_in = pyqtSignal(object)  # Emitted when user logs in
    user_logged_out = pyqtSignal()       # Emitted when user logs out
    theme_changed = pyqtSignal(str)      # Emitted when theme changes
    language_changed = pyqtSignal(str)   # Emitted when language changes
    
    def __init__(self, config_manager: ConfigManager, db_manager: DatabaseManager):
        """
        Initialize the main application
        Инициализация основного приложения
        """
        super().__init__()
        
        # Core managers
        self.config_manager = config_manager
        self.db_manager = db_manager
        
        # UI components
        self.main_window = None
        self.login_window = None
        self.splash_screen = None
        self.system_tray = None
        
        # Managers and services
        self.theme_manager = None
        self.notification_manager = None
        self.session_manager = None
        self.user_service = None
        self.project_service = None
        self.task_service = None
        self.report_service = None
        
        # Application state
        self.current_user = None
        self.is_initialized = False
        self.auto_save_timer = None
        self.translator = QTranslator()
        
        # Setup application
        self.setup_application()
        
    def setup_application(self):
        """
        Setup the main application components
        Настройка основных компонентов приложения
        """
        try:
            # Setup basic window properties
            self.setWindowTitle("Project Management System - Система управления проектами")
            self.setMinimumSize(1200, 800)
            
            # Load application icon
            self.setup_application_icon()
            
            # Initialize managers
            self.setup_managers()
            
            # Initialize services
            self.setup_services()
            
            # Setup UI components
            self.setup_ui_components()
            
            # Setup system tray
            self.setup_system_tray()
            
            # Setup auto-save
            self.setup_auto_save()
            
            # Setup signal connections
            self.setup_signal_connections()
            
            # Apply theme and localization
            self.apply_theme()
            self.apply_localization()
            
            # Restore window state
            self.restore_window_state()
            
            self.is_initialized = True
            logging.info("Application initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to setup application: {e}")
            logging.error(traceback.format_exc())
            raise
            
    def setup_application_icon(self):
        """
        Setup application icon
        Настройка иконки приложения
        """
        icon_path = Path("resources/icons/app_icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            # Create a default icon if none exists
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#2196F3"))
            self.setWindowIcon(QIcon(pixmap))
            
    def setup_managers(self):
        """
        Initialize all manager components
        Инициализация всех компонентов менеджеров
        """
        self.theme_manager = ThemeManager(self.config_manager)
        self.notification_manager = NotificationManager(self.config_manager)
        self.session_manager = SessionManager(self.config_manager, self.db_manager)
        
    def setup_services(self):
        """
        Initialize all service components
        Инициализация всех компонентов сервисов
        """
        self.user_service = UserService(self.db_manager)
        self.project_service = ProjectService(self.db_manager)
        self.task_service = TaskService(self.db_manager)
        self.report_service = ReportService(self.db_manager)
        
    def setup_ui_components(self):
        """
        Setup main UI components
        Настройка основных компонентов UI
        """
        # Create main window
        self.main_window = MainWindow(
            self.config_manager,
            self.db_manager,
            self.user_service,
            self.project_service,
            self.task_service,
            self.report_service
        )
        
        # Create login window
        self.login_window = LoginWindow(
            self.config_manager,
            self.user_service,
            self.session_manager
        )
        
        # Set main window as central widget
        self.setCentralWidget(self.main_window)
        
        # Hide main window initially (show after login)
        self.main_window.hide()
        
    def setup_system_tray(self):
        """
        Setup system tray functionality
        Настройка функциональности системного трея
        """
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.system_tray = QSystemTrayIcon(self)
            self.system_tray.setIcon(self.windowIcon())
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Show/Hide action
            show_action = tray_menu.addAction("Показать")
            show_action.triggered.connect(self.show_main_window)
            
            tray_menu.addSeparator()
            
            # Quick actions
            new_project_action = tray_menu.addAction("Новый проект")
            new_project_action.triggered.connect(self.show_new_project_dialog)
            
            new_task_action = tray_menu.addAction("Новая задача")
            new_task_action.triggered.connect(self.show_new_task_dialog)
            
            tray_menu.addSeparator()
            
            # Exit action
            exit_action = tray_menu.addAction("Выход")
            exit_action.triggered.connect(self.quit_application)
            
            self.system_tray.setContextMenu(tray_menu)
            self.system_tray.activated.connect(self.tray_icon_activated)
            self.system_tray.show()
            
    def setup_auto_save(self):
        """
        Setup automatic saving functionality
        Настройка функциональности автосохранения
        """
        auto_save_interval = self.config_manager.get_setting(
            "ui", "auto_save_interval", 300
        ) * 1000  # Convert to milliseconds
        
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.perform_auto_save)
        self.auto_save_timer.start(auto_save_interval)
        
    def setup_signal_connections(self):
        """
        Setup signal connections between components
        Настройка соединений сигналов между компонентами
        """
        # Connect login window signals
        if self.login_window:
            self.login_window.login_successful.connect(self.on_user_logged_in)
            self.login_window.login_cancelled.connect(self.quit_application)
            
        # Connect main window signals
        if self.main_window:
            self.main_window.logout_requested.connect(self.on_user_logout)
            self.main_window.theme_change_requested.connect(self.change_theme)
            self.main_window.language_change_requested.connect(self.change_language)
            
        # Connect session manager signals
        if self.session_manager:
            self.session_manager.session_expired.connect(self.on_session_expired)
            
    def apply_theme(self):
        """
        Apply the current theme to the application
        Применение текущей темы к приложению
        """
        if self.theme_manager:
            current_theme = self.config_manager.get_setting("ui", "theme", "light")
            self.theme_manager.apply_theme(self, current_theme)
            
    def apply_localization(self):
        """
        Apply localization settings
        Применение настроек локализации
        """
        language = self.config_manager.get_setting("ui", "language", "ru")
        
        # Load translation file
        translation_file = f"translations/{language}.qm"
        if Path(translation_file).exists():
            if self.translator.load(translation_file):
                QApplication.instance().installTranslator(self.translator)
                
    def restore_window_state(self):
        """
        Restore window geometry and state from settings
        Восстановление геометрии и состояния окна из настроек
        """
        settings = QSettings()
        
        # Restore geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Center window on screen
            self.center_on_screen()
            
        # Restore window state
        window_state = settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
            
    def center_on_screen(self):
        """
        Center the window on the screen
        Центрирование окна на экране
        """
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        
        self.move(x, y)
        
    def show_login_window(self):
        """
        Show the login window
        Показать окно входа
        """
        if self.login_window:
            self.login_window.show()
            self.login_window.raise_()
            self.login_window.activateWindow()
            
    def show_main_window(self):
        """
        Show the main application window
        Показать главное окно приложения
        """
        self.show()
        self.raise_()
        self.activateWindow()
        
        if self.main_window:
            self.main_window.show()
            
    def hide_main_window(self):
        """
        Hide the main application window
        Скрыть главное окно приложения
        """
        self.hide()
        
    def on_user_logged_in(self, user):
        """
        Handle successful user login
        Обработка успешного входа пользователя
        """
        self.current_user = user
        
        # Hide login window
        if self.login_window:
            self.login_window.hide()
            
        # Show main window
        self.show_main_window()
        
        # Update main window with user data
        if self.main_window:
            self.main_window.set_current_user(user)
            
        # Start session
        if self.session_manager:
            self.session_manager.start_session(user)
            
        # Show notification
        if self.notification_manager:
            self.notification_manager.show_notification(
                "Добро пожаловать!",
                f"Пользователь {user.username} успешно вошел в систему"
            )
            
        # Emit signal
        self.user_logged_in.emit(user)
        
        logging.info(f"User {user.username} logged in successfully")
        
    def on_user_logout(self):
        """
        Handle user logout
        Обработка выхода пользователя
        """
        if self.current_user:
            logging.info(f"User {self.current_user.username} logging out")
            
        # End session
        if self.session_manager:
            self.session_manager.end_session()
            
        # Clear current user
        self.current_user = None
        
        # Hide main window
        self.hide_main_window()
        
        # Show login window
        self.show_login_window()
        
        # Clear main window data
        if self.main_window:
            self.main_window.clear_user_data()
            
        # Emit signal
        self.user_logged_out.emit()
        
    def on_session_expired(self):
        """
        Handle session expiration
        Обработка истечения сессии
        """
        if self.notification_manager:
            self.notification_manager.show_notification(
                "Сессия истекла",
                "Ваша сессия истекла. Пожалуйста, войдите снова.",
                level="warning"
            )
            
        self.on_user_logout()
        
    def change_theme(self, theme_name: str):
        """
        Change application theme
        Изменение темы приложения
        """
        if self.theme_manager:
            self.theme_manager.apply_theme(self, theme_name)
            self.config_manager.set_setting("ui", "theme", theme_name)
            self.config_manager.save_config()
            self.theme_changed.emit(theme_name)
            
    def change_language(self, language: str):
        """
        Change application language
        Изменение языка приложения
        """
        self.config_manager.set_setting("ui", "language", language)
        self.config_manager.save_config()
        self.apply_localization()
        self.language_changed.emit(language)
        
    def show_new_project_dialog(self):
        """
        Show new project creation dialog
        Показать диалог создания нового проекта
        """
        if self.main_window and self.current_user:
            self.show_main_window()
            self.main_window.show_new_project_dialog()
            
    def show_new_task_dialog(self):
        """
        Show new task creation dialog
        Показать диалог создания новой задачи
        """
        if self.main_window and self.current_user:
            self.show_main_window()
            self.main_window.show_new_task_dialog()
            
    def tray_icon_activated(self, reason):
        """
        Handle system tray icon activation
        Обработка активации иконки системного трея
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide_main_window()
            else:
                self.show_main_window()
                
    def perform_auto_save(self):
        """
        Perform automatic save of application data
        Выполнение автоматического сохранения данных приложения
        """
        try:
            if self.main_window and self.current_user:
                self.main_window.auto_save_data()
                
            # Save configuration
            self.config_manager.save_config()
            
            logging.debug("Auto-save completed successfully")
            
        except Exception as e:
            logging.error(f"Auto-save failed: {e}")
            
    def save_window_state(self):
        """
        Save current window state to settings
        Сохранение текущего состояния окна в настройки
        """
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
    def quit_application(self):
        """
        Quit the application gracefully
        Корректное завершение работы приложения
        """
        self.cleanup()
        QApplication.quit()
        
    def cleanup(self):
        """
        Cleanup resources before application exit
        Очистка ресурсов перед выходом из приложения
        """
        try:
            # Save window state
            self.save_window_state()
            
            # Save configuration
            self.config_manager.save_config()
            self.config_manager.save_user_preferences()
            
            # End current session
            if self.session_manager and self.current_user:
                self.session_manager.end_session()
                
            # Stop auto-save timer
            if self.auto_save_timer:
                self.auto_save_timer.stop()
                
            # Hide system tray
            if self.system_tray:
                self.system_tray.hide()
                
            # Close database connections
            if self.db_manager:
                self.db_manager.close()
                
            logging.info("Application cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            
    def closeEvent(self, event: QCloseEvent):
        """
        Handle application close event
        Обработка события закрытия приложения
        """
        if self.system_tray and self.system_tray.isVisible():
            # Minimize to tray instead of closing
            event.ignore()
            self.hide_main_window()
            
            if self.notification_manager:
                self.notification_manager.show_notification(
                    "Приложение свернуто",
                    "Приложение продолжает работать в системном трее"
                )
        else:
            # Actually quit the application
            self.quit_application()
            event.accept()
            
    def showEvent(self, event: QShowEvent):
        """
        Handle window show event
        Обработка события показа окна
        """
        super().showEvent(event)
        
        # Start with login if no user is logged in
        if not self.current_user and self.is_initialized:
            QTimer.singleShot(100, self.show_login_window)
            
    def resizeEvent(self, event: QResizeEvent):
        """
        Handle window resize event
        Обработка события изменения размера окна
        """
        super().resizeEvent(event)
        
        # Update window geometry in config
        if self.is_initialized:
            geometry = {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height()
            }
            self.config_manager.ui_config.window_geometry = geometry
