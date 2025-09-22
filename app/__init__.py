#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Management System - Application Package
Система управления проектами - Пакет приложения

This package contains the core application logic and components.
Этот пакет содержит основную логику приложения и компоненты.
"""

__version__ = "1.0.0"
__author__ = "Genocide12"
__email__ = "contact@example.com"
__description__ = "Advanced Project Management System with PyQt6 GUI"

# Import core modules
from app.core.application import ProjectManagerApp
from app.core.config import Config, ConfigManager
from app.database.connection import DatabaseManager

__all__ = [
    "ProjectManagerApp",
    "Config", 
    "ConfigManager",
    "DatabaseManager"
]
