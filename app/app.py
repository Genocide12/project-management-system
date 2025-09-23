import sys
from PyQt6 import QtWidgets
from app.config import Settings
from app.logging_conf import configure_logging
from app.db.connection import Database
from ui.main_window import MainWindow
from utils.settings import AppSettings

class ProjectApp(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setOrganizationName('Genocide12')
        self.setApplicationName('Project Management System')
        self.settings = AppSettings()
        self.cfg = Settings.load()
        configure_logging(self.cfg)
        self.db = Database(self.cfg.database_url)
        self.db.ensure_initialized()
        self.window = MainWindow(self)
    def run(self):
        self.window.show()
        return self.exec()
