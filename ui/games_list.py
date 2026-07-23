from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QScrollArea,
                                QFrame, QMessageBox)
from PySide6.QtCore import Qt


class GameCard(QFrame):
    def __init__(self, game, on_delete):
        super().__init__()
        self.game = game
        self.on_delete = on_delete
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet('''
            QFrame {
                background: #1e1e2e;
                border-radius: 10px;
                padding: 8px;
            }
        ''')
        layout = QHBoxLayout(self)

        name_label = QLabel(game['name'])
        name_label.setStyleSheet('color: #fff; font-size: 15px; font-weight: bold;')

        exe_label = QLabel(game['executable'])
        exe_label.setStyleSheet('color: #888; font-size: 12px;')

        info_layout = QVBoxLayout()
        info_layout.addWidget(name_label)
        info_layout.addWidget(exe_label)

        delete_btn = QPushButton('Remover')
        delete_btn.setStyleSheet('''
            QPushButton {
                background: #3a1a1a;
                color: #f87171;
                border: 1px solid #7f1d1d;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #7f1d1d;
                color: #fff;
            }
        ''')
        delete_btn.clicked.connect(self._confirm_delete)

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(delete_btn)

    def _confirm_delete(self):
        msg = QMessageBox()
        msg.setWindowTitle('Remover jogo')
        msg.setText(f'Remover "{self.game["name"]}"?')
        msg.setInformativeText('O histórico de sessões também será apagado.')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText('Remover')
        msg.button(QMessageBox.Cancel).setText('Cancelar')
        msg.setStyleSheet('''
            QMessageBox {
                background: #13131f;
                color: #fff;
            }
            QLabel {
                color: #fff;
                font-size: 13px;
            }
            QPushButton {
                background: #2a2a3e;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover { background: #3a3a4e; }
        ''')

        if msg.exec() == QMessageBox.Yes:
            self._delete()

    def _delete(self):
        from database.db import connect
        conn = connect()
        # Deleta as sessões primeiro por causa da foreign key
        conn.execute('DELETE FROM sessions WHERE game_id = ?', (self.game['id'],))
        conn.execute('DELETE FROM games WHERE id = ?', (self.game['id'],))
        conn.commit()
        conn.close()
        self.on_delete()


class GamesList(QWidget):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QHBoxLayout()

        title = QLabel('Jogos')
        title.setStyleSheet('font-size: 22px; font-weight: bold; color: #fff;')

        add_btn = QPushButton('+ Adicionar jogo')
        add_btn.setStyleSheet('''
            QPushButton {
                background: #7c3aed;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover { background: #6d28d9; }
        ''')
        add_btn.clicked.connect(self._open_add_dialog)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

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

        self.refresh()

    def refresh(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from database.game_repository import get_all_games
        games = get_all_games()

        for game in games:
            card = GameCard(game, on_delete=self.refresh)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _open_add_dialog(self):
        from ui.add_game_dialog import AddGameDialog
        dialog = AddGameDialog(self)
        if dialog.exec():
            self.refresh()
            self.monitor.load_games()