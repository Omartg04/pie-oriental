"""
M1 · Panorama Territorial — PIE Oriental
Mapa seccional con ITerMC + tabla de ranking
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
from DEMO_CONFIG import *
from auth import require_auth
import generar_datos

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
[data-testid="stSidebar"] {{ background: {GRADIENTE_HEADER} !important; }}
[data-testid="stSidebar"] * {{ color: #ffffff !important; }}
.page-header {{
    background: {GRADIENTE_HEADER};
    border-radius: 14px; padding: 28px 36px 22px;
    margin-bottom: 24px;
}}
.page-tag {{ font-size:0.70rem; font-weight:700; letter-spacing:0.14em;
             color:#FF8200; text-transform:uppercase; margin-bottom:6px; }}
.page-title {{ font-size:1.7rem; font-weight:700; color:#fff; margin-bottom:4px; }}
.page-sub {{ font-size:0.92rem; color:rgba(255,255,255,0.70); }}
.section-title {{
    font-size:0.95rem; font-weight:700; color:#1e293b;
    border-bottom:3px solid #FF8200; padding-bottom:6px;
    margin-top:28px; margin-bottom:14px;
}}
.tier-alta    {{ background:#FFF4E6; border-left:4px solid #FF8200;
                 border-radius:0 8px 8px 0; padding:10px 14px; margin-bottom:6px; }}
.tier-oport   {{ background:#FFFBF5; border-left:4px solid #FFB366;
                 border-radius:0 8px 8px 0; padding:10px 14px; margin-bottom:6px; }}
.tier-dificil {{ background:#F8F9FA; border-left:4px solid #CBD5E0;
                 border-radius:0 8px 8px 0; padding:10px 14px; margin-bottom:6px; }}
.tier-sec  {{ font-size:1.0rem; font-weight:700; color:#333F48; }}
.tier-score {{ font-size:0.80rem; background:#FF8200; color:#fff;
               border-radius:20px; padding:2px 10px; font-weight:700;
               display:inline-block; margin-left:6px; }}
.tier-score.oport {{ background:#FFB366; color:#333; }}
.tier-score.dif   {{ background:#8B9299; }}
.tier-rec  {{ font-size:0.80rem; color:#475569; margin-top:3px; }}
.legend-box {{
    background:#fff; border:1px solid #E2E8F0; border-radius:10px;
    padding:14px 16px; margin-bottom:12px;
}}
.legend-item {{ display:flex; align-items:center; gap:8px;
                font-size:0.82rem; color:#333F48; margin-bottom:6px; }}
.legend-dot  {{ width:14px; height:14px; border-radius:3px; flex-shrink:0; }}
.kpi-mini {{ background:#fff; border:1px solid #E2E8F0; border-radius:10px;
             padding:14px; border-top:3px solid #FF8200; margin-bottom:10px; }}
.kpi-mini-val {{ font-size:1.6rem; font-weight:700; color:#1e293b; }}
.kpi-mini-lbl {{ font-size:0.75rem; color:#64748b; margin-top:2px; }}
.footer {{ margin-top:36px; padding-top:12px; border-top:1px solid #E2E8F0;
           text-align:center; font-size:0.70rem; color:#94a3b8; }}
</style>
"""

@st.cache_data(ttl=300)
def cargar_datos():
    generar_datos.generar_si_necesario()
    sdf = pd.read_csv(os.path.join(DATA, "secciones_itermc.csv"))
    with open(os.path.join(DATA, "PIE_Oriental_manzanas.geojson")) as f:
        geo = json.load(f)
    with open(os.path.join(DATA, "secciones_contornos.geojson")) as f:
        contornos = json.load(f)
    return sdf, geo, contornos

def color_por_itermc(itermc):
    if itermc >= ITERMC_UMBRAL_ALTA:
        return COLOR_ALTA
    elif itermc >= ITERMC_UMBRAL_OPT:
        return COLOR_OPT
    else:
        return COLOR_DIFICIL

def construir_mapa_seccional(sdf, geo, contornos):
    """Crea mapa Folium con polígonos a nivel sección coloreados por ITerMC."""
    m = folium.Map(
        location=[MAPA_LAT, MAPA_LON], zoom_start=MAPA_ZOOM,
        tiles="CartoDB positron"
    )

    # Crear lookup ITerMC por sección
    itermc_map = dict(zip(sdf["seccion"], sdf["itermc"]))
    clasif_map  = dict(zip(sdf["seccion"], sdf["clasificacion"]))
    ln_map      = dict(zip(sdf["seccion"], sdf["LN_total"]))
    ln39_map    = dict(zip(sdf["seccion"], sdf["LN_1839"]))
    pct_j_map   = dict(zip(sdf["seccion"], sdf["pct_joven"]))
    pct_mor_map = dict(zip(sdf["seccion"], sdf["pct_morena"]))
    rec_map     = dict(zip(sdf["seccion"], sdf["recomendacion"]))

    # Dibujar cada manzana coloreada por su sección
    for feat in geo["features"]:
        p   = feat["properties"]
        sec = p["SECCION"]
        it  = itermc_map.get(sec, 35)
        cl  = clasif_map.get(sec, "Oportunidad")
        col = color_por_itermc(it)

        tooltip_html = f"""
        <b>Sección {sec}</b><br>
        <span style='color:{col};font-weight:700;'>ITerMC: {it}</span>
        · {cl}<br>
        LN Total: {ln_map.get(sec,0):,} &nbsp;|&nbsp; LN 18–39: {ln39_map.get(sec,0):,}
        ({pct_j_map.get(sec,0)}%)<br>
        Morena: {pct_mor_map.get(sec,0)}%<br>
        <i>{rec_map.get(sec,'')}</i>
        """

        folium.GeoJson(
            feat,
            style_function=lambda f, c=col, it=it: {
                "fillColor": c,
                "color": "#ffffff",
                "weight": 1.5,
                "fillOpacity": 0.75,
            },
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)

    # Añadir centroide por sección con etiqueta
    secciones_vistas = set()
    for feat in geo["features"]:
        p   = feat["properties"]
        sec = p["SECCION"]
        if sec in secciones_vistas:
            continue
        secciones_vistas.add(sec)

        it  = itermc_map.get(sec, 35)
        col = color_por_itermc(it)

        # Calcular centroide aproximado del primer polígono de la sección
        coords = feat["geometry"]["coordinates"][0]
        if isinstance(coords[0][0], list):
            coords = coords[0]
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        clat = sum(lats) / len(lats)
        clon = sum(lons) / len(lons)

        folium.Marker(
            location=[clat, clon],
            icon=folium.DivIcon(
                html=f"""<div style='
                    background:{col}; color:#fff; font-weight:700;
                    font-size:11px; padding:3px 7px; border-radius:6px;
                    white-space:nowrap; box-shadow:0 2px 4px rgba(0,0,0,0.3);
                    font-family:DM Sans,sans-serif; border:1px solid rgba(255,255,255,0.4);
                '>§{sec} · {it:.0f}</div>""",
                icon_size=(80, 24), icon_anchor=(40, 12),
            ),
        ).add_to(m)

    # ── Capa de contornos seccionales (encima de todo) ──────────────────────
    for feat in contornos["features"]:
        sec = feat["properties"]["SECCION"]
        folium.GeoJson(
            feat,
            style_function=lambda f: {
                "fillColor": "transparent",
                "fillOpacity": 0,
                "color": "#333F48",
                "weight": 3.5,
                "dashArray": None,
            },
            tooltip=folium.Tooltip(f"Sección {sec}", sticky=False),
        ).add_to(m)

    return m

def main():
    st.set_page_config(page_title=PAGE_TITLE_M1, page_icon="🗺️",
                       layout="wide", initial_sidebar_state="collapsed")
    require_auth()
    st.markdown(CSS, unsafe_allow_html=True)

    sdf, geo, contornos = cargar_datos()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-tag">M1 · Panorama Territorial · {MUNICIPIO}, {ESTADO}</div>
        <div class="page-title">¿Dónde está el electorado natural de MC?</div>
        <div class="page-sub">
            Índice de Territorio MC (ITerMC) sección por sección —
            combinando potencial joven, competitividad electoral y movilización disponible.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout: mapa + sidebar ─────────────────────────────────────────────────
    col_mapa, col_panel = st.columns([3, 1], gap="medium")

    with col_panel:
        # Leyenda
        st.markdown('<div class="section-title">🎨 Leyenda ITerMC</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="legend-box">
            <div class="legend-item">
                <div class="legend-dot" style="background:#FF8200;"></div>
                <span><b>Alta prioridad</b> (≥ 65)</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#FFB366;"></div>
                <span><b>Oportunidad</b> (35–64)</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#CBD5E0;"></div>
                <span><b>Terreno difícil</b> (< 35)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPIs mini
        n_alta  = len(sdf[sdf["clasificacion"] == "Alta prioridad"])
        n_oport = len(sdf[sdf["clasificacion"] == "Oportunidad"])
        n_dif   = len(sdf[sdf["clasificacion"] == "Terreno difícil"])
        ln_alta = sdf[sdf["clasificacion"] == "Alta prioridad"]["LN_1839"].sum()

        st.markdown(f"""
        <div class="kpi-mini">
            <div class="kpi-mini-val">{n_alta}</div>
            <div class="kpi-mini-lbl">🟠 Sección Alta prioridad</div>
        </div>
        <div class="kpi-mini" style="border-top-color:#FFB366;">
            <div class="kpi-mini-val">{n_oport}</div>
            <div class="kpi-mini-lbl">🔸 Secciones Oportunidad</div>
        </div>
        <div class="kpi-mini" style="border-top-color:#8B9299;">
            <div class="kpi-mini-val">{n_dif}</div>
            <div class="kpi-mini-lbl">⬜ Secciones Terreno difícil</div>
        </div>
        <div class="kpi-mini">
            <div class="kpi-mini-val">{ln_alta:,}</div>
            <div class="kpi-mini-lbl">LN 18–39 en zona alta prioridad</div>
        </div>
        """, unsafe_allow_html=True)

    with col_mapa:
        st.markdown('<div class="section-title">🗺️ Mapa seccional · ITerMC</div>',
                    unsafe_allow_html=True)
        with st.spinner("Cargando mapa…"):
            m = construir_mapa_seccional(sdf, geo, contornos)
            st_folium(m, width="100%", height=520, returned_objects=[])

    # ── Ranking de secciones ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Ranking de secciones — de mayor a menor ITerMC</div>',
                unsafe_allow_html=True)

    tier_icons = {"Alta prioridad": ("tier-alta", "score"),
                  "Oportunidad": ("tier-oport", "oport"),
                  "Terreno difícil": ("tier-dificil", "dif")}

    sdf_sorted = sdf.sort_values("itermc", ascending=False)
    rank = 1
    for _, row in sdf_sorted.iterrows():
        tier_class, score_class = tier_icons.get(row["clasificacion"],
                                                  ("tier-oport", "oport"))
        clasif_icon = {"Alta prioridad": "🟠", "Oportunidad": "🔸",
                       "Terreno difícil": "⬜"}.get(row["clasificacion"], "")
        st.markdown(f"""
        <div class="{tier_class}">
            <span class="tier-sec">
                #{rank} &nbsp; §{int(row['seccion'])}
                <span class="tier-score {score_class}">ITerMC {row['itermc']:.1f}</span>
                &nbsp; {clasif_icon} {row['clasificacion']}
            </span>
            <div class="tier-rec">
                👥 LN Total: {int(row['LN_total']):,}
                &nbsp;|&nbsp; 18–39: {int(row['LN_1839']):,} ({row['pct_joven']}%)
                &nbsp;|&nbsp; Morena: {row['pct_morena']}%
                &nbsp;|&nbsp; PVEM 3ª vía: {row['pct_pvem']}%
                &nbsp;|&nbsp; Abstención: {row['abstencion']}%
            </div>
            <div class="tier-rec" style="color:#FF8200; font-weight:600;">
                → {row['recomendacion']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        rank += 1

    # ── Gráfico de barras ITerMC ──────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 ITerMC por sección</div>',
                unsafe_allow_html=True)

    fig = go.Figure()
    colors = [color_por_itermc(v) for v in sdf_sorted["itermc"]]
    labels = [f"§{int(s)}" for s in sdf_sorted["seccion"]]

    fig.add_trace(go.Bar(
        x=labels,
        y=sdf_sorted["itermc"],
        marker_color=colors,
        marker_line_color="#ffffff",
        marker_line_width=1.5,
        text=[f"{v:.1f}" for v in sdf_sorted["itermc"]],
        textposition="outside",
        textfont=dict(size=12, color="#333F48", family="DM Sans"),
    ))

    # Línea de umbral Alta
    fig.add_hline(y=ITERMC_UMBRAL_ALTA, line_dash="dash",
                  line_color="#FF8200", line_width=1.5,
                  annotation_text="Alta prioridad (65)",
                  annotation_position="top right",
                  annotation_font_color="#FF8200")
    fig.add_hline(y=ITERMC_UMBRAL_OPT, line_dash="dot",
                  line_color="#8B9299", line_width=1,
                  annotation_text="Oportunidad (35)",
                  annotation_position="bottom right",
                  annotation_font_color="#8B9299")

    fig.update_layout(
        height=340,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(range=[0, 85], gridcolor="#F0F0F0",
                   title="ITerMC", title_font_color="#333F48"),
        xaxis=dict(title="Sección", title_font_color="#333F48"),
        font=dict(family="DM Sans", color="#333F48"),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Navegación ────────────────────────────────────────────────────────────
    st.markdown("<div class='nav-row'>", unsafe_allow_html=True)
    nav1, nav_mid, nav2 = st.columns([1, 4, 1])
    with nav1:
        if st.button("← Inicio", use_container_width=True):
            st.switch_page("Home.py")
    with nav2:
        if st.button("Territorios →", type="primary", use_container_width=True):
            st.switch_page("pages/2_M2_Territorio.py")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="footer">{FOOTER_TEXTO}</div>', unsafe_allow_html=True)

main()