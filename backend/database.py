import sqlite3
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_df(sql: str, params: tuple = ()):
    """Execute SQL and return list of dicts."""
    with get_db() as conn:
        cur = conn.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def query_one(sql: str, params: tuple = ()):
    """Execute SQL and return first row as dict, or None."""
    rows = query_df(sql, params)
    return rows[0] if rows else None


def db_exists() -> bool:
    return DB_PATH.exists()
