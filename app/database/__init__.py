#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Package
Пакет базы данных

This package contains all database-related functionality including:
- Database connection management
- ORM models
- Migration scripts
- Repository patterns

Этот пакет содержит всю функциональность, связанную с базой данных:
- Управление подключениями к базе данных
- ORM модели
- Скрипты миграций
- Паттерны репозитория
"""

from app.database.connection import DatabaseManager
from app.database.models import Base, User, Project, Task, Comment, Attachment
from app.database.repository import BaseRepository

__all__ = [
    "DatabaseManager",
    "Base",
    "User", 
    "Project",
    "Task",
    "Comment",
    "Attachment",
    "BaseRepository"
]
