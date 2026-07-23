import sqlite3
import os
import sys


def _get_base_dir():
    """Retorna a pasta base correta tanto rodando pelo .py quanto pelo .exe."""
    if getattr(sys, 'frozen', False):
        # Rodando como .exe gerado pelo PyInstaller
        return sys._MEIPASS
    # Rodando normalmente como .py
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _get_base_dir()

# O banco fica na pasta onde o .exe está, não dentro dele
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), 'gametracker.db')
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gametracker.db')

SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def connect() -> sqlite3.Connection:
    """
    Abre a conexão com o banco de dados SQLite.

    Returns:
        Conexão configurada com row_factory para acesso por nome de coluna.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Inicializa o banco de dados executando o schema.sql.
    Cria as tabelas se ainda não existirem.
    """
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()

    conn = connect()
    conn.executescript(schema)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('Banco iniciado com sucesso!')