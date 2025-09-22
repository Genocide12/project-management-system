#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Connection Manager
Менеджер подключения к базе данных

This module handles database connections, session management, and basic
database operations for the project management system.

Этот модуль обрабатывает подключения к базе данных, управление сессиями
и базовые операции с базой данных для системы управления проектами.
"""

import os
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator, Any, Dict
from sqlalchemy import (
    create_engine, Engine, text, inspect, event,
    pool, exc as sqlalchemy_exc
)
from sqlalchemy.orm import (
    sessionmaker, Session, scoped_session,
    declarative_base
)
from sqlalchemy.pool import QueuePool, StaticPool
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

# Import models after they are defined
from app.database.models import Base
from app.core.config import ConfigManager


class DatabaseManager:
    """
    Database connection and session manager
    Менеджер подключений к базе данных и сессий
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize database manager
        Инициализация менеджера базы данных
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Database configuration
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session: Optional[scoped_session] = None
        
        # Thread safety
        self._lock = threading.RLock()
        self._initialized = False
        
        # Connection settings
        self._database_url = self._get_database_url()
        self._engine_options = self._get_engine_options()
        
    def _get_database_url(self) -> str:
        """
        Get database URL from configuration
        Получение URL базы данных из конфигурации
        """
        if self.config_manager:
            db_config = self.config_manager.db_config
            
            if db_config.type == "sqlite":
                # Ensure data directory exists
                db_path = Path(db_config.sqlite_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                return f"sqlite:///{db_path.absolute()}"
                
            elif db_config.type == "postgresql":
                # Build PostgreSQL URL
                username = db_config.username
                password = db_config.password
                host = db_config.host
                port = db_config.port
                database = db_config.database
                
                if username and password:
                    return f"postgresql://{username}:{password}@{host}:{port}/{database}"
                else:
                    return f"postgresql://{host}:{port}/{database}"
        
        # Default SQLite database
        default_path = Path("data/project_management.db")
        default_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{default_path.absolute()}"
        
    def _get_engine_options(self) -> Dict[str, Any]:
        """
        Get SQLAlchemy engine options
        Получение опций движка SQLAlchemy
        """
        options = {
            "echo": False,  # Set to True for SQL debugging
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        }
        
        if self.config_manager:
            db_config = self.config_manager.db_config
            options["echo"] = db_config.echo_sql
            
            if db_config.type == "sqlite":
                # SQLite-specific options
                options.update({
                    "poolclass": StaticPool,
                    "connect_args": {
                        "check_same_thread": False,
                        "timeout": db_config.connection_timeout
                    }
                })
            elif db_config.type == "postgresql":
                # PostgreSQL-specific options
                options.update({
                    "poolclass": QueuePool,
                    "pool_size": db_config.max_connections,
                    "max_overflow": 20,
                    "pool_timeout": db_config.connection_timeout
                })
        else:
            # Default SQLite options
            options.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 30
                }
            })
            
        return options
        
    def initialize(self) -> bool:
        """
        Initialize database connection and create tables
        Инициализация подключения к базе данных и создание таблиц
        """
        with self._lock:
            if self._initialized:
                return True
                
            try:
                # Create engine
                self._engine = create_engine(
                    self._database_url,
                    **self._engine_options
                )
                
                # Setup event listeners
                self._setup_event_listeners()
                
                # Test connection
                self._test_connection()
                
                # Create session factory
                self._session_factory = sessionmaker(
                    bind=self._engine,
                    expire_on_commit=False
                )
                
                # Create scoped session
                self._scoped_session = scoped_session(self._session_factory)
                
                # Create tables if they don't exist
                self._create_tables()
                
                # Run migrations
                self._run_migrations()
                
                self._initialized = True
                self.logger.info(f"Database initialized successfully: {self._database_url}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to initialize database: {e}")
                self._cleanup()
                raise
                
    def _setup_event_listeners(self):
        """
        Setup SQLAlchemy event listeners
        Настройка слушателей событий SQLAlchemy
        """
        if self._database_url.startswith("sqlite"):
            # Enable foreign key constraints for SQLite
            @event.listens_for(self._engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
                
    def _test_connection(self):
        """
        Test database connection
        Тестирование подключения к базе данных
        """
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                self.logger.debug("Database connection test successful")
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise
            
    def _create_tables(self):
        """
        Create database tables if they don't exist
        Создание таблиц базы данных, если они не существуют
        """
        try:
            Base.metadata.create_all(self._engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {e}")
            raise
            
    def _run_migrations(self):
        """
        Run database migrations using Alembic
        Выполнение миграций базы данных с использованием Alembic
        """
        try:
            # Check if Alembic is initialized
            alembic_dir = Path("alembic")
            if not alembic_dir.exists():
                self.logger.info("Alembic not initialized, skipping migrations")
                return
                
            # Load Alembic configuration
            alembic_cfg = AlembicConfig("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", self._database_url)
            
            # Run migrations to head
            alembic_command.upgrade(alembic_cfg, "head")
            self.logger.info("Database migrations completed successfully")
            
        except Exception as e:
            self.logger.warning(f"Migration failed or not configured: {e}")
            # Don't raise here as migrations might not be set up yet
            
    def get_session(self) -> Session:
        """
        Get a new database session
        Получение новой сессии базы данных
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
            
        return self._session_factory()
        
    def get_scoped_session(self) -> scoped_session:
        """
        Get thread-local scoped session
        Получение локальной для потока scoped сессии
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
            
        return self._scoped_session
        
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with automatic commit/rollback
        Контекстный менеджер для сессий базы данных с автоматическим commit/rollback
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """
        Execute raw SQL query
        Выполнение прямого SQL запроса
        """
        with self.session_scope() as session:
            return session.execute(text(sql), params or {})
            
    def verify_integrity(self) -> bool:
        """
        Verify database integrity
        Проверка целостности базы данных
        """
        try:
            with self.session_scope() as session:
                # Check if all required tables exist
                inspector = inspect(self._engine)
                existing_tables = inspector.get_table_names()
                
                required_tables = [
                    'users', 'projects', 'tasks', 'comments', 
                    'attachments', 'activity_logs', 'project_members', 'task_assignees'
                ]
                
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if missing_tables:
                    self.logger.error(f"Missing database tables: {missing_tables}")
                    return False
                    
                # Basic data integrity checks
                result = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
                self.logger.debug(f"Users table contains {result} records")
                
                self.logger.info("Database integrity check passed")
                return True
                
        except Exception as e:
            self.logger.error(f"Database integrity check failed: {e}")
            return False
            
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create database backup
        Создание резервной копии базы данных
        """
        try:
            if self._database_url.startswith("sqlite"):
                return self._backup_sqlite(backup_path)
            else:
                return self._backup_postgresql(backup_path)
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
            
    def _backup_sqlite(self, backup_path: Optional[Path] = None) -> bool:
        """
        Backup SQLite database
        Резервное копирование базы данных SQLite
        """
        import shutil
        from datetime import datetime
        
        # Extract database file path from URL
        db_file = Path(self._database_url.replace("sqlite:///", ""))
        
        if not db_file.exists():
            self.logger.error(f"Database file not found: {db_file}")
            return False
            
        if backup_path is None:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"database_backup_{timestamp}.db"
            
        # Copy database file
        shutil.copy2(db_file, backup_path)
        self.logger.info(f"SQLite database backed up to: {backup_path}")
        return True
        
    def _backup_postgresql(self, backup_path: Optional[Path] = None) -> bool:
        """
        Backup PostgreSQL database using pg_dump
        Резервное копирование базы данных PostgreSQL с использованием pg_dump
        """
        import subprocess
        from datetime import datetime
        
        if backup_path is None:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"database_backup_{timestamp}.sql"
            
        try:
            # Extract connection parameters from URL
            db_config = self.config_manager.db_config
            
            cmd = [
                "pg_dump",
                "-h", db_config.host,
                "-p", str(db_config.port),
                "-U", db_config.username,
                "-d", db_config.database,
                "-f", str(backup_path)
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config.password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"PostgreSQL database backed up to: {backup_path}")
                return True
            else:
                self.logger.error(f"pg_dump failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            self.logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            return False
        except Exception as e:
            self.logger.error(f"PostgreSQL backup failed: {e}")
            return False
            
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics
        Получение информации и статистики базы данных
        """
        info = {
            "url": self._database_url,
            "initialized": self._initialized,
            "engine_info": None,
            "table_stats": {}
        }
        
        if not self._initialized:
            return info
            
        try:
            # Engine information
            info["engine_info"] = {
                "driver": self._engine.driver,
                "dialect": str(self._engine.dialect),
                "pool_size": getattr(self._engine.pool, 'size', None),
                "pool_checked_out": getattr(self._engine.pool, 'checkedout', None)
            }
            
            # Table statistics
            with self.session_scope() as session:
                tables = ['users', 'projects', 'tasks', 'comments', 'attachments']
                
                for table in tables:
                    try:
                        result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        info["table_stats"][table] = result
                    except Exception:
                        info["table_stats"][table] = "Error"
                        
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            
        return info
        
    def _cleanup(self):
        """
        Cleanup database resources
        Очистка ресурсов базы данных
        """
        try:
            if self._scoped_session:
                self._scoped_session.remove()
                self._scoped_session = None
                
            if self._session_factory:
                self._session_factory = None
                
            if self._engine:
                self._engine.dispose()
                self._engine = None
                
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")
            
    def close(self):
        """
        Close database connections and cleanup
        Закрытие подключений к базе данных и очистка
        """
        with self._lock:
            if self._initialized:
                self._cleanup()
                self._initialized = False
                self.logger.info("Database connections closed")
                
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def __del__(self):
        """Destructor"""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup in destructor
