"""
pages/5_Profil.py
===================
Halaman Profil: tampilan read-only + tombol Edit Profil yang membuka
popup (st.dialog) berisi form ubah data & kata sandi.
"""

import streamlit as st

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar
from datetime import datetime as _dt

st.set_page_config(page_title="TanyaHukum - Profil", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

logged_in, user = auth.require_guard()

if not logged_in:
    st.warning("Kamu perlu masuk untuk mengakses halaman ini.")
    if st.button("Masuk sekarang"):
        st.switch_page("pages/0_Login.py")
    st.stop()

render_sidebar(active="")


@st.dialog("Edit Profil")
def edit_profile_dialog():
    st.caption("Perbarui informasi akun Anda")

    new_full_name = st.text_input("Nama Lengkap", value=user["full_name"])
    new_username = st.text_input("Username", value=user["username"])
    new_age = st.number_input("Umur", min_value=0, max_value=120,
                               value=user["age"] if user["age"] else 0)
    new_email = st.text_input("Email", value=user["email"])

    st.markdown("**Ubah Kata Sandi** _(opsional, kosongkan jika tidak ingin mengubah)_")
    old_password = st.text_input("Kata Sandi Lama", type="password")
    new_password = st.text_input("Kata Sandi Baru", type="password", help="Min. 8 karakter")
    confirm_password = st.text_input("Konfirmasi Kata Sandi Baru", type="password")

    col_cancel, col_save = st.columns(2)
    with col_save:
        if st.button("Simpan perubahan", type="primary", use_container_width=True):
            password_hash = None
            error = None

            if new_password or confirm_password or old_password:
                if not auth.verify_password(old_password, user["password_hash"]):
                    error = "Kata sandi lama tidak sesuai."
                elif len(new_password) < 8:
                    error = "Kata sandi baru minimal 8 karakter."
                elif new_password != confirm_password:
                    error = "Konfirmasi kata sandi tidak cocok."
                else:
                    password_hash = auth.hash_password(new_password)

            if error:
                st.error(error)
            else:
                db.update_user_profile(
                    user_id=user["id"], full_name=new_full_name, username=new_username,
                    age=int(new_age) if new_age else None, email=new_email,
                    password_hash=password_hash,
                )
                st.toast("Perubahan berhasil disimpan!")
                st.session_state.user = db.get_user_by_username(new_username)
                st.rerun()

    with col_cancel:
        if st.button("Batal", use_container_width=True):
            st.rerun()


col_back, col_title, col_edit = st.columns([1, 4, 1])
with col_back:
    if st.button("← Kembali"):
        st.switch_page("app.py")
with col_title:
    st.markdown("## Profil")
with col_edit:
    if st.button(" Edit Profil", use_container_width=True, type="primary"):
        edit_profile_dialog()

st.divider()

with st.container(border=True, key="profile_header_card"):
    st.markdown(f"### {user['full_name']}")
    try:
        joined = _dt.fromisoformat(user["created_at"])
        bulan_id = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        joined_str = f"{joined.day} {bulan_id[joined.month - 1]} {joined.year}"
    except Exception:
        joined_str = "-"
    st.caption(f"Bergabung sejak {joined_str}")

st.markdown("**INFORMASI AKUN**")

info_rows = [
    ("Username", user["username"]),
    ("Email", user["email"]),
    ("Umur", str(user["age"]) if user["age"] else "-"),
]

for label, value in info_rows:
    if label == "Email":
        value_html = f'<a href="mailto:{value}" style="color:#4A9EFF; text-decoration:none;">{value}</a>'
    else:
        value_html = value

    st.markdown(
        f"""
        <div style="padding: 10px 0; border-bottom: 1px solid #35302A;">
            <div style="font-size: 13px; color: #9A9284;">{label}</div>
            <div style="font-size: 16px; color: #E8E2D8; font-weight: 500;">{value_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

with st.container(border=True, key="delete_account_card"):
    st.markdown("#### Hapus Akun")
    st.caption("Semua data dan riwayat akan dihapus permanen")
    if st.button("Hapus Akun", type="secondary"):
        st.session_state.confirm_delete = True

    if st.session_state.get("confirm_delete"):
        st.warning("Yakin ingin menghapus akun ini secara permanen? Tindakan ini tidak bisa dibatalkan.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Ya, hapus akun saya", type="primary"):
                db.delete_user(user["id"])
                auth.logout()
                st.toast("Akun berhasil dihapus.")
                st.session_state.confirm_delete = False
                st.switch_page("app.py")
        with c2:
            if st.button("Batalkan"):
                st.session_state.confirm_delete = False
                st.rerun()

st.divider()
if st.button("Keluar dari akun"):
    auth.logout()
    st.switch_page("app.py")