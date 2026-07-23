from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QStackedWidget)
from ui.dashboard import Dashboard
from ui.games_list import GamesList
from ui.history import History

class MainWindow(QMainWindow):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.setWindowTitle('GameTracker')
        self.setMinimumSize(800, 600)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet('background: #13131f;')
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_navbar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet('background: #13131f;')

        self.dashboard = Dashboard(self.monitor)
        self.games_list = GamesList(self.monitor)
        self.history = History()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.games_list)
        self.stack.addWidget(self.history)

        layout.addWidget(self.stack)

    def _build_navbar(self):
        navbar = QWidget()
        navbar.setStyleSheet('background: #1e1e2e; border-bottom: 1px solid #2a2a3e;')
        navbar.setFixedHeight(50)

        layout = QHBoxLayout(navbar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(8)

        btn_style = '''
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                padding: 6px 14px;
                font-size: 13px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #2a2a3e; color: #fff; }
        '''

        self.btn_dashboard = QPushButton('Dashboard')
        self.btn_dashboard.setStyleSheet(btn_style)
        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))

        self.btn_games = QPushButton('Jogos')
        self.btn_games.setStyleSheet(btn_style)
        self.btn_games.clicked.connect(lambda: self._navigate(1))

        self.btn_history = QPushButton('Histórico')
        self.btn_history.setStyleSheet(btn_style)
        self.btn_history.clicked.connect(lambda: self._navigate(2))

        title = QPushButton('GameTracker')
        title.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: #7c3aed;
                border: none;
                font-size: 15px;
                font-weight: bold;
            }
        ''')

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_games)
        layout.addWidget(self.btn_history)

        return navbar

    def _navigate(self, index):
        self.stack.setCurrentIndex(index)

    def closeEvent(self, event):
        event.ignore()
        self.hide()