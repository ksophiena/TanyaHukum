"""
pages/0_Login.py
=================
Halaman Login/Signup — split panel: kiri branding (custom HTML/CSS),
kanan form native Streamlit. Login bersifat opsional.
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.theme import get_image_base64
from utils import auth, database as db
from utils.theme import apply_theme

db.init_db()
auth.init_session_state()
apply_theme()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="TanyaHukum - Masuk", page_icon="⚖️", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    section[data-testid='stSidebar'] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.logged_in:
    st.success(f"Kamu sudah masuk sebagai {st.session_state.user['full_name']}.")
    if st.button("Kembali ke Chatbot"):
        st.switch_page("app.py")
    st.stop()

st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.15], gap="large")

with col_left:
    logo_justice = get_image_base64("logo.png")
    
    badge = lambda t: f"""<span style="font-size:11px;padding:4px 12px;border-radius:6px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);
        color:rgba(243,231,211,0.75);letter-spacing:0.02em;">{t}</span>"""
    
    item = lambda t, d: f"""<div style="display:flex;gap:12px;align-items:flex-start;">
        <div style="width:3px;height:36px;background:#C4956A;border-radius:2px;flex-shrink:0;margin-top:2px;"></div>
        <div><div style="font-size:14px;font-weight:600;">{t}</div>
        <div style="font-size:13px;opacity:.70;line-height:1.45;">{d}</div></div></div>"""

    components.html(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lora:wght@600&family=Inter:wght@400;500&family=IBM+Plex+Mono&display=swap');
            html, body {{ margin:0; padding:0; background:#1A1613; }}
        </style>
        <div style="background:linear-gradient(160deg,#4A382D 0%,#181513 100%);height:520px;
            border-radius:16px;padding:40px;display:flex;flex-direction:column;color:#F3E7D3;
            box-sizing:border-box;font-family:'Inter',sans-serif;border-left:4px solid #C4956A;">

            <img src="data:image/png;base64,{logo_justice}" style="width:52px;margin-bottom:18px;" />

            <div style="font-family:'Lora',serif;font-size:32px;font-weight:600;margin-bottom:8px;">TanyaHukum</div>
            <div style="font-size:15px;opacity:0.85;line-height:1.5;max-width:320px;margin-bottom:32px;">
                Memahami putusan pengadilan menjadi lebih mudah dengan asisten hukum berbasis AI.
            </div>

            <div style="display:flex;flex-direction:column;gap:14px;">
                {item("Chatbot Yurisprudensi", "Tanya jawab seputar putusan pencurian secara instan.")}
                {item("Analisis Putusan Otomatis", "Ekstraksi entitas penting dari dokumen putusan pengadilan.")}
                {item("Statistik Menyeluruh", "Statistik yang dihitung dari keseluruhan basis data putusan.")}
            </div>

            <div style="margin-top:auto;padding-top:20px;border-top:1px solid rgba(243,231,211,.15);">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;opacity:.85;margin-bottom:10px;">
                    2.687 Putusan Pengadilan
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    {badge("IndoBERT")} {badge("Gemini Flash 2.5")} {badge("FAISS")}
                </div>
            </div>

        </div>
    """, height=520)

with col_right:
    tab_login, tab_signup = st.tabs(["Masuk", "Daftar"])

    with tab_login:
        st.subheader("Masuk ke akun Anda")
        st.caption("Gunakan username dan kata sandi Anda")

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Kata Sandi", type="password", key="login_password")

        if st.button("Masuk", type="primary", use_container_width=True, key="btn_login"):
            success, error = auth.login(login_username, login_password)
            if success:
                st.success("Berhasil masuk!")
                st.switch_page("app.py")
            else:
                st.error(error)

        st.caption("Belum punya akun? Gunakan tab **Daftar** di atas.")

    with tab_signup:
        st.subheader("Buat akun baru")
        st.caption("Isi data berikut untuk mendaftar")

        c1, c2 = st.columns(2)
        with c1:
            signup_name = st.text_input("Nama Lengkap", key="signup_name")
            signup_username = st.text_input("Username", key="signup_username")
        with c2:
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Kata Sandi", type="password", key="signup_password",
                                             help="Minimal 8 karakter")

        if st.button("Daftar", type="primary", use_container_width=True, key="btn_signup"):
            success, error = auth.signup(signup_name, signup_username, signup_email, signup_password)
            if success:
                st.session_state.signup_name = ""
                st.session_state.signup_username = ""
                st.session_state.signup_email = ""
                st.session_state.signup_password = ""
            
                st.toast("Akun berhasil dibuat!")
            
                st.rerun()
            else:
                st.error(error)

        st.caption("Sudah punya akun? Gunakan tab **Masuk** di atas.")

st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
if st.button("← Lanjutkan tanpa masuk (mode tamu)"):
    st.switch_page("app.py")
