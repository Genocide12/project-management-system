#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Manager - Менеджер экспорта
Advanced data export functionality with multiple formats
"""

import io
import csv
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union


class ExportFormat:
    """Export format constants"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"
    HTML = "html"


class DataExporter:
    """Base data exporter class"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export data to CSV format"""
        if not data:
            return ""

        output = io.StringIO()

        # Get field names from first row
        fieldnames = list(data[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            # Convert objects to strings
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, (datetime, date)):
                    clean_row[key] = value.isoformat()
                elif value is None:
                    clean_row[key] = ""
                else:
                    clean_row[key] = str(value)
            writer.writerow(clean_row)

        content = output.getvalue()
        output.close()

        if filename:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                f.write(content)

        return content

    def export_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export data to JSON format"""

        def json_serializer(obj):
            """JSON serializer for datetime objects"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        json_content = json.dumps(data, indent=2, ensure_ascii=False, default=json_serializer)

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)

        return json_content

    def export_to_html(self, data: List[Dict[str, Any]], filename: str = None, title: str = "Отчет") -> str:
        """Export data to HTML format"""
        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="ru">')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append(f'<title>{title}</title>')
        html_parts.append('<style>')
        html_parts.append('body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }')
        html_parts.append('.container { background-color: white; padding: 30px; border-radius: 8px; }')
        html_parts.append('h1 { color: #333; text-align: center; margin-bottom: 30px; }')
        html_parts.append('table { width: 100%; border-collapse: collapse; margin: 20px 0; }')
        html_parts.append('th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }')
        html_parts.append('th { background-color: #f8f9fa; font-weight: bold; color: #495057; }')
        html_parts.append('tr:nth-child(even) { background-color: #f8f9fa; }')
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('<div class="container">')
        html_parts.append(f'<h1>{title}</h1>')

        if not data:
            html_parts.append('<p>Нет данных для отображения</p>')
        else:
            html_parts.append('<table>')

            # Headers
            headers = list(data[0].keys())
            html_parts.append('<thead><tr>')
            for header in headers:
                html_parts.append(f'<th>{header}</th>')
            html_parts.append('</tr></thead>')

            # Data rows
            html_parts.append('<tbody>')
            for item in data:
                html_parts.append('<tr>')
                for key in headers:
                    value = item[key]
                    if isinstance(value, (datetime, date)):
                        formatted_value = value.strftime("%d.%m.%Y")
                    elif value is None:
                        formatted_value = ""
                    else:
                        formatted_value = str(value)
                    html_parts.append(f'<td>{formatted_value}</td>')
                html_parts.append('</tr>')
            html_parts.append('</tbody></table>')

        generation_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        html_parts.append(f'<p>Сгенерировано: {generation_time}</p>')
        html_parts.append('</div>')
        html_parts.append('</body>')
        html_parts.append('</html>')

        html_content = '\n'.join(html_parts)

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return html_content


class ProjectExporter(DataExporter):
    """Project-specific data exporter"""

    def export_projects(self, projects, export_format: str, filename: str = None) -> Union[str, bytes]:
        """Export projects data"""
        data = []

        for project in projects:
            project_data = {
                'ID': project.id,
                'Код': getattr(project, 'code', ''),
                'Название': project.name,
                'Описание': project.description or '',
                'Статус': project.status.value if hasattr(project.status, 'value') else str(project.status),
                'Приоритет': getattr(project, 'priority', {}).get('value', '') if hasattr(getattr(project, 'priority', None), 'value') else '',
                'Дата создания': project.created_at,
                'Прогресс (%)': getattr(project, 'progress', 0)
            }
            data.append(project_data)

        return self._export_by_format(data, export_format, filename, "Проекты")

    def _export_by_format(self, data: List[Dict[str, Any]], export_format: str, filename: str = None, title: str = "Отчет") -> str:
        """Export data in specified format"""
        if export_format == ExportFormat.CSV:
            return self.export_to_csv(data, filename)
        elif export_format == ExportFormat.JSON:
            return self.export_to_json(data, filename)
        elif export_format == ExportFormat.HTML:
            return self.export_to_html(data, filename, title)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")


class TaskExporter(DataExporter):
    """Task-specific data exporter"""

    def export_tasks(self, tasks, export_format: str, filename: str = None) -> Union[str, bytes]:
        """Export tasks data"""
        data = []

        for task in tasks:
            task_data = {
                'ID': task.id,
                'Название': task.title,
                'Описание': task.description or '',
                'Статус': task.status.value if hasattr(task.status, 'value') else str(task.status),
                'Приоритет': getattr(task, 'priority', {}).get('value', '') if hasattr(getattr(task, 'priority', None), 'value') else '',
                'Проект': task.project.name if hasattr(task, 'project') and task.project else '',
                'Дата создания': task.created_at,
                'Прогресс (%)': getattr(task, 'progress', 0)
            }
            data.append(task_data)

        return self._export_by_format(data, export_format, filename, "Задачи")

    def _export_by_format(self, data: List[Dict[str, Any]], export_format: str, filename: str = None, title: str = "Отчет") -> str:
        """Export data in specified format"""
        if export_format == ExportFormat.CSV:
            return self.export_to_csv(data, filename)
        elif export_format == ExportFormat.JSON:
            return self.export_to_json(data, filename)
        elif export_format == ExportFormat.HTML:
            return self.export_to_html(data, filename, title)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")


class ExportManager:
    """
    Main export manager
    Основной менеджер экспорта
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_exporter = ProjectExporter()
        self.task_exporter = TaskExporter()
        self.data_exporter = DataExporter()

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.HTML]

    def export_projects(self, projects, export_format: str, filename: str = None) -> str:
        """Export projects list"""
        return self.project_exporter.export_projects(projects, export_format, filename)

    def export_tasks(self, tasks, export_format: str, filename: str = None) -> str:
        """Export tasks list"""
        return self.task_exporter.export_tasks(tasks, export_format, filename)

    def validate_format(self, export_format: str) -> bool:
        """Validate export format"""
        return export_format in self.get_supported_formats()

    def get_format_mime_type(self, export_format: str) -> str:
        """Get MIME type for export format"""
        mime_types = {
            ExportFormat.CSV: 'text/csv',
            ExportFormat.JSON: 'application/json',
            ExportFormat.HTML: 'text/html'
        }
        return mime_types.get(export_format, 'application/octet-stream')
