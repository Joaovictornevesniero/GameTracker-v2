from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QMainWindow, QPushButton,
                               QStackedWidget, QVBoxLayout, QWidget)

from ui.common import app_icon, label
from ui.dashboard import Dashboard
from ui.games import GamesPage
from ui.history import HistoryPage


class MainWindow(QMainWindow):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.setWindowTitle('GameTracker')
        self.resize(1000, 650)
        self.setMinimumSize(820, 540)

        root = QWidget()
        root.setObjectName('root')
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self.stack = QStackedWidget()
        pages = [('Dashboard', Dashboard(monitor)), ('Jogos', GamesPage(monitor)), ('Histórico', HistoryPage())]

        sidebar = QWidget()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(210)
        v = QVBoxLayout(sidebar)
        v.setContentsMargins(14, 22, 14, 18)
        v.setSpacing(4)

        brand = QHBoxLayout()
        icon = label('')
        icon.setPixmap(app_icon().pixmap(30, 30))
        brand.addWidget(icon)
        brand.addWidget(label('GameTracker', 'h2'))
        brand.addStretch()
        v.addLayout(brand)
        v.addSpacing(22)

        group = QButtonGroup(self)
        for i, (title, page) in enumerate(pages):
            btn = QPushButton(title)
            btn.setObjectName('nav')
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            group.addButton(btn, i)
            v.addWidget(btn)
            self.stack.addWidget(page)
        group.idClicked.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self._shown)

        v.addStretch()
        self.status = label('', 'muted')
        v.addWidget(self.status)

        h.addWidget(sidebar)
        h.addWidget(self.stack, 1)

        timer = QTimer(self)
        timer.timeout.connect(self._status)
        timer.start(1000)
        self._status()

    def _shown(self, i):
        page = self.stack.widget(i)
        if hasattr(page, 'refresh'):
            page.refresh()

    def _status(self):
        n = len(self.monitor.sessions)
        self.status.setText(f'● {n} jogo{"s" if n != 1 else ""} ativo{"s" if n != 1 else ""}' if n
                            else '○ Monitorando…')

    def closeEvent(self, event):  # fechar a janela só esconde; "Sair" fica no ícone da bandeja
        event.ignore()
        self.hide()
