"""
pages/2_Analisis_Putusan.py
============================
Upload atau tempel teks putusan mentah untuk ekstraksi entitas NER
otomatis (menggunakan model token-classification) + pencarian
putusan serupa di basis pengetahuan.
"""

import io
import json
from collections import defaultdict

import streamlit as st
from pypdf import PdfReader

from utils import auth, database as db
from utils.theme import apply_theme
from utils.components import render_sidebar, render_topbar, law_disclaimer
from utils import rag_engine as rag
from utils.validator import validate_court_decision

st.set_page_config(page_title="TanyaHukum - Analisis Putusan", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

render_sidebar(active="Analisis Putusan")
render_topbar("Analisis Putusan", "Unggah teks putusan untuk melihat ringkasan dokumen dan mengekstrak entitas otomatis")

tokenizer, model, ner_pipeline, kb, embeddings, index = rag.load_resources()

# Label entitas yang benar-benar dilatih pada model
ENTITY_LABELS = {
    "DecisionNumber": "No. Putusan",
    "Defendant": "Terdakwa",
    "ChargeArticles": "Pasal & Dakwaan",
    "CourtRuling": "Putusan",
    "PrisonSentence": "Pidana",
    "Evidence": "Barang Bukti",
    "AggravatingFactors": "Faktor Memberatkan",
    "MitigatingFactors": "Faktor Meringankan",
}

uploaded_file = st.file_uploader("Upload teks putusan", type=["txt", "pdf"], label_visibility="visible")
pasted_text = st.text_area("Atau tempel teks putusan di sini", height=200,
                            placeholder="Tempel isi putusan pengadilan di sini...")

raw_text = ""
if uploaded_file is not None:
    if uploaded_file.name.lower().endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(uploaded_file.read()))
            raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if not raw_text.strip():
                st.warning(
                    "Tidak ada teks yang bisa diekstrak dari PDF ini. "
                    "Kemungkinan PDF berupa hasil scan/gambar, gunakan file dengan format .txt sebagai alternatif."
                )
        except Exception:
            st.error("Gagal membaca PDF. Pastikan file tidak terenkripsi/rusak, atau upload file dengan format .txt.")
    else:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
elif pasted_text.strip():
    raw_text = pasted_text.strip()

if raw_text and st.button("Analisis Putusan", type="primary"):
    valid, message = validate_court_decision(raw_text)
    if not valid:
        st.error(message)
        st.stop()

    with st.spinner("Menyusun ringkasan & mencari putusan serupa..."):
        summary = rag.build_case_summary(raw_text)
        similar_docs = rag.retrieve(raw_text[:500], tokenizer, model, kb, index, top_k=3)

    with st.spinner("Mengekstrak entitas..."):
        words = raw_text[:5000].split()
        CHUNK_WORD_SIZE = 200
        text_chunks = [
            " ".join(words[i:i + CHUNK_WORD_SIZE])
            for i in range(0, len(words), CHUNK_WORD_SIZE)
        ]

        MIN_CONFIDENCE = 0.6
        grouped = defaultdict(list)

        for chunk in text_chunks:
            if not chunk.strip():
                continue
            try:
                ner_results = ner_pipeline(chunk, truncation=True)
            except TypeError:
                ner_results = ner_pipeline(chunk)

            for ent in ner_results:
                word = ent["word"].strip()
                # Buang artefak subword yang gagal digabung 
                if word.startswith("##"):
                    continue
                # Buang entitas dengan confidence rendah
                if ent["score"] < MIN_CONFIDENCE:
                    continue
                # Buang kata umum pendek yang bukan entitas bermakna
                if word.lower() in {"pidana", "pasal", "ayat", "kuhp"}:
                    continue
                grouped[ent["entity_group"]].append(word)

    # KONTEN UTAMA 
    # Ringkasan Putusan
    st.markdown("### Ringkasan Putusan")
    with st.container(border=True):
        st.markdown(summary)

    st.divider()

    # 2. Ekstrak Entitas
    with st.expander("Lihat entitas terdeteksi"):
        st.caption(
            "Hasil ekstraksi NER otomatis pada teks yang diunggah. ")
        if not grouped:
            st.info("Tidak ada entitas dengan tingkat keyakinan tinggi yang terdeteksi.")
        for label_key, display_name in ENTITY_LABELS.items():
            values = grouped.get(label_key)
            if not values:
                continue
            unique_values = list(dict.fromkeys(v for v in values if len(v) > 1))
            if not unique_values:
                continue
            st.markdown(f"**{display_name}**")
            st.write(", ".join(unique_values[:5]))
        st.caption(
            "Catatan: hasil ekstraksi entitas hanya mencakup jenis entitas dari model yang dilatih")

    st.divider()

    # 3. Putusan Serupa
    st.markdown("### Putusan Serupa")
    if not similar_docs:
        st.info("Tidak ditemukan putusan serupa di basis pengetahuan.")
    for i, doc in enumerate(similar_docs, 1):
        ents = doc.get("entities", {})
        charge = ents.get("ChargeArticles", ["-"])[0] if ents.get("ChargeArticles") else "-"
        sentence = ents.get("PrisonSentence", ["-"])[0] if ents.get("PrisonSentence") else "-"

        court_display = (doc.get("court_name") or "").strip()
        parts = court_display.split()
        if parts and parts[0] in rag.PREFIX_MAP:
            parts[0] = rag.PREFIX_MAP[parts[0]]
        court_display = " ".join(parts)

        with st.container(border=True):
            st.markdown(f"**{i}. {court_display}**")
            st.caption(f"Pasal {charge} · Hukuman {sentence}")
            st.progress(min(doc["score"], 1.0), text=f"Similarity: {doc['score']:.3f}")

    logged_in, user = auth.require_guard()
    if logged_in:
        db.save_chat(
            user_id=user["id"], category="analisis",
            question=f"Analisis putusan ({len(raw_text)} karakter)",
            answer=summary,
            sources_json=json.dumps(similar_docs, ensure_ascii=False, default=str),
        )

elif not raw_text:
    st.caption(".txt atau .pdf — maks. 5.000 karakter")

law_disclaimer()
