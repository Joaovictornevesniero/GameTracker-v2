"""Thread em segundo plano: detecta jogos abertos e registra as sessões."""
import logging
import threading
import time
from dataclasses import dataclass

import db
import rom

INTERVAL = 2      # segundos entre varreduras
SAVE_EVERY = 15   # a cada quanto tempo grava o progresso (um crash perde no máximo isso)


@dataclass
class Session:
    game: dict
    id: int
    seconds: float = 0.0


class Monitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name='monitor')
        self.sessions = {}  # game_id -> Session (substituído por inteiro a cada ciclo: a UI pode ler sem lock)
        self._games = []
        self._reload = True
        self._halt = threading.Event()

    def reload(self):
        """Avisa que a lista de jogos mudou."""
        self._reload = True

    def stop(self):
        self._halt.set()
        if self.is_alive():
            self.join(timeout=5)

    def run(self):
        last = saved = time.monotonic()
        while True:
            now = time.monotonic()
            dt, last = min(now - last, 10), now  # teto: suspensão do PC não vira tempo de jogo
            save = now - saved >= SAVE_EVERY
            if save:
                saved = now
            try:
                self._step(dt, save)
            except Exception:
                logging.exception('erro no monitor')
            if self._halt.wait(INTERVAL):
                break
        for s in self.sessions.values():
            db.save_session(s.id, s.seconds, end=True)

    def _step(self, dt, save):
        if self._reload:
            self._reload = False
            self._games = db.games()

        active = rom.find_active(self._games)
        by_id = {g['id']: g for g in self._games}
        sessions = dict(self.sessions)

        for gid in [g for g in sessions if g not in active]:
            s = sessions.pop(gid)
            db.save_session(s.id, s.seconds, end=True)

        for gid in active:
            s = sessions.get(gid)
            if s is None:
                sessions[gid] = Session(by_id[gid], db.start_session(gid))
            else:
                s.seconds += dt
                if save:
                    db.save_session(s.id, s.seconds)

        self.sessions = sessions
