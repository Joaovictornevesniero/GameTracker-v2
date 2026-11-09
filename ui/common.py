"""Tema, formatação e blocos de interface compartilhados."""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

STYLE = '''
* { color: #e8eaf0; font-family: "Segoe UI", sans-serif; font-size: 13px; }
QMainWindow, QDialog, QMessageBox, QWidget#root { background: #0f1117; }
QWidget#sidebar { background: #12151d; border-right: 1px solid #1d212d; }

QLabel#h1 { font-size: 24px; font-weight: 600; }
QLabel#h2 { font-size: 17px; font-weight: 600; }
QLabel#name { font-size: 14px; font-weight: 600; }
QLabel#section { color: #8b91a3; font-size: 12px; font-weight: 600; }
QLabel#muted { color: #8b91a3; }
QLabel#big { font-size: 30px; font-weight: 600; }
QLabel#mid { font-size: 18px; font-weight: 600; }
QLabel#live { color: #34d399; font-size: 12px; font-weight: 600; }
QLabel#error { color: #f87171; }
QLabel#chip { background: #1f2330; color: #a5abc0; border-radius: 9px; padding: 2px 9px; font-size: 11px; }

QFrame#card { background: #161922; border: 1px solid #222736; border-radius: 12px; }
QFrame#livecard { background: #161922; border: 1px solid #2b2350; border-radius: 12px; }

QPushButton { background: #1f2330; border: none; border-radius: 8px; padding: 9px 16px; }
QPushButton:hover { background: #2a2f42; }
QPushButton#primary { background: #8b5cf6; color: #fff; font-weight: 600; }
QPushButton#primary:hover { background: #7c47f0; }
QPushButton#danger { background: transparent; color: #f87171; padding: 7px 12px; }
QPushButton#danger:hover { background: #2a1a20; }
QPushButton#nav { background: transparent; color: #8b91a3; text-align: left; padding: 10px 14px; font-size: 14px; }
QPushButton#nav:hover { background: #1a1e29; color: #e8eaf0; }
QPushButton#nav:checked { background: #1f2330; color: #fff; font-weight: 600; }

QLineEdit, QComboBox { background: #12151d; border: 1px solid #262b3a; border-radius: 8px; padding: 8px 10px; selection-background-color: #8b5cf6; }
QLineEdit:focus, QComboBox:focus { border-color: #8b5cf6; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView { background: #161922; border: 1px solid #262b3a; selection-background-color: #8b5cf6; outline: 0; }

QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
QScrollBar::handle:vertical { background: #2a3042; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background: #161922; border: 1px solid #262b3a; padding: 4px; }
QMenu::item { padding: 7px 20px; border-radius: 6px; }
QMenu::item:selected { background: #8b5cf6; }
QMenu::separator { height: 1px; background: #262b3a; margin: 4px 6px; }
'''


def app_icon():
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor('#8b5cf6'))
    p.drawRoundedRect(4, 4, 56, 56, 16, 16)
    p.setPen(QColor('white'))
    p.setFont(QFont('Segoe UI', 28, QFont.Bold))
    p.drawText(pm.rect(), Qt.AlignCenter, 'G')
    p.end()
    return QIcon(pm)


def clock(seconds):
    h, rest = divmod(int(seconds), 3600)
    m, s = divmod(rest, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def human(seconds):
    seconds = int(seconds)
    h, m = divmod(seconds // 60, 60)
    return f'{h}h {m:02d}min' if h else f'{m}min' if m else f'{seconds}s'


def fmt_date(text):
    try:
        return datetime.fromisoformat(text[:19]).strftime('%d/%m/%Y  %H:%M')
    except (ValueError, TypeError):
        return text or ''


def label(text, name=None, wrap=False, align=None):
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    if wrap:
        w.setWordWrap(True)
    if align:
        w.setAlignment(align)
    return w


def empty_state(title, hint):
    f = QFrame()
    f.setObjectName('card')
    v = QVBoxLayout(f)
    v.setContentsMargins(24, 30, 24, 30)
    v.setSpacing(6)
    v.addWidget(label(title, 'h2', align=Qt.AlignCenter))
    v.addWidget(label(hint, 'muted', wrap=True, align=Qt.AlignCenter))
    return f


def row(title, sub='', value='', value_sub='', chip='', action=None):
    """Linha de lista: título (+ chip) e subtítulo à esquerda, valor à direita, botão opcional."""
    f = QFrame()
    f.setObjectName('card')
    h = QHBoxLayout(f)
    h.setContentsMargins(18, 14, 18, 14)
    h.setSpacing(16)

    left = QVBoxLayout()
    left.setSpacing(3)
    top = QHBoxLayout()
    top.setSpacing(8)
    top.addWidget(label(title, 'name'))
    if chip:
        top.addWidget(label(chip, 'chip'))
    top.addStretch()
    left.addLayout(top)
    if sub:
        left.addWidget(label(sub, 'muted'))
    h.addLayout(left, 1)

    right = QVBoxLayout()
    right.setSpacing(2)
    right.addWidget(label(value, 'mid', align=Qt.AlignRight))
    if value_sub:
        right.addWidget(label(value_sub, 'muted', align=Qt.AlignRight))
    h.addLayout(right)
    if action:
        h.addWidget(action)
    return f


class Page(QWidget):
    """Título (+ ação à direita), área de extras (self.top) e lista rolável (self.add / self.clear)."""

    def __init__(self, title, action=None):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(32, 28, 32, 20)
        v.setSpacing(16)

        head = QHBoxLayout()
        head.addWidget(label(title, 'h1'))
        head.addStretch()
        if action:
            head.addWidget(action)
        v.addLayout(head)

        self.top = QVBoxLayout()
        self.top.setSpacing(12)
        v.addLayout(self.top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        self.items = QVBoxLayout(body)
        self.items.setContentsMargins(0, 0, 8, 0)
        self.items.setSpacing(10)
        self.items.addStretch()
        scroll.setWidget(body)
        v.addWidget(scroll, 1)

    def add(self, widget):
        self.items.insertWidget(self.items.count() - 1, widget)

    def clear(self):
        while self.items.count() > 1:
            w = self.items.takeAt(0).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
