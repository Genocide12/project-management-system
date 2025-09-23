#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Service - Сервис аутентификации
Advanced authentication with session management and security features
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from werkzeug.security import check_password_hash


class AuthenticationError(Exception):
    """Authentication related errors"""
    pass


class SessionManager:
    """Manages user sessions and tokens"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour default

    def create_session(self, user) -> str:
        """Create new user session"""
        session_token = secrets.token_urlsafe(32)

        session_data = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
        }

        self.active_sessions[session_token] = session_data
        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate and refresh session"""
        session_data = self.active_sessions.get(session_token)

        if not session_data:
            return None

        # Check if session expired
        last_activity = session_data['last_activity']
        if datetime.utcnow() - last_activity > timedelta(seconds=self.session_timeout):
            self.destroy_session(session_token)
            return None

        # Update last activity
        session_data['last_activity'] = datetime.utcnow()
        return session_data

    def destroy_session(self, session_token: str):
        """Destroy user session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]


class AuthService:
    """
    Main authentication service
    Основной сервис аутентификации
    """

    def __init__(self, db_session: Session, config_manager):
        self.db = db_session
        self.config = config_manager
        self.session_manager = SessionManager(config_manager)
        self.logger = logging.getLogger(__name__)

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with username and password"""
        try:
            from app.models.user import User, UserStatus

            # Find user
            user = self.db.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if not user:
                raise AuthenticationError("Invalid username or password")

            # Check if user is active
            if user.status != UserStatus.ACTIVE:
                raise AuthenticationError("Account is not active")

            # Verify password
            if not user.check_password(password):
                raise AuthenticationError("Invalid username or password")

            # Complete login
            return self._complete_login(user)

        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError("Authentication failed")

    def _complete_login(self, user) -> Dict[str, Any]:
        """Complete the login process"""
        user.last_login = datetime.utcnow()
        session_token = self.session_manager.create_session(user)
        self.db.commit()

        return {
            'status': 'success',
            'session_token': session_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role.value,
                'email': user.email
            },
            'message': 'Login successful'
        }

    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and destroy session"""
        session_data = self.session_manager.validate_session(session_token)

        if session_data:
            username = session_data['username']
            self.session_manager.destroy_session(session_token)
            self.logger.info(f"User {username} logged out")

        return {'status': 'success', 'message': 'Logged out successfully'}

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate user session"""
        return self.session_manager.validate_session(session_token)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password with validation"""
        try:
            from app.models.user import User

            # Get user
            user = self.db.get(User, user_id)
            if not user:
                raise AuthenticationError("User not found")

            # Verify current password
            if not user.check_password(current_password):
                raise AuthenticationError("Current password is incorrect")

            # Set new password
            user.set_password(new_password)
            self.db.commit()

            return {'status': 'success', 'message': 'Password changed successfully'}

        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Password change error: {str(e)}")
            raise AuthenticationError("Failed to change password")
