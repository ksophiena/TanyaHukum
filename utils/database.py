import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "tanyahukum.db")


def init_db():
    """Membuat folder & file database beserta tabel-tabelnya jika belum ada."""
    os.makedirs(DB_DIR, exist_ok=True)

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                full_name     TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                age           INTEGER,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                category        TEXT NOT NULL,   -- 'chatbot' atau 'analisis'
                question        TEXT NOT NULL,
                answer          TEXT NOT NULL,
                sources_json    TEXT,            -- disimpan sebagai string JSON
                created_at      TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()


@contextmanager
def get_connection():
    """Context manager untuk koneksi SQLite yang aman (auto-close)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_user(username: str, full_name: str, email: str, age, password_hash: str) -> bool:
    """Menyimpan user baru. Return False jika username/email sudah dipakai."""
    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO users (username, full_name, email, age, password_hash, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, full_name, email, age, password_hash, datetime.now().isoformat()),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None


def update_user_profile(user_id: int, full_name: str = None, username: str = None,
                         age=None, email: str = None, password_hash: str = None):
    fields, values = [], []
    if full_name is not None:
        fields.append("full_name = ?"); values.append(full_name)
    if username is not None:
        fields.append("username = ?"); values.append(username)
    if age is not None:
        fields.append("age = ?"); values.append(age)
    if email is not None:
        fields.append("email = ?"); values.append(email)
    if password_hash is not None:
        fields.append("password_hash = ?"); values.append(password_hash)

    if not fields:
        return

    values.append(user_id)
    with get_connection() as conn:
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()


def delete_user(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

def save_chat(user_id: int, category: str, question: str, answer: str, sources_json: str = ""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO chat_history (user_id, category, question, answer, sources_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, category, question, answer, sources_json, datetime.now().isoformat()),
        )
        conn.commit()


def get_chat_history(user_id: int, category: str = None):
    with get_connection() as conn:
        if category and category != "Semua":
            rows = conn.execute(
                """SELECT * FROM chat_history WHERE user_id = ? AND category = ?
                   ORDER BY created_at DESC""",
                (user_id, category.lower()),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

def delete_chat(chat_id: int, user_id: int):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM chat_history
            WHERE id = ? AND user_id = ?
            """,
            (chat_id, user_id),
        )
        conn.commit()


def delete_all_chat(user_id: int):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM chat_history
            WHERE user_id = ?
            """,
            (user_id,),
        )
        conn.commit()