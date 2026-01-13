import sqlite3
from pathlib import Path

DB_PATH = Path("barber.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def _try_add_column(conn: sqlite3.Connection, table: str, col_def: str):
    # SQLite doesn't support IF NOT EXISTS for columns; do best-effort.
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
        conn.commit()
    except sqlite3.OperationalError:
        # column probably exists
        pass


def init_db():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            no_show_count INTEGER DEFAULT 0
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            duration_minutes INTEGER NOT NULL,
            buffer_minutes INTEGER DEFAULT 0
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            paid INTEGER DEFAULT 0,
            payment_method TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        )
        """)

        conn.commit()

        # best-effort columns for older DBs
        _try_add_column(conn, "clients", "notes TEXT DEFAULT ''")
        _try_add_column(conn, "clients", "no_show_count INTEGER DEFAULT 0")

        _try_add_column(conn, "services", "buffer_minutes INTEGER DEFAULT 0")

        _try_add_column(conn, "appointments", "paid INTEGER DEFAULT 0")
        _try_add_column(conn, "appointments", "payment_method TEXT DEFAULT ''")
        _try_add_column(conn, "appointments", "notes TEXT DEFAULT ''")
