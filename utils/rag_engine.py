"""
rag_engine.py
=============
Semua fungsi inti RAG pipeline, dipindahkan dari notebook
05_RAG_Gemini.ipynb. Model NER & data KB dimuat dari Hugging Face Hub
(bukan path lokal Google Drive), agar bisa jalan di Streamlit
Community Cloud.

Ganti nilai di bagian KONFIGURASI sesuai repo HF milikmu.
"""

import os
import re
import json
import time
import numpy as np
import random
import torch
import faiss
import streamlit as st
from datetime import datetime
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModel, AutoModelForTokenClassification, pipeline
from google import genai
from google.genai import types

# KONFIGURASI
MODEL_NER_REPO   = "ksophiena/ner-indobert-pencurian"
DATASET_REPO     = "ksophiena/kb-yurisprudensi-pencurian"

GEMINI_MODEL       = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.4
GEMINI_TOP_P       = 0.9
GEMINI_MAX_TOKENS  = 1024
GEMINI_MAX_RETRIES = 4
GEMINI_BASE_DELAY  = 5.0

TOP_K_DEFAULT   = 3
MAX_CONTEXT_DOCS = 3
MIN_SIMILARITY   = 0.5

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# LOADING
@st.cache_resource(show_spinner="Memuat model NER & basis pengetahuan...")
def load_resources():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NER_REPO)
    model = AutoModel.from_pretrained(MODEL_NER_REPO).to(DEVICE)
    model.eval()

    ner_model = AutoModelForTokenClassification.from_pretrained(MODEL_NER_REPO).to(DEVICE)
    ner_pipeline = pipeline(
        task="ner", model=ner_model, tokenizer=tokenizer,
        aggregation_strategy="simple",
        device=0 if DEVICE == "cuda" else -1,
    )

    kb_file    = hf_hub_download(repo_id=DATASET_REPO, filename="knowledge_base.json", repo_type="dataset")
    emb_file   = hf_hub_download(repo_id=DATASET_REPO, filename="kb_embeddings.npy", repo_type="dataset")
    faiss_file = hf_hub_download(repo_id=DATASET_REPO, filename="kb_faiss.index", repo_type="dataset")

    with open(kb_file, encoding="utf-8") as f:
        kb = json.load(f)

    embeddings = np.load(emb_file)
    index = faiss.read_index(faiss_file)

    return tokenizer, model, ner_pipeline, kb, embeddings, index


@st.cache_resource(show_spinner=False)
def get_gemini_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)


# PREPROCESSING TEKS

def prepare_legal_text(text: str) -> str:
    text = str(text).strip()
    text = text.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")
    text = re.sub(
        r"DEMI\s+KEADILAN\s+BERDASARKAN\s+KETUHANAN\s+YANG\s+MAHA\s+ESA",
        " ", text, flags=re.IGNORECASE)
    text = re.sub(
        r"Disclaimer\s+Kepaniteraan.*?(?=Halaman|\n\n|$)",
        " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Mahkamah Agung Republik Indonesia(\s+Mahkamah Agung Republik Indonesia)+", " ", text)
    text = re.sub(r"Halaman \d+ dari \d+", " ", text)
    text = re.sub(r"Putusan Nomor.{0,50}?Halaman\s*\d+", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"Direktori Putusan Mahkamah Agung Republik Indonesia\s+putusan\.mahkamahagung\.go\.id"," ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\n\s*(?=[a-z])", " ", text)

    match = re.search(r"\bDAKWAAN\b", text)  
    if not match:
        match = re.search(r"DAKWAAN", text, flags=re.IGNORECASE)
    if match:
        text = text[match.start():]
    return text

def _cut_to_sentence_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text.strip()
    snippet = text[:max_chars]
    candidates = [m.end() for m in re.finditer(r"(?<!\d)[.!?;]", snippet)]
    if candidates and candidates[-1] > max_chars * 0.5:
        return snippet[:candidates[-1]].strip()
    return snippet.strip() + "..."

def _format_numbered_points(text: str) -> str:
    return re.sub(r"(?<!\d)(\d{1,2}\.\s+[A-Z])", r"\n\1", text)

def build_case_summary(text: str, head_chars: int = 400, consider_chars: int = 1600,
                        verdict_chars: int = 800) -> str:
    text = prepare_legal_text(text)
    parts = []

    head = _cut_to_sentence_boundary(text[:head_chars + 100], head_chars)
    head = _format_numbered_points(head)
    if head:
        parts.append("=== DAKWAAN DAN FAKTA PERKARA ===\n" + head)

    m = re.search(r"unsur[\s\-]*(pertama|ke[- ]?\d|ke\s*satu)", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"MENIMBANG", text, flags=re.IGNORECASE)
    if m:
        raw_consider = text[m.start(): m.start() + consider_chars + 200]
        consider = _cut_to_sentence_boundary(raw_consider, consider_chars)
        parts.append("=== PERTIMBANGAN HAKIM ===\n" + consider)

    m = re.search(r"\bM\s*E\s*N\s*G\s*A\s*D\s*I\s*L\s*I\b", text, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"^\s*MENGADILI\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        m = re.search(r"(MENGADILI|MEMUTUSKAN)", text, flags=re.IGNORECASE)
    if m:
        raw_verdict = text[m.start(): m.start() + verdict_chars + 200]
        verdict = _cut_to_sentence_boundary(raw_verdict, verdict_chars)
        verdict = _format_numbered_points(verdict)
        parts.append("=== AMAR PUTUSAN ===\n" + verdict)

    summary = "\n\n".join(parts)
    if not summary.strip():
        summary = text[:1500]
    return summary


def build_doc_text_for_embed(doc: dict) -> str:
    text = str(doc.get("text", "")).strip()
    if not text:
        return "dokumen kosong"
    text = prepare_legal_text(text)
    words = text.split()
    return " ".join(words[:400])


def mean_pooling(model_output, attention_mask: torch.Tensor) -> torch.Tensor:
    token_emb = model_output.last_hidden_state
    mask_exp = attention_mask.unsqueeze(-1).expand(token_emb.size()).float()
    return torch.sum(token_emb * mask_exp, 1) / torch.clamp(mask_exp.sum(1), min=1e-9)


def embed_texts(texts: list, tokenizer, model, batch_size: int = 16) -> np.ndarray:
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch, max_length=256, truncation=True, padding=True,
                            return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            output = model(**inputs)
        emb = mean_pooling(output, inputs["attention_mask"])
        emb = torch.nn.functional.normalize(emb, p=2, dim=1)
        all_embs.append(emb.cpu().numpy())
    if not all_embs:
        return np.empty((0, model.config.hidden_size))
    return np.vstack(all_embs)


# ── RETRIEVAL ────────────────────────────────────────────────────────────

def retrieve(query: str, tokenizer, model, kb: list, index, top_k: int = TOP_K_DEFAULT,
             level_filter: str = None, filter_entities: dict = None,
             min_score: float = MIN_SIMILARITY) -> list:
    query = str(query).strip()
    if not query:
        return []

    query_emb = embed_texts([query], tokenizer, model).astype("float32")

    has_filter = level_filter is not None or filter_entities is not None
    k_search = index.ntotal if has_filter else top_k

    scores, indices = index.search(query_emb, k_search)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score < min_score:
            continue
        if idx < 0 or idx >= len(kb):
            continue
        doc = kb[idx]

        if level_filter is not None and doc["court_level"] != level_filter:
            continue

        if filter_entities:
            match = True
            for etype, val in filter_entities.items():
                if etype == "year":
                    if doc["year"] != val:
                        match = False
                        break
                else:
                    values = doc["entities"].get(etype, [])
                    if not any(str(val).lower() in str(v).lower() for v in values):
                        match = False
                        break
            if not match:
                continue

        results.append({
            "doc_id": doc["doc_id"], "court_level": doc["court_level"],
            "court_label": doc["court_label"], "court_name": doc["court_name"],
            "year": doc["year"], "score": round(float(score), 4),
            "text_snippet": build_doc_text_for_embed(doc)[:500],
            "full_text": doc["text"], "entities": doc["entities"],
            "text_length": doc["text_length"], "n_entities": doc["n_entities"],
        })
        if len(results) >= top_k:
            break

    return results


#  DETEKSI METADATA QUERY
def detect_level_filter(question: str):
    q = question.lower()
    if any(k in q for k in ["mahkamah agung", "kasasi", "putusan kasasi"]):
        return "cassation"
    if any(k in q for k in ["pengadilan tinggi", "banding", "putusan banding"]):
        return "appellate"
    if any(k in q for k in ["pengadilan negeri", "tingkat pertama", "putusan tingkat pertama"]):
        return "first_instance"
    return None


def detect_entity_filters(question: str) -> dict:
    filters = {}
    q = question.lower()

    m = re.search(r"pasal\s+(\d+)", q)
    if m:
        filters["ChargeArticles"] = f"Pasal {m.group(1)}"
    else:
        # Mapping istilah umum ke pasal spesifik jika nomor pasal tidak disebutkan
        if "pencurian biasa" in q:
            filters["ChargeArticles"] = "362"
        elif "pemberatan" in q:
            filters["ChargeArticles"] = "363"
        elif "kekerasan" in q:
            filters["ChargeArticles"] = "365"
        elif "pencurian ringan" in q:
            filters["ChargeArticles"] = "364"

    m = re.search(r"(19|20)\d{2}", q)
    if m:
        filters["year"] = int(m.group())
    return filters


def detect_question_type(question: str) -> str:
    q = question.lower()

    analytical_markers = ["apa saja", "bagaimana", "mengapa", "jelaskan",
                           "unsur", "alasan", "faktor", "penerapan",
                           "diterapkan", "pertimbangan"]
    if any(k in q for k in analytical_markers):
        return "ruling"

    if any(k in q for k in ["barang bukti", "bukti", "disita", "dikembalikan"]):
        return "evidence"

    if any(k in q for k in ["hakim", "mengadili", "amar", "putusan"]):
        return "ruling"

    if any(k in q for k in ["berapa lama", "berapa tahun", "berapa bulan",
                             "jenis pidana", "lama hukuman"]):
        return "sentence"

    if any(k in q for k in ["pasal", "dakwaan", "kuhp"]):
        return "charge"

    return "general"


# CONTEXT BUILDER

PREFIX_MAP = {"Pn": "Pengadilan Negeri", "Pt": "Pengadilan Tinggi", "Ma": "Mahkamah Agung"}

def _fmt(lst, max_items=2):
    vals = []
    for v in lst:
        v = str(v).strip()
        if not v or v.lower() in {"-", "nan", "none"} or len(v) < 3:
            continue
        vals.append(v)
    vals = list(dict.fromkeys(vals))
    return "; ".join(vals[:max_items]) if vals else "-"

def build_context(retrieved_docs: list, question: str = "") -> str:
    qtype = detect_question_type(question)
    if not retrieved_docs:
        return "Tidak ditemukan putusan yang relevan."

    context_parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        ents = doc.get("entities", {})

        court = (doc.get("court_name") or "").strip()
        parts = court.split()
        if parts and parts[0] in PREFIX_MAP:
            parts[0] = PREFIX_MAP[parts[0]]
        court = " ".join(parts)

        year  = doc.get("year", "")
        label = f"{court}, {year}" if court and year else (court or str(year) or f"Putusan {i}")

        charges  = ents.get("ChargeArticles", [])
        sentence = ents.get("PrisonSentence", [])
        evidence = ents.get("Evidence", [])

        full_text = doc.get("full_text", doc.get("text", doc.get("text_snippet", "")))
        summary   = build_case_summary(full_text) or "-"

        lines = [
            f"--- PUTUSAN ({label}) ---", 
            f"Pasal Dakwaan  : {_fmt(charges)}",
            f"Pidana         : {_fmt(sentence)}",
        ]
        if qtype == "evidence":
            lines.append(f"Barang Bukti   : {_fmt(evidence, max_items=5)}")
        if qtype in ["general", "ruling"]:
            lines.append("")
            lines.append("Ringkasan Putusan:")
            lines.append(summary)

        context_parts.append("\n".join(lines))

    return "\n\n".join(context_parts)


# PROMPT ENGINEERING

SYSTEM_PROMPT = """Anda adalah Asisten Hukum Indonesia yang membantu pengguna memahami yurisprudensi putusan pengadilan tindak pidana pencurian.
Peran Anda adalah menjawab pertanyaan pengguna berdasarkan putusan pengadilan yang diberikan melalui mekanisme Retrieval-Augmented Generation (RAG). Gunakan konteks sebagai sumber pengetahuan untuk menyusun jawaban yang akurat, ringkas, natural, dan mudah dipahami.

ATURAN UTAMA
=========================
1. Gunakan informasi yang terdapat pada konteks putusan yang diberikan sebagai landasan jawaban.
2. Untuk pertanyaan faktual spesifik: jangan menambahkan fakta yang tidak ada di konteks.
3. Jangan pasif dengan langsung bilang "tidak tersedia". Coba simpulkan dari pola yang ada di konteks terlebih dahulu. Hanya katakan "tidak tersedia" jika konteks benar-benar tidak mengandung petunjuk apapun — bukan karena jawabannya butuh inferensi.
4. Untuk pertanyaan analitis/statistikal/komparatif: BOLEH dan DIHARAPKAN menyimpulkan, menghitung estimasi, dan menganalisis pola dari data yang ada di konteks — ini bukan mengarang, ini analisis berbasis data.
5. Perlakukan konteks seperti seorang analis yang membaca kumpulan data, bukan seperti mesin yang hanya mengutip kalimat yang ada.
6. Fokus menjawab pertanyaan pengguna, bukan menjelaskan seluruh isi putusan.

PANDUAN PER TIPE PERTANYAAN
=========================
[PERTANYAAN STATISTIKAL — rata-rata, paling sering, umumnya, dll.]
→ Analisis pola dari semua putusan di konteks. Hitung estimasi rata-rata,
  identifikasi kecenderungan, sebutkan rentang yang terlihat.
  Contoh: jika konteks berisi hukuman 1 tahun, 2 tahun, 1,5 tahun → simpulkan
  rata-rata sekitar 1,5 tahun, bukan bilang "tidak tersedia".

[PERTANYAAN KOMPARATIF — perbedaan, perbandingan, antara X dan Y]
→ Bandingkan pola antar kasus/pasal yang relevan dari konteks.
  Sintesis perbedaan yang terlihat dari data putusan yang ada.

[PERTANYAAN KONTEKSTUAL — kasus/putusan spesifik]
→ Jawab berdasarkan dokumen yang paling relevan dari konteks.

GAYA MENJAWAB
=========================
- Jawablah seperti seorang asisten hukum yang sedang mengobrol langsung dengan pengguna, BUKAN seperti menulis laporan atau ringkasan resmi.
- Gunakan bahasa Indonesia yang hangat, natural, dan mengalir seperti percakapan biasa.
- Jawab dengan kalimat/paragraf mengalir. HINDARI bullet point, penomoran, atau bold text KECUALI pengguna memang meminta daftar/list secara eksplisit.
- Berikan jawaban langsung pada inti pertanyaan di kalimat pertama, tanpa basa-basi pembuka.
- Gunakan kalimat sendiri, jangan menyalin isi putusan.
- Tulis nama pengadilan secara LENGKAP (contoh: "Pengadilan Negeri Watampone"), JANGAN disingkat menjadi "PN".
- Jangan mengulang informasi yang sama dua kali.
- JANGAN mencantumkan daftar sumber putusan di akhir jawaban — ini sudah ditampilkan secara terpisah oleh sistem.
- Jangan menyebut "Putusan 1", "Putusan 2", dan seterusnya. Jika perlu merujuk sumber spesifik, sebutkan nama pengadilan dan tahunnya saja (contoh: "dalam kasus di PN Makassar tahun 2021..."). Namun jika tidak perlu merujuk sumber spesifik, cukup buat jawaban mengalir tanpa referensi eksplisit — sumber sudah ditampilkan terpisah oleh sistem.
- Akhiri jawaban dengan satu kalimat penutup singkat yang merangkum inti jawaban, khusus untuk pertanyaan analitis yang butuh sintesis beberapa putusan.
- Panjang jawaban idealnya 2-5 kalimat untuk pertanyaan sederhana, maksimal 1-2 paragraf pendek untuk pertanyaan yang butuh sintesis.

KETERBATASAN
=========================
Hanya katakan "tidak tersedia" jika konteks benar-benar tidak mengandung
informasi apapun yang relevan — bukan karena jawabannya butuh inferensi.
"""

def build_rag_prompt(question: str, context: str) -> str:
    return f"""
{SYSTEM_PROMPT}

=========================
KONTEKS PUTUSAN
=========================

{context}

=========================
PERTANYAAN PENGGUNA
=========================

{question}

=========================
INSTRUKSI
=========================

- Gunakan hanya informasi dari konteks.
- Jawab pertanyaan secara langsung pada kalimat pertama.
- Sintesis informasi dari beberapa putusan menjadi satu jawaban yang utuh apabila diperlukan.
- Jangan menjelaskan proses berpikir ataupun reasoning internal.

Jawaban:
"""


# ── GEMINI CALL DENGAN RETRY ─────────────────────────────────────────────

def call_gemini_with_retry(prompt: str) -> str:
    client = get_gemini_client()
    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=GEMINI_TEMPERATURE,
                    top_p=GEMINI_TOP_P,
                    max_output_tokens=GEMINI_MAX_TOKENS,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            answer = getattr(response, "text", "").strip()
            if not answer:
                return "Maaf, model tidak menghasilkan jawaban. Silahkan coba gunakan pertanyaan lain."
            return answer

        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg

            if is_rate_limit and attempt < GEMINI_MAX_RETRIES:
                wait_time = GEMINI_BASE_DELAY * (2 ** (attempt - 1))
                time.sleep(wait_time)
                continue
            elif is_rate_limit:
                return "Layanan Gemini sedang mencapai batas kuota. Silahkan coba beberapa saat lagi."
            else:
                return "Terjadi kesalahan saat menghubungi layanan Gemini. Silahkan coba beberapa saat lagi."


# KLASIFIKASI TIPE PERTANYAAN 

def classify_question(question: str) -> str:
    """
    Klasifikasi tipe pertanyaan untuk menentukan strategi retrieval.
    - statistical : butuh agregat/pola dari banyak dokumen
    - comparative : butuh perbandingan antar pasal/kasus
    - contextual  : butuh dokumen spesifik yang relevan (default)
    """
    q = question.lower()
    stat_kw = [
        'rata-rata', 'berapa banyak', 'total', 'paling sering', 'terbanyak',
        'umumnya', 'pada umumnya', 'secara umum', 'berapa kasus', 'frekuensi',
        'mayoritas', 'distribusi', 'tren', 'seberapa sering', 'persentase',
        'kebanyakan', 'dominan', 'paling umum', 'rata rata'
    ]
    comp_kw = [
        'perbedaan', 'bedanya', 'beda antara', 'dibanding', 'lebih berat',
        'lebih ringan', 'dibandingkan', 'versus', ' vs ', 'mana yang',
        'lebih sering', 'lebih banyak', 'antara pasal'
    ]
    if any(k in q for k in stat_kw):
        return 'statistical'
    if any(k in q for k in comp_kw):
        return 'comparative'
    return 'contextual'


# RAG PIPELINE UTAMA
def rag_answer(question: str, tokenizer, model, kb: list, index,
               top_k: int = MAX_CONTEXT_DOCS, level_filter: str = None,
               filter_entities: dict = None) -> dict:
    start_time = datetime.now()

    # Klasifikasi pertanyaan untuk routing retrieval
    q_type = classify_question(question)

    if level_filter is None:
        level_filter = detect_level_filter(question)

    auto_filters = detect_entity_filters(question)
    if filter_entities is None:
        filter_entities = {}
    filter_entities.update(auto_filters)

    # Routing retrieval berdasarkan tipe pertanyaan
    if q_type == 'statistical':
        # Sampling representatif dari KB untuk analisis pola
        sample = random.sample(kb, min(25, len(kb)))
        base_retrieve = retrieve(question, tokenizer, model, kb, index,
                                  top_k=5, level_filter=level_filter,
                                  filter_entities=filter_entities)
        # Gabung sampling + hasil retrieval, deduplikasi
        all_docs = base_retrieve + [{**d, 'score': 0.6} for d in sample]
        seen, retrieved = set(), []
        for d in all_docs:
            if d['doc_id'] not in seen:
                seen.add(d['doc_id'])
                retrieved.append(d)
        retrieved = retrieved[:20]  

    elif q_type == 'comparative':
        retrieved = retrieve(question, tokenizer, model, kb, index,
                              top_k=6, level_filter=level_filter,
                              filter_entities=filter_entities)
        pasals = re.findall(r'pasal\s*(\d+)', question.lower())
        for p in pasals[:2]:
            extra = retrieve(f'pasal {p} pencurian', tokenizer, model,
                             kb, index, top_k=3)
            retrieved += extra
        seen, unique = set(), []
        for d in retrieved:
            if d['doc_id'] not in seen:
                seen.add(d['doc_id'])
                unique.append(d)
        retrieved = unique
    # contextual
    else:
        retrieved = retrieve(question, tokenizer, model, kb, index,
                              top_k=top_k, level_filter=level_filter,
                              filter_entities=filter_entities)

    context = build_context(retrieved, question=question)
    prompt  = build_rag_prompt(question, context)

    if not retrieved:
        answer = ("Maaf, tidak ditemukan putusan pengadilan yang relevan dengan "
                  "pertanyaan Anda dalam basis data kami. Silakan coba pertanyaan "
                  "dengan kata kunci yang berbeda.")
    else:
        answer = call_gemini_with_retry(prompt)

    elapsed = (datetime.now() - start_time).total_seconds()

    sources = []
    for doc in retrieved:
        ents = doc.get("entities", {})
        sources.append({
            "doc_id": doc["doc_id"], "court_label": doc["court_label"],
            "court_name": doc["court_name"], "year": doc["year"],
            "similarity": doc["score"],
            "decision_num": ents.get("DecisionNumber", ["-"])[0] if ents.get("DecisionNumber") else "-",
            "charge": ents.get("ChargeArticles", ["-"])[0] if ents.get("ChargeArticles") else "-",
            "sentence": ents.get("PrisonSentence", ["-"])[0] if ents.get("PrisonSentence") else "-",
        })

    return {
        "question": question, "answer": answer, "context": context, "sources": sources,
        "metadata": {
            "model": GEMINI_MODEL,
            "n_sources_retrieved": len(retrieved),
            "avg_similarity": round(float(np.mean([d["score"] for d in retrieved])), 4) if retrieved else 0.0,
            "max_similarity": max((d["score"] for d in retrieved), default=0.0),
            "elapsed_seconds": round(elapsed, 2),
        }
    }
