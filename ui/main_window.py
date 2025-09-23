from PyQt6 import QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle('Project Management System')
        self.resize(1000, 700)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        self.info = QtWidgets.QLabel('Добро пожаловать! База данных инициализирована.')
        lay.addWidget(self.info)
        self.setCentralWidget(w)
