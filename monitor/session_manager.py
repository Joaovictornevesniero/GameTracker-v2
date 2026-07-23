import time
from datetime import datetime
from database.game_repository import create_session, finish_session
from monitor.afk_detector import is_afk
from monitor.window_focus import is_focused

AFK_THRESHOLD = 180  #180 segundos/3 minutos

class SessionManager:
    def __init__(self, game):
        self.game = game
        self.session_id = None
        self.started_at = None
        self.raw_seconds = 0
        self.afk_seconds = 0
        self.is_active = False
        self.last_tick = None
        self.afk_started_at = None  # momento em que o AFK começou

    def start(self):
        self.session_id = create_session(self.game['id'])
        self.started_at = datetime.now()
        self.last_tick = time.time()
        self.is_active = True
        print(f'Sessão iniciada: {self.game["name"]}')

    def tick(self):
        if not self.is_active:
            return

        now = time.time()
        elapsed = now - self.last_tick
        self.last_tick = now
        self.raw_seconds += elapsed

        usuario_ausente = is_afk(threshold_seconds=10) or not is_focused(self.game['executable'])

        if usuario_ausente:
            if self.afk_started_at is None:
                self.afk_started_at = now  # marca quando o AFK começou
            
            tempo_afk_continuo = now - self.afk_started_at
            
            if tempo_afk_continuo >= AFK_THRESHOLD:
                self.afk_seconds += elapsed  # só desconta após 5 min contínuos
        else:
            self.afk_started_at = None  # voltou, reseta o contador de AFK

    def finish(self):
        if not self.is_active:
            return
        self.is_active = False
        finish_session(self.session_id, int(self.raw_seconds), int(self.afk_seconds))
        print(f'Sessão finalizada: {self.game["name"]} | '
              f'Total: {int(self.raw_seconds)}s | '
              f'AFK: {int(self.afk_seconds)}s | '
              f'Válido: {int(self.raw_seconds - self.afk_seconds)}s')