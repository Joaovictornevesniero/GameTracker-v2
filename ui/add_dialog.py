import os

from PySide6.QtWidgets import (QComboBox, QDialog, QFileDialog, QHBoxLayout, QInputDialog,
                               QLineEdit, QPushButton, QVBoxLayout, QWidget)

import db
import rom
from ui.common import label

PLATFORMS = ['PC', 'Steam', 'Epic', 'GOG', 'Emulador']


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Adicionar jogo')
        self.setMinimumWidth(500)
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 24, 26, 22)
        v.setSpacing(6)

        v.addWidget(label('Adicionar jogo', 'h1'))
        v.addWidget(label('Abra o jogo (ou o emulador com a ROM/ISO carregada) e clique em detectar '
                          'para preencher os campos.', 'muted', wrap=True))
        detect = QPushButton('Detectar jogo aberto')
        detect.clicked.connect(self.detect)
        v.addSpacing(4)
        v.addWidget(detect)

        self.name = QLineEdit()
        self.platform = QComboBox()
        self.platform.setEditable(True)
        self.platform.addItems(PLATFORMS)
        self.exe = QLineEdit()
        self.exe.setPlaceholderText('ex: eldenring.exe ou mgba-qt.exe')
        self.rom = QLineEdit()
        self.rom.setPlaceholderText('opcional: nome da ROM/ISO ou trecho do título')

        self.field('Nome', self.name, v)
        self.field('Plataforma', self.platform, v)
        self.field('Executável (.exe)', self.with_button(self.exe, self.browse_exe), v)
        self.field('ROM / ISO (só para emuladores)', self.with_button(self.rom, self.browse_rom), v)
        v.addWidget(label('Serve para separar jogos do mesmo emulador. Se o emulador mostra FPS no '
                          'título da janela, use só um trecho fixo (o nome do jogo).', 'muted', wrap=True))

        self.msg = label('', 'error', wrap=True)
        v.addSpacing(6)
        v.addWidget(self.msg)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton('Cancelar')
        cancel.clicked.connect(self.reject)
        save = QPushButton('Salvar')
        save.setObjectName('primary')
        save.clicked.connect(self.save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        v.addLayout(buttons)

    @staticmethod
    def field(caption, widget, layout):
        layout.addSpacing(8)
        layout.addWidget(label(caption, 'muted'))
        layout.addWidget(widget)

    def with_button(self, edit, slot):
        """Campo de texto + botão 'Procurar' lado a lado."""
        box = QWidget()
        h = QHBoxLayout(box)
        h.setContentsMargins(0, 0, 0, 0)
        btn = QPushButton('Procurar')
        btn.clicked.connect(slot)
        h.addWidget(edit, 1)
        h.addWidget(btn)
        return box

    def browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecionar executável', '', 'Executável (*.exe)')
        if path:
            self.exe.setText(os.path.basename(path))

    def browse_rom(self):
        exts = ' '.join('*' + e for e in sorted(rom.ROM_EXT))
        path, _ = QFileDialog.getOpenFileName(self, 'Selecionar ROM/ISO', '', f'Jogos ({exts});;Todos (*)')
        if path:
            self.rom.setText(os.path.basename(path))
            if not self.name.text():
                self.name.setText(os.path.splitext(os.path.basename(path))[0])

    def detect(self):
        found = rom.running_windows()
        if not found:
            self.msg.setText('Nenhuma janela de programa encontrada.')
            return
        items = [f'{f["exe"]}  —  {f["rom"] or f["title"]}' for f in found]
        item, ok = QInputDialog.getItem(self, 'Detectar jogo', 'Programas abertos:', items, 0, False)
        if not ok:
            return
        f = found[items.index(item)]
        self.exe.setText(f['exe'])
        if f['rom']:
            self.rom.setText(f['rom'])
            self.msg.setText('')
        else:
            self.rom.clear()
            self.msg.setText(f'Título da janela: "{f["title"]}". Se for um emulador, copie um trecho '
                             f'fixo dele para o campo ROM / ISO.')
        if not self.name.text():
            self.name.setText(os.path.splitext(f['rom'])[0] if f['rom'] else os.path.splitext(f['exe'])[0])

    def save(self):
        name, exe = self.name.text().strip(), self.exe.text().strip()
        if not name:
            return self.msg.setText('Dê um nome ao jogo.')
        if not exe.lower().endswith('.exe'):
            return self.msg.setText('Informe o executável (termina em .exe).')
        db.add_game(name, exe, self.rom.text().strip() or None, self.platform.currentText().strip() or 'PC')
        self.accept()
