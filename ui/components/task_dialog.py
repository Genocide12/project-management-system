#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Dialog - Диалог создания/редактирования задач
Advanced task creation and editing dialog with dependencies and time tracking
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QGroupBox, QCheckBox, QListWidget, QListWidgetItem,
    QTabWidget, QWidget, QScrollArea, QProgressBar, QSlider, QDialogButtonBox,
    QMessageBox, QTimeEdit, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPalette, QFont, QIcon
from datetime import datetime, date, time


class TaskDialog(QDialog):
    """
    Advanced task creation/editing dialog
    Расширенный диалог создания/редактирования задач
    """

    task_saved = pyqtSignal(object)  # Emitted when task is saved

    def __init__(self, parent=None, task=None, project=None, users=None, tasks=None):
        """
        Initialize task dialog

        Args:
            parent: Parent widget
            task: Task to edit (None for new task)
            project: Current project
            users: List of available users
            tasks: List of existing tasks for dependencies
        """
        super().__init__(parent)
        self.task = task
        self.project = project
        self.users = users or []
        self.tasks = tasks or []
        self.is_editing = task is not None

        self.setup_ui()
        self.setup_connections()
        self.load_data()
        self.setup_validation()

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Редактировать задачу" if self.is_editing else "Новая задача")
        self.setModal(True)
        self.resize(900, 700)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_basic_tab()
        self.create_details_tab()
        self.create_time_tracking_tab()
        self.create_dependencies_tab()
        self.create_attachments_tab()

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        main_layout.addWidget(self.button_box)

        self.apply_styles()

    def create_basic_tab(self):
        """Create basic information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Task info group
        info_group = QGroupBox("Информация о задаче")
        info_layout = QFormLayout(info_group)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Введите название задачи...")
        info_layout.addRow("Название:", self.title_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(120)
        self.description_edit.setPlaceholderText("Подробное описание задачи...")
        info_layout.addRow("Описание:", self.description_edit)

        # Task type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Функциональность", "Ошибка", "Улучшение", 
            "Документация", "Исследование", "Обслуживание"
        ])
        info_layout.addRow("Тип:", self.type_combo)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "К выполнению", "В работе", "На проверке", 
            "Тестирование", "Выполнено", "Отменено"
        ])
        info_layout.addRow("Статус:", self.status_combo)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий", "Критический"])
        self.priority_combo.setCurrentIndex(1)
        info_layout.addRow("Приоритет:", self.priority_combo)

        layout.addWidget(info_group)

        # Assignment group
        assignment_group = QGroupBox("Назначение")
        assignment_layout = QVBoxLayout(assignment_group)

        # Project selection (if not pre-selected)
        if not self.project:
            project_layout = QHBoxLayout()
            project_label = QLabel("Проект:")
            self.project_combo = QComboBox()
            project_layout.addWidget(project_label)
            project_layout.addWidget(self.project_combo)
            assignment_layout.addLayout(project_layout)
        else:
            project_info = QLabel(f"Проект: {self.project.name}")
            project_info.setStyleSheet("font-weight: bold; color: #2196F3;")
            assignment_layout.addWidget(project_info)

        # Assignees
        assignees_label = QLabel("Исполнители:")
        assignment_layout.addWidget(assignees_label)

        self.assignees_list = QListWidget()
        self.assignees_list.setMaximumHeight(100)
        self.assignees_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        assignment_layout.addWidget(self.assignees_list)

        layout.addWidget(assignment_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Основное")

    def create_details_tab(self):
        """Create detailed information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Technical details group
        tech_group = QGroupBox("Технические детали")
        tech_layout = QFormLayout(tech_group)

        # Story points
        self.story_points_spin = QSpinBox()
        self.story_points_spin.setRange(0, 100)
        self.story_points_spin.setSuffix(" SP")
        tech_layout.addRow("Story Points:", self.story_points_spin)

        # Branch name
        self.branch_edit = QLineEdit()
        self.branch_edit.setPlaceholderText("feature/task-description")
        tech_layout.addRow("Ветка:", self.branch_edit)

        # Pull request URL
        self.pr_url_edit = QLineEdit()
        self.pr_url_edit.setPlaceholderText("https://github.com/user/repo/pull/123")
        tech_layout.addRow("Pull Request:", self.pr_url_edit)

        # Quality score
        quality_widget = QWidget()
        quality_layout = QHBoxLayout(quality_widget)
        quality_layout.setContentsMargins(0, 0, 0, 0)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 10)
        self.quality_slider.setValue(5)

        self.quality_label = QLabel("5/10")
        self.quality_label.setMinimumWidth(50)

        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)

        tech_layout.addRow("Качество:", quality_widget)

        layout.addWidget(tech_group)

        # Subtasks group
        subtasks_group = QGroupBox("Подзадачи")
        subtasks_layout = QVBoxLayout(subtasks_group)

        # Subtasks list
        self.subtasks_list = QListWidget()
        self.subtasks_list.setMaximumHeight(150)
        subtasks_layout.addWidget(self.subtasks_list)

        # Subtask management buttons
        subtask_buttons = QHBoxLayout()

        self.add_subtask_btn = QPushButton("Добавить подзадачу")
        self.edit_subtask_btn = QPushButton("Редактировать")
        self.remove_subtask_btn = QPushButton("Удалить")

        subtask_buttons.addWidget(self.add_subtask_btn)
        subtask_buttons.addWidget(self.edit_subtask_btn)
        subtask_buttons.addWidget(self.remove_subtask_btn)
        subtask_buttons.addStretch()

        subtasks_layout.addLayout(subtask_buttons)

        layout.addWidget(subtasks_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Детали")

    def create_time_tracking_tab(self):
        """Create time tracking tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Time estimates group
        estimates_group = QGroupBox("Временные оценки")
        estimates_layout = QFormLayout(estimates_group)

        # Estimated hours
        self.estimated_hours_spin = QDoubleSpinBox()
        self.estimated_hours_spin.setRange(0, 9999.99)
        self.estimated_hours_spin.setDecimals(2)
        self.estimated_hours_spin.setSuffix(" ч")
        estimates_layout.addRow("Оценка времени:", self.estimated_hours_spin)

        # Actual hours
        self.actual_hours_spin = QDoubleSpinBox()
        self.actual_hours_spin.setRange(0, 9999.99)
        self.actual_hours_spin.setDecimals(2)
        self.actual_hours_spin.setSuffix(" ч")
        estimates_layout.addRow("Фактическое время:", self.actual_hours_spin)

        # Remaining hours (calculated)
        self.remaining_hours_label = QLabel("0.00 ч")
        estimates_layout.addRow("Осталось времени:", self.remaining_hours_label)

        # Efficiency indicator
        self.efficiency_label = QLabel("N/A")
        estimates_layout.addRow("Эффективность:", self.efficiency_label)

        layout.addWidget(estimates_group)

        # Time tracking group
        tracking_group = QGroupBox("Отслеживание времени")
        tracking_layout = QVBoxLayout(tracking_group)

        # Current session
        session_layout = QHBoxLayout()

        self.start_timer_btn = QPushButton("Начать работу")
        self.stop_timer_btn = QPushButton("Остановить")
        self.stop_timer_btn.setEnabled(False)

        self.current_session_label = QLabel("Текущая сессия: 00:00:00")

        session_layout.addWidget(self.start_timer_btn)
        session_layout.addWidget(self.stop_timer_btn)
        session_layout.addWidget(self.current_session_label)
        session_layout.addStretch()

        tracking_layout.addLayout(session_layout)

        # Time log
        time_log_label = QLabel("История работы:")
        tracking_layout.addWidget(time_log_label)

        self.time_log_list = QListWidget()
        self.time_log_list.setMaximumHeight(120)
        tracking_layout.addWidget(self.time_log_list)

        layout.addWidget(tracking_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Время")

    def create_dependencies_tab(self):
        """Create dependencies management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Dependencies group
        deps_group = QGroupBox("Зависимости задач")
        deps_layout = QVBoxLayout(deps_group)

        # Splitter for two lists
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Available tasks
        available_widget = QWidget()
        available_layout = QVBoxLayout(available_widget)

        available_label = QLabel("Доступные задачи:")
        available_layout.addWidget(available_label)

        self.available_tasks_list = QListWidget()
        available_layout.addWidget(self.available_tasks_list)

        splitter.addWidget(available_widget)

        # Dependency management buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.addStretch()

        self.add_dependency_btn = QPushButton("Добавить →")
        self.remove_dependency_btn = QPushButton("← Удалить")

        buttons_layout.addWidget(self.add_dependency_btn)
        buttons_layout.addWidget(self.remove_dependency_btn)
        buttons_layout.addStretch()

        splitter.addWidget(buttons_widget)

        # Task dependencies
        dependencies_widget = QWidget()
        dependencies_layout = QVBoxLayout(dependencies_widget)

        dependencies_label = QLabel("Зависимости этой задачи:")
        dependencies_layout.addWidget(dependencies_label)

        self.dependencies_list = QListWidget()
        dependencies_layout.addWidget(self.dependencies_list)

        splitter.addWidget(dependencies_widget)

        deps_layout.addWidget(splitter)

        # Dependency validation
        validation_frame = QFrame()
        validation_frame.setFrameStyle(QFrame.Shape.Box)
        validation_layout = QHBoxLayout(validation_frame)

        self.can_start_label = QLabel("✓ Задача может быть начата")
        self.can_start_label.setStyleSheet("color: green; font-weight: bold;")
        validation_layout.addWidget(self.can_start_label)

        deps_layout.addWidget(validation_frame)

        layout.addWidget(deps_group)

        self.tab_widget.addTab(tab, "Зависимости")

    def create_attachments_tab(self):
        """Create attachments tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Attachments group
        attachments_group = QGroupBox("Вложения")
        attachments_layout = QVBoxLayout(attachments_group)

        # Attachments list
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(200)
        attachments_layout.addWidget(self.attachments_list)

        # Attachment buttons
        attachment_buttons = QHBoxLayout()

        self.add_file_btn = QPushButton("Добавить файл")
        self.remove_file_btn = QPushButton("Удалить")
        self.download_file_btn = QPushButton("Скачать")

        attachment_buttons.addWidget(self.add_file_btn)
        attachment_buttons.addWidget(self.remove_file_btn)
        attachment_buttons.addWidget(self.download_file_btn)
        attachment_buttons.addStretch()

        attachments_layout.addLayout(attachment_buttons)

        layout.addWidget(attachments_group)

        # Comments group
        comments_group = QGroupBox("Комментарии")
        comments_layout = QVBoxLayout(comments_group)

        # Comments list
        self.comments_list = QListWidget()
        self.comments_list.setMaximumHeight(150)
        comments_layout.addWidget(self.comments_list)

        # New comment
        comment_input_layout = QHBoxLayout()

        self.new_comment_edit = QLineEdit()
        self.new_comment_edit.setPlaceholderText("Добавить комментарий...")

        self.add_comment_btn = QPushButton("Добавить")

        comment_input_layout.addWidget(self.new_comment_edit)
        comment_input_layout.addWidget(self.add_comment_btn)

        comments_layout.addLayout(comment_input_layout)

        layout.addWidget(comments_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Вложения")

    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.button_box.accepted.connect(self.save_task)
        self.button_box.rejected.connect(self.reject)

        apply_btn = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        if apply_btn:
            apply_btn.clicked.connect(self.apply_changes)

        # Progress and time tracking
        if hasattr(self, 'estimated_hours_spin') and hasattr(self, 'actual_hours_spin'):
            self.estimated_hours_spin.valueChanged.connect(self.update_time_display)
            self.actual_hours_spin.valueChanged.connect(self.update_time_display)

        # Quality slider
        if hasattr(self, 'quality_slider'):
            self.quality_slider.valueChanged.connect(self.update_quality_display)

        # Dependencies
        if hasattr(self, 'add_dependency_btn'):
            self.add_dependency_btn.clicked.connect(self.add_dependency)
            self.remove_dependency_btn.clicked.connect(self.remove_dependency)

        # Attachments
        if hasattr(self, 'add_file_btn'):
            self.add_file_btn.clicked.connect(self.add_attachment)
            self.remove_file_btn.clicked.connect(self.remove_attachment)
            self.download_file_btn.clicked.connect(self.download_attachment)

        # Comments
        if hasattr(self, 'add_comment_btn'):
            self.add_comment_btn.clicked.connect(self.add_comment)
            self.new_comment_edit.returnPressed.connect(self.add_comment)

        # Auto-generate branch name
        self.title_edit.textChanged.connect(self.auto_generate_branch)

    def setup_validation(self):
        """Setup input validation"""
        self.title_edit.textChanged.connect(self.validate_inputs)
        self.validate_inputs()

    def load_data(self):
        """Load task data for editing"""
        if not self.task:
            return

        # Basic information
        self.title_edit.setText(self.task.title or "")
        self.description_edit.setPlainText(self.task.description or "")

        # Status and priority mapping
        status_map = {
            "todo": 0, "in_progress": 1, "review": 2,
            "testing": 3, "done": 4, "cancelled": 5
        }
        self.status_combo.setCurrentIndex(status_map.get(self.task.status, 0))

        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        self.priority_combo.setCurrentIndex(priority_map.get(self.task.priority, 1))

        type_map = {
            "feature": 0, "bug": 1, "improvement": 2,
            "documentation": 3, "research": 4, "maintenance": 5
        }
        if hasattr(self.task, 'task_type'):
            self.type_combo.setCurrentIndex(type_map.get(self.task.task_type, 0))

        # Time tracking
        if hasattr(self, 'estimated_hours_spin'):
            self.estimated_hours_spin.setValue(float(self.task.estimated_hours or 0))
            self.actual_hours_spin.setValue(float(self.task.actual_hours or 0))

        # Technical details
        if hasattr(self, 'story_points_spin'):
            self.story_points_spin.setValue(self.task.story_points or 0)

        if hasattr(self, 'branch_edit'):
            self.branch_edit.setText(self.task.branch_name or "")
            self.pr_url_edit.setText(self.task.pull_request_url or "")

        if hasattr(self, 'quality_slider'):
            self.quality_slider.setValue(self.task.quality_score or 5)

        self.update_displays()

    def auto_generate_branch(self):
        """Auto-generate branch name from task title"""
        if not self.is_editing and hasattr(self, 'branch_edit') and not self.branch_edit.text():
            title = self.title_edit.text().strip().lower()
            if title:
                # Convert to kebab-case
                branch_name = "feature/" + "".join(
                    c if c.isalnum() else "-" for c in title
                ).strip("-")
                # Remove multiple dashes
                while "--" in branch_name:
                    branch_name = branch_name.replace("--", "-")

                self.branch_edit.setText(branch_name)

    def update_time_display(self):
        """Update time-related displays"""
        if hasattr(self, 'estimated_hours_spin') and hasattr(self, 'actual_hours_spin'):
            estimated = self.estimated_hours_spin.value()
            actual = self.actual_hours_spin.value()
            remaining = max(0, estimated - actual)

            self.remaining_hours_label.setText(f"{remaining:.2f} ч")

            # Calculate efficiency
            if estimated > 0:
                efficiency = (estimated / max(actual, 0.01)) * 100
                self.efficiency_label.setText(f"{efficiency:.1f}%")

                # Color coding
                if efficiency > 100:
                    color = "green"
                elif efficiency > 80:
                    color = "orange"
                else:
                    color = "red"

                self.efficiency_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            else:
                self.efficiency_label.setText("N/A")

    def update_quality_display(self):
        """Update quality score display"""
        if hasattr(self, 'quality_slider'):
            value = self.quality_slider.value()
            self.quality_label.setText(f"{value}/10")

            # Color coding
            if value >= 8:
                color = "green"
            elif value >= 6:
                color = "orange"
            else:
                color = "red"

            self.quality_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_displays(self):
        """Update all display elements"""
        self.update_time_display()
        if hasattr(self, 'quality_slider'):
            self.update_quality_display()

    def add_dependency(self):
        """Add task dependency"""
        current_item = self.available_tasks_list.currentItem()
        if current_item:
            # Move to dependencies list
            task_data = current_item.data(Qt.ItemDataRole.UserRole)
            dep_item = QListWidgetItem(current_item.text())
            dep_item.setData(Qt.ItemDataRole.UserRole, task_data)
            self.dependencies_list.addItem(dep_item)

            # Remove from available
            row = self.available_tasks_list.row(current_item)
            self.available_tasks_list.takeItem(row)

            self.validate_dependencies()

    def remove_dependency(self):
        """Remove task dependency"""
        current_item = self.dependencies_list.currentItem()
        if current_item:
            # Move back to available tasks
            task_data = current_item.data(Qt.ItemDataRole.UserRole)
            available_item = QListWidgetItem(current_item.text())
            available_item.setData(Qt.ItemDataRole.UserRole, task_data)
            self.available_tasks_list.addItem(available_item)

            # Remove from dependencies
            row = self.dependencies_list.row(current_item)
            self.dependencies_list.takeItem(row)

            self.validate_dependencies()

    def validate_dependencies(self):
        """Validate task dependencies"""
        # Check if all dependencies are completed
        can_start = True
        for i in range(self.dependencies_list.count()):
            item = self.dependencies_list.item(i)
            task_data = item.data(Qt.ItemDataRole.UserRole)
            if task_data and not getattr(task_data, 'is_completed', False):
                can_start = False
                break

        if can_start:
            self.can_start_label.setText("✓ Задача может быть начата")
            self.can_start_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.can_start_label.setText("⚠ Есть незавершенные зависимости")
            self.can_start_label.setStyleSheet("color: orange; font-weight: bold;")

    def add_attachment(self):
        """Add file attachment"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл для прикрепления",
            "",
            "Все файлы (*.*)"
        )

        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)

            item_text = f"{file_name} ({size_mb:.2f} MB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, file_path)

            self.attachments_list.addItem(item)

    def remove_attachment(self):
        """Remove selected attachment"""
        current_item = self.attachments_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Удалить вложение",
                f"Удалить вложение '{current_item.text()}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                row = self.attachments_list.row(current_item)
                self.attachments_list.takeItem(row)

    def download_attachment(self):
        """Download selected attachment"""
        current_item = self.attachments_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.ItemDataRole.UserRole)
            if file_path and os.path.exists(file_path):
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Сохранить файл",
                    os.path.basename(file_path)
                )

                if save_path:
                    try:
                        import shutil
                        shutil.copy2(file_path, save_path)
                        QMessageBox.information(
                            self, 
                            "Успех", 
                            "Файл успешно сохранен"
                        )
                    except Exception as e:
                        QMessageBox.warning(
                            self, 
                            "Ошибка", 
                            f"Ошибка при сохранении файла: {str(e)}"
                        )

    def add_comment(self):
        """Add new comment"""
        comment_text = self.new_comment_edit.text().strip()
        if comment_text:
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
            comment_item = f"[{timestamp}] Вы: {comment_text}"

            self.comments_list.addItem(comment_item)
            self.new_comment_edit.clear()

    def validate_inputs(self):
        """Validate all inputs"""
        is_valid = True

        # Check required fields
        title = self.title_edit.text().strip()

        if not title:
            self.title_edit.setStyleSheet("border: 2px solid red;")
            is_valid = False
        else:
            self.title_edit.setStyleSheet("")

        # Enable/disable buttons
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)

        if ok_button:
            ok_button.setEnabled(is_valid)
        if apply_button:
            apply_button.setEnabled(is_valid)

        return is_valid

    def save_task(self):
        """Save task and close dialog"""
        if self.apply_changes():
            self.accept()

    def apply_changes(self):
        """Apply changes without closing dialog"""
        if not self.validate_inputs():
            QMessageBox.warning(
                self,
                "Ошибка валидации", 
                "Пожалуйста, заполните все обязательные поля"
            )
            return False

        try:
            # Collect all form data
            task_data = {
                'title': self.title_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'status': self.get_status_value(),
                'priority': self.get_priority_value(),
                'task_type': self.get_type_value(),
                'project': self.project,
            }

            # Add optional fields if they exist
            if hasattr(self, 'estimated_hours_spin'):
                task_data['estimated_hours'] = self.estimated_hours_spin.value()
                task_data['actual_hours'] = self.actual_hours_spin.value()

            if hasattr(self, 'story_points_spin'):
                task_data['story_points'] = self.story_points_spin.value() if self.story_points_spin.value() > 0 else None

            if hasattr(self, 'branch_edit'):
                task_data['branch_name'] = self.branch_edit.text().strip() or None
                task_data['pull_request_url'] = self.pr_url_edit.text().strip() or None

            if hasattr(self, 'quality_slider'):
                task_data['quality_score'] = self.quality_slider.value()

            # Collect assignees
            assignees = []
            for i in range(self.assignees_list.count()):
                item = self.assignees_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    user_data = item.data(Qt.ItemDataRole.UserRole)
                    if user_data:
                        assignees.append(user_data)
            task_data['assignees'] = assignees

            # Collect dependencies
            dependencies = []
            if hasattr(self, 'dependencies_list'):
                for i in range(self.dependencies_list.count()):
                    item = self.dependencies_list.item(i)
                    task_data_dep = item.data(Qt.ItemDataRole.UserRole)
                    if task_data_dep:
                        dependencies.append(task_data_dep)
            task_data['dependencies'] = dependencies

            # Emit signal
            self.task_saved.emit(task_data)

            QMessageBox.information(
                self,
                "Успех",
                "Задача успешно сохранена!"
            )

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Произошла ошибка при сохранении задачи:\n{str(e)}"
            )
            return False

    def get_status_value(self) -> str:
        """Get status value from combo"""
        status_map = {
            0: "todo", 1: "in_progress", 2: "review",
            3: "testing", 4: "done", 5: "cancelled"
        }
        return status_map.get(self.status_combo.currentIndex(), "todo")

    def get_priority_value(self) -> str:
        """Get priority value from combo"""
        priority_map = {0: "low", 1: "medium", 2: "high", 3: "critical"}
        return priority_map.get(self.priority_combo.currentIndex(), "medium")

    def get_type_value(self) -> str:
        """Get task type value from combo"""
        type_map = {
            0: "feature", 1: "bug", 2: "improvement",
            3: "documentation", 4: "research", 5: "maintenance"
        }
        return type_map.get(self.type_combo.currentIndex(), "feature")

    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #007bff;
                outline: none;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #fff;
            }
            QListWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
