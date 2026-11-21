import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("bot_syria.db")


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        isolation_level=None,
    )
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                code_verified INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT,
                reward INTEGER NOT NULL DEFAULT 0,
                seats INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                telegram_id INTEGER NOT NULL,
                proof TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                method TEXT NOT NULL,
                address TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)

        conn.commit()


def get_user(telegram_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ).fetchone()


def create_user(telegram_id, first_name=None, username=None):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO users
            (telegram_id, first_name, username)
            VALUES (?, ?, ?)
        """, (telegram_id, first_name, username))
        conn.commit()


def is_code_verified(telegram_id):
    user = get_user(telegram_id)
    return bool(user and user["code_verified"])


def set_code_verified(telegram_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET code_verified = 1 WHERE telegram_id = ?",
            (telegram_id,)
        )
        conn.commit()
