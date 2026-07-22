"""
components.py
==============
Komponen UI reusable: sidebar navigasi custom & topbar profil,
diselaraskan dengan tema "Kertas Malam".
"""

import streamlit as st
from utils import auth
from utils.theme import get_image_base64

def render_sidebar(active: str):
    logo_justice = get_image_base64("logo.png")
    with st.sidebar:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:8px; padding: 4px 0;">
                <img src="data:image/png;base64,{logo_justice}" style="width:32px; height:32px;" />
                <div>
                    <div style="font-family:'Lora',serif; font-size:19px;
                                color:#E8E2D8; font-weight:600; line-height:1.2;">TanyaHukum</div>
                    <div style="font-family:'Inter',sans-serif; font-size:11px;
                                color:#8A8378; line-height:1.2;">Yurisprudensi Pencurian</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.caption("MENU UTAMA")

        pages = [
            (" Chatbot", "app.py"),
            (" Analisis Putusan", "pages/2_Analisis_Putusan.py"),
            (" Statistik", "pages/3_Statistik.py"),
            (" Riwayat", "pages/4_Riwayat.py"),
            (" Informasi", "pages/6_Informasi.py"),
        ]

        for label, target in pages:
            is_active = active in label
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{label}", use_container_width=True, type=btn_type):
                st.switch_page(target)

        st.divider()
        st.caption("Berbasis Teknologi")
        st.caption("IndoBERT • Gemini Flash 2.5")

def render_topbar(title: str, subtitle: str):
    logged_in, user = auth.require_guard()

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"## {title}")
        st.caption(subtitle)
    with col2:
        if logged_in:
            if st.button(f"👤 {user['full_name'].split()[0]}", key="topbar_profile", use_container_width=True):
                st.switch_page("pages/5_Profil.py")
        else:
            if st.button("Masuk", key="topbar_login", use_container_width=True, type="primary"):
                st.switch_page("pages/0_Login.py")
    st.divider()

def render_chat_bubble(role: str, content: str):
    is_user = role == "user"
    avatar_b64 = get_image_base64("user.png" if is_user else "assistant.png")

    bg_avatar = "var(--border-color)" if is_user else "var(--accent-main)"
    bg_bubble = "var(--bg-card-hover)" if is_user else "var(--bg-card)"
    flex_direction = "row-reverse" if is_user else "row"

    bubble_html = f"""
        <div style="display:flex; flex-direction:{flex_direction}; align-items:flex-start;
                    gap:10px; margin-bottom:14px;">
            <div style="width:36px; height:36px; border-radius:50%; background:{bg_avatar};
                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <img src="data:image/png;base64,{avatar_b64}" style="width:20px; height:20px;" />
            </div>
            <div style="background:{bg_bubble}; border:1px solid var(--border-color);
                        border-radius:14px; padding:12px 16px;
                        color:var(--text-main); font-family:'Inter',sans-serif;
                        font-size:15px; line-height:1.5;">
                {content}
            </div>
        </div>
    """

    if is_user:
        _, col = st.columns([1, 2])
        with col:
            st.markdown(bubble_html, unsafe_allow_html=True)
    else:
        col, _ = st.columns([3, 1])
        with col:
            st.markdown(bubble_html, unsafe_allow_html=True)

def law_disclaimer():
    st.caption(
        "⚠️ Sistem ini menggunakan basis pengetahuan yang bersumber dari putusan "
        "pengadilan historis. Referensi pasal yang ditampilkan masih mengikuti ketentuan "
        "hukum yang berlaku pada saat putusan tersebut diterbitkan dan belum mengacu "
        "pada KUHP Nasional (UU Nomor 1 Tahun 2023). "
    )
