"""
auth.py
=======
Modul autentikasi sederhana berbasis SQLite + bcrypt.
Login bersifat OPSIONAL — pengguna tetap bisa memakai Chatbot,
Analisis Putusan, dan Statistik tanpa login. Login hanya dibutuhkan
untuk menyimpan & melihat riwayat permanen serta mengubah profil.
"""

import re
import bcrypt
import streamlit as st
from utils import database as db


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def init_session_state():
    """Panggil di awal setiap halaman agar session_state konsisten."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "guest_chat_history" not in st.session_state:
        st.session_state.guest_chat_history = []  # riwayat sementara untuk guest (non-permanen)


def login(username: str, password: str) -> tuple[bool, str]:
    """Return (sukses, pesan_error)."""
    user = db.get_user_by_username(username.strip())
    if not user:
        return False, "Username tidak ditemukan."
    if not verify_password(password, user["password_hash"]):
        return False, "Kata sandi salah."

    st.session_state.logged_in = True
    st.session_state.user = user
    return True, ""


def signup(full_name: str, username: str, email: str, password: str) -> tuple[bool, str]:
    """Return (sukses, pesan_error)."""
    full_name = full_name.strip()
    username = username.strip()
    email = email.strip().lower()

    if not full_name or not username or not email or not password:
        return False, "Semua field wajib diisi."
    if not is_valid_email(email):
        return False, "Format email tidak valid."
    if len(password) < 8:
        return False, "Kata sandi minimal 8 karakter."
    if db.get_user_by_username(username):
        return False, "Username sudah digunakan."

    success = db.create_user(
        username=username,
        full_name=full_name,
        email=email,
        age=None,
        password_hash=hash_password(password),
    )
    if not success:
        return False, "Username atau email sudah terdaftar."
    return True, ""


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None


def require_guard():
    """
    Dipanggil di halaman yang butuh konten publik+privat campuran (mis. Riwayat).
    Tidak memblokir akses, hanya menyediakan flag untuk UI kondisional.
    """
    init_session_state()
    return st.session_state.logged_in, st.session_state.user
