"""
pages/6_Informasi.py
======================
Halaman "Tentang" — penjelasan singkat mengenai sistem, metodologi,
sumber data, dan keterbatasan yang perlu diketahui pengguna.
"""

import streamlit as st

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar, render_topbar, law_disclaimer

st.set_page_config(page_title="TanyaHukum - Tentang", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

render_sidebar(active="Tentang")
render_topbar("Tentang TanyaHukum", "Informasi mengenai sistem, metodologi, dan keterbatasannya")

with st.container(border=True):
    st.markdown("### Apa itu TanyaHukum?")
    st.markdown(
        "TanyaHukum merupakan aplikasi berbasis kecerdasan buatan (AI) yang dirancang untuk membantu "
        "pengguna memahami putusan perkara pencurian di Indonesia melalui chatbot interaktif dan analisis " 
        "putusan pengadilan. Sistem ini memanfaatkan pendekatan Retrieval-Augmented Generation (RAG) " 
        "dengan menggabungkan model Named Entity Recognition (NER) berbasis IndoBERT, pencarian dokumen " 
        "menggunakan FAISS, serta model bahasa generatif Gemini Flash untuk menghasilkan jawaban yang relevan " 
        "berdasarkan putusan pengadilan."
    )

st.markdown("### Bagaimana Cara Kerja Sistem?")

with st.container(border=True):
    st.markdown("**1. Memahami Pertanyaan Pengguna**")
    st.markdown(
        "Pertanyaan yang dimasukkan pengguna terlebih dahulu diproses untuk memahami "
        "konteks dan informasi yang ingin dicari."
    )

with st.container(border=True):
    st.markdown("**2. Mencari Putusan yang Relevan**")
    st.markdown(
        "Sistem melakukan pencarian pada basis pengetahuan menggunakan pendekatan "
        "Retrieval-Augmented Generation (RAG) sehingga putusan pengadilan yang paling "
        "relevan dengan pertanyaan pengguna dapat ditemukan."
    )

with st.container(border=True):
    st.markdown("**3. Menganalisis Informasi Penting**")
    st.markdown(
        "Putusan yang berhasil ditemukan kemudian dianalisis menggunakan model "
        "Named Entity Recognition (NER) untuk mengenali informasi penting, seperti "
        "terdakwa, pasal dakwaan, putusan, pidana, barang bukti, serta faktor "
        "yang memberatkan dan meringankan."
    )

with st.container(border=True):
    st.markdown("**4. Menyusun Jawaban**")
    st.markdown(
        "Informasi hasil pencarian digunakan sebagai konteks bagi model bahasa "
        "generatif untuk menghasilkan jawaban yang relevan serta menyertakan "
        "referensi putusan sebagai dasar penyusunan jawaban."
    )

st.markdown("### Cara Menggunakan TanyaHukum")

with st.container(border=True):
    st.markdown("**1. Pilih Fitur yang Ingin Digunakan**")
    st.markdown(
        "Pilih fitur **Chatbot** untuk mengajukan pertanyaan mengenai putusan "
        "perkara pencurian, atau gunakan fitur **Analisis Putusan** untuk "
        "menganalisis dokumen putusan pengadilan."
    )

with st.container(border=True):
    st.markdown("**2. Masukkan Pertanyaan atau Unggah Dokumen**")
    st.markdown(
        "Pada fitur Chatbot, pengguna cukup mengetikkan pertanyaan. "
        "Pada fitur Analisis Putusan, pengguna mengunggah dokumen putusan "
        "berformat PDF yang ingin dianalisis."
    )

with st.container(border=True):
    st.markdown("**3. Tunggu Proses Analisis**")
    st.markdown(
        "Sistem akan memproses pertanyaan atau dokumen, mencari informasi yang "
        "relevan, kemudian menyusun hasil analisis secara otomatis."
    )

with st.container(border=True):
    st.markdown("**4. Pelajari Hasil Analisis**")
    st.markdown(
        "Pengguna dapat membaca jawaban chatbot beserta referensi putusan yang "
        "digunakan atau melihat hasil ekstraksi entitas dan ringkasan pada fitur "
        "Analisis Putusan."
    )

st.markdown("### Sumber Data")
with st.container(border=True):
    st.markdown(
        "Basis pengetahuan sistem ini dibangun dari 2.687 putusan perkara pencurian yang " 
        "berasal dari Direktori Putusan Mahkamah Agung Republik Indonesia. Seluruh putusan " 
        "merupakan dokumen publik yang tersedia secara terbuka dan digunakan sebagai sumber " 
        "informasi untuk proses pencarian dokumen serta penyusunan jawaban chatbot. "
    )

st.markdown("### Keterbatasan Sistem")
with st.container(border=True):
    st.markdown("""
        1. **Distribusi data belum merata**  
        Sebagian besar putusan pada basis pengetahuan berasal dari wilayah Sulawesi Selatan sehingga data yang digunakan belum sepenuhnya merepresentasikan karakteristik perkara pencurian di seluruh wilayah Indonesia.

        2. **Cakupan data masih terbatas**  
        Basis pengetahuan hanya mencakup putusan pengadilan mengenai tindak pidana pencurian sehingga sistem belum dapat digunakan untuk menganalisis jenis tindak pidana lainnya.

        3. **Jenis entitas yang dikenali masih terbatas**  
        Model Named Entity Recognition (NER) yang dilatih hanya dapat mengenali delapan jenis entitas, yaitu Terdakwa, Pasal Dakwaan, Putusan, Pidana, Barang Bukti, Nomor Putusan, Faktor Memberatkan, dan Faktor Meringankan.

        4. **Kualitas jawaban dipengaruhi oleh basis pengetahuan**  
        Jawaban chatbot dihasilkan berdasarkan informasi yang tersedia pada basis pengetahuan. Apabila informasi yang relevan tidak tersedia atau cakupan data masih terbatas, jawaban yang diberikan juga dapat menjadi kurang lengkap.

        5. **Hasil analisis dokumen dipengaruhi oleh kualitas berkas**  
        Fitur Analisis Putusan memproses dokumen secara *real-time*. Oleh karena itu, format dokumen yang tidak standar maupun hasil pemindaian (OCR) yang kurang baik dapat memengaruhi kualitas ringkasan dan hasil ekstraksi entitas.
        """)

st.markdown("### Rujukan Hukum")
with st.container(border=True):
    st.markdown(
        "Knowledge base pada sistem ini dibangun dari kumpulan putusan pengadilan "
        "historis yang diterbitkan sebelum berlakunya Kitab Undang-Undang Hukum Pidana "
        "Nasional (UU Nomor 1 Tahun 2023). Oleh karena itu, pasal-pasal yang ditampilkan "
        "dalam hasil analisis dan chatbot mengacu pada ketentuan hukum yang berlaku pada "
        "saat putusan tersebut diterbitkan."
    )

st.markdown("### Teknologi yang Digunakan")
with st.container(border=True):
    st.markdown(
        """
- **Named Entity Recognition (NER) & Embedding**: IndoBERT (fine-tuned)
- **Model Generatif**: Gemini Flash 2.5
- **Retrieval**: FAISS (Facebook AI Similarity Search)
- **Antarmuka**: Streamlit
- **Basis Data**: SQLite
- **Metodologi Pengembangan**: CRISP-DM
        """
    )

st.divider()
st.caption(
    "© TanyaHukum. 2026 — Dikembangkan sebagai bagian dari penelitian skripsi "
    "mengenai analisis yurisprudensi perkara pencurian di Indonesia "
    "menggunakan pendekatan Retrieval-Augmented Generation (RAG)."
)
