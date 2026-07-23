from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                QLabel, QLineEdit, QPushButton, QFileDialog)
from PySide6.QtCore import Qt

class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Adicionar jogo')
        self.setMinimumWidth(400)
        self.setStyleSheet('background: #13131f;')
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel('Adicionar jogo')
        title.setStyleSheet('color: #fff; font-size: 18px; font-weight: bold;')
        layout.addWidget(title)

        layout.addWidget(self._field_label('Nome do jogo'))
        self.name_input = self._input()
        layout.addWidget(self.name_input)

        layout.addWidget(self._field_label('Executável (.exe)'))
        exe_layout = QHBoxLayout()
        self.exe_input = self._input('ex: eldenring.exe')
        browse_btn = QPushButton('Procurar')
        browse_btn.setStyleSheet('''
            QPushButton {
                background: #2a2a3e;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QPushButton:hover { background: #3a3a4e; }
        ''')
        browse_btn.clicked.connect(self._browse_exe)
        exe_layout.addWidget(self.exe_input)
        exe_layout.addWidget(browse_btn)
        layout.addLayout(exe_layout)

        layout.addWidget(self._field_label('Plataforma'))
        self.platform_input = self._input('ex: Steam, Epic, PC')
        layout.addWidget(self.platform_input)

        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #f87171; font-size: 12px;')
        layout.addWidget(self.error_label)

        buttons = QHBoxLayout()
        cancel_btn = QPushButton('Cancelar')
        cancel_btn.setStyleSheet('''
            QPushButton {
                background: #2a2a3e;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover { background: #3a3a4e; }
        ''')
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton('Salvar')
        save_btn.setStyleSheet('''
            QPushButton {
                background: #7c3aed;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover { background: #6d28d9; }
        ''')
        save_btn.clicked.connect(self._save)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def _field_label(self, text):
        label = QLabel(text)
        label.setStyleSheet('color: #888; font-size: 13px;')
        return label

    def _input(self, placeholder=''):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet('''
            QLineEdit {
                background: #1e1e2e;
                color: #fff;
                border: 1px solid #2a2a3e;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #7c3aed; }
        ''')
        return field

    def _browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecionar executável', '', 'Executável (*.exe)')
        if path:
            exe_name = path.split('/')[-1]
            self.exe_input.setText(exe_name)

    def _save(self):
        name = self.name_input.text().strip()
        exe = self.exe_input.text().strip()
        platform = self.platform_input.text().strip() or 'PC'

        if not name:
            self.error_label.setText('Nome é obrigatório.')
            return
        if not exe:
            self.error_label.setText('Executável é obrigatório.')
            return
        if not exe.endswith('.exe'):
            self.error_label.setText('Executável deve terminar com .exe')
            return

        from database.db import connect
        conn = connect()
        conn.execute(
            'INSERT INTO games (name, executable, platform) VALUES (?, ?, ?)',
            (name, exe, platform)
        )
        conn.commit()
        conn.close()
        self.accept()