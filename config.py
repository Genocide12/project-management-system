#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Management System - Configuration Module
Модуль конфигурации системы управления проектами

This module handles all configuration-related functionality including:
- Application settings
- Database configuration  
- User preferences
- Theme and UI settings
- Localization settings

Этот модуль обрабатывает всю функциональность, связанную с конфигурацией:
- Настройки приложения
- Конфигурация базы данных
- Пользовательские предпочтения
- Настройки темы и интерфейса
- Настройки локализации
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import configparser
from cryptography.fernet import Fernet
from PyQt6.QtCore import QSettings, QStandardPaths


@dataclass
class DatabaseConfig:
    """
    Database configuration settings
    Настройки конфигурации базы данных
    """
    type: str = "sqlite"  # sqlite, postgresql
    host: str = "localhost"
    port: int = 5432
    database: str = "project_management"
    username: str = ""
    password: str = ""
    sqlite_path: str = "data/project_management.db"
    connection_timeout: int = 30
    max_connections: int = 10
    echo_sql: bool = False
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    encryption_enabled: bool = False
    

@dataclass
class UIConfig:
    """
    User interface configuration
    Конфигурация пользовательского интерфейса
    """
    theme: str = "light"  # light, dark, auto
    language: str = "ru"  # ru, en
    font_family: str = "Segoe UI"
    font_size: int = 9
    window_geometry: Dict[str, int] = field(default_factory=dict)
    window_state: bytes = b""
    show_splash_screen: bool = True
    enable_animations: bool = True
    show_tooltips: bool = True
    auto_save_interval: int = 300  # seconds
    recent_files_count: int = 10
    grid_snap_enabled: bool = True
    grid_size: int = 10
    

@dataclass
class ApplicationConfig:
    """
    Main application configuration
    Основная конфигурация приложения
    """
    app_name: str = "Project Management System"
    version: str = "1.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    log_file_path: str = "logs/app.log"
    log_max_size_mb: int = 10
    log_backup_count: int = 5
    data_directory: str = "data"
    temp_directory: str = "temp"
    backup_directory: str = "backups"
    plugins_directory: str = "plugins"
    check_updates: bool = True
    telemetry_enabled: bool = False
    

@dataclass
class SecurityConfig:
    """
    Security-related configuration
    Конфигурация безопасности
    """
    encryption_key: str = ""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = False
    session_timeout_minutes: int = 480  # 8 hours
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    two_factor_enabled: bool = False
    

@dataclass
class NotificationConfig:
    """
    Notification system configuration
    Конфигурация системы уведомлений
    """
    desktop_notifications: bool = True
    email_notifications: bool = False
    sound_enabled: bool = True
    notification_duration: int = 5000  # milliseconds
    show_task_reminders: bool = True
    show_deadline_warnings: bool = True
    warning_days_before_deadline: int = 3
    

class ConfigManager:
    """
    Central configuration manager for the application
    Центральный менеджер конфигурации для приложения
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager
        Инициализация менеджера конфигурации
        """
        self.config_dir = config_dir or self._get_config_directory()
        self.config_file = self.config_dir / "config.yaml"
        self.user_config_file = self.config_dir / "user_config.yaml"
        self.encrypted_config_file = self.config_dir / "secure_config.enc"
        
        # Configuration objects
        self.app_config = ApplicationConfig()
        self.db_config = DatabaseConfig()
        self.ui_config = UIConfig()
        self.security_config = SecurityConfig()
        self.notification_config = NotificationConfig()
        
        # QSettings for Qt-specific settings
        self.qt_settings = QSettings()
        
        # Encryption key for sensitive data
        self._encryption_key = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _get_config_directory(self) -> Path:
        """
        Get the appropriate configuration directory for the platform
        Получить подходящий каталог конфигурации для платформы
        """
        if sys.platform == "win32":
            config_dir = Path(os.environ.get("APPDATA", ".")) / "ProjectManagement"
        elif sys.platform == "darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "ProjectManagement"
        else:  # Linux and other Unix-like
            config_dir = Path.home() / ".config" / "ProjectManagement"
            
        return config_dir
        
    def _generate_encryption_key(self) -> str:
        """
        Generate a new encryption key
        Генерация нового ключа шифрования
        """
        return Fernet.generate_key().decode()
        
    def _get_encryption_key(self) -> Fernet:
        """
        Get or create encryption key for sensitive data
        Получить или создать ключ шифрования для чувствительных данных
        """
        if self._encryption_key is None:
            key_file = self.config_dir / "key.enc"
            
            if key_file.exists():
                with open(key_file, "rb") as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                    
            self._encryption_key = Fernet(key)
            
        return self._encryption_key
        
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive configuration data
        Шифрование чувствительных данных конфигурации
        """
        fernet = self._get_encryption_key()
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()
        
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive configuration data
        Расшифровка чувствительных данных конфигурации
        """
        fernet = self._get_encryption_key()
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
        
    def load_config(self) -> bool:
        """
        Load configuration from files
        Загрузка конфигурации из файлов
        """
        try:
            # Load main configuration
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    
                if config_data:
                    self._update_config_objects(config_data)
                    
            # Load user-specific configuration
            if self.user_config_file.exists():
                with open(self.user_config_file, "r", encoding="utf-8") as f:
                    user_config_data = yaml.safe_load(f)
                    
                if user_config_data:
                    self._update_config_objects(user_config_data)
                    
            # Load encrypted sensitive configuration
            self._load_encrypted_config()
            
            self.logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
            
    def save_config(self) -> bool:
        """
        Save configuration to files
        Сохранение конфигурации в файлы
        """
        try:
            # Prepare configuration data
            config_data = {
                "application": asdict(self.app_config),
                "database": asdict(self.db_config),
                "ui": asdict(self.ui_config),
                "notifications": asdict(self.notification_config)
            }
            
            # Save main configuration
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
            # Save encrypted sensitive configuration
            self._save_encrypted_config()
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
            
    def _update_config_objects(self, config_data: Dict[str, Any]):
        """
        Update configuration objects with loaded data
        Обновление объектов конфигурации загруженными данными
        """
        if "application" in config_data:
            app_data = config_data["application"]
            for key, value in app_data.items():
                if hasattr(self.app_config, key):
                    setattr(self.app_config, key, value)
                    
        if "database" in config_data:
            db_data = config_data["database"]
            for key, value in db_data.items():
                if hasattr(self.db_config, key):
                    setattr(self.db_config, key, value)
                    
        if "ui" in config_data:
            ui_data = config_data["ui"]
            for key, value in ui_data.items():
                if hasattr(self.ui_config, key):
                    setattr(self.ui_config, key, value)
                    
        if "notifications" in config_data:
            notif_data = config_data["notifications"]
            for key, value in notif_data.items():
                if hasattr(self.notification_config, key):
                    setattr(self.notification_config, key, value)
                    
    def _load_encrypted_config(self):
        """
        Load encrypted sensitive configuration
        Загрузка зашифрованной чувствительной конфигурации
        """
        try:
            if self.encrypted_config_file.exists():
                with open(self.encrypted_config_file, "r", encoding="utf-8") as f:
                    encrypted_data = f.read()
                    
                decrypted_data = self.decrypt_sensitive_data(encrypted_data)
                sensitive_config = json.loads(decrypted_data)
                
                # Update security configuration
                for key, value in sensitive_config.get("security", {}).items():
                    if hasattr(self.security_config, key):
                        setattr(self.security_config, key, value)
                        
        except Exception as e:
            self.logger.warning(f"Could not load encrypted configuration: {e}")
            
    def _save_encrypted_config(self):
        """
        Save encrypted sensitive configuration
        Сохранение зашифрованной чувствительной конфигурации
        """
        try:
            sensitive_data = {
                "security": asdict(self.security_config)
            }
            
            json_data = json.dumps(sensitive_data)
            encrypted_data = self.encrypt_sensitive_data(json_data)
            
            with open(self.encrypted_config_file, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
                
        except Exception as e:
            self.logger.error(f"Failed to save encrypted configuration: {e}")
            
    def get_config(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary
        Получить всю конфигурацию как словарь
        """
        return {
            "application": asdict(self.app_config),
            "database": asdict(self.db_config),
            "ui": asdict(self.ui_config),
            "security": asdict(self.security_config),
            "notifications": asdict(self.notification_config)
        }
        
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration setting
        Получить конкретную настройку конфигурации
        """
        config_map = {
            "application": self.app_config,
            "database": self.db_config,
            "ui": self.ui_config,
            "security": self.security_config,
            "notifications": self.notification_config
        }
        
        if section in config_map:
            return getattr(config_map[section], key, default)
        return default
        
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """
        Set a specific configuration setting
        Установить конкретную настройку конфигурации
        """
        config_map = {
            "application": self.app_config,
            "database": self.db_config,
            "ui": self.ui_config,
            "security": self.security_config,
            "notifications": self.notification_config
        }
        
        if section in config_map and hasattr(config_map[section], key):
            setattr(config_map[section], key, value)
            return True
        return False
        
    def load_user_preferences(self):
        """
        Load user preferences from Qt settings
        Загрузка пользовательских предпочтений из настроек Qt
        """
        # Load window geometry and state
        geometry = self.qt_settings.value("geometry", {})
        if geometry:
            self.ui_config.window_geometry = geometry
            
        window_state = self.qt_settings.value("windowState", b"")
        if window_state:
            self.ui_config.window_state = window_state
            
        # Load other UI preferences
        self.ui_config.theme = self.qt_settings.value("theme", self.ui_config.theme)
        self.ui_config.language = self.qt_settings.value("language", self.ui_config.language)
        self.ui_config.font_family = self.qt_settings.value("fontFamily", self.ui_config.font_family)
        self.ui_config.font_size = int(self.qt_settings.value("fontSize", self.ui_config.font_size))
        
    def save_user_preferences(self):
        """
        Save user preferences to Qt settings
        Сохранение пользовательских предпочтений в настройки Qt
        """
        # Save window geometry and state
        if self.ui_config.window_geometry:
            self.qt_settings.setValue("geometry", self.ui_config.window_geometry)
            
        if self.ui_config.window_state:
            self.qt_settings.setValue("windowState", self.ui_config.window_state)
            
        # Save other UI preferences
        self.qt_settings.setValue("theme", self.ui_config.theme)
        self.qt_settings.setValue("language", self.ui_config.language)
        self.qt_settings.setValue("fontFamily", self.ui_config.font_family)
        self.qt_settings.setValue("fontSize", self.ui_config.font_size)
        
        self.qt_settings.sync()
        
    def reset_to_defaults(self):
        """
        Reset all configuration to default values
        Сброс всей конфигурации к значениям по умолчанию
        """
        self.app_config = ApplicationConfig()
        self.db_config = DatabaseConfig()
        self.ui_config = UIConfig()
        self.security_config = SecurityConfig()
        self.notification_config = NotificationConfig()
        
        # Clear Qt settings
        self.qt_settings.clear()
        
        self.logger.info("Configuration reset to defaults")
        
    def create_backup(self) -> bool:
        """
        Create a backup of current configuration
        Создание резервной копии текущей конфигурации
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            backup_file = backup_dir / f"config_backup_{timestamp}.yaml"
            
            config_data = self.get_config()
            with open(backup_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"Configuration backup created: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create configuration backup: {e}")
            return False
            
    def get_data_directory(self) -> Path:
        """
        Get the data directory path
        Получить путь к каталогу данных
        """
        data_dir = Path(self.app_config.data_directory)
        if not data_dir.is_absolute():
            data_dir = Path.cwd() / data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
        
    def get_temp_directory(self) -> Path:
        """
        Get the temporary directory path
        Получить путь к временному каталогу
        """
        temp_dir = Path(self.app_config.temp_directory)
        if not temp_dir.is_absolute():
            temp_dir = Path.cwd() / temp_dir
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
        
    def get_backup_directory(self) -> Path:
        """
        Get the backup directory path
        Получить путь к каталогу резервных копий
        """
        backup_dir = Path(self.app_config.backup_directory)
        if not backup_dir.is_absolute():
            backup_dir = Path.cwd() / backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir


# Global configuration instance
# Глобальный экземпляр конфигурации
config_manager = ConfigManager()


class Config:
    """
    Simple configuration access class
    Простой класс доступа к конфигурации
    """
    
    @staticmethod
    def get(section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        Получить значение конфигурации
        """
        return config_manager.get_setting(section, key, default)
        
    @staticmethod
    def set(section: str, key: str, value: Any) -> bool:
        """
        Set configuration value
        Установить значение конфигурации
        """
        return config_manager.set_setting(section, key, value)
        
    @staticmethod
    def save() -> bool:
        """
        Save configuration
        Сохранить конфигурацию
        """
        return config_manager.save_config()
        
    @staticmethod
    def load() -> bool:
        """
        Load configuration
        Загрузить конфигурацию
        """
        return config_manager.load_config()
