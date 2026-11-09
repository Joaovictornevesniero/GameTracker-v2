"""Banco SQLite: schema, migração do banco antigo e consultas."""
import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime

# Fica ao lado do .exe (empacotado) ou na raiz do projeto (rodando pelo .py)
if getattr(sys, 'frozen', False):
    DIR = os.path.dirname(sys.executable)
else:
    DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, 'gametracker.db')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS games (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    executable TEXT NOT NULL,
    rom        TEXT,
    platform   TEXT DEFAULT 'PC',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id    INTEGER NOT NULL REFERENCES games(id),
    started_at TEXT NOT NULL,
    ended_at   TEXT,
    seconds    INTEGER NOT NULL DEFAULT 0
);
'''


def connect():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def _now():
    return datetime.now().isoformat(sep=' ', timespec='seconds')


def _all(sql, args=()):
    with closing(connect()) as c:
        return [dict(r) for r in c.execute(sql, args)]


def _exec(sql, args=()):
    with closing(connect()) as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def _migrate(c):
    """Traz um banco da versão antiga (com AFK) para o schema atual, sem perder histórico."""
    games = {r[1] for r in c.execute('PRAGMA table_info(games)')}
    if 'rom' not in games:
        c.execute('ALTER TABLE games ADD COLUMN rom TEXT')

    sess = {r[1] for r in c.execute('PRAGMA table_info(sessions)')}
    if 'seconds' not in sess and 'valid_seconds' in sess:
        c.execute('ALTER TABLE sessions RENAME COLUMN valid_seconds TO seconds')
    for col in ('raw_seconds', 'afk_seconds'):
        if col in sess:
            try:
                c.execute(f'ALTER TABLE sessions DROP COLUMN {col}')
            except sqlite3.OperationalError:
                pass  # SQLite antigo: a coluna sobra, mas é inofensiva


def init():
    with closing(connect()) as c:
        c.executescript(SCHEMA)
        _migrate(c)
        # Sessões que ficaram abertas (crash, PC desligado): fecha com o tempo já salvo
        c.execute("UPDATE sessions SET ended_at = datetime(started_at, '+' || COALESCE(seconds, 0) || ' seconds') "
                  "WHERE ended_at IS NULL")
        c.commit()


# ---------- jogos ----------

def games():
    return _all('SELECT * FROM games')


def games_with_totals():
    return _all('''
        SELECT g.*, COALESCE(SUM(s.seconds), 0) AS total, COUNT(s.id) AS n, MAX(s.started_at) AS last
        FROM games g LEFT JOIN sessions s ON s.game_id = g.id
        GROUP BY g.id
        ORDER BY (last IS NULL), last DESC, g.name COLLATE NOCASE''')


def add_game(name, executable, rom, platform):
    return _exec('INSERT INTO games (name, executable, rom, platform) VALUES (?, ?, ?, ?)',
                 (name, executable, rom, platform))


def delete_game(game_id):
    with closing(connect()) as c:
        c.execute('DELETE FROM sessions WHERE game_id = ?', (game_id,))
        c.execute('DELETE FROM games WHERE id = ?', (game_id,))
        c.commit()


# ---------- sessões ----------

def start_session(game_id):
    return _exec('INSERT INTO sessions (game_id, started_at) VALUES (?, ?)', (game_id, _now()))


def save_session(session_id, seconds, end=False):
    _exec('UPDATE sessions SET seconds = ?, ended_at = ? WHERE id = ?',
          (int(seconds), _now() if end else None, session_id))


def total_seconds(since=None, game_id=None, exclude=()):
    """Soma de segundos, opcionalmente desde uma data, de um jogo, ignorando sessões (ids)."""
    sql, args = 'SELECT COALESCE(SUM(seconds), 0) FROM sessions WHERE 1=1', []
    if since:
        sql += ' AND DATE(started_at) >= ?'
        args.append(str(since))
    if game_id:
        sql += ' AND game_id = ?'
        args.append(game_id)
    if exclude:
        sql += f' AND id NOT IN ({",".join("?" * len(exclude))})'
        args += list(exclude)
    with closing(connect()) as c:
        return c.execute(sql, args).fetchone()[0]


def sessions_list(game_id=None):
    sql = ('SELECT s.*, g.name FROM sessions s JOIN games g ON g.id = s.game_id '
           'WHERE s.ended_at IS NOT NULL')
    args = []
    if game_id:
        sql += ' AND s.game_id = ?'
        args.append(game_id)
    return _all(sql + ' ORDER BY s.started_at DESC', args)
