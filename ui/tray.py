from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QStyle, QApplication
from PySide6.QtGui import QAction
from monitor import startup

class Tray(QSystemTrayIcon):
    def __init__(self, window):
        icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        super().__init__(icon, window)
        self.window = window
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()

        show_action = QAction('Abrir GameTracker', menu)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        self.startup_action = QAction('Iniciar com o Windows', menu)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(startup.is_enabled())
        self.startup_action.triggered.connect(self._toggle_startup)
        menu.addAction(self.startup_action)

        menu.addSeparator()

        quit_action = QAction('Sair', menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setToolTip('GameTracker')

    def _toggle_startup(self, checked):
        if checked:
            startup.enable()
        else:
            startup.disable()

    def _show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()

    def _quit(self):
        QApplication.instance().quit()