"""
pages/6_Informasi.py
======================
Halaman "Tentang" — penjelasan singkat mengenai sistem, metodologi,
sumber data, dan keterbatasan yang perlu diketahui pengguna.
"""

import streamlit as st

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar, render_topbar, render_footer, law_disclaimer

st.set_page_config(page_title="TanyaHukum - Informasi", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

render_sidebar(active="Informasi")
render_topbar(
    "Tentang TanyaHukum",
    "Pelajari informasi, cara penggunaan, sumber data, dan teknologi yang digunakan dalam aplikasi."
)

with st.container(border=True):
    st.markdown("### Apa itu TanyaHukum?")
    st.markdown(
        "TanyaHukum merupakan aplikasi berbasis kecerdasan buatan (AI) yang dirancang "
        "untuk membantu pengguna memperoleh informasi mengenai putusan perkara pencurian "
        "di Indonesia. Aplikasi ini menyediakan chatbot interaktif, analisis dokumen "
        "putusan, serta visualisasi statistik untuk memudahkan pengguna memahami isi "
        "putusan pengadilan. Jawaban yang diberikan disusun berdasarkan dokumen putusan "
        "yang tersedia pada basis pengetahuan sehingga informasi yang dihasilkan tetap "
        "mengacu pada sumber data yang digunakan."
    )

with st.container(border=True):
    st.markdown("### Bagaimana Cara Kerja Sistem?")
    st.markdown(
        "Ketika pengguna mengajukan pertanyaan, sistem akan mencari dokumen putusan "
        "pengadilan yang paling relevan dari basis pengetahuan. Informasi yang ditemukan "
        "kemudian digunakan sebagai dasar untuk menyusun jawaban sehingga respons yang "
        "diberikan sesuai dengan konteks putusan. Pada fitur Analisis Putusan, dokumen "
        "yang diunggah akan diproses secara otomatis untuk menghasilkan ringkasan serta "
        "menampilkan informasi penting yang terdapat dalam putusan."
    )

with st.container(border=True):
    st.markdown("### Cara Menggunakan TanyaHukum")
    st.markdown(
        "Setelah berhasil masuk ke dalam aplikasi, pengguna dapat memilih fitur yang "
        "ingin digunakan melalui menu navigasi. Fitur Chatbot digunakan untuk mengajukan "
        "pertanyaan mengenai putusan perkara pencurian, sedangkan fitur Analisis Putusan "
        "digunakan untuk menganalisis dokumen putusan dalam format PDF. Selain itu, "
        "pengguna juga dapat melihat statistik data putusan, riwayat penggunaan, serta "
        "mengelola informasi akun melalui halaman yang tersedia."
    )

with st.container(border=True):
    st.markdown("### Sumber Data")
    st.markdown(
        "Basis pengetahuan aplikasi dibangun dari 2.687 putusan perkara pencurian " 
        "dari Pengadilan Negeri, Pengadilan Tinggi, dan Mahkamah Agung. Seluruh dokumen "
        "berasal dari Direktori Putusan Mahkamah Agung Republik Indonesia dan digunakan "
        "sebagai sumber informasi dalam proses pencarian dokumen maupun penyusunan "
        "jawaban chatbot."
    )

with st.container(border=True):
    st.markdown("### Keterbatasan Sistem")
    st.markdown(
        "Aplikasi ini dirancang khusus untuk menganalisis putusan perkara pencurian yang "
        "tersedia pada basis pengetahuan. Oleh karena itu, jawaban yang diberikan "
        "bergantung pada informasi yang terdapat dalam dokumen tersebut dan mungkin "
        "belum mencakup kasus di luar ruang lingkup data yang tersedia. Selain itu, "
        "hasil analisis dokumen dapat dipengaruhi oleh kualitas berkas PDF yang diunggah, "
        "terutama apabila dokumen merupakan hasil pemindaian dengan kualitas yang kurang baik. "
        "Informasi yang disajikan bertujuan sebagai media pembelajaran dan pencarian informasi, "
        "bukan sebagai pengganti konsultasi maupun pendapat hukum profesional."
    )

st.markdown("### Rujukan Hukum")
with st.container(border=True):
    st.markdown(
        "Informasi hukum yang disajikan dalam aplikasi mengacu pada putusan pengadilan "
        "yang menjadi sumber data pada basis pengetahuan. Seluruh putusan tersebut "
        "diterbitkan sebelum berlakunya Kitab Undang-Undang Hukum Pidana Nasional "
        "(UU Nomor 1 Tahun 2023), sehingga pasal maupun ketentuan hukum yang muncul "
        "mengikuti peraturan yang berlaku pada saat putusan diterbitkan. "
    )

with st.container(border=True):
    st.markdown("### Teknologi yang Digunakan")
    st.markdown(
        "Aplikasi ini dikembangkan menggunakan beberapa teknologi yang saling "
        "terintegrasi. Antarmuka aplikasi dibangun dengan Streamlit, proses autentikasi "
        "dan penyimpanan data dikelola menggunakan Supabase, ekstraksi informasi dari "
        "dokumen dilakukan menggunakan model Named Entity Recognition (NER) berbasis "
        "IndoBERT, pencarian dokumen memanfaatkan FAISS, sedangkan penyusunan jawaban "
        "chatbot didukung oleh model Gemini Flash. Seluruh proses pengembangan sistem "
        "mengikuti metodologi CRISP-DM."
    )

render_footer()
