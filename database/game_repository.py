from database.db import connect
from datetime import datetime, date


def get_all_games():
    conn = connect()
    games = conn.execute('SELECT * FROM games').fetchall()
    conn.close()
    return games


def get_game_by_exe(exe_name):
    conn = connect()
    game = conn.execute(
        'SELECT * FROM games WHERE LOWER(executable) = ?',
        (exe_name.lower(),)
    ).fetchone()
    conn.close()
    return game


def create_session(game_id):
    conn = connect()
    conn.execute(
        'INSERT INTO sessions (game_id, started_at) VALUES (?, ?)',
        (game_id, datetime.now())
    )
    conn.commit()

    session_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return session_id


def finish_session(session_id, raw_seconds, afk_seconds):
    valid_seconds = raw_seconds - afk_seconds

    conn = connect()
    conn.execute(
        '''UPDATE sessions
           SET ended_at      = ?,
               raw_seconds   = ?,
               afk_seconds   = ?,
               valid_seconds = ?
           WHERE id = ?''',
        (datetime.now(), raw_seconds, afk_seconds, valid_seconds, session_id)
    )
    conn.commit()
    conn.close()


def get_today_seconds():
    conn = connect()
    result = conn.execute(
        '''SELECT COALESCE(SUM(valid_seconds), 0) AS total
           FROM sessions
           WHERE DATE(started_at) = ?
             AND ended_at IS NOT NULL''',
        (str(date.today()),)
    ).fetchone()
    conn.close()
    return result['total']

def get_today_seconds_by_game(game_id: int) -> int:
    """
    Retorna o total de segundos válidos jogados hoje para um jogo específico.
    Ignora a sessão atual (ended_at IS NOT NULL) — ela é somada no dashboard em tempo real.

    Args:
        game_id: ID do jogo a filtrar.

    Returns:
        Total de segundos jogados hoje nesse jogo. Retorna 0 se não houver sessões.
    """
    conn = connect()
    result = conn.execute(
        '''SELECT COALESCE(SUM(valid_seconds), 0) AS total
           FROM sessions
           WHERE game_id = ?
             AND DATE(started_at) = ?
             AND ended_at IS NOT NULL''',
        (game_id, str(date.today()))
    ).fetchone()
    conn.close()
    return result['total']