import logging
import os
import sys

from PySide6.QtCore import QDir, QLockFile
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import db
from monitor import Monitor
from ui.common import STYLE, app_icon
from ui.main_window import MainWindow


def make_tray(app, window):
    tray = QSystemTrayIcon(app_icon(), app)
    menu = QMenu()

    def show():
        window.show()
        window.raise_()
        window.activateWindow()

    menu.addAction('Abrir GameTracker', show)
    if sys.platform == 'win32':
        import startup
        auto = QAction('Iniciar com o Windows', menu, checkable=True, checked=startup.enabled())
        auto.toggled.connect(startup.set_enabled)
        menu.addSeparator()
        menu.addAction(auto)
    menu.addSeparator()
    menu.addAction('Sair', app.quit)

    tray.setContextMenu(menu)
    tray.setToolTip('GameTracker')
    tray.activated.connect(lambda r: show() if r in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick) else None)
    tray.show()
    tray._menu = menu  # mantém referência
    return tray


def main():
    logging.basicConfig(filename=os.path.join(db.DIR, 'gametracker.log'), level=logging.WARNING,
                        format='%(asctime)s %(levelname)s %(message)s')
    app = QApplication(sys.argv)

    lock = QLockFile(os.path.join(QDir.tempPath(), 'gametracker.lock'))
    if not lock.tryLock(100):  # já existe uma instância rodando
        return 0

    app.setStyleSheet(STYLE)
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)

    db.init()
    monitor = Monitor()
    monitor.start()
    app.aboutToQuit.connect(monitor.stop)  # fecha as sessões abertas ao sair

    window = MainWindow(monitor)
    tray = make_tray(app, window)
    if '--tray' not in sys.argv:
        window.show()
    code = app.exec()
    del tray
    return code


if __name__ == '__main__':
    sys.exit(main())
