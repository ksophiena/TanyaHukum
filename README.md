# TanyaHukum: Chatbot Yurisprudensi Pencurian Berbasis Retrieval-Augmented Generation (RAG)

TanyaHukum merupakan aplikasi chatbot berbasis web yang dikembangkan untuk membantu pengguna memperoleh informasi mengenai yurisprudensi tindak pidana pencurian di Indonesia melalui pertanyaan dalam bahasa alami. Sistem menerapkan pendekatan **Retrieval-Augmented Generation (RAG)** yang mengombinasikan proses pencarian dokumen secara semantik dengan Large Language Model (LLM) sehingga jawaban yang dihasilkan didasarkan pada dokumen putusan pengadilan yang relevan.

Aplikasi memanfaatkan **IndoBERT** untuk proses *Named Entity Recognition (NER)* sekaligus pembentukan embedding, **FAISS** sebagai mesin pencarian dokumen berbasis kemiripan semantik, **Google Gemini Flash 2.5** sebagai Large Language Model (LLM) untuk menghasilkan jawaban, serta **Supabase** sebagai basis data untuk autentikasi pengguna dan penyimpanan riwayat percakapan.

> **Repository ini merupakan implementasi dari penelitian skripsi Program Studi Informatika mengenai penerapan Retrieval-Augmented Generation (RAG) pada chatbot yurisprudensi tindak pidana pencurian di Indonesia.**

---

# Fitur

- Chatbot yurisprudensi tindak pidana pencurian berbasis RAG
- Named Entity Recognition (NER) menggunakan IndoBERT
- Semantic Retrieval menggunakan FAISS
- Generasi jawaban menggunakan Google Gemini Flash 2.5
- Analisis putusan pengadilan
- Visualisasi statistik dataset
- Autentikasi pengguna
- Penyimpanan riwayat percakapan menggunakan Supabase

---

# Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Basis Data | Supabase (PostgreSQL) |
| Named Entity Recognition | IndoBERT |
| Embedding | IndoBERT |
| Semantic Retrieval | FAISS |
| Large Language Model | Google Gemini Flash 2.5 |
| Model Repository | Hugging Face |
| Knowledge Base Repository | Hugging Face |

---

# Instalasi

## 1. Clone repository

```bash
git clone https://github.com/username/TANYAHUKUM.git
cd TANYAHUKUM
```

## 2. Install seluruh dependensi

```bash
pip install -r requirements.txt
```

## 3. Buat file Secrets

Buat file berikut.

```
.streamlit/secrets.toml
```

Isi dengan konfigurasi berikut.

```toml
GEMINI_API_KEY = "your-gemini-api-key"

SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
```

## 4. Jalankan aplikasi

```bash
streamlit run app.py
```

---

# Deployment

Aplikasi dapat dideploy menggunakan **Streamlit Community Cloud**.

1. Push repository ke GitHub.
2. Login ke Streamlit Community Cloud.
3. Buat aplikasi baru.
4. Pilih repository GitHub.
5. Tentukan `app.py` sebagai Main File.
6. Tambahkan seluruh Secrets yang diperlukan pada menu **Settings → Secrets**.
7. Deploy aplikasi.

---

# Sumber Daya Eksternal

Untuk menjaga ukuran repository tetap ringan, model dan knowledge base tidak disimpan secara langsung di repository GitHub. Seluruh sumber daya akan diunduh secara otomatis saat aplikasi dijalankan.

## Hugging Face Model Hub

Model Named Entity Recognition (NER)

```
ksophiena/ner-indobert-pencurian
```

## Hugging Face Dataset Hub

Knowledge Base, Embedding, dan FAISS Index

```
ksophiena/kb-yurisprudensi-pencurian
```

---

# Struktur Proyek

```text
.
├── app.py                         # Halaman utama chatbot
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   ├── config.toml                # Konfigurasi Streamlit
│   └── secrets.toml               # API Key & kredensial (tidak di-commit)
│
├── assets/
│   ├── assistant.png
│   ├── logo.png
│   └── user.png
│
├── pages/
│   ├── 0_Login.py                 # Login dan registrasi pengguna
│   ├── 2_Analisis_Putusan.py      # Analisis putusan pengadilan
│   ├── 3_Statistik.py             # Visualisasi statistik dataset
│   ├── 4_Riwayat.py               # Riwayat percakapan
│   ├── 5_Profil.py                # Profil pengguna
│   └── 6_Informasi.py             # Informasi aplikasi
│
└── utils/
    ├── auth.py                    # Autentikasi pengguna
    ├── chart_helpers.py           # Helper visualisasi statistik
    ├── components.py              # Komponen antarmuka
    ├── database.py                # Koneksi dan operasi Supabase
    ├── rag_engine.py              # Pipeline Retrieval-Augmented Generation
    ├── theme.py                   # Tema aplikasi
    └── validator.py               # Validasi input dan data
```

---

# Catatan

- Model NER, Knowledge Base, Embedding, dan FAISS Index diunduh secara otomatis dari Hugging Face.
- File `.streamlit/secrets.toml` bersifat rahasia dan tidak disertakan dalam repository.
- Aplikasi memerlukan koneksi internet untuk mengakses Hugging Face, Supabase, dan Google Gemini API.

---

# Pengembang

**TanyaHukum** dikembangkan sebagai implementasi penelitian skripsi pada Program Studi Informatika mengenai penerapan **Retrieval-Augmented Generation (RAG)** untuk sistem chatbot yurisprudensi tindak pidana pencurian di Indonesia.
