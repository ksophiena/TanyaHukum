"""
chart_helpers.py
================
Fungsi render chart Plotly (bar & pie), tema menyesuaikan palet
Kertas Malam, background transparan biar menyatu dengan halaman.
"""

import plotly.graph_objects as go
import streamlit as st

PLOT_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#E8E2D8"


def render_bar_chart(data: list, color: str, height: int = 260):
    """data: list of (label, count) tuples. Bar horizontal."""
    if not data:
        st.caption("Data tidak tersedia.")
        return
    labels = [d[0] for d in data][::-1]
    values = [d[1] for d in data][::-1]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=color),
        text=values, textposition="auto",
    ))
    fig.update_layout(
        height=height, margin=dict(l=15, r=70, t=15, b=15),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif", size=13),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_pie_chart(data: list, palette: list, height: int = 340, hole: float = 0.45):
    """data: list of (label, count) tuples. Donut/pie chart."""
    if not data:
        st.caption("Data tidak tersedia.")
        return
    labels = [d[0] for d in data]
    values = [d[1] for d in data]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=hole,
        marker=dict(colors=palette[:len(labels)], line=dict(color="#1A1613", width=2)),
        textfont=dict(color=FONT_COLOR, size=12),
        textinfo="percent",              # slice cuma nampilin persen, label lengkap di legend
        textposition="inside",
        insidetextorientation="radial",
    ))
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=90),   # ruang bawah dilebarin buat legend
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif", size=13),
        legend=dict(
            orientation="h", yanchor="top", y=-0.1,
            xanchor="center", x=0.5,
            font=dict(size=11),
        ),
        uniformtext=dict(minsize=9, mode="hide"),   # sembunyiin teks yang kepaksa numpuk, bukan dipaksa muat
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})