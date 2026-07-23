from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import QTimer
from database.game_repository import get_today_seconds_by_game


class GameBlock(QFrame):
    """Bloco com 3 cards para um jogo ativo. Um bloco por jogo."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet('background: transparent;')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_jogando = self._make_card('Jogando agora')
        self.card_sessao  = self._make_card('Tempo da sessão')
        self.card_hoje    = self._make_card('Tempo hoje')

        cards_layout.addWidget(self.card_jogando)
        cards_layout.addWidget(self.card_sessao)
        cards_layout.addWidget(self.card_hoje)

        layout.addLayout(cards_layout)

    def _make_card(self, title):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet('''
            QFrame {
                background: #1e1e2e;
                border-radius: 10px;
                padding: 10px;
            }
        ''')
        inner = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet('color: #888; font-size: 13px;')

        value_label = QLabel('--')
        value_label.setStyleSheet('color: #fff; font-size: 24px; font-weight: bold;')
        value_label.setObjectName('value')

        inner.addWidget(title_label)
        inner.addWidget(value_label)
        return card

    def _val(self, card):
        return card.findChild(QLabel, 'value')

    def update_data(self, game_name, session_seconds, hoje_seconds):
        self._val(self.card_jogando).setText(game_name)
        self._val(self.card_sessao).setText(self._fmt(session_seconds))
        self._val(self.card_hoje).setText(self._fmt(hoje_seconds))

    def clear(self):
        self._val(self.card_jogando).setText('--')
        self._val(self.card_sessao).setText('--')
        self._val(self.card_hoje).setText('--')

    def _fmt(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f'{h:02d}:{m:02d}:{s:02d}'


class Dashboard(QWidget):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._blocks = {}  # game_id -> GameBlock
        self._empty_block = None
        self._build_ui()
        self._start_timer()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel('Dashboard')
        title.setStyleSheet('font-size: 22px; font-weight: bold; color: #fff;')
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        self.content = QWidget()
        self.content.setStyleSheet('background: transparent;')
        self.blocks_layout = QVBoxLayout(self.content)
        self.blocks_layout.setSpacing(20)
        self.blocks_layout.addStretch()

        scroll.setWidget(self.content)
        main_layout.addWidget(scroll)

        # Bloco vazio inicial
        self._show_empty()

    def _show_empty(self):
        if self._empty_block is None:
            self._empty_block = GameBlock()
            self.blocks_layout.insertWidget(0, self._empty_block)

    def _hide_empty(self):
        if self._empty_block is not None:
            self.blocks_layout.removeWidget(self._empty_block)
            self._empty_block.deleteLater()
            self._empty_block = None

    def _start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _update(self):
        active    = self.monitor.active_sessions
        active_ids = set(active.keys())
        block_ids  = set(self._blocks.keys())

        # Remove blocos de jogos que fecharam
        for gid in block_ids - active_ids:
            block = self._blocks.pop(gid)
            self.blocks_layout.removeWidget(block)
            block.deleteLater()

        # Cria blocos para jogos novos
        for gid in active_ids - block_ids:
            block = GameBlock()
            self.blocks_layout.insertWidget(self.blocks_layout.count() - 1, block)
            self._blocks[gid] = block

        # Mostra ou esconde bloco vazio
        if active_ids:
            self._hide_empty()
        else:
            self._show_empty()

        # Atualiza valores
        for gid, block in self._blocks.items():
            session = active[gid]
            hoje = (
                get_today_seconds_by_game(gid)
                + int(session.raw_seconds - session.afk_seconds)
            )
            block.update_data(
                session.game['name'],
                int(session.raw_seconds),
                hoje
            )