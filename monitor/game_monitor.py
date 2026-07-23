import time
from monitor.process_watcher import is_running
from monitor.session_manager import SessionManager
from database.game_repository import get_all_games

GAME_RELOAD_INTERVAL = 30  # recarrega a lista de jogos a cada 30 segundos


class GameMonitor:
    def __init__(self):
        self.games = []
        self.active_sessions = {}
        self._last_reload = 0

    def load_games(self):
        self.games = get_all_games()
        self._last_reload = time.time()
        print(f'{len(self.games)} jogo(s) carregado(s)')

    def _should_reload(self):
        return time.time() - self._last_reload >= GAME_RELOAD_INTERVAL

    def run(self):
        self.load_games()
        print('Monitor iniciado... (Ctrl+C para parar)')
        print('-' * 50)

        while True:
            if self._should_reload():
                self.load_games()

            for game in self.games:
                exe = game['executable']
                game_id = game['id']

                if is_running(exe):
                    if game_id not in self.active_sessions:
                        session = SessionManager(game)
                        session.start()
                        self.active_sessions[game_id] = session
                    else:
                        self.active_sessions[game_id].tick()

                else:
                    if game_id in self.active_sessions:
                        self.active_sessions[game_id].finish()
                        del self.active_sessions[game_id]

            time.sleep(1)