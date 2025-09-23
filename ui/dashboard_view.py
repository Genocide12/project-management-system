# -*- coding: utf-8 -*-
"""
Dashboard View Module for Project Management System

Панель управления - главный экран системы управления проектами

Features:
- Real-time project statistics
- Task progress overview
- Recent activities feed
- Quick action buttons
- Performance metrics
- Notification center
- Resource utilization charts

Author: Genocide12
Date: September 2025
"""

import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QProgressBar, QListWidget, QListWidgetItem,
    QGroupBox, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QSpinBox, QCheckBox, QSlider,
    QSplitter, QStackedWidget, QToolBox,
    QCalendarWidget, QTreeWidget, QTreeWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsItem
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QRect,
    QPropertyAnimation, QEasingCurve, QDate,
    QAbstractTableModel, QModelIndex, QVariant
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QIcon,
    QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QConicalGradient, QPolygonF,
    QPainterPath, QFontMetrics, QAction
)

# Import custom components and services
try:
    from ..app.models.project import Project, ProjectStatus
    from ..app.models.task import Task, TaskStatus, TaskPriority
    from ..app.models.user import User
    from ..app.services.notification_service import NotificationService
    from ..app.database.database_manager import DatabaseManager
    from ..app.utils.date_utils import DateUtils
    from ..app.core.exceptions import PMSError
except ImportError:
    # Fallback imports for development
    logging.warning("Could not import all required modules. Using mock implementations.")


class MetricCard(QFrame):
    """
    Карточка метрики для отображения ключевых показателей
    """
    
    def __init__(self, title: str, value: str, icon: str = None, 
                 color: str = "#3498db", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = color
        self.icon = icon
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setFixedSize(200, 120)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Заголовок
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 10))
        self.title_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        
        # Значение
        self.value_label = QLabel(self.value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        
        # Иконка (если есть)
        if self.icon:
            icon_label = QLabel()
            icon_label.setFixedSize(32, 32)
            icon_label.setStyleSheet(f"""
                background-color: {self.color};
                border-radius: 16px;
                margin-bottom: 5px;
            """)
            
            icon_layout = QHBoxLayout()
            icon_layout.addStretch()
            icon_layout.addWidget(icon_label)
            layout.addLayout(icon_layout)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
    
    def apply_styles(self):
        """Применение стилей"""
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                border-left: 4px solid {self.color};
            }}
            MetricCard:hover {{
                border-color: {self.color};
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
        """)
    
    def update_value(self, new_value: str):
        """Обновление значения метрики"""
        self.value = new_value
        self.value_label.setText(new_value)
    
    def animate_update(self, new_value: str):
        """Анимированное обновление значения"""
        # Добавить анимацию изменения значения
        self.update_value(new_value)


class ActivityFeed(QListWidget):
    """
    Лента активности для отображения последних действий
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self.setup_ui()
        self.load_recent_activities()
    
    def setup_ui(self):
        """Настройка интерфейса ленты активности"""
        self.setMaximumHeight(300)
        self.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 3px solid #2196f3;
            }
        """)
    
    def load_recent_activities(self):
        """Загрузка последних активностей"""
        # Примеры активностей для демонстрации
        sample_activities = [
            {
                'type': 'task_completed',
                'message': 'Задача "Создание дизайна" завершена',
                'user': 'Иван Петров',
                'timestamp': datetime.now() - timedelta(minutes=15)
            },
            {
                'type': 'project_created',
                'message': 'Создан новый проект "Веб-приложение"',
                'user': 'Мария Сидорова',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'type': 'comment_added',
                'message': 'Добавлен комментарий к задаче "Тестирование"',
                'user': 'Алексей Козлов',
                'timestamp': datetime.now() - timedelta(hours=4)
            },
            {
                'type': 'deadline_approaching',
                'message': 'Приближается дедлайн проекта "Мобильное приложение"',
                'user': 'Система',
                'timestamp': datetime.now() - timedelta(hours=6)
            }
        ]
        
        for activity in sample_activities:
            self.add_activity(activity)
    
    def add_activity(self, activity: Dict[str, Any]):
        """Добавление новой активности в ленту"""
        item = QListWidgetItem()
        
        # Форматирование времени
        time_diff = datetime.now() - activity['timestamp']
        if time_diff.seconds < 3600:
            time_str = f"{time_diff.seconds // 60} мин назад"
        elif time_diff.seconds < 86400:
            time_str = f"{time_diff.seconds // 3600} ч назад"
        else:
            time_str = activity['timestamp'].strftime("%d.%m.%Y")
        
        # Создание текста элемента
        item_text = f"{activity['message']}\n{activity['user']} • {time_str}"
        item.setText(item_text)
        
        # Цвет в зависимости от типа активности
        colors = {
            'task_completed': '#27ae60',
            'project_created': '#3498db',
            'comment_added': '#f39c12',
            'deadline_approaching': '#e74c3c'
        }
        color = colors.get(activity['type'], '#95a5a6')
        
        item.setData(Qt.ItemDataRole.UserRole, activity)
        self.insertItem(0, item)  # Добавляем в начало списка
        
        # Ограничиваем количество элементов
        if self.count() > 10:
            self.takeItem(self.count() - 1)
    
    def refresh_activities(self):
        """Обновление ленты активности"""
        # Здесь должна быть логика загрузки из базы данных
        pass


class QuickActionsWidget(QFrame):
    """
    Виджет быстрых действий
    """
    
    project_create_requested = pyqtSignal()
    task_create_requested = pyqtSignal()
    report_generate_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса быстрых действий"""
        self.setFixedHeight(120)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Кнопки быстрых действий
        self.create_project_btn = self.create_action_button(
            "Создать проект", "#3498db", "📊"
        )
        self.create_task_btn = self.create_action_button(
            "Новая задача", "#27ae60", "📝"
        )
        self.generate_report_btn = self.create_action_button(
            "Создать отчет", "#e67e22", "📈"
        )
        self.view_calendar_btn = self.create_action_button(
            "Календарь", "#9b59b6", "📅"
        )
        
        # Подключение сигналов
        self.create_project_btn.clicked.connect(self.project_create_requested.emit)
        self.create_task_btn.clicked.connect(self.task_create_requested.emit)
        self.generate_report_btn.clicked.connect(self.report_generate_requested.emit)
        
        # Добавление кнопок в layout
        layout.addWidget(self.create_project_btn)
        layout.addWidget(self.create_task_btn)
        layout.addWidget(self.generate_report_btn)
        layout.addWidget(self.view_calendar_btn)
        layout.addStretch()
    
    def create_action_button(self, text: str, color: str, icon: str) -> QPushButton:
        """Создание кнопки быстрого действия"""
        btn = QPushButton(f"{icon} {text}")
        btn.setFixedSize(150, 60)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """)
        return btn
    
    def darken_color(self, color: str, factor: float = 0.9) -> str:
        """Затемнение цвета"""
        # Простое затемнение для демонстрации
        return color  # В реальности здесь должна быть логика затемнения


class ProjectProgressWidget(QFrame):
    """
    Виджет отображения прогресса проектов
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects_data = []
        self.setup_ui()
        self.load_project_progress()
    
    def setup_ui(self):
        """Настройка интерфейса прогресса проектов"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title = QLabel("Прогресс проектов")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Контейнер для прогресс-баров
        self.progress_container = QVBoxLayout()
        layout.addLayout(self.progress_container)
        
        layout.addStretch()
    
    def load_project_progress(self):
        """Загрузка данных о прогрессе проектов"""
        # Примеры данных для демонстрации
        sample_projects = [
            {'name': 'Веб-приложение', 'progress': 75, 'color': '#3498db'},
            {'name': 'Мобильное приложение', 'progress': 45, 'color': '#27ae60'},
            {'name': 'Система аналитики', 'progress': 90, 'color': '#e67e22'},
            {'name': 'CRM система', 'progress': 30, 'color': '#9b59b6'}
        ]
        
        for project in sample_projects:
            self.add_project_progress(project)
    
    def add_project_progress(self, project: Dict[str, Any]):
        """Добавление прогресса проекта"""
        container = QFrame()
        container.setMaximumHeight(60)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Название проекта и процент
        header_layout = QHBoxLayout()
        
        name_label = QLabel(project['name'])
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #2c3e50;")
        
        progress_label = QLabel(f"{project['progress']}%")
        progress_label.setFont(QFont("Arial", 10))
        progress_label.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(progress_label)
        
        # Прогресс-бар
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(project['progress'])
        progress_bar.setFixedHeight(8)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #ecf0f1;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {project['color']};
                border-radius: 4px;
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(progress_bar)
        
        self.progress_container.addWidget(container)
    
    def refresh_progress(self):
        """Обновление данных прогресса"""
        # Здесь должна быть логика загрузки из базы данных
        pass


class DashboardView(QWidget):
    """
    Основной класс панели управления
    
    Отображает:
    - Ключевые метрики системы
    - Прогресс проектов
    - Ленту активности
    - Быстрые действия
    - Уведомления
    """
    
    # Сигналы для взаимодействия с главным окном
    project_create_requested = pyqtSignal()
    task_create_requested = pyqtSignal()
    report_generate_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = None
        self.notification_service = None
        self.update_timer = QTimer()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Настройка интерфейса панели управления"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок панели управления
        self.setup_header(main_layout)
        
        # Создание основного контента
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Левая панель (метрики и прогресс)
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Правая панель (активность и быстрые действия)
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Настройка пропорций
        content_splitter.setSizes([700, 400])
    
    def setup_header(self, layout: QVBoxLayout):
        """Настройка заголовка"""
        header_layout = QHBoxLayout()
        
        # Заголовок
        title = QLabel("Панель управления")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Дата и время
        datetime_label = QLabel(datetime.now().strftime("%d.%m.%Y • %H:%M"))
        datetime_label.setFont(QFont("Arial", 12))
        datetime_label.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(datetime_label)
        
        layout.addLayout(header_layout)
    
    def create_left_panel(self) -> QWidget:
        """Создание левой панели с метриками и прогрессом"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Карточки метрик
        metrics_layout = self.create_metrics_section()
        left_layout.addLayout(metrics_layout)
        
        # Прогресс проектов
        self.progress_widget = ProjectProgressWidget()
        left_layout.addWidget(self.progress_widget)
        
        # Календарь (мини-версия)
        calendar_widget = self.create_mini_calendar()
        left_layout.addWidget(calendar_widget)
        
        left_layout.addStretch()
        
        return left_widget
    
    def create_right_panel(self) -> QWidget:
        """Создание правой панели с активностью и действиями"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        
        # Быстрые действия
        self.quick_actions = QuickActionsWidget()
        right_layout.addWidget(self.quick_actions)
        
        # Лента активности
        activity_label = QLabel("Последние активности")
        activity_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        activity_label.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(activity_label)
        
        self.activity_feed = ActivityFeed()
        right_layout.addWidget(self.activity_feed)
        
        right_layout.addStretch()
        
        return right_widget
    
    def create_metrics_section(self) -> QHBoxLayout:
        """Создание секции метрик"""
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        # Создание карточек метрик
        self.total_projects_card = MetricCard(
            "Всего проектов", "12", color="#3498db"
        )
        self.active_tasks_card = MetricCard(
            "Активные задачи", "47", color="#27ae60"
        )
        self.completed_tasks_card = MetricCard(
            "Завершенные задачи", "134", color="#e67e22"
        )
        self.team_members_card = MetricCard(
            "Участники команды", "8", color="#9b59b6"
        )
        
        metrics_layout.addWidget(self.total_projects_card)
        metrics_layout.addWidget(self.active_tasks_card)
        metrics_layout.addWidget(self.completed_tasks_card)
        metrics_layout.addWidget(self.team_members_card)
        
        return metrics_layout
    
    def create_mini_calendar(self) -> QFrame:
        """Создание мини-календаря"""
        calendar_frame = QFrame()
        calendar_frame.setFixedHeight(200)
        calendar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(calendar_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        title = QLabel("Календарь")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Мини-календарь
        calendar = QCalendarWidget()
        calendar.setFixedHeight(150)
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: none;
            }
        """)
        layout.addWidget(calendar)
        
        return calendar_frame
    
    def setup_connections(self):
        """Настройка подключений сигналов"""
        # Подключение сигналов от быстрых действий
        self.quick_actions.project_create_requested.connect(
            self.project_create_requested.emit
        )
        self.quick_actions.task_create_requested.connect(
            self.task_create_requested.emit
        )
        self.quick_actions.report_generate_requested.connect(
            self.report_generate_requested.emit
        )
    
    def setup_timer(self):
        """Настройка таймера для автообновления"""
        self.update_timer.timeout.connect(self.refresh_dashboard)
        self.update_timer.start(30000)  # Обновление каждые 30 секунд
    
    def load_dashboard_data(self):
        """Загрузка данных панели управления"""
        try:
            # Здесь должна быть загрузка реальных данных из базы
            # Пока используем mock данные
            self.update_metrics()
            
        except Exception as e:
            logging.error(f"Error loading dashboard data: {e}")
    
    def update_metrics(self):
        """Обновление метрик"""
        try:
            # В реальном приложении здесь будут запросы к базе данных
            # Пока обновляем случайными значениями для демонстрации
            import random
            
            # Можно добавить анимацию обновления
            self.total_projects_card.update_value(str(random.randint(10, 20)))
            self.active_tasks_card.update_value(str(random.randint(40, 60)))
            self.completed_tasks_card.update_value(str(random.randint(120, 150)))
            self.team_members_card.update_value(str(random.randint(6, 12)))
            
        except Exception as e:
            logging.error(f"Error updating metrics: {e}")
    
    def refresh_dashboard(self):
        """Обновление панели управления"""
        try:
            self.update_metrics()
            self.progress_widget.refresh_progress()
            self.activity_feed.refresh_activities()
            
            # Обновление времени в заголовке
            datetime_labels = self.findChildren(QLabel)
            for label in datetime_labels:
                if "•" in label.text() and ":" in label.text():
                    label.setText(datetime.now().strftime("%d.%m.%Y • %H:%M"))
                    break
            
        except Exception as e:
            logging.error(f"Error refreshing dashboard: {e}")
    
    def set_database_manager(self, db_manager):
        """Установка менеджера базы данных"""
        self.db_manager = db_manager
    
    def set_notification_service(self, notification_service):
        """Установка сервиса уведомлений"""
        self.notification_service = notification_service
    
    def showEvent(self, event):
        """Обработка события показа виджета"""
        super().showEvent(event)
        # Обновление данных при показе панели
        self.refresh_dashboard()
    
    def closeEvent(self, event):
        """Обработка события закрытия"""
        # Остановка таймера
        if self.update_timer.isActive():
            self.update_timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    """Тестирование виджета панели управления"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyleSheet("""
        QApplication {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    dashboard = DashboardView()
    dashboard.resize(1200, 800)
    dashboard.show()
    
    sys.exit(app.exec())