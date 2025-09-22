#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Models
Модели базы данных

This module contains all SQLAlchemy ORM models for the project management system.
Этот модуль содержит все ORM модели SQLAlchemy для системы управления проектами.
"""

import enum
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean,
    ForeignKey, Enum, Numeric, LargeBinary, UniqueConstraint,
    Index, CheckConstraint, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Create base class for all models
Base = declarative_base()


class UserRole(enum.Enum):
    """
    User roles enumeration
    Перечисление ролей пользователей
    """
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"


class ProjectStatus(enum.Enum):
    """
    Project status enumeration
    Перечисление статусов проекта
    """
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(enum.Enum):
    """
    Task status enumeration
    Перечисление статусов задач
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    """
    Task priority enumeration
    Перечисление приоритетов задач
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Association table for project members
project_members = Table(
    'project_members',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', Enum(UserRole), nullable=False, default=UserRole.DEVELOPER),
    Column('joined_at', DateTime, default=func.now()),
    Column('is_active', Boolean, default=True)
)


# Association table for task assignees
task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('assigned_at', DateTime, default=func.now()),
    Column('is_active', Boolean, default=True)
)


class User(Base):
    """
    User model
    Модель пользователя
    """
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Personal information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Profile information
    avatar = Column(LargeBinary, nullable=True)
    bio = Column(Text, nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # System fields
    role = Column(Enum(UserRole), nullable=False, default=UserRole.DEVELOPER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Security fields
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    
    # Preferences
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='ru')
    theme = Column(String(20), default='light')
    notifications_enabled = Column(Boolean, default=True)
    
    # Relationships
    created_projects = relationship('Project', back_populates='creator', foreign_keys='Project.creator_id')
    assigned_tasks = relationship('Task', secondary=task_assignees, back_populates='assignees')
    created_tasks = relationship('Task', back_populates='creator', foreign_keys='Task.creator_id')
    comments = relationship('Comment', back_populates='author')
    attachments = relationship('Attachment', back_populates='uploaded_by')
    
    # Project memberships (many-to-many)
    projects = relationship('Project', secondary=project_members, back_populates='members')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('length(username) >= 3', name='username_min_length'),
        CheckConstraint('length(password_hash) >= 8', name='password_min_length'),
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_username_active', 'username', 'is_active'),
    )
    
    def set_password(self, password: str):
        """
        Set user password with hashing
        Установка пароля пользователя с хешированием
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches stored hash
        Проверка соответствия введенного пароля сохраненному хешу
        """
        return check_password_hash(self.password_hash, password)
        
    @property
    def full_name(self) -> str:
        """
        Get user's full name
        Получение полного имени пользователя
        """
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
        
    @property
    def display_name(self) -> str:
        """
        Get user's display name
        Получение отображаемого имени пользователя
        """
        return f"{self.first_name} {self.last_name}"
        
    def is_admin(self) -> bool:
        """
        Check if user is an administrator
        Проверка, является ли пользователь администратором
        """
        return self.role == UserRole.ADMIN
        
    def is_manager(self) -> bool:
        """
        Check if user is a manager
        Проверка, является ли пользователь менеджером
        """
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)
        
    def can_manage_project(self, project: 'Project') -> bool:
        """
        Check if user can manage a specific project
        Проверка возможности управления конкретным проектом
        """
        if self.is_admin() or project.creator_id == self.id:
            return True
            
        # Check if user is a manager in this project
        for member in project.project_members:
            if member.user_id == self.id and member.role == UserRole.MANAGER:
                return True
                
        return False
        
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Project(Base):
    """
    Project model
    Модель проекта
    """
    __tablename__ = 'projects'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    
    # Dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    
    # Budget and progress
    budget = Column(Numeric(15, 2), nullable=True)
    progress = Column(Integer, default=0, nullable=False)  # Percentage 0-100
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = relationship('User', back_populates='created_projects', foreign_keys=[creator_id])
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')
    attachments = relationship('Attachment', back_populates='project')
    
    # Project members (many-to-many)
    members = relationship('User', secondary=project_members, back_populates='projects')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='progress_range'),
        CheckConstraint('budget >= 0', name='budget_positive'),
        CheckConstraint('start_date <= end_date', name='valid_date_range'),
        Index('idx_project_status_priority', 'status', 'priority'),
        Index('idx_project_creator_status', 'creator_id', 'status'),
    )
    
    @property
    def is_active(self) -> bool:
        """
        Check if project is currently active
        Проверка активности проекта
        """
        return self.status == ProjectStatus.ACTIVE
        
    @property
    def is_completed(self) -> bool:
        """
        Check if project is completed
        Проверка завершенности проекта
        """
        return self.status == ProjectStatus.COMPLETED
        
    @property
    def is_overdue(self) -> bool:
        """
        Check if project is overdue
        Проверка просрочки проекта
        """
        if self.deadline and not self.is_completed:
            return datetime.now().date() > self.deadline
        return False
        
    @property
    def task_count(self) -> int:
        """
        Get total number of tasks in project
        Получение общего количества задач в проекте
        """
        return len(self.tasks)
        
    @property
    def completed_task_count(self) -> int:
        """
        Get number of completed tasks
        Получение количества завершенных задач
        """
        return len([task for task in self.tasks if task.status == TaskStatus.DONE])
        
    def calculate_progress(self):
        """
        Calculate project progress based on completed tasks
        Расчет прогресса проекта на основе завершенных задач
        """
        if not self.tasks:
            return 0
            
        completed_tasks = self.completed_task_count
        total_tasks = self.task_count
        
        return int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
    def update_progress(self):
        """
        Update project progress automatically
        Автоматическое обновление прогресса проекта
        """
        self.progress = self.calculate_progress()
        
    def __repr__(self):
        return f"<Project(id={self.id}, code='{self.code}', name='{self.name}', status='{self.status.value}')>"


class Task(Base):
    """
    Task model
    Модель задачи
    """
    __tablename__ = 'tasks'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic information
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    
    # Time tracking
    estimated_hours = Column(Numeric(8, 2), nullable=True)
    actual_hours = Column(Numeric(8, 2), default=0, nullable=False)
    
    # Dates
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress
    progress = Column(Integer, default=0, nullable=False)  # Percentage 0-100
    
    # Hierarchy support
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    project = relationship('Project', back_populates='tasks')
    creator = relationship('User', back_populates='created_tasks', foreign_keys=[creator_id])
    assignees = relationship('User', secondary=task_assignees, back_populates='assigned_tasks')
    comments = relationship('Comment', back_populates='task', cascade='all, delete-orphan')
    attachments = relationship('Attachment', back_populates='task')
    
    # Self-referential relationship for subtasks
    parent_task = relationship('Task', remote_side=[id], backref='subtasks')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='task_progress_range'),
        CheckConstraint('estimated_hours >= 0', name='estimated_hours_positive'),
        CheckConstraint('actual_hours >= 0', name='actual_hours_positive'),
        Index('idx_task_project_status', 'project_id', 'status'),
        Index('idx_task_creator_status', 'creator_id', 'status'),
        Index('idx_task_due_date', 'due_date'),
    )
    
    @property
    def is_completed(self) -> bool:
        """
        Check if task is completed
        Проверка завершенности задачи
        """
        return self.status == TaskStatus.DONE
        
    @property
    def is_overdue(self) -> bool:
        """
        Check if task is overdue
        Проверка просрочки задачи
        """
        if self.due_date and not self.is_completed:
            return datetime.now().date() > self.due_date
        return False
        
    @property
    def is_subtask(self) -> bool:
        """
        Check if this is a subtask
        Проверка является ли задача подзадачей
        """
        return self.parent_task_id is not None
        
    @property
    def has_subtasks(self) -> bool:
        """
        Check if task has subtasks
        Проверка наличия подзадач
        """
        return len(self.subtasks) > 0
        
    def mark_completed(self):
        """
        Mark task as completed
        Отметить задачу как завершенную
        """
        self.status = TaskStatus.DONE
        self.progress = 100
        self.completed_at = func.now()
        
    def calculate_progress_from_subtasks(self):
        """
        Calculate progress based on subtasks completion
        Расчет прогресса на основе завершения подзадач
        """
        if not self.subtasks:
            return self.progress
            
        completed_subtasks = len([subtask for subtask in self.subtasks if subtask.is_completed])
        total_subtasks = len(self.subtasks)
        
        return int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
        
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}', project_id={self.project_id})>"


class Comment(Base):
    """
    Comment model for tasks and projects
    Модель комментариев для задач и проектов
    """
    __tablename__ = 'comments'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    # Relationships
    author = relationship('User', back_populates='comments')
    task = relationship('Task', back_populates='comments')
    project = relationship('Project')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('(task_id IS NOT NULL) OR (project_id IS NOT NULL)', 
                       name='comment_target_required'),
        Index('idx_comment_task_created', 'task_id', 'created_at'),
        Index('idx_comment_project_created', 'project_id', 'created_at'),
    )
    
    def __repr__(self):
        target = f"task_id={self.task_id}" if self.task_id else f"project_id={self.project_id}"
        return f"<Comment(id={self.id}, author_id={self.author_id}, {target})>"


class Attachment(Base):
    """
    File attachment model
    Модель файловых вложений
    """
    __tablename__ = 'attachments'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # File hash for deduplication
    file_hash = Column(String(64), nullable=False, index=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Foreign keys
    uploaded_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    # Relationships
    uploaded_by = relationship('User', back_populates='attachments')
    task = relationship('Task', back_populates='attachments')
    project = relationship('Project', back_populates='attachments')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('(task_id IS NOT NULL) OR (project_id IS NOT NULL)', 
                       name='attachment_target_required'),
        CheckConstraint('file_size > 0', name='file_size_positive'),
        Index('idx_attachment_task', 'task_id'),
        Index('idx_attachment_project', 'project_id'),
        Index('idx_attachment_hash', 'file_hash'),
    )
    
    @property
    def file_size_mb(self) -> float:
        """
        Get file size in megabytes
        Получение размера файла в мегабайтах
        """
        return round(self.file_size / (1024 * 1024), 2)
        
    def __repr__(self):
        target = f"task_id={self.task_id}" if self.task_id else f"project_id={self.project_id}"
        return f"<Attachment(id={self.id}, filename='{self.filename}', {target})>"


class ActivityLog(Base):
    """
    Activity log model for tracking user actions
    Модель журнала активности для отслеживания действий пользователей
    """
    __tablename__ = 'activity_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Activity information
    action = Column(String(100), nullable=False)  # create, update, delete, etc.
    entity_type = Column(String(50), nullable=False)  # project, task, user, etc.
    entity_id = Column(Integer, nullable=False)
    
    # Details
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationship
    user = relationship('User')
    
    # Constraints
    __table_args__ = (
        Index('idx_activity_user_created', 'user_id', 'created_at'),
        Index('idx_activity_entity', 'entity_type', 'entity_id'),
        Index('idx_activity_action_created', 'action', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action='{self.action}', entity_type='{self.entity_type}', user_id={self.user_id})>"
