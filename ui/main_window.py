# -*- coding: utf-8 -*-
"""
Main Window Module for Project Management System

Главное окно системы управления проектами

Features:
- Tabbed interface with Dashboard, Projects, Tasks, Reports, Settings
- Modern navigation and menu system
- Integration with dashboard view
- Theme management and shortcuts
- Session management and user authentication

Author: Genocide12
Date: September 2025
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QToolBar, QStatusBar,
    QAction, QSplitter, QStackedWidget, QFrame,
    QLabel, QPushButton, QMessageBox, QDialog,
    QApplication, QShortcut, QSystemTrayIcon,
    QMenu, QStyle, QProgressBar, QComboBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, pyqtSignal, QThread,
    QSettings, QStandardPaths, QDir
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QAction as QGuiAction,
    QKeySequence, QPalette, QColor
)

# Import views and components
try:
    from .dashboard_view import DashboardView
except ImportError:
    # Fallback dashboard if not available yet
    class DashboardView(QWidget):
        project_create_requested = pyqtSignal()
        task_create_requested = pyqtSignal()
        report_generate_requested = pyqtSignal()
        
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            welcome_label = QLabel("Добро пожаловать! База данных инициализирована.")
            welcome_label.setStyleSheet("font-size: 16px; padding: 20px; color: #2c3e50; font-weight: bold;")
            layout.addWidget(welcome_label)
            
            # Add some dashboard-like content
            dashboard_label = QLabel("📊 Dashboard View - Панель управления (В разработке)")
            dashboard_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 10px;")
            layout.addWidget(dashboard_label)
            
            # Add some quick action buttons
            actions_frame = QFrame()
            actions_layout = QHBoxLayout(actions_frame)
            
            project_btn = QPushButton("📁 Новый проект")
            task_btn = QPushButton("📝 Новая задача")
            report_btn = QPushButton("📈 Отчеты")
            
            for btn in [project_btn, task_btn, report_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-size: 12px;
                        margin: 5px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
            
            project_btn.clicked.connect(self.project_create_requested.emit)
            task_btn.clicked.connect(self.task_create_requested.emit)
            report_btn.clicked.connect(self.report_generate_requested.emit)
            
            actions_layout.addWidget(project_btn)
            actions_layout.addWidget(task_btn)
            actions_layout.addWidget(report_btn)
            actions_layout.addStretch()
            
            layout.addWidget(actions_frame)
            layout.addStretch()


class NavigationBar(QFrame):
    """
    Боковая панель навигации с иконками и текстом
    """
    
    tab_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tab = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса навигации"""
        self.setFixedWidth(200)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: none;
                border-right: 1px solid #2c3e50;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Логотип приложения
        logo_label = QLabel("PMS")
        logo_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
            }
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #2c3e50;")
        layout.addWidget(separator)
        
        # Создание кнопок навигации
        nav_items = [
            ("📊", "Панель", "Dashboard"),
            ("📁", "Проекты", "Projects"),
            ("📝", "Задачи", "Tasks"),
            ("📈", "Отчеты", "Reports"),
            ("⚙️", "Настройки", "Settings")
        ]
        
        self.nav_buttons = []
        for i, (icon, text, tooltip) in enumerate(nav_items):
            btn = self.create_nav_button(icon, text, tooltip, i)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Выбираем первую вкладку по умолчанию
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
    
    def create_nav_button(self, icon: str, text: str, tooltip: str, index: int) -> QPushButton:
        """Создание кнопки навигации"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setToolTip(tooltip)
        btn.clicked.connect(lambda: self.select_tab(index))
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ecf0f1;
                text-align: left;
                padding: 8px 15px;
                font-size: 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3d566e;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        
        return btn
    
    def select_tab(self, index: int):
        """Выбор вкладки"""
        if index != self.current_tab:
            # Снимаем выделение с предыдущей кнопки
            if 0 <= self.current_tab < len(self.nav_buttons):
                self.nav_buttons[self.current_tab].setChecked(False)
            
            # Выделяем новую кнопку
            if 0 <= index < len(self.nav_buttons):
                self.nav_buttons[index].setChecked(True)
                self.current_tab = index
                self.tab_changed.emit(index)
    
    def set_current_tab(self, index: int):
        """Установка текущей вкладки извне"""
        self.select_tab(index)


class StatusBarWidget(QStatusBar):
    """
    Расширенная строка состояния
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Настройка интерфейса строки состояния"""
        # Основное сообщение
        self.main_label = QLabel("Готов")
        self.addWidget(self.main_label)
        
        # Прогресс-бар для длительных операций
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.addWidget(self.progress_bar)
        
        # Информация о пользователе
        self.user_label = QLabel("Пользователь не авторизован")
        self.addPermanentWidget(self.user_label)
        
        # Информация о базе данных
        self.db_label = QLabel("БД: SQLite")
        self.addPermanentWidget(self.db_label)
        
        # Время
        self.time_label = QLabel()
        self.addPermanentWidget(self.time_label)
        
        self.setStyleSheet("""
            QStatusBar {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
                font-size: 11px;
            }
            QLabel {
                padding: 2px 8px;
                color: #2c3e50;
            }
        """)
    
    def setup_timer(self):
        """Настройка таймера для обновления времени"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Обновление каждую секунду
        self.update_time()
    
    def update_time(self):
        """Обновление времени"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
    
    def show_message(self, message: str, timeout: int = 3000):
        """Показ временного сообщения"""
        self.main_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.main_label.setText("Готов"))


class MainWindow(QMainWindow):
    """
    Главное окно приложения Project Management System
    """
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        
        # Настройки приложения
        self.settings = QSettings("ProjectManagementSystem", "MainWindow")
        
        # Инициализация UI
        self.views = {}
        self.current_view_index = 0
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_connections()
        
        self.restore_settings()
        
        # Установка начальных значений
        self.setWindowTitle("Project Management System")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
    
    def setup_ui(self):
        """Настройка основного интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Боковая панель навигации
        self.navigation_bar = NavigationBar()
        main_layout.addWidget(self.navigation_bar)
        
        # Основная область содержимого
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Создание и добавление представлений
        self.create_views()
        
        # Настройка строки состояния
        self.status_bar = StatusBarWidget()
        self.setStatusBar(self.status_bar)
        
        # Показать приветственное сообщение
        self.status_bar.show_message("Приложение готово к работе")
    
    def create_views(self):
        """Создание всех представлений приложения"""
        # Dashboard
        self.dashboard_view = DashboardView()
        self.views['dashboard'] = self.dashboard_view
        self.content_stack.addWidget(self.dashboard_view)
        
        # Projects (placeholder)
        self.project_view = self.create_placeholder_view("📁 Project View", "Просмотр и управление проектами - В разработке")
        self.views['projects'] = self.project_view
        self.content_stack.addWidget(self.project_view)
        
        # Tasks (placeholder)
        self.task_view = self.create_placeholder_view("📝 Task View", "Управление задачами и канбан-доской - В разработке")
        self.views['tasks'] = self.task_view
        self.content_stack.addWidget(self.task_view)
        
        # Reports (placeholder)
        self.report_view = self.create_placeholder_view("📈 Report View", "Отчеты и аналитика проектов - В разработке")
        self.views['reports'] = self.report_view
        self.content_stack.addWidget(self.report_view)
        
        # Settings (placeholder)
        self.settings_view = self.create_placeholder_view("⚙️ Settings View", "Настройки приложения и профилей - В разработке")
        self.views['settings'] = self.settings_view
        self.content_stack.addWidget(self.settings_view)
    
    def create_placeholder_view(self, title: str, description: str) -> QWidget:
        """Создание заглушки для представления"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 10px;
                text-align: center;
            }
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        return widget
    
    def setup_menu(self):
        """Настройка главного меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("&Файл")
        
        # Создание проекта
        new_project_action = QAction("&Новый проект", self)
        new_project_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_project_action.triggered.connect(self.create_project)
        file_menu.addAction(new_project_action)
        
        # Создание задачи
        new_task_action = QAction("&Новая задача", self)
        new_task_action.setShortcut(QKeySequence("Ctrl+N"))
        new_task_action.triggered.connect(self.create_task)
        file_menu.addAction(new_task_action)
        
        file_menu.addSeparator()
        
        # Импорт/Экспорт
        export_action = QAction("&Экспорт...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction("В&ыход", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Вид
        view_menu = menubar.addMenu("&Вид")
        
        # Обновить
        refresh_action = QAction("&Обновить", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_current_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Полноэкранный режим
        fullscreen_action = QAction("&Полноэкранный режим", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Инструменты
        tools_menu = menubar.addMenu("&Инструменты")
        
        # Настройки
        settings_action = QAction("&Настройки", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(lambda: self.switch_to_view(4))  # Settings view
        tools_menu.addAction(settings_action)
        
        # Справка
        help_menu = menubar.addMenu("&Справка")
        
        about_action = QAction("&О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Настройка панели инструментов"""
        toolbar = self.addToolBar("Главная")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Создать проект
        new_project_action = QAction("📁 Новый проект", self)
        new_project_action.triggered.connect(self.create_project)
        toolbar.addAction(new_project_action)
        
        # Создать задачу
        new_task_action = QAction("📝 Новая задача", self)
        new_task_action.triggered.connect(self.create_task)
        toolbar.addAction(new_task_action)
        
        toolbar.addSeparator()
        
        # Обновить
        refresh_action = QAction("🔄 Обновить", self)
        refresh_action.triggered.connect(self.refresh_current_view)
        toolbar.addAction(refresh_action)
        
        # Экспорт
        export_action = QAction("📄 Экспорт", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Комбо-бокс для быстрого переключения проектов
        toolbar.addWidget(QLabel("Проект: "))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.addItem("Все проекты")
        toolbar.addWidget(self.project_combo)
    
    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # Переключение между вкладками
        for i in range(5):  # 5 основных вкладок
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.switch_to_view(idx))
    
    def setup_connections(self):
        """Настройка подключений сигналов"""
        # Навигация
        self.navigation_bar.tab_changed.connect(self.switch_to_view)
        
        # Dashboard сигналы
        if hasattr(self.dashboard_view, 'project_create_requested'):
            self.dashboard_view.project_create_requested.connect(self.create_project)
        if hasattr(self.dashboard_view, 'task_create_requested'):
            self.dashboard_view.task_create_requested.connect(self.create_task)
        if hasattr(self.dashboard_view, 'report_generate_requested'):
            self.dashboard_view.report_generate_requested.connect(lambda: self.switch_to_view(3))
    
    def switch_to_view(self, index: int):
        """Переключение между представлениями"""
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            self.current_view_index = index
            self.navigation_bar.set_current_tab(index)
            
            # Обновление заголовка окна
            view_names = ["Панель управления", "Проекты", "Задачи", "Отчеты", "Настройки"]
            if index < len(view_names):
                self.setWindowTitle(f"Project Management System - {view_names[index]}")
            
            # Обновление статуса
            self.status_bar.show_message(f"Переключено на: {view_names[index] if index < len(view_names) else 'Неизвестно'}")
    
    def refresh_current_view(self):
        """Обновление текущего представления"""
        current_widget = self.content_stack.currentWidget()
        
        # Вызываем метод refresh, если он существует
        if hasattr(current_widget, 'refresh_dashboard'):
            current_widget.refresh_dashboard()
        elif hasattr(current_widget, 'refresh'):
            current_widget.refresh()
        
        self.status_bar.show_message("Данные обновлены")
    
    def create_project(self):
        """Создание нового проекта"""
        QMessageBox.information(self, "Создание проекта", 
                              "Функция создания проекта будет доступна в следующей версии.")
        self.status_bar.show_message("Запрошен диалог создания проекта")
    
    def create_task(self):
        """Создание новой задачи"""
        QMessageBox.information(self, "Создание задачи", 
                              "Функция создания задачи будет доступна в следующей версии.")
        self.status_bar.show_message("Запрошен диалог создания задачи")
    
    def export_data(self):
        """Экспорт данных"""
        QMessageBox.information(self, "Экспорт данных", 
                              "Функция экспорта будет доступна в следующей версии.")
        self.status_bar.show_message("Запрошен экспорт данных")
    
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.isFullScreen():
            self.showNormal()
            self.status_bar.show_message("Обычный режим")
        else:
            self.showFullScreen()
            self.status_bar.show_message("Полноэкранный режим")
    
    def show_about(self):
        """Показ информации о программе"""
        QMessageBox.about(self, "О программе", 
                         "Project Management System v1.0\n\n"
                         "Комплексная система управления проектами\n"
                         "с современным интерфейсом PyQt6\n\n"
                         "Автор: Genocide12\n"
                         "Дата: Сентябрь 2025\n\n"
                         "🔗 GitHub: https://github.com/Genocide12/project-management-system")
    
    def save_settings(self):
        """Сохранение настроек окна"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("currentView", self.current_view_index)
    
    def restore_settings(self):
        """Восстановление настроек окна"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
        
        current_view = self.settings.value("currentView", 0, type=int)
        self.switch_to_view(current_view)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Сохранение настроек
        self.save_settings()
        self.status_bar.show_message("Сохранение настроек...")
        event.accept()


if __name__ == "__main__":
    """Запуск приложения для тестирования"""
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9pt;
        }
        
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QMenuBar {
            background-color: #ffffff;
            border-bottom: 1px solid #dee2e6;
            padding: 2px;
        }
        
        QMenuBar::item {
            padding: 6px 12px;
            background-color: transparent;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #e9ecef;
        }
        
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #dee2e6;
            spacing: 6px;
            padding: 4px;
        }
        
        QToolBar QToolButton {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            background-color: transparent;
        }
        
        QToolBar QToolButton:hover {
            background-color: #e9ecef;
        }
        
        QToolBar::separator {
            background-color: #dee2e6;
            width: 1px;
            margin: 8px 4px;
        }
        
        QComboBox {
            padding: 4px 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }
        
        QComboBox:focus {
            border-color: #3498db;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())