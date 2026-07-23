import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import threading
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.tray import Tray
from database.db import init_db
from monitor.game_monitor import GameMonitor

if __name__ == '__main__':
    init_db()

    monitor = GameMonitor()

    thread = threading.Thread(target=monitor.run, daemon=True)
    thread.start()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(monitor)
    window.show()

    tray = Tray(window)
    tray.show()

    sys.exit(app.exec())