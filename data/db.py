import json
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

        c.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            UNIQUE(user_id, preference_key)
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


def save_user_preference(user_id: int, key: str, value: str):
    """Save a user preference to the database."""
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value)
            VALUES (?, ?, ?)
        """, (user_id, key, value))
        conn.commit()


def get_user_preference(user_id: int, key: str, default: str = None) -> str:
    """Get a user preference from the database."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT preference_value FROM user_preferences
            WHERE user_id = ? AND preference_key = ?
        """, (user_id, key))
        row = cursor.fetchone()
        return row[0] if row else default


def save_tab_order(user_id: int, tab_order: list):
    """Save the sidebar tab order for a user."""
    save_user_preference(user_id, "tab_order", json.dumps(tab_order))


def get_tab_order(user_id: int) -> list:
    """Get the sidebar tab order for a user. Returns None if not set."""
    value = get_user_preference(user_id, "tab_order")
    if value:
        return json.loads(value)
    return None
