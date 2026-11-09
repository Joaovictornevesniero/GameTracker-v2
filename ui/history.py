from PySide6.QtWidgets import QComboBox

import db
from ui.common import Page, empty_state, fmt_date, human, label, row

MAX_ROWS = 150


class HistoryPage(Page):
    def __init__(self):
        combo = QComboBox()
        combo.setMinimumWidth(240)
        super().__init__('Histórico', combo)
        self.combo = combo
        self.summary = label('', 'muted')
        self.top.addWidget(self.summary)
        combo.currentIndexChanged.connect(self.load)

    def refresh(self):
        current = self.combo.currentData()
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItem('Todos os jogos', None)
        for g in sorted(db.games(), key=lambda g: g['name'].lower()):
            self.combo.addItem(g['name'], g['id'])
        self.combo.setCurrentIndex(self.combo.findData(current) if current is not None else 0)
        if self.combo.currentIndex() < 0:
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self.load()

    def load(self):
        self.clear()
        rows = db.sessions_list(self.combo.currentData())
        n = len(rows)
        self.summary.setText(f'{n} sessão · {human(sum(r["seconds"] or 0 for r in rows))}' if n == 1
                             else f'{n} sessões · {human(sum(r["seconds"] or 0 for r in rows))}')
        if not rows:
            self.add(empty_state('Sem sessões ainda', 'As sessões aparecem aqui quando o jogo é fechado.'))
            return
        for r in rows[:MAX_ROWS]:
            self.add(row(r['name'], fmt_date(r['started_at']), human(r['seconds'] or 0)))
        if n > MAX_ROWS:
            self.add(label(f'Mostrando as {MAX_ROWS} mais recentes.', 'muted'))
