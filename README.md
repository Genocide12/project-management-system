# Project Management System / Система управления проектами

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-success.svg)]()

## Overview / Обзор

**Project Management System** is a comprehensive desktop application built with PyQt6 that provides advanced project and task management capabilities with a modern, user-friendly interface.

**Система управления проектами** - это комплексное настольное приложение, созданное с использованием PyQt6, которое предоставляет расширенные возможности управления проектами и задачами с современным, удобным интерфейсом.

## Features / Возможности

### 🚀 Core Features / Основные возможности
- **Project Management** / **Управление проектами**
  - Create, edit, and organize projects
  - Project templates and categories
  - Project timeline and milestones
  - Resource allocation and budgeting

- **Task Management** / **Управление задачами**
  - Hierarchical task structure
  - Task dependencies and relationships
  - Priority levels and status tracking
  - Time tracking and estimation

- **Team Collaboration** / **Командная работа**
  - User management and roles
  - Team assignment and workload distribution
  - Real-time notifications
  - Activity logging and history

- **Reporting & Analytics** / **Отчетность и аналитика**
  - Comprehensive project reports
  - Performance metrics and KPIs
  - Export to PDF, Excel, and other formats
  - Interactive charts and graphs

### 🎨 User Interface / Пользовательский интерфейс
- Modern Qt6-based GUI
- Dark and light themes
- Customizable layouts
- Multi-language support (English/Russian)
- High-DPI display support

### 💾 Data Management / Управление данными
- SQLite and PostgreSQL support
- Automatic data backup
- Import/Export functionality
- Data encryption and security

## Screenshots / Скриншоты

*Screenshots will be added as development progresses*
*Скриншоты будут добавлены по мере развития проекта*

## Installation / Установка

### Prerequisites / Предварительные требования
- Python 3.8 or higher / Python 3.8 или выше
- pip package manager

### Clone the Repository / Клонирование репозитория
```bash
git clone https://github.com/Genocide12/project-management-system.git
cd project-management-system
```

### Install Dependencies / Установка зависимостей
```bash
pip install -r requirements.txt
```

### Run the Application / Запуск приложения
```bash
python main.py
```

## Project Structure / Структура проекта

```
project-management-system/
├── main.py                 # Application entry point / Точка входа
├── requirements.txt        # Dependencies / Зависимости
├── README.md              # This file / Этот файл
├── LICENSE                # License file / Файл лицензии
├── config/                # Configuration files / Файлы конфигурации
├── app/                   # Main application code / Основной код приложения
│   ├── core/             # Core application logic / Основная логика
│   ├── ui/               # User interface modules / Модули интерфейса
│   ├── database/         # Database models and operations / БД модели и операции
│   ├── utils/            # Utility functions / Вспомогательные функции
│   └── resources/        # Resources (icons, styles, etc.) / Ресурсы
├── tests/                 # Unit tests / Модульные тесты
├── docs/                  # Documentation / Документация
└── scripts/              # Build and deployment scripts / Скрипты сборки
```

## Development / Разработка

### Setting up Development Environment / Настройка среды разработки

1. **Create virtual environment / Создание виртуального окружения:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. **Install development dependencies / Установка зависимостей для разработки:**
```bash
pip install -r requirements.txt
```

3. **Run tests / Запуск тестов:**
```bash
pytest tests/
```

### Code Style / Стиль кода
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use mypy for type checking

```bash
# Format code / Форматирование кода
black .

# Check linting / Проверка линтинга
flake8 .

# Type checking / Проверка типов
mypy .
```

## Configuration / Конфигурация

The application uses YAML configuration files located in the `config/` directory:

- `config/app.yaml` - Main application settings
- `config/database.yaml` - Database configuration
- `config/ui.yaml` - User interface settings

## Database / База данных

The system supports both SQLite (default) and PostgreSQL databases:

### SQLite (Default)
- No additional setup required
- Database file stored locally
- Perfect for single-user installations

### PostgreSQL (Advanced)
- Requires PostgreSQL server
- Supports multiple concurrent users
- Better performance for large datasets

## Features in Development / Возможности в разработке

- [ ] REST API for external integrations
- [ ] Mobile application companion
- [ ] Advanced reporting dashboards
- [ ] Integration with popular tools (Slack, Trello, etc.)
- [ ] Plugin system for extensibility
- [ ] Cloud synchronization

## Contributing / Участие в разработке

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License / Лицензия

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support / Поддержка

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact the developer: [GitHub Profile](https://github.com/Genocide12)

## Changelog / Журнал изменений

### Version 1.0.0 (In Development)
- Initial release
- Basic project and task management
- User interface implementation
- Database integration
- Reporting system

## Acknowledgments / Благодарности

- PyQt6 community for excellent documentation
- Contributors and testers
- Open source libraries used in this project

---

**Made with ❤️ by Genocide12**

*This project is actively developed and maintained. Star ⭐ the repository if you find it useful!*

*Этот проект активно разрабатывается и поддерживается. Поставьте звезду ⭐ репозиторию, если он оказался полезным!*
