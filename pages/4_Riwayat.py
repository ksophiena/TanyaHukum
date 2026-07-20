"""
pages/4_Riwayat.py
====================
- User yang login  : riwayat permanen dari database SQLite
- Guest (belum login): hanya riwayat sesi saat ini (session_state), hilang saat tab ditutup
"""

import streamlit as st

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar, render_topbar

st.set_page_config(page_title="TanyaHukum - Riwayat", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

render_sidebar(active="Riwayat")
render_topbar("Riwayat Pencarian", "Histori pertanyaan dan analisis")

logged_in, user = auth.require_guard()

tab_labels = ["Semua", "Chatbot", "Analisis"]
selected_tab = st.radio("Filter", tab_labels, horizontal=True, label_visibility="collapsed")

if not logged_in:
    st.warning(
        "Kamu belum masuk — Fitur daftar riwayat hanya dapat diakses jika pengguna telah melakukan Login. "
        " **Masuk** untuk menyimpan riwayat secara permanen."
    )
    if st.button("Masuk sekarang"):
        st.switch_page("pages/0_Login.py")

    guest_history = st.session_state.get("guest_chat_history", [])
    if not guest_history:
        st.caption("Belum ada riwayat pada sesi ini.")
    for item in reversed(guest_history):
        with st.container(border=True):
            st.markdown(f"**{item['question']}**")
            st.caption(f"{item['category'].capitalize()} · sesi ini")

else:
    history = db.get_chat_history(user["id"], category=selected_tab)

    if not history:
        st.caption("Belum ada riwayat tersimpan.")

    else:
        # Tombol hapus semua
        col1, col2 = st.columns([5, 1])

        with col2:
            if st.button(" Hapus Semua"):
                db.delete_all_chat(user["id"])
                st.success("Semua riwayat berhasil dihapus.")
                st.rerun()

        # Daftar riwayat
        for item in history:

            title = item["question"]
            if len(title) > 80:
                title = title[:80] + "..."

            with st.expander(
                f"{title} ({item['created_at'][:16].replace('T', ' ')})"
            ):

                st.markdown("#### Pertanyaan")
                st.write(item["question"])

                st.markdown("#### Jawaban")
                st.write(item["answer"])

                if st.button(" Hapus Riwayat", key=f"del_{item['id']}"):
                    db.delete_chat(item["id"], user["id"])
                    st.success("Riwayat berhasil dihapus.")
                    st.rerun()
