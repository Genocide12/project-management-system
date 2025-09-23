#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Model - Модель пользователя
Advanced user management with roles, permissions, and profile data
"""

from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum
from .base import Base


class UserRole(enum.Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    MANAGER = "manager" 
    DEVELOPER = "developer"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserStatus(enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """
    User model with comprehensive profile and security features
    Модель пользователя с полным профилем и функциями безопасности
    """
    __tablename__ = 'users'

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Authentication
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # Profile information
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Work information
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employee_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # System fields
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEVELOPER)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE)

    # Preferences
    language: Mapped[str] = mapped_column(String(10), default="ru")
    theme: Mapped[str] = mapped_column(String(20), default="light")
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Security
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    account_locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    two_factor_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str):
        """Set password with secure hashing"""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(filter(None, parts))

    @property
    def display_name(self) -> str:
        """Get display name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
