#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Model - Модель проекта
Comprehensive project management with status tracking, budgeting, and team management
"""

from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Numeric, Date, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
import enum
from .base import Base


class ProjectStatus(enum.Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(enum.Enum):
    """Project priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Association table for project members
project_members = Table(
    'project_members',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role', String(50), default="member"),
    Column('joined_at', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True)
)


class Project(Base):
    """
    Project model with comprehensive management features
    Модель проекта с комплексными возможностями управления
    """
    __tablename__ = 'projects'

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Basic information
    name: Mapped[str] = mapped_column(String(200), index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status and priority
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    priority: Mapped[ProjectPriority] = mapped_column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM)

    # Dates
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Budget and progress
    budget: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    spent: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100%

    # Technical details
    repository_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    members: Mapped[list["User"]] = relationship("User", secondary=project_members, back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        """Check if project is active"""
        return self.status == ProjectStatus.ACTIVE

    @property
    def is_completed(self) -> bool:
        """Check if project is completed"""
        return self.status == ProjectStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue"""
        if self.deadline and not self.is_completed:
            return datetime.now().date() > self.deadline
        return False

    @property
    def budget_remaining(self) -> float:
        """Get remaining budget"""
        if self.budget is None:
            return 0.0
        return float(self.budget - self.spent)

    @property
    def budget_usage_percent(self) -> float:
        """Get budget usage percentage"""
        if not self.budget or self.budget == 0:
            return 0.0
        return (float(self.spent) / float(self.budget)) * 100

    def calculate_progress(self) -> int:
        """Calculate progress based on completed tasks"""
        if not self.tasks:
            return 0

        completed_tasks = len([t for t in self.tasks if t.is_completed])
        total_tasks = len(self.tasks)

        return int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    def update_progress(self):
        """Update project progress automatically"""
        self.progress = self.calculate_progress()

    def __repr__(self):
        return f"<Project(id={self.id}, code='{self.code}', name='{self.name}')>"
