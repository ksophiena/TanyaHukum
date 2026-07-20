"""
app.py
======
Entry point aplikasi TanyaHukum. Halaman ini merangkap sebagai
halaman "Chatbot" (halaman utama saat app dibuka).
"""

import json
import streamlit as st

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar, render_topbar, law_disclaimer, render_chat_bubble
from utils import rag_engine as rag

st.set_page_config(page_title="TanyaHukum - Chatbot", page_icon="⚖️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    [data-testid="stBottom"] > div {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_sidebar(active="Chatbot")
render_topbar("Chatbot", "Selamat datang! Silahkan pilih salah satu contoh pertanyaan atau ketik pertanyaan Anda seputar kasus pencurian")

# Inisialisasi resource RAG 
tokenizer, model, ner_pipeline, kb, embeddings, index = rag.load_resources()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── Contoh pertanyaan (tampil hanya jika chat masih kosong) ────────────
if not st.session_state.chat_messages:
    logged_in, current_user = auth.require_guard()
    greeting_name = current_user["full_name"].split()[0] if logged_in else "Sobat TanyaHukum"

    st.markdown(
        f"""
        <div style="text-align:center; margin: 20px 0 30px 0;">
            <div style="font-family:'Lora',serif; font-size:28px; color:var(--text-main);">
                Halo, {greeting_name}! 👋
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("💡 Mulai percakapan dengan salah satu pertanyaan berikut")

    example_questions = [
        "💬 Bagaimana hakim menerapkan Pasal 363 KUHP dalam perkara pencurian?",
        "💬 Apa saja pertimbangan hakim dalam menjatuhkan pidana pada perkara pencurian?",
        "💬 Bagaimana hakim menerapkan unsur pemberatan dalam putusan pencurian?",
        "💬 Berapa lama pidana penjara yang paling sering dijatuhkan pada putusan?",
    ]

    cols = st.columns(2)
    clicked_example = None
    for i, eq in enumerate(example_questions):
        with cols[i % 2]:
            if st.button(eq, key=f"example_{i}", use_container_width=True):
                clicked_example = eq.replace("💬 ", "")
else:
    clicked_example = None


def _render_sources(sources: list):
    """Tampilkan expander 'Lihat detail sumber' dengan lebar terbatas (bukan full-width)."""
    col_src, _ = st.columns([3, 1])
    with col_src:
        with st.expander("Lihat detail sumber"):
            for src in sources:
                court_display = (src.get("court_name") or "").strip()
                parts = court_display.split()
                if parts and parts[0] in rag.PREFIX_MAP:
                    parts[0] = rag.PREFIX_MAP[parts[0]]
                court_display = " ".join(parts)

                st.markdown(
                    f"**{court_display} ({src['year']})** — Similarity: `{src['similarity']:.4f}`\n\n"
                    f"No. Putusan: {src['decision_num']} · Pasal: {src['charge']} · Hukuman: {src['sentence']}"
                )


# ── Render riwayat chat ──────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    render_chat_bubble(msg["role"], msg["content"])
    if msg.get("sources"):
        _render_sources(msg["sources"])

# ── Input pertanyaan ──────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center; color:#9A9284; font-size:14px; margin-top:4px;'>"
    "Hasil ini hanya sebagai referensi dan bukan pengganti konsultasi hukum.</p>",
    unsafe_allow_html=True,
)
law_disclaimer()

user_input = st.chat_input("Ketik pertanyaan tentang yurisprudensi kasus pencurian...")
question = clicked_example or user_input

if question:
    st.session_state.chat_messages.append({"role": "user", "content": question, "sources": None})
    render_chat_bubble("user", question)

    with st.spinner("Mencari putusan relevan & menyusun jawaban..."):
        result = rag.rag_answer(question, tokenizer, model, kb, index)

    render_chat_bubble("assistant", result["answer"])
    if result["sources"]:
        _render_sources(result["sources"])

    st.session_state.chat_messages.append({
        "role": "assistant", "content": result["answer"], "sources": result["sources"]
    })

    # Simpan ke riwayat permanen HANYA jika user sudah login
    logged_in, user = auth.require_guard()
    if logged_in:
        db.save_chat(
            user_id=user["id"], category="chatbot",
            question=question, answer=result["answer"],
            sources_json=json.dumps(result["sources"], ensure_ascii=False),
        )

    st.rerun()
