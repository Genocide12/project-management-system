#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Dialog - Диалог создания/редактирования проекта
Advanced dialog for project creation and editing with validation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QGroupBox, QCheckBox, QListWidget, QListWidgetItem,
    QTabWidget, QWidget, QScrollArea, QProgressBar, QSlider, QDialogButtonBox,
    QMessageBox, QFileDialog, QColorDialog
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPalette, QFont, QIcon
from datetime import datetime, date
import os
from pathlib import Path


class ProjectDialog(QDialog):
    """
    Advanced project creation/editing dialog
    Расширенный диалог создания/редактирования проекта
    """

    project_saved = pyqtSignal(object)  # Emitted when project is saved

    def __init__(self, parent=None, project=None, users=None):
        """
        Initialize project dialog

        Args:
            parent: Parent widget
            project: Project to edit (None for new project)
            users: List of available users for assignment
        """
        super().__init__(parent)
        self.project = project
        self.users = users or []
        self.is_editing = project is not None

        self.setup_ui()
        self.setup_connections()
        self.load_data()
        self.setup_validation()

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Редактировать проект" if self.is_editing else "Новый проект")
        self.setModal(True)
        self.resize(800, 600)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Tab widget for organized sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_basic_info_tab()
        self.create_schedule_tab()
        self.create_budget_tab()
        self.create_team_tab()
        self.create_settings_tab()

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        main_layout.addWidget(self.button_box)

        # Style the dialog
        self.apply_styles()

    def create_basic_info_tab(self):
        """Create basic information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Basic info group
        basic_group = QGroupBox("Основная информация")
        basic_layout = QFormLayout(basic_group)

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название проекта...")
        basic_layout.addRow("Название:", self.name_edit)

        # Project code
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("PROJ-001")
        basic_layout.addRow("Код проекта:", self.code_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Описание проекта...")
        basic_layout.addRow("Описание:", self.description_edit)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Планирование", "Активный", "Приостановлен", 
            "Завершен", "Отменен"
        ])
        basic_layout.addRow("Статус:", self.status_combo)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий", "Критический"])
        self.priority_combo.setCurrentIndex(1)  # Medium by default
        basic_layout.addRow("Приоритет:", self.priority_combo)

        layout.addWidget(basic_group)

        # Progress group
        progress_group = QGroupBox("Прогресс")
        progress_layout = QFormLayout(progress_group)

        # Progress slider and display
        progress_widget = QWidget()
        progress_widget_layout = QHBoxLayout(progress_widget)
        progress_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)

        self.progress_label = QLabel("0%")
        self.progress_label.setMinimumWidth(40)

        progress_widget_layout.addWidget(self.progress_slider)
        progress_widget_layout.addWidget(self.progress_label)

        progress_layout.addRow("Выполнение:", progress_widget)

        # Progress bar for visual feedback
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addRow("Визуальный:", self.progress_bar)

        layout.addWidget(progress_group)

        # URLs group
        urls_group = QGroupBox("Ссылки")
        urls_layout = QFormLayout(urls_group)

        self.repository_edit = QLineEdit()
        self.repository_edit.setPlaceholderText("https://github.com/user/repo")
        urls_layout.addRow("Репозиторий:", self.repository_edit)

        self.documentation_edit = QLineEdit()
        self.documentation_edit.setPlaceholderText("https://docs.example.com")
        urls_layout.addRow("Документация:", self.documentation_edit)

        layout.addWidget(urls_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Основное")

    def create_schedule_tab(self):
        """Create schedule tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Dates group
        dates_group = QGroupBox("Даты проекта")
        dates_layout = QFormLayout(dates_group)

        # Start date
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        dates_layout.addRow("Дата начала:", self.start_date_edit)

        # End date
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(3))
        self.end_date_edit.setCalendarPopup(True)
        dates_layout.addRow("Дата окончания:", self.end_date_edit)

        # Deadline
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate().addMonths(3))
        self.deadline_edit.setCalendarPopup(True)
        dates_layout.addRow("Крайний срок:", self.deadline_edit)

        layout.addWidget(dates_group)

        # Timeline visualization (placeholder)
        timeline_group = QGroupBox("Временная шкала")
        timeline_layout = QVBoxLayout(timeline_group)

        self.timeline_label = QLabel("Визуализация временной шкалы будет добавлена в следующих версиях")
        self.timeline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timeline_layout.addWidget(self.timeline_label)

        layout.addWidget(timeline_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Расписание")

    def create_budget_tab(self):
        """Create budget tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Budget group
        budget_group = QGroupBox("Бюджет проекта")
        budget_layout = QFormLayout(budget_group)

        # Total budget
        self.budget_spin = QDoubleSpinBox()
        self.budget_spin.setRange(0, 9999999.99)
        self.budget_spin.setDecimals(2)
        self.budget_spin.setSuffix(" ₽")
        budget_layout.addRow("Общий бюджет:", self.budget_spin)

        # Spent amount
        self.spent_spin = QDoubleSpinBox()
        self.spent_spin.setRange(0, 9999999.99)
        self.spent_spin.setDecimals(2)
        self.spent_spin.setSuffix(" ₽")
        budget_layout.addRow("Потрачено:", self.spent_spin)

        # Remaining display
        self.remaining_label = QLabel("0.00 ₽")
        budget_layout.addRow("Остаток:", self.remaining_label)

        # Budget usage progress bar
        self.budget_progress = QProgressBar()
        self.budget_progress.setRange(0, 100)
        budget_layout.addRow("Использование бюджета:", self.budget_progress)

        layout.addWidget(budget_group)

        # Cost tracking group
        cost_group = QGroupBox("Отслеживание расходов")
        cost_layout = QVBoxLayout(cost_group)

        cost_info = QLabel("Детальное отслеживание расходов будет доступно в будущих версиях")
        cost_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cost_layout.addWidget(cost_info)

        layout.addWidget(cost_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Бюджет")

    def create_team_tab(self):
        """Create team management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Team members group
        team_group = QGroupBox("Участники проекта")
        team_layout = QVBoxLayout(team_group)

        # Available users list
        available_label = QLabel("Доступные пользователи:")
        team_layout.addWidget(available_label)

        self.available_users_list = QListWidget()
        self.available_users_list.setMaximumHeight(150)
        team_layout.addWidget(self.available_users_list)

        # Buttons for member management
        buttons_layout = QHBoxLayout()

        self.add_member_btn = QPushButton("Добавить →")
        self.remove_member_btn = QPushButton("← Удалить")

        buttons_layout.addWidget(self.add_member_btn)
        buttons_layout.addWidget(self.remove_member_btn)
        buttons_layout.addStretch()

        team_layout.addLayout(buttons_layout)

        # Project members list
        members_label = QLabel("Участники проекта:")
        team_layout.addWidget(members_label)

        self.project_members_list = QListWidget()
        self.project_members_list.setMaximumHeight(150)
        team_layout.addWidget(self.project_members_list)

        layout.addWidget(team_group)

        # Roles group
        roles_group = QGroupBox("Роли и права")
        roles_layout = QVBoxLayout(roles_group)

        roles_info = QLabel("Управление ролями участников будет добавлено в следующих версиях")
        roles_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        roles_layout.addWidget(roles_info)

        layout.addWidget(roles_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Команда")

    def create_settings_tab(self):
        """Create settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Notifications group
        notifications_group = QGroupBox("Уведомления")
        notifications_layout = QVBoxLayout(notifications_group)

        self.email_notifications_cb = QCheckBox("Уведомления по email")
        self.desktop_notifications_cb = QCheckBox("Уведомления на рабочем столе")
        self.milestone_notifications_cb = QCheckBox("Уведомления о вехах")

        notifications_layout.addWidget(self.email_notifications_cb)
        notifications_layout.addWidget(self.desktop_notifications_cb)
        notifications_layout.addWidget(self.milestone_notifications_cb)

        layout.addWidget(notifications_group)

        # Integration group
        integration_group = QGroupBox("Интеграции")
        integration_layout = QFormLayout(integration_group)

        # Slack integration
        self.slack_webhook_edit = QLineEdit()
        self.slack_webhook_edit.setPlaceholderText("https://hooks.slack.com/...")
        integration_layout.addRow("Slack Webhook:", self.slack_webhook_edit)

        # Jira integration
        self.jira_url_edit = QLineEdit()
        self.jira_url_edit.setPlaceholderText("https://company.atlassian.net")
        integration_layout.addRow("JIRA URL:", self.jira_url_edit)

        layout.addWidget(integration_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Настройки")

    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.button_box.accepted.connect(self.save_project)
        self.button_box.rejected.connect(self.reject)

        # Progress slider connection
        self.progress_slider.valueChanged.connect(self.update_progress_display)

        # Budget calculations
        self.budget_spin.valueChanged.connect(self.update_budget_display)
        self.spent_spin.valueChanged.connect(self.update_budget_display)

        # Team management
        self.add_member_btn.clicked.connect(self.add_team_member)
        self.remove_member_btn.clicked.connect(self.remove_team_member)

        # Auto-generate project code
        self.name_edit.textChanged.connect(self.auto_generate_code)

    def setup_validation(self):
        """Setup input validation"""
        # Name validation
        self.name_edit.textChanged.connect(self.validate_inputs)
        self.code_edit.textChanged.connect(self.validate_inputs)

        # Initial validation
        self.validate_inputs()

    def load_data(self):
        """Load project data for editing"""
        if not self.project:
            return

        # Basic information
        self.name_edit.setText(self.project.name or "")
        self.code_edit.setText(self.project.code or "")
        self.description_edit.setPlainText(self.project.description or "")

        # Status and priority
        status_map = {
            "planning": 0, "active": 1, "on_hold": 2,
            "completed": 3, "cancelled": 4
        }
        self.status_combo.setCurrentIndex(status_map.get(self.project.status, 0))

        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        self.priority_combo.setCurrentIndex(priority_map.get(self.project.priority, 1))

        # Progress
        self.progress_slider.setValue(self.project.progress or 0)
        self.progress_bar.setValue(self.project.progress or 0)

        # Dates
        if self.project.start_date:
            self.start_date_edit.setDate(QDate.fromString(str(self.project.start_date), "yyyy-MM-dd"))
        if self.project.end_date:
            self.end_date_edit.setDate(QDate.fromString(str(self.project.end_date), "yyyy-MM-dd"))
        if self.project.deadline:
            self.deadline_edit.setDate(QDate.fromString(str(self.project.deadline), "yyyy-MM-dd"))

        # Budget
        if self.project.budget:
            self.budget_spin.setValue(float(self.project.budget))
        if self.project.spent:
            self.spent_spin.setValue(float(self.project.spent))

        # URLs
        self.repository_edit.setText(self.project.repository_url or "")
        self.documentation_edit.setText(self.project.documentation_url or "")

        # Update displays
        self.update_progress_display()
        self.update_budget_display()

    def auto_generate_code(self):
        """Auto-generate project code from name"""
        if not self.is_editing and not self.code_edit.text():
            name = self.name_edit.text().strip()
            if name:
                # Generate code from first letters of words
                words = name.upper().split()
                code = "".join(word[0] for word in words if word)[:4]
                if len(code) < 2:
                    code = name[:4].upper()

                # Add number suffix
                code += "-001"
                self.code_edit.setText(code)

    def update_progress_display(self):
        """Update progress display elements"""
        value = self.progress_slider.value()
        self.progress_label.setText(f"{value}%")
        self.progress_bar.setValue(value)

        # Color coding
        if value < 30:
            color = "#f44336"  # Red
        elif value < 70:
            color = "#ff9800"  # Orange
        else:
            color = "#4caf50"  # Green

        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

    def update_budget_display(self):
        """Update budget display elements"""
        budget = self.budget_spin.value()
        spent = self.spent_spin.value()
        remaining = budget - spent

        self.remaining_label.setText(f"{remaining:.2f} ₽")

        # Update progress bar
        if budget > 0:
            usage_percent = int((spent / budget) * 100)
            self.budget_progress.setValue(usage_percent)

            # Color coding
            if usage_percent > 90:
                color = "#f44336"  # Red - over budget
            elif usage_percent > 75:
                color = "#ff9800"  # Orange - warning
            else:
                color = "#4caf50"  # Green - good

            self.budget_progress.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)
        else:
            self.budget_progress.setValue(0)

    def add_team_member(self):
        """Add selected user to project team"""
        current_item = self.available_users_list.currentItem()
        if current_item:
            # Move item to project members
            user_data = current_item.data(Qt.ItemDataRole.UserRole)

            # Create new item for project members
            member_item = QListWidgetItem(current_item.text())
            member_item.setData(Qt.ItemDataRole.UserRole, user_data)
            self.project_members_list.addItem(member_item)

            # Remove from available users
            row = self.available_users_list.row(current_item)
            self.available_users_list.takeItem(row)

    def remove_team_member(self):
        """Remove selected user from project team"""
        current_item = self.project_members_list.currentItem()
        if current_item:
            # Move item back to available users
            user_data = current_item.data(Qt.ItemDataRole.UserRole)

            # Create new item for available users
            user_item = QListWidgetItem(current_item.text())
            user_item.setData(Qt.ItemDataRole.UserRole, user_data)
            self.available_users_list.addItem(user_item)

            # Remove from project members
            row = self.project_members_list.row(current_item)
            self.project_members_list.takeItem(row)

    def validate_inputs(self):
        """Validate form inputs"""
        is_valid = True

        # Check required fields
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()

        if not name:
            self.name_edit.setStyleSheet("border: 2px solid red;")
            is_valid = False
        else:
            self.name_edit.setStyleSheet("")

        if not code:
            self.code_edit.setStyleSheet("border: 2px solid red;")
            is_valid = False
        else:
            self.code_edit.setStyleSheet("")

        # Enable/disable OK button
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(is_valid)

        return is_valid

    def save_project(self):
        """Save project data"""
        if not self.validate_inputs():
            QMessageBox.warning(
                self, 
                "Ошибка валидации",
                "Пожалуйста, заполните все обязательные поля"
            )
            return

        try:
            # Collect form data
            project_data = {
                'name': self.name_edit.text().strip(),
                'code': self.code_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'status': self.get_status_value(),
                'priority': self.get_priority_value(),
                'progress': self.progress_slider.value(),
                'start_date': self.start_date_edit.date().toPython(),
                'end_date': self.end_date_edit.date().toPython(),
                'deadline': self.deadline_edit.date().toPython(),
                'budget': self.budget_spin.value() if self.budget_spin.value() > 0 else None,
                'spent': self.spent_spin.value(),
                'repository_url': self.repository_edit.text().strip() or None,
                'documentation_url': self.documentation_edit.text().strip() or None,
            }

            # Get selected team members
            team_members = []
            for i in range(self.project_members_list.count()):
                item = self.project_members_list.item(i)
                user_data = item.data(Qt.ItemDataRole.UserRole)
                if user_data:
                    team_members.append(user_data)

            project_data['team_members'] = team_members

            # Emit signal with project data
            self.project_saved.emit(project_data)

            # Show success message
            QMessageBox.information(
                self,
                "Успех",
                "Проект успешно сохранен!"
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения", 
                f"Произошла ошибка при сохранении проекта:\n{str(e)}"
            )

    def get_status_value(self) -> str:
        """Get status value from combo box"""
        status_map = {
            0: "planning", 1: "active", 2: "on_hold",
            3: "completed", 4: "cancelled"
        }
        return status_map.get(self.status_combo.currentIndex(), "planning")

    def get_priority_value(self) -> str:
        """Get priority value from combo box"""
        priority_map = {0: "low", 1: "medium", 2: "high", 3: "critical"}
        return priority_map.get(self.priority_combo.currentIndex(), "medium")

    def apply_styles(self):
        """Apply custom styles to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
