from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QFrame, QScrollArea, QComboBox)
from PySide6.QtCore import Qt
from database.game_repository import get_all_games
from database.db import connect


class SessionCard(QFrame):
    def __init__(self, session):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet('''
            QFrame {
                background: #1e1e2e;
                border-radius: 10px;
                padding: 8px;
            }
        ''')
        layout = QHBoxLayout(self)

        date_label = QLabel(session['started_at'][:16].replace('T', ' '))
        date_label.setStyleSheet('color: #888; font-size: 12px;')

        valid = session['valid_seconds']
        time_label = QLabel(self._format(valid))
        time_label.setStyleSheet('color: #fff; font-size: 14px; font-weight: bold;')

        layout.addWidget(date_label)
        layout.addStretch()
        layout.addWidget(time_label)

    def _format(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f'{h:02d}:{m:02d}:{s:02d}'


class History(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel('Histórico')
        title.setStyleSheet('font-size: 22px; font-weight: bold; color: #fff;')
        layout.addWidget(title)

        self.combo = QComboBox()
        self.combo.setStyleSheet('''
            QComboBox {
                background: #1e1e2e;
                color: #fff;
                border: 1px solid #2a2a3e;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1e1e2e;
                color: #fff;
                selection-background-color: #7c3aed;
                selection-color: #fff;
                border: 1px solid #2a2a3e;
                border-radius: 8px;
                padding: 4px;
            }
        ''')
        self.combo.currentIndexChanged.connect(self._load_sessions)
        layout.addWidget(self.combo)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet('background: transparent;')
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()

        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)

        self._load_games()

    def _load_games(self):
        self.games = get_all_games()
        self.combo.clear()
        for game in self.games:
            self.combo.addItem(game['name'], game['id'])

    def _load_sessions(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        game_id = self.combo.currentData()
        if game_id is None:
            return

        conn = connect()
        cursor = conn.execute(
            '''SELECT * FROM sessions
               WHERE game_id = ? AND ended_at IS NOT NULL
               ORDER BY started_at DESC''',
            (game_id,)
        )
        sessions = cursor.fetchall()
        conn.close()

        for session in sessions:
            card = SessionCard(session)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)