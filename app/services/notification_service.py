#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Service - Сервис уведомлений
Comprehensive notification system with multiple delivery channels
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    PROJECT_MILESTONE = "project_milestone"
    DEADLINE_REMINDER = "deadline_reminder"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    IN_APP = "in_app"
    DESKTOP = "desktop"
    SLACK = "slack"


@dataclass
class Notification:
    """Notification data structure"""
    id: Optional[str] = None
    user_id: int = 0
    title: str = ""
    message: str = ""
    notification_type: NotificationType = NotificationType.INFO
    channels: List[NotificationChannel] = None
    data: Dict[str, Any] = None
    created_at: datetime = None
    read_at: Optional[datetime] = None

    def __post_init__(self):
        if self.channels is None:
            self.channels = [NotificationChannel.IN_APP]
        if self.data is None:
            self.data = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class EmailSender:
    """Email notification sender"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send email notification"""
        try:
            # Email configuration (placeholder)
            self.logger.info(f"Email would be sent to {recipient}: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False


class NotificationTemplateEngine:
    """Notification template engine"""

    def __init__(self):
        self.templates = {
            NotificationType.TASK_ASSIGNED: {
                'title': 'Новая задача назначена',
                'email_subject': 'Вам назначена новая задача: {task_title}',
                'email_body': 'Здравствуйте!\n\nВам назначена новая задача: {task_title}\n\nПроект: {project_name}',
            },
            NotificationType.TASK_COMPLETED: {
                'title': 'Задача выполнена',
                'email_subject': 'Задача выполнена: {task_title}',
                'email_body': 'Здравствуйте!\n\nЗадача была выполнена: {task_title}',
            }
        }

    def render_template(self, notification_type: NotificationType, template_type: str, **kwargs) -> str:
        """Render notification template"""
        template = self.templates.get(notification_type, {}).get(template_type, '')

        if template:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                logging.error(f"Missing template variable: {e}")
                return template

        return ''


class NotificationService:
    """
    Main notification service
    Основной сервис уведомлений
    """

    def __init__(self, db_session: Session, config):
        self.db = db_session
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.email_sender = EmailSender(config)
        self.template_engine = NotificationTemplateEngine()
        self.in_app_notifications: Dict[int, List[Notification]] = {}

    def send_notification(self, notification: Notification) -> bool:
        """Send notification through specified channels"""
        success = True

        try:
            # Send through each channel
            for channel in notification.channels:
                if channel == NotificationChannel.EMAIL:
                    success = success and self._send_email_notification(notification)
                elif channel == NotificationChannel.IN_APP:
                    self._store_in_app_notification(notification)

            return success

        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            return False

    def _send_email_notification(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            from app.models.user import User

            # Get user
            user = self.db.get(User, notification.user_id)
            if not user or not user.email:
                return False

            # Render email content
            subject = self.template_engine.render_template(
                notification.notification_type,
                'email_subject',
                **notification.data
            ) or notification.title

            body = self.template_engine.render_template(
                notification.notification_type,
                'email_body',
                **notification.data
            ) or notification.message

            return self.email_sender.send_email(user.email, subject, body)

        except Exception as e:
            self.logger.error(f"Email notification error: {str(e)}")
            return False

    def _store_in_app_notification(self, notification: Notification):
        """Store in-app notification"""
        if notification.user_id not in self.in_app_notifications:
            self.in_app_notifications[notification.user_id] = []

        self.in_app_notifications[notification.user_id].append(notification)

        # Keep only last 100 notifications per user
        if len(self.in_app_notifications[notification.user_id]) > 100:
            self.in_app_notifications[notification.user_id] =                 self.in_app_notifications[notification.user_id][-100:]

    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        """Get notifications for user"""
        user_notifications = self.in_app_notifications.get(user_id, [])

        if unread_only:
            user_notifications = [n for n in user_notifications if n.read_at is None]

        # Sort by creation time (newest first)
        user_notifications.sort(key=lambda x: x.created_at, reverse=True)
        return user_notifications[:limit]

    def mark_notification_read(self, user_id: int, notification_id: str) -> bool:
        """Mark notification as read"""
        user_notifications = self.in_app_notifications.get(user_id, [])

        for notification in user_notifications:
            if notification.id == notification_id:
                notification.read_at = datetime.utcnow()
                return True

        return False

    def send_task_assigned_notification(self, task_data: Dict[str, Any], assignee_user_ids: List[int]) -> bool:
        """Send task assignment notification"""
        success = True

        for user_id in assignee_user_ids:
            notification = Notification(
                id=f"task_assigned_{task_data.get('id')}_{user_id}",
                user_id=user_id,
                title="Новая задача назначена",
                message=f"Вам назначена задача: {task_data.get('title')}",
                notification_type=NotificationType.TASK_ASSIGNED,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                data=task_data
            )

            result = self.send_notification(notification)
            success = success and result

        return success

    def send_task_completed_notification(self, task_data: Dict[str, Any], stakeholder_user_ids: List[int]) -> bool:
        """Send task completion notification"""
        success = True

        for user_id in stakeholder_user_ids:
            notification = Notification(
                id=f"task_completed_{task_data.get('id')}_{user_id}",
                user_id=user_id,
                title="Задача выполнена",
                message=f"Задача выполнена: {task_data.get('title')}",
                notification_type=NotificationType.TASK_COMPLETED,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                data=task_data
            )

            result = self.send_notification(notification)
            success = success and result

        return success

    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old in-app notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cleaned_count = 0

        for user_id in self.in_app_notifications:
            original_count = len(self.in_app_notifications[user_id])
            self.in_app_notifications[user_id] = [
                n for n in self.in_app_notifications[user_id]
                if n.created_at > cutoff_date
            ]
            cleaned_count += original_count - len(self.in_app_notifications[user_id])

        self.logger.info(f"Cleaned up {cleaned_count} old notifications")
        return cleaned_count
