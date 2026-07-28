# TanyaHukum: Chatbot Yurisprudensi Pencurian Berbasis Retrieval-Augmented Generation (RAG)

TanyaHukum merupakan aplikasi chatbot berbasis web yang dirancang untuk membantu pengguna memperoleh informasi mengenai yurisprudensi tindak pidana pencurian di Indonesia melalui pertanyaan dalam bahasa alami. Sistem menerapkan pendekatan **Retrieval-Augmented Generation (RAG)** yang mengombinasikan proses pencarian dokumen secara semantik dengan Large Language Model (LLM) untuk menghasilkan jawaban yang kontekstual berdasarkan putusan pengadilan.

Aplikasi memanfaatkan model **IndoBERT** untuk proses *Named Entity Recognition (NER)*, **FAISS** untuk pencarian dokumen berdasarkan kemiripan semantik, **Google Gemini Flash 2.5** sebagai model pembangkit jawaban, serta **Supabase** sebagai basis data untuk autentikasi pengguna dan penyimpanan riwayat percakapan.

---

## Fitur

- Chatbot tanya jawab yurisprudensi tindak pidana pencurian
- Retrieval-Augmented Generation (RAG)
- Named Entity Recognition (NER) menggunakan IndoBERT
- Pencarian dokumen berbasis kemiripan semantik menggunakan FAISS
- Analisis putusan pengadilan
- Visualisasi statistik dataset
- Autentikasi pengguna
- Penyimpanan riwayat percakapan menggunakan Supabase

---

## Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Basis Data | Supabase (PostgreSQL) |
| Model NER | IndoBERT |
| Vector Retrieval | FAISS |
| Large Language Model | Google Gemini Flash 2.5 |

---

## Instalasi

Instal seluruh dependensi yang diperlukan.

```bash
pip install -r requirements.txt
```

Buat file berikut:

```text
.streamlit/secrets.toml
```

Contoh konfigurasi:

```toml
GEMINI_API_KEY = "your-gemini-api-key"

SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
```

Jalankan aplikasi menggunakan perintah berikut.

```bash
streamlit run app.py
```

---

## Deployment

Aplikasi dapat dideploy menggunakan **Streamlit Community Cloud**.

1. Push repository ke GitHub.
2. Buat aplikasi baru pada Streamlit Community Cloud.
3. Tentukan `app.py` sebagai entry point.
4. Tambahkan secrets berikut:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
5. Deploy aplikasi.

---

## Sumber Daya Eksternal

Untuk menjaga ukuran repository tetap ringan, beberapa komponen tidak disimpan langsung pada repository GitHub dan akan diunduh secara otomatis saat aplikasi dijalankan.

### Hugging Face Model Hub

**Model Named Entity Recognition (NER)**

- `ksophiena/ner-indobert-pencurian`

### Hugging Face Dataset Hub

**Knowledge Base, Embedding, dan FAISS Index**

- `ksophiena/kb-yurisprudensi-pencurian`

---

## Struktur Proyek

```text
.
├── app.py                          # Halaman utama aplikasi
├── pages/
│   ├── 0_Login.py                  # Login dan registrasi pengguna
│   ├── 2_Analisis_Putusan.py       # Analisis putusan
│   ├── 3_Statistik.py              # Statistik dataset
│   ├── 4_Riwayat.py                # Riwayat percakapan
│   └── 5_Profil.py                 # Profil pengguna
├── utils/
│   ├── auth.py                     # Autentikasi pengguna
│   ├── components.py               # Komponen antarmuka
│   ├── database.py                 # Koneksi dan operasi Supabase
│   ├── rag_engine.py               # Pipeline Retrieval-Augmented Generation
│   └── theme.py                    # Tema aplikasi
├── assets/                         # Aset gambar dan ikon
├── requirements.txt
└── README.md
```

---

## Catatan

Repository ini hanya memuat kode sumber aplikasi. Model NER, knowledge base, embedding, dan indeks FAISS disimpan pada Hugging Face sehingga aplikasi dapat dijalankan tanpa perlu menyimpan file berukuran besar di repository.

---

## Lisensi

Proyek ini dikembangkan untuk keperluan pendidikan dan penelitian.
