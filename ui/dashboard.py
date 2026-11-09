from datetime import date, timedelta

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout

import db
from ui.common import Page, clock, empty_state, human, label


class Stat(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName('card')
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 14, 18, 14)
        v.setSpacing(2)
        v.addWidget(label(title, 'muted'))
        self.value = label('0s', 'mid')
        v.addWidget(self.value)


class LiveCard(QFrame):
    """Um jogo em execução: tempo da sessão e total de hoje."""

    def __init__(self, session):
        super().__init__()
        self.setObjectName('livecard')
        self.session = session
        g = session.game
        self.base = db.total_seconds(since=date.today(), game_id=g['id'], exclude=[session.id])

        h = QHBoxLayout(self)
        h.setContentsMargins(22, 18, 22, 18)
        h.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(4)
        left.addWidget(label('● JOGANDO AGORA', 'live'))
        left.addWidget(label(g['name'], 'h2'))
        sub = '  ·  '.join(x for x in (g['platform'], g['rom'] or g['executable']) if x)
        left.addWidget(label(sub, 'muted'))
        h.addLayout(left, 1)

        self.clock = label('00:00:00', 'big')
        self.today = label('', 'big')
        for title, value in (('Sessão', self.clock), ('Hoje', self.today)):
            col = QVBoxLayout()
            col.setSpacing(0)
            col.addWidget(label(title, 'muted'))
            col.addWidget(value)
            h.addLayout(col)
        self.refresh()

    def refresh(self):
        self.clock.setText(clock(self.session.seconds))
        self.today.setText(human(self.base + self.session.seconds))


class Dashboard(Page):
    def __init__(self, monitor):
        super().__init__('Dashboard')
        self.monitor = monitor
        self.cards = {}
        self._base = None
        self._tick = 0

        row = QHBoxLayout()
        row.setSpacing(12)
        self.stats = {}
        for key, title in (('today', 'Hoje'), ('week', 'Últimos 7 dias'), ('all', 'Total')):
            self.stats[key] = Stat(title)
            row.addWidget(self.stats[key])
        self.top.addLayout(row)
        self.top.addSpacing(6)
        self.top.addWidget(label('EM EXECUÇÃO', 'section'))

        self.empty = empty_state('Nenhum jogo em execução',
                                 'Abra um jogo cadastrado e ele aparece aqui automaticamente.')
        self.add(self.empty)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(1000)

    def update_view(self):
        sessions = self.monitor.sessions  # dicionário substituído por inteiro pela thread: leitura segura

        for gid in [g for g, c in self.cards.items() if sessions.get(g) is not c.session]:
            card = self.cards.pop(gid)
            card.setParent(None)
            card.deleteLater()
            self._base = None
        for gid, s in sessions.items():
            if gid not in self.cards:
                self.cards[gid] = LiveCard(s)
                self.add(self.cards[gid])
                self._base = None
        self.empty.setVisible(not self.cards)

        self._tick += 1
        if self._base is None or self._tick % 30 == 0:
            ids = [s.id for s in sessions.values()]
            today = date.today()
            self._base = {
                'today': db.total_seconds(since=today, exclude=ids),
                'week': db.total_seconds(since=today - timedelta(days=6), exclude=ids),
                'all': db.total_seconds(exclude=ids),
            }
        live = sum(s.seconds for s in sessions.values())
        for key, stat in self.stats.items():
            stat.value.setText(human(self._base[key] + live))
        for card in self.cards.values():
            card.refresh()
