"""
theme.py
========
Tema "Kertas Malam" — charcoal hangat bernuansa berkas/arsip hukum.
"""

import streamlit as st
import base64
import os

def get_image_base64(filename: str) -> str:
    """Membaca file gambar dari folder assets lalu mengubahnya menjadi string Base64."""
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", filename,)
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
            --bg-main:        #181513;
            --bg-sidebar:     #2B211C;
            --bg-card:        #3A2D25;
            --bg-card-hover:  #44342B;
            --accent-main:    #C4956A;
            --accent-hover:   #B9875D;
            --button-bg:      #7A5C3E;
            --button-hover:   #8A6948;
            --accent-danger:  #A34D4D;
            --text-main:      #F3E7D3;
            --text-secondary: #C9B59E;
            --border-color:   #6B5444;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
    }

    .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    [data-testid="stBottomBlockContainer"] {
        max-width: 1000px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: 100% !important;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-testid="stBottom"] > div {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }

    h1, h2, h3, h4 {
        font-family: 'Lora', serif !important;
        color: var(--text-main) !important;
        letter-spacing: 0.2px;
    }

    p, span, div, label { color: var(--text-main); }

    .stCaption,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span,
    small {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        border-right: 1px solid var(--border-color);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-card); !important;
        border: 1px solid var(--border-color) !important;
        border-left: 3px solid var(--accent-main) !important;
        border-radius: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.25);
        transition: box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        background-color: var(--bg-card-hover);
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }

    .st-key-profile_header_card {
        border-left-color: var(--accent-main) !important;
        background: linear-gradient(135deg, rgba(196,149,106,0.08), var(--bg-card)) !important;
    }
    .st-key-delete_account_card {
        border-color: var(--accent-danger) !important;
        border-left-color: var(--accent-danger) !important;
        background-color: rgba(179,58,58,0.10) !important;
    }

    .stButton > button {
        background-color: var(--button-bg);
        color: var(--text-main);
        border: 1px solid var(--button-bg);
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.8rem 1rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background-color: var(--button-hover);
        border-color: var(--button-hover);
        transform: translateY(-1.5px);
        box-shadow: 0 6px 10px rgba(61, 43, 26, 0.25);
    }
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-main);
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent-main);
        color: var(--accent-main);
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: var(--bg-main) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-main) !important;
        box-shadow: 0 0 0 1px var(--accent-main) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-main) !important;
        border-bottom-color: var(--accent-main) !important;
    }

    [data-testid="stChatMessage"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
    }

    hr { border-color: var(--border-color) !important; }

    .th-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        background-color: rgba(196,149,106,0.15);
        border: 1px solid rgba(196,149,106,0.20);
        color: var(--accent-main);
        margin-right: 6px;
        font-family: 'IBM Plex Mono', monospace;
    }
</style>
"""

def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def badge(text: str) -> str:
    return f'<span class="th-badge">{text}</span>'


def render_bar(label: str, count: int, max_count: int, color: str):
    pct = min(count / max_count, 1.0) * 100 if max_count else 0
    st.markdown(
        f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between;
                        font-size:14px; margin-bottom:5px; color:#E8E2D8;">
                <span>{label}</span>
                <span style="font-family:'IBM Plex Mono',monospace;">{count}</span>
            </div>
            <div style="background:#35302A; border-radius:6px; height:9px; overflow:hidden;">
                <div style="width:{pct}%; background:{color}; height:100%; border-radius:6px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_metric(label, value, caption):
    html = f"""
<div style="width:100%; min-height:135px; padding:8px 4px; display:flex; flex-direction:column; justify-content:space-between;">

<div style="font-family:'Inter', sans-serif; font-size:16px; font-weight:500; color:var(--text-secondary); margin-bottom:8px;">
{label}
</div>

<div style="font-family:'IBM Plex Mono', monospace; font-size:1.8rem; font-weight:600; color:#BEB5A9; line-height:1.2; margin-bottom:6px; max-width:180px; white-space:normal; word-break:break-word;">
{value}
</div>

<div style="font-family:'Inter', sans-serif; font-size:15px; color:var(--text-secondary); margin-top:auto;">
{caption}
</div>

</div>
"""
    st.markdown(html, unsafe_allow_html=True)

