import psycopg
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation
import streamlit as st
from contextlib import contextmanager
from datetime import datetime, timezone

@contextmanager
def get_connection():
    """
    Membuat koneksi ke database PostgreSQL Supabase.
    """
    conn = psycopg.connect(
        st.secrets["DATABASE_URL"],
        row_factory=dict_row,
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    """
    Tabel sudah dibuat di Supabase.
    Fungsi ini hanya mengecek apakah koneksi berhasil.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")

def create_user(username: str, full_name: str, email: str, age, password_hash: str) -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users
                    (username, full_name, email, age, password_hash, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        username,
                        full_name,
                        email,
                        age,
                        password_hash,
                        datetime.now(timezone.utc),
                    ),
                )
            conn.commit()

        return True

    except UniqueViolation:
        return False

def get_user_by_username(username: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
            )
            return cur.fetchone()

def update_user_profile(
    user_id: int,
    full_name: str = None,
    username: str = None,
    age=None,
    email: str = None,
    password_hash: str = None,
) -> bool:
    fields = []
    values = []

    if full_name is not None:
        fields.append("full_name = %s")
        values.append(full_name)

    if username is not None:
        fields.append("username = %s")
        values.append(username)

    if age is not None:
        fields.append("age = %s")
        values.append(age)

    if email is not None:
        fields.append("email = %s")
        values.append(email)

    if password_hash is not None:
        fields.append("password_hash = %s")
        values.append(password_hash)

    if not fields:
        return False

    values.append(user_id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE users
                    SET {", ".join(fields)}
                    WHERE id = %s
                    """,
                    values,
                )
            conn.commit()

        return True

    except UniqueViolation:
        return False

def delete_user(user_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,),
            )
        conn.commit()

def save_chat(
    user_id: int,
    category: str,
    question: str,
    answer: str,
    sources_json: str = "",
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_history
                (user_id, category, question, answer, sources_json, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    category,
                    question,
                    answer,
                    sources_json,
                    datetime.now(timezone.utc),
                ),
            )

        conn.commit()

def get_chat_history(user_id: int, category: str = None) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:

            if category and category != "Semua":
                cur.execute(
                    """
                    SELECT *
                    FROM chat_history
                    WHERE user_id = %s
                    AND category = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id, category.lower()),
                )
            else:
                cur.execute(
                    """
                    SELECT *
                    FROM chat_history
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )

            return cur.fetchall()

def delete_chat(chat_id: int, user_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM chat_history
                WHERE id = %s
                AND user_id = %s
                """,
                (chat_id, user_id),
            )

        conn.commit()

def delete_all_chat(user_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM chat_history
                WHERE user_id = %s
                """,
                (user_id,),
            )

        conn.commit()