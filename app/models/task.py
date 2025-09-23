#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Model - Модель задачи
Advanced task management with hierarchy, time tracking, and dependencies
"""

from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Numeric, Date, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
import enum
from .base import Base


class TaskStatus(enum.Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(enum.Enum):
    """Task type enumeration"""
    FEATURE = "feature"
    BUG = "bug"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"


# Association table for task assignees
task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True)
)


# Association table for task dependencies
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('depends_on_id', Integer, ForeignKey('tasks.id')),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Task(Base):
    """
    Task model with comprehensive project management features
    Модель задачи с комплексными возможностями управления проектами
    """
    __tablename__ = 'tasks'

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Basic information
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType), default=TaskType.FEATURE)

    # Time tracking
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    actual_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    story_points: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Dates
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Progress and quality
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100%
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10

    # Hierarchy
    parent_task_id: Mapped[int | None] = mapped_column(ForeignKey('tasks.id'), nullable=True)

    # Technical details
    branch_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pull_request_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    assignees: Mapped[list["User"]] = relationship("User", secondary=task_assignees)

    # Self-referential for subtasks
    parent_task: Mapped["Task"] = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks: Mapped[list["Task"]] = relationship("Task", back_populates="parent_task")

    # Dependencies
    dependencies: Mapped[list["Task"]] = relationship(
        "Task", 
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
        back_populates="dependents"
    )
    dependents: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.depends_on_id,
        secondaryjoin=id == task_dependencies.c.task_id,
        back_populates="dependencies"
    )

    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.DONE

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and not self.is_completed:
            return datetime.now().date() > self.due_date
        return False

    @property
    def is_subtask(self) -> bool:
        """Check if this is a subtask"""
        return self.parent_task_id is not None

    @property
    def has_subtasks(self) -> bool:
        """Check if task has subtasks"""
        return len(self.subtasks) > 0

    @property
    def completion_ratio(self) -> float:
        """Get completion ratio (0.0 - 1.0)"""
        return self.progress / 100.0

    @property
    def time_efficiency(self) -> float | None:
        """Calculate time efficiency (actual vs estimated)"""
        if self.estimated_hours and self.actual_hours > 0:
            return float(self.estimated_hours) / float(self.actual_hours)
        return None

    def mark_completed(self):
        """Mark task as completed"""
        self.status = TaskStatus.DONE
        self.progress = 100
        self.completed_at = datetime.utcnow()

    def add_dependency(self, task: "Task"):
        """Add task dependency"""
        if task not in self.dependencies:
            self.dependencies.append(task)

    def remove_dependency(self, task: "Task"):
        """Remove task dependency"""
        if task in self.dependencies:
            self.dependencies.remove(task)

    def can_start(self) -> bool:
        """Check if task can be started (all dependencies completed)"""
        return all(dep.is_completed for dep in self.dependencies)

    def calculate_subtask_progress(self) -> int:
        """Calculate progress based on subtasks"""
        if not self.subtasks:
            return self.progress

        total_progress = sum(subtask.progress for subtask in self.subtasks)
        return total_progress // len(self.subtasks) if self.subtasks else 0

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
