"""
pages/3_Statistik.py
=====================
Statistik agregat dihitung LANGSUNG dari seluruh knowledge_base.
"""

import re
from collections import Counter, defaultdict

import streamlit as st
import folium
from streamlit_folium import st_folium

from utils import auth, database as db
from utils.theme import apply_theme, render_metric
from utils.components import render_sidebar, render_topbar, law_disclaimer
from utils.chart_helpers import render_bar_chart, render_pie_chart
from utils import rag_engine as rag

st.set_page_config(page_title="TanyaHukum - Statistik", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db.init_db()
auth.init_session_state()
apply_theme()

render_sidebar(active="Statistik")
render_topbar("Statistik & Visualisasi",
              "Analisis pola yurisprudensi kasus pencurian berdasarkan putusan pengadilan di Indonesia")

tokenizer, model, ner_pipeline, kb, embeddings, index = rag.load_resources()

CITY_COORDS = {
    "makassar": (-5.1477, 119.4327), "mamuju": (-2.6785, 118.8887),
    "palopo": (-2.9925, 120.1969), "bulukumba": (-5.5407, 120.2280),
    "sungguminasa": (-5.1997, 119.4489), "watampone": (-4.5386, 120.3308),
    "polewali": (-3.4322, 119.3411), "makale": (-3.0777, 119.8467),
    "sinjai": (-5.1263, 120.2553), "maros": (-5.0059, 119.5714),
    "selayar": (-6.1273, 120.4573), "pinrang": (-3.7861, 119.6511),
    "sengkang": (-4.1274, 120.0089), "pare pare": (-4.0135, 119.6255),
    "barru": (-4.4194, 119.6198), "malili": (-2.6372, 121.3572),
    "pangkajene": (-4.7981, 119.5645), "enrekang": (-3.5522, 119.7887),
    "masamba": (-2.5522, 120.3273), "pasangkayu": (-1.2683, 119.2662),
    "donggala": (-0.6683, 119.7414), "salatiga": (-7.3305, 110.5084),
    "kolaka": (-4.0575, 121.6053), "kalianda": (-5.7333, 105.5667),
    "ketapang": (-1.8503, 109.9633), "stabat": (3.7594, 98.4508),
    "bantul": (-7.8891, 110.3288), "denpasar": (-8.6705, 115.2126),
    "rokan hilir": (1.4508, 100.7167), "wamena": (-4.0925, 138.9386),
    "jayapura": (-2.5337, 140.7181), "ambon": (-3.6954, 128.1814),
    "batulicin": (-3.4531, 115.6231), "pelalawan": (0.3167, 101.9333),
    "atambua": (-9.1061, 124.8919), "jeneponto": (-5.6317, 119.7311),
    "medan": (3.5952, 98.6722), "banjarbaru": (-3.4383, 114.8306),
    "soe": (-9.8608, 124.2856), "jakarta utara": (-6.1384, 106.8636),
    "bangkinang": (0.3333, 101.0500), "tabanan": (-8.5416, 115.1252),
    "ruteng": (-8.6136, 120.4676), "tual": (-5.6702, 132.7495),
    "unaaha": (-3.9167, 121.9667), "tenggarong": (-0.4019, 116.9944),
    "andoolo": (-4.1667, 122.3500), "gianyar": (-8.5385, 115.3266),
    "masohi": (-3.2000, 128.9500), "banjarmasin": (-3.3194, 114.5908),
    "bondowoso": (-7.9126, 113.8215), "jakarta pusat": (-6.1862, 106.8347),
    "soasiu": (0.7333, 127.3833), "bontang": (0.1324, 117.4747),
    "sarolangun": (-2.3000, 102.6500), "tanjung karang": (-5.4292, 105.2610),
    "sanggau": (0.1167, 110.5833), "rantau prapat": (2.1000, 99.8333),
    "sukoharjo": (-7.6819, 110.8286), "watansopeng": (-4.1333, 119.9000),
    "pulau punjung": (-1.5333, 101.4500), "klaten": (-7.7056, 110.6069),
    "kotabumi": (-4.8333, 104.9000), "banda aceh": (5.5483, 95.3238),
    "sibuhuan": (1.4667, 99.9333), "bengkulu": (-3.7928, 102.2608),
    "bireuen": (5.2000, 96.7000), "kuala tungkal": (-0.8000, 103.4500),
    "paringin": (-2.0500, 115.4000), "tanjung balai karimun": (1.0500, 103.4333),
    "palangkaraya": (-2.2136, 113.9108), "pagar alam": (-4.0167, 103.2500),
    "raha": (-4.8333, 122.7167), "waingapu": (-9.6567, 120.2600),
    "martapura": (-3.4167, 114.8333), "tobelo": (1.7500, 128.0000),
    "arga makmur": (-3.4667, 102.2167), "menggala": (-4.1667, 105.2833),
    "mandailing natal": (0.9500, 99.4333), "pariaman": (-0.6167, 100.1167),
    "belopa": (-3.4333, 120.4000), "waikabubak": (-9.6500, 119.4167),
    "siak sri indrapura": (0.8167, 102.0333), "suka makmue": (4.2833, 96.4167),
    "bogor": (-6.5971, 106.8060), "balige": (2.3333, 99.0667),
    "pasuruan": (-7.6453, 112.9075), "pulang pisau": (-2.8667, 114.2833),
    "singaraja": (-8.1120, 115.0882), "tarakan": (3.3000, 117.6333),
    "amlapura": (-8.4500, 115.6167), "buol": (1.1167, 121.4667),
    "manna": (-4.4667, 102.9167), "jakarta selatan": (-6.2615, 106.8106),
    "kota agung": (-5.5000, 104.6333), "biak": (-1.1833, 136.0833),
    "pekalongan": (-6.8886, 109.6753), "sambas": (1.3667, 109.3167),
}

LEVEL_LABELS = {
    "first_instance": "Pengadilan Negeri",
    "appellate": "Pengadilan Tinggi",
    "cassation": "Mahkamah Agung",
}


def _normalize_city_name(court_name: str) -> str:
    name = (court_name or "").strip().lower()
    for prefix in ("pn ", "pt ", "ma "):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    return name.strip()

def _parse_sentence_months(text: str):
    if not text:
        return None
    text = text.lower()
    total_months = 0
    found = False

    m_tahun = re.search(r'(\d+)\s*\(?\s*\w*\s*\)?\s*tahun', text)
    if m_tahun:
        total_months += int(m_tahun.group(1)) * 12
        found = True

    m_bulan = re.search(r'(\d+)\s*\(?\s*\w*\s*\)?\s*bulan', text)
    if m_bulan:
        total_months += int(m_bulan.group(1))
        found = True

    return total_months if found else None


def _bucket_duration(months: int) -> str:
    years = months / 12
    if years < 1:
        return "< 1 Tahun"
    elif years < 2:
        return "1-2 Tahun"
    elif years < 3:
        return "2-3 Tahun"
    elif years < 5:
        return "4-5 Tahun"
    else:
        return "> 5 Tahun"


def _format_avg_duration(avg_months: float) -> str:
    total_months = round(avg_months)
    years = total_months // 12
    months = total_months % 12
    if years and months:
        return f"{years} Tahun {months} Bulan"
    elif years:
        return f"{years} Tahun"
    elif months:
        return f"{months} Bulan"
    return "-"

@st.cache_data(show_spinner=False)
def compute_stats(_kb):
    total = len(_kb)

    charge_counter = Counter()
    year_counter = Counter()
    duration_counter = Counter()
    location_counter = Counter()
    evidence_counter = Counter()
    stolen_object_counter = Counter()
    level_counter = Counter()
    all_months = []

    MONEY_WORDS = {"rupiah", "ribu", "juta", "rp", "puluh", "ratus"}

    CRIME_TOOLS = {
        "obeng", "gergaji", "palu", "kunci inggris", "kunci letter t",
        "kunci t", "linggis", "tang", "pisau", "cutter", "kunci leter t",
        "kunci duplikat", "kunci palsu", "besi", "golok", "parang",
        "senter", "korek api", "sarung tangan", "tali",
    }

    EXCLUDE_PHRASES = [
        "kunci motor", "kunci sepeda motor", "kunci mobil",
        "charger laptop", "dus laptop", "casing laptop", "tas laptop",
        "kalung sapi", "kalung kambing",
        "stnk", "bpkb", "surat bukti kepemilikan",
    ]

    STOLEN_OBJECT_KEYWORDS = {
        "kaca spion": "Kaca Spion", "spion": "Kaca Spion",
        "sepeda motor": "Sepeda Motor", "motor": "Sepeda Motor",
        "mobil": "Mobil", "laptop": "Laptop",
        "handphone": "Handphone", " hp ": "Handphone", "hp merk": "Handphone",
        "telepon genggam": "Handphone",
        "emas": "Perhiasan Emas",
        "sapi": "Ternak", "kambing": "Ternak", "ayam": "Ternak",
        "tabung gas": "Tabung Gas", "flashdisk": "Flashdisk",
        "sepeda": "Sepeda",
    }

    for doc in _kb:
        for c in doc["entities"].get("ChargeArticles", []):
            m_pasal = c.lower().replace("pasal", "").strip().split()
            if m_pasal and m_pasal[0].isdigit():
                charge_counter[f"Pasal {m_pasal[0]}"] += 1
        year_counter[doc.get("year")] += 1
        level_counter[doc.get("court_level")] += 1

        city = _normalize_city_name(doc.get("court_name"))
        if city:
            location_counter[city] += 1

        for sentence_text in doc["entities"].get("PrisonSentence", []):
            months = _parse_sentence_months(sentence_text)
            if months:
                all_months.append(months)
                duration_counter[_bucket_duration(months)] += 1

        for ev in doc["entities"].get("Evidence", []):
            ev_clean = ev.strip().lower()
            ev_clean = ev_clean.strip(" .,;()")

            if not (3 <= len(ev_clean) <= 30):
                continue
            if any(w in ev_clean for w in MONEY_WORDS):
                continue
            if not any(c.isalpha() for c in ev_clean):
                continue

            evidence_counter[ev_clean] += 1

            if any(tool in ev_clean for tool in CRIME_TOOLS):
                continue
            if any(phrase in ev_clean for phrase in EXCLUDE_PHRASES):
                continue
            for keyword, label in STOLEN_OBJECT_KEYWORDS.items():
                if keyword in ev_clean:
                    stolen_object_counter[label] += 1
                    break

    top_year = year_counter.most_common(1)[0][0] if year_counter else "-"
    top_charge = charge_counter.most_common(1)[0][0] if charge_counter else "-"
    avg_months = (sum(all_months) / len(all_months)) if all_months else 0

    level_dist = [
        (LEVEL_LABELS.get(lvl, lvl or "-"), c)
        for lvl, c in level_counter.most_common()
    ]

    return {
        "total": total,
        "top_charge": top_charge,
        "top_year": top_year,
        "avg_sentence_display": _format_avg_duration(avg_months),
        "charge_dist": charge_counter.most_common(5),
        "duration_dist": duration_counter.most_common(5),
        "location_dist": location_counter.most_common(5),
        "evidence_dist": evidence_counter.most_common(5),
        "stolen_object_dist": stolen_object_counter.most_common(5),
        "level_dist": level_dist,
    }


@st.cache_data(show_spinner=False)
def compute_city_stats(_kb):
    city_data = defaultdict(lambda: {"total": 0, "months": [], "charges": Counter(), "years": Counter()})

    for doc in _kb:
        city = _normalize_city_name(doc.get("court_name"))
        if city not in CITY_COORDS:
            continue

        city_data[city]["total"] += 1
        city_data[city]["years"][doc.get("year")] += 1
        for sentence_text in doc["entities"].get("PrisonSentence", []):
            months = _parse_sentence_months(sentence_text)
            if months:
                city_data[city]["months"].append(months)
        for c in doc["entities"].get("ChargeArticles", []):
            m_pasal = c.lower().replace("pasal", "").strip().split()
            if m_pasal and m_pasal[0].isdigit():
                city_data[city]["charges"][f"Pasal {m_pasal[0]}"] += 1

    result = {}
    for city, data in city_data.items():
        avg_m = sum(data["months"]) / len(data["months"]) if data["months"] else 0
        top_charge = data["charges"].most_common(1)[0][0] if data["charges"] else "-"
        top_year = data["years"].most_common(1)[0][0] if data["years"] else "-"
        result[city] = {
            "total": data["total"],
            "avg_display": _format_avg_duration(avg_m),
            "top_charge": top_charge,
            "top_year": top_year,
        }
    return result


stats = compute_stats(kb)

st.markdown("### Ringkasan Data")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Total Putusan", f"{stats['total']:,}", "Seluruh basis data")
with col2:
    render_metric("Rata-rata Hukuman", stats["avg_sentence_display"], "Berdasarkan seluruh kasus")
with col3:
    render_metric("Pasal Dominan", stats["top_charge"], "Frekuensi tertinggi")
with col4:
    render_metric("Tahun Terbanyak", str(stats["top_year"]), "Jumlah kasus tertinggi")

st.divider()

st.markdown("### Peta Sebaran Kasus Pencurian")
city_stats = compute_city_stats(kb)

m = folium.Map(location=[-3.5, 118], zoom_start=5, tiles="CartoDB dark_matter")

for city, city_data in city_stats.items():
    if city not in CITY_COORDS:
        continue
    lat, lon = CITY_COORDS[city]
    popup_html = f"""
    <b>{city.title()}</b><br>
    Total Kasus: {city_data['total']}<br>
    Rata-rata Hukuman: {city_data['avg_display']}<br>
    Pasal Dominan: {city_data['top_charge']}<br>
    Tahun Terbanyak Kasus: {city_data['top_year']}
    """
    folium.CircleMarker(
        location=[lat, lon],
        radius=6 + min(city_data["total"] / 30, 20),
        popup=folium.Popup(popup_html, max_width=250),
        color="#C4956A", fill=True, fill_color="#6B4226", fill_opacity=0.85,
    ).add_to(m)

st.markdown(
    """
    <style>
    .leaflet-popup-content-wrapper, .leaflet-popup-tip {
    background-color: #3A2D25 !important;
    color: #F3E7D3 !important;
    }
    .leaflet-popup-content b { color: #C4956A !important; }
    .leaflet-container a.leaflet-popup-close-button { color: #F3E7D3 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
st_folium(m, width=None, height=450, returned_objects=[])
st.caption("Klik marker pada peta untuk melihat detail statistik per daerah.")

st.divider()
st.markdown("### Distribusi & Pola Kasus")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Distribusi Pasal yang Digunakan**")
    render_bar_chart(stats["charge_dist"], color="#8B2C2C")

with col_b:
    st.markdown("**Distribusi Lama Hukuman**")
    render_pie_chart(
        stats["duration_dist"],
        palette=["#3E7C74", "#5B7A9D", "#C9A227", "#B5651D", "#6B8F5E"],
    )

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("**Top Lokasi Kasus Pencurian**")
    render_bar_chart(stats["location_dist"], color="#C9A227")

with col_d:
    st.markdown("**Jenis Barang yang Paling Sering Dicuri**")
    render_pie_chart(
        stats["stolen_object_dist"],
        palette=["#5B7A9D", "#8B2C2C", "#C9A227", "#3E7C74", "#B5651D"],
    )

col_e, col_f = st.columns(2)
with col_e:
    st.markdown("**Barang Bukti yang Paling Sering Ditemukan**")
    render_bar_chart(stats["evidence_dist"], color="#B5651D")

with col_f:
    st.markdown("**Distribusi Tingkat Pengadilan**")
    render_pie_chart(
        stats["level_dist"],
        palette=["#6B8F5E", "#8B2C2C", "#C9A227"],
        hole=0.5,
    )

st.divider()
st.info(
    "Statistik dihitung secara langsung berdasarkan keseluruhan dokumen pada knowledge base."
)
law_disclaimer()
