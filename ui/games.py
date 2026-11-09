from PySide6.QtWidgets import QMessageBox, QPushButton

import db
from ui.add_dialog import AddDialog
from ui.common import Page, empty_state, human, row


class GamesPage(Page):
    def __init__(self, monitor):
        btn = QPushButton('+ Adicionar jogo')
        btn.setObjectName('primary')
        super().__init__('Jogos', btn)
        self.monitor = monitor
        btn.clicked.connect(self.add_game)

    def refresh(self):
        self.clear()
        games = db.games_with_totals()
        if not games:
            self.add(empty_state('Nenhum jogo cadastrado',
                                 'Clique em "+ Adicionar jogo". Para emuladores, informe também a ROM/ISO.'))
            return
        for g in games:
            sub = g['executable'] + (f'  ·  {g["rom"]}' if g['rom'] else '')
            remove = QPushButton('Remover')
            remove.setObjectName('danger')
            remove.clicked.connect(lambda _=False, game=g: self.remove(game))
            n = g['n']
            self.add(row(g['name'], sub, human(g['total']),
                         f'{n} sessão' if n == 1 else f'{n} sessões',
                         chip=g['platform'] or '', action=remove))

    def add_game(self):
        if AddDialog(self).exec():
            self.monitor.reload()
            self.refresh()

    def remove(self, game):
        box = QMessageBox(self)
        box.setWindowTitle('Remover jogo')
        box.setText(f'Remover "{game["name"]}"?')
        box.setInformativeText('O histórico de sessões dele também será apagado.')
        yes = box.addButton('Remover', QMessageBox.DestructiveRole)
        box.addButton('Cancelar', QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() is yes:
            db.delete_game(game['id'])
            self.monitor.reload()
            self.refresh()
