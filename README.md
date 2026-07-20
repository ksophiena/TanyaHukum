# TanyaHukum — Chatbot Yurisprudensi Pencurian

Chatbot RAG (Retrieval-Augmented Generation) untuk yurisprudensi kasus
pidana pencurian di Indonesia, dibangun dengan IndoBERT (NER + embedding),
FAISS (retrieval), dan Google Gemini Flash 2.5 (generasi jawaban).

## Setup lokal

```bash
pip install -r requirements.txt
```

Buat file `.streamlit/secrets.toml` (tidak ikut di-commit ke git):
```toml
GEMINI_API_KEY = "isi-api-key-kamu-di-sini"
```

Jalankan:
```bash
streamlit run app.py
```

## Deployment ke Streamlit Community Cloud

1. Push folder ini ke GitHub repo.
2. Di Streamlit Community Cloud, buat app baru, arahkan ke `app.py`.
3. Di menu **Settings → Secrets**, tambahkan `GEMINI_API_KEY = "..."`.
4. Deploy.

## Sumber daya eksternal (di-load otomatis, tidak perlu di-commit)

- Model NER: `ksophiena/ner-indobert-pencurian` (Hugging Face Model Hub)
- Knowledge Base + Embeddings + FAISS Index: `ksophiena/kb-yurisprudensi-pencurian` (Hugging Face Dataset Hub)

## Struktur folder

```
app.py                      # entry point + halaman Chatbot
pages/
  0_Login.py                # login/signup (opsional, tidak wajib untuk pakai chatbot)
  2_Analisis_Putusan.py
  3_Statistik.py
  4_Riwayat.py
  5_Profil.py
utils/
  rag_engine.py             # semua fungsi RAG (retrieval, context builder, prompt, Gemini call)
  auth.py                   # login/signup/hash password
  database.py                # skema & fungsi SQLite
  theme.py                   # CSS tema merah
  components.py               # sidebar & topbar reusable
data/
  tanyahukum.db               # dibuat otomatis saat app pertama kali start
```
