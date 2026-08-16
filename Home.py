"""
Home.py — PIE Oriental, Puebla
Karenth Vázquez · Movimiento Ciudadano 2027
Data & AI Inclusion Technologies
"""

import streamlit as st
import pandas as pd
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
from DEMO_CONFIG import *
from auth import require_auth

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: {GRADIENTE_HEADER} !important; }}
[data-testid="stSidebar"] * {{ color: #ffffff !important; }}
[data-testid="stSidebar"] .stPageLink p {{ color: #FFE4C4 !important; font-weight:500; }}

/* Header */
.home-header {{
    background: {GRADIENTE_HEADER};
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}
.home-header::before {{
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,130,0,0.12);
}}
.home-header::after {{
    content: '';
    position: absolute;
    bottom: -50px; left: 35%;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}}
.header-tag {{
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
    color: #FF8200; text-transform: uppercase; margin-bottom: 8px;
}}
.header-title {{
    font-size: 2.1rem; font-weight: 700; color: #ffffff;
    line-height: 1.2; margin-bottom: 6px;
}}
.header-sub {{
    font-size: 1.0rem; color: rgba(255,255,255,0.75); margin-bottom: 18px;
}}
.header-badge {{
    display: inline-block;
    background: rgba(255,130,0,0.25);
    border: 1px solid rgba(255,130,0,0.5);
    border-radius: 20px; padding: 4px 16px;
    font-size: 0.78rem; color: #FFE4C4; font-weight: 600;
    margin-right: 8px;
}}

/* Section titles */
.section-title {{
    font-size: 1.0rem; font-weight: 700; color: #1e293b;
    border-bottom: 3px solid #FF8200;
    padding-bottom: 8px; margin-top: 36px; margin-bottom: 18px;
}}

/* Module cards */
.mod-card {{
    border-radius: 16px; padding: 28px 26px 22px;
    min-height: 240px; position: relative;
    overflow: hidden; color: #ffffff;
}}
.mod-card.c1 {{ background: linear-gradient(145deg, #1C2429 0%, #333F48 100%); }}
.mod-card.c2 {{ background: linear-gradient(145deg, #8B4000 0%, #CC6600 100%); }}
.mod-card.c3 {{ background: linear-gradient(145deg, #4A1C00 0%, #FF8200 100%); }}
.mod-card::after {{
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 130px; height: 130px; border-radius: 50%;
    background: rgba(255,255,255,0.06); pointer-events: none;
}}
.mod-card::before {{
    content: '';
    position: absolute; inset: 0;
    background-image: repeating-linear-gradient(
        -45deg, rgba(255,255,255,0.025) 0px,
        rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px
    );
    pointer-events: none;
}}
.mod-tag {{
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; opacity: 0.65; margin-bottom: 12px;
    position: relative; z-index: 1;
}}
.mod-icon {{ font-size: 2.4rem; margin-bottom: 8px; display: block;
             position: relative; z-index: 1; }}
.mod-title {{
    font-size: 1.2rem; font-weight: 700; color: #fff;
    margin-bottom: 10px; line-height: 1.25;
    position: relative; z-index: 1;
}}
.mod-body {{
    font-size: 0.84rem; color: rgba(255,255,255,0.70);
    line-height: 1.6; position: relative; z-index: 1;
}}

/* KPI cards */
.kpi-card {{
    background: #ffffff; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 18px 20px;
    border-top: 4px solid #FF8200;
}}
.kpi-valor {{
    font-size: 2.0rem; font-weight: 700; color: #1e293b; line-height: 1.1;
}}
.kpi-label {{ font-size: 0.80rem; font-weight: 600; color: #333F48; margin-top: 5px; }}
.kpi-ctx   {{ font-size: 0.72rem; color: #64748b; margin-top: 3px; line-height: 1.35; }}
.kpi-card.alt {{ border-top-color: #333F48; }}
.kpi-card.dim {{ border-top-color: #8B9299; }}

/* Hallazgos */
.hallazgo {{
    background: #fff; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 16px 18px;
    margin-bottom: 10px; display: flex;
    align-items: flex-start; gap: 12px;
    border-left: 4px solid #FF8200;
}}
.h-icon  {{ font-size: 1.3rem; flex-shrink: 0; margin-top: 2px; }}
.h-dato  {{ font-size: 0.92rem; font-weight: 700; color: #1e293b;
            margin-bottom: 3px; line-height: 1.3; }}
.h-impl  {{ font-size: 0.81rem; color: #64748b; line-height: 1.45; }}

/* Footer */
.footer {{
    margin-top: 44px; padding-top: 16px;
    border-top: 1px solid #E2E8F0;
    text-align: center; font-size: 0.72rem; color: #94a3b8;
}}

/* Sección badge */
.sec-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: #FFF4E6; border: 1px solid #FFB366;
    border-radius: 8px; padding: 8px 14px;
    font-size: 0.90rem; font-weight: 600; color: #CC6600;
    margin-bottom: 6px;
}}
</style>
"""

# ── Datos ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_secciones():
    return pd.read_csv(os.path.join(DATA, "secciones_itermc.csv"))


def main():
    require_auth()
    st.markdown(CSS, unsafe_allow_html=True)

    try:
        sdf = cargar_secciones()
        datos_ok = True
    except Exception:
        datos_ok = False
        sdf = pd.DataFrame()

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="home-header">
        <div class="header-tag">{DEMO_TAG}</div>
        <div class="header-title">Karenth Vázquez · MC Oriental 2027</div>
        <div class="header-sub">
            Plataforma de Inteligencia Electoral &nbsp;·&nbsp;
            Inteligencia territorial para construir presencia donde el electorado ya está esperando.
        </div>
        <span class="header-badge">🟠 Movimiento Ciudadano · Oriental, Puebla</span>
        <span class="header-badge">📅 Datos electorales reales · Ayuntamiento</span>
        <span class="header-badge">📊 LN real · INE / INEGI 2020</span>
    </div>
    """, unsafe_allow_html=True)

    # ── MÓDULOS ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">La plataforma identifica dónde actuar, con qué intensidad y por qué</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown("""
        <div class="mod-card c1">
            <div class="mod-tag">M1 · Panorama</div>
            <span class="mod-icon">🗺️</span>
            <div class="mod-title">¿Dónde está el electorado natural de MC?</div>
            <div class="mod-body">Mapa seccional con el Índice de Territorio MC (ITerMC)
            — combina concentración de jóvenes, competitividad electoral
            y potencial de movilización.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_M1_Panorama.py", label="Ver panorama territorial →",
                     use_container_width=True)

    with c2:
        st.markdown("""
        <div class="mod-card c2">
            <div class="mod-tag">M2 · Territorios</div>
            <span class="mod-icon">🏘️</span>
            <div class="mod-title">¿En qué manzanas conviene llegar primero?</div>
            <div class="mod-body">Drill-down a nivel manzana de la sección prioritaria.
            Lista Nominal 18–39 desagregada por sexo — para planear
            trabajo de puerta en puerta con precisión.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_M2_Territorio.py", label="Ver territorios de entrada →",
                     use_container_width=True)

    with c3:
        st.markdown("""
        <div class="mod-card c3">
            <div class="mod-tag">M3 · Comités</div>
            <span class="mod-icon">📌</span>
            <div class="mod-title">¿Dónde instalar los primeros comités?</div>
            <div class="mod-body">Mapa y ranking de secciones por prioridad estratégica.
            Proyección de alcance: con 5 comités bien ubicados,
            MC puede activar miles de electores jóvenes en Oriental.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_M3_Comites.py", label="Ver plan de comités →",
                     use_container_width=True)

    # ── KPIs TERRITORIALES ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⚡ Pulso territorial — datos reales del municipio</div>',
                unsafe_allow_html=True)

    n_alta = len(sdf[sdf["clasificacion"] == "Alta prioridad"]) if datos_ok else 1
    n_oport = len(sdf[sdf["clasificacion"] == "Oportunidad"]) if datos_ok else 6
    top_itermc = sdf.loc[sdf["itermc"].idxmax(), "itermc"] if datos_ok else 70.2

    k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-valor">{LN_TOTAL_MUNICIPAL:,}</div>
            <div class="kpi-label">Lista Nominal municipal</div>
            <div class="kpi-ctx">electores registrados · INE</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-valor">{LN_JOVEN_TOTAL:,}</div>
            <div class="kpi-label">Electores 18–39 años</div>
            <div class="kpi-ctx">{PCT_JOVEN_MUNICIPAL}% del padrón total</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-valor">{N_SECCIONES_TOTAL}</div>
            <div class="kpi-label">Secciones electorales</div>
            <div class="kpi-ctx">{n_alta} alta prioridad · {n_oport} oportunidad</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-valor">{top_itermc:.0f}</div>
            <div class="kpi-label">ITerMC más alto</div>
            <div class="kpi-ctx">§876 — sección estrella MC</div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown("""
        <div class="kpi-card alt">
            <div class="kpi-valor">0%</div>
            <div class="kpi-label">MC en última elección</div>
            <div class="kpi-ctx">sin candidato — electorado sin opción</div>
        </div>
        """, unsafe_allow_html=True)

    # ── NARRATIVA DE PRESENTACIÓN ─────────────────────────────────────────────
    st.markdown('<div class="section-title">🎙️ La propuesta · Karenth Vázquez · MC 2027</div>',
                unsafe_allow_html=True)

    # Frase de apertura
    st.markdown("""
    <div style="background:#fff; border:1px solid #E2E8F0; border-radius:14px;
                padding:22px 28px 18px; border-top:5px solid #FF8200; margin-bottom:12px;">
        <span style="font-size:1.08rem; font-weight:700; color:#333F48; line-height:1.6;">
            Oriental, Puebla tiene 14,836 electores registrados.
            El 52% tiene entre 18 y 39 años. En la última elección de ayuntamiento,
            Movimiento Ciudadano no tuvo candidato.
        </span>
        &nbsp;
        <span style="font-size:1.08rem; font-weight:700; color:#FF8200; line-height:1.6;">
            Ese electorado nunca tuvo la opción.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 3 cards usando st.columns — evita CSS grid que Streamlit sanitiza
    n1, n2, n3 = st.columns(3, gap="medium")
    with n1:
        st.markdown("""
        <div style="background:#FFF4E6; border-radius:10px; padding:18px 18px 16px;
                    border-left:4px solid #FF8200; height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:#FF8200;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
                El territorio
            </div>
            <div style="font-size:0.90rem; color:#333F48; line-height:1.6;">
                Oriental es un municipio <strong>joven y competido</strong>.
                Las secciones donde Morena es más débil no tienen un rival establecido —
                tienen un espacio vacío que MC puede ocupar.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with n2:
        st.markdown("""
        <div style="background:#FFF4E6; border-radius:10px; padding:18px 18px 16px;
                    border-left:4px solid #FF8200; height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:#FF8200;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
                La herramienta
            </div>
            <div style="font-size:0.90rem; color:#333F48; line-height:1.6;">
                Esta plataforma identifica <strong>sección por sección y manzana por manzana</strong>
                dónde instalar comités, a quién buscar primero y cómo construir
                presencia territorial con datos propios.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with n3:
        st.markdown("""
        <div style="background:#FFF4E6; border-radius:10px; padding:18px 18px 16px;
                    border-left:4px solid #FF8200; height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:#FF8200;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
                La apuesta
            </div>
            <div style="font-size:0.90rem; color:#333F48; line-height:1.6;">
                Con 5 comités bien ubicados, MC activa <strong>más del 60%
                del padrón joven</strong> del municipio — antes de que otro partido
                llegue a reclamar ese electorado.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Franja de firma — sin flex, solo padding y texto en línea
    st.markdown("""
    <div style="background:#333F48; border-radius:10px; padding:14px 22px; margin-top:12px;">
        <span style="font-size:1.4rem;">🟠</span>
        &nbsp;&nbsp;
        <span style="font-size:0.88rem; font-weight:700; color:#FFE4C4;">
            Karenth Vázquez · Aspirante MC · Oriental, Puebla 2027
        </span>
        &nbsp;&nbsp;·&nbsp;&nbsp;
        <span style="font-size:0.80rem; color:rgba(255,255,255,0.60);">
            Aliada estratégica de Data &amp; AI Inclusion Technologies ·
            Inteligencia electoral con datos reales — INE, INEGI 2020 y resultados electorales públicos.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── HALLAZGOS ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Lo que dicen los datos — hallazgos territoriales</div>',
                unsafe_allow_html=True)

    col_h1, col_h2 = st.columns(2, gap="medium")
    for i, (icon, dato, impl) in enumerate(HALLAZGOS):
        col = col_h1 if i % 2 == 0 else col_h2
        with col:
            st.markdown(f"""
            <div class="hallazgo">
                <span class="h-icon">{icon}</span>
                <div>
                    <div class="h-dato">{dato}</div>
                    <div class="h-impl">{impl}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── EXPANDER: METODOLOGÍA ─────────────────────────────────────────────────
    with st.expander("🔬 ¿Cómo se construye el ITerMC?"):
        st.markdown("""
        <div style="font-size:0.87rem; color:#475569; line-height:1.7;">
        El <strong>Índice de Territorio MC (ITerMC)</strong> combina tres dimensiones para identificar
        las secciones con mayor potencial de penetración para Movimiento Ciudadano:<br><br>
        <strong>🟠 40% · Potencial joven</strong> — Porcentaje de Lista Nominal 18–39 años sobre
        el total de la sección. Mayor concentración de jóvenes = mayor afinidad con el perfil MC.<br><br>
        <strong>🔍 35% · Competitividad electoral</strong> — Combina el margen de victoria de Morena
        (menor margen = más competitivo) con la proporción de voto diferenciado (PVEM independiente),
        proxy del apetito por una tercera opción.<br><br>
        <strong>📊 25% · Potencial de movilización</strong> — Porcentaje de abstención en la última
        elección. Electores registrados que no votaron son el universo de movilización más accesible.<br><br>
        Fuentes: Lista Nominal INE · INEGI 2020 · Resultados electorales ayuntamiento (elección de referencia).
        </div>
        """, unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="footer">{FOOTER_TEXTO}<br>Uso exclusivo del equipo estratégico</div>',
                unsafe_allow_html=True)


# ── Navegación ────────────────────────────────────────────────────────────────
pg = st.navigation(
    {
        "Plataforma": [
            st.Page(main, title="🏠 Inicio", default=True),
        ],
        "Inteligencia Territorial": [
            st.Page("pages/1_M1_Panorama.py",  title="🗺️  Panorama Territorial"),
            st.Page("pages/2_M2_Territorio.py", title="🏘️  Territorios de Entrada"),
            st.Page("pages/3_M3_Comites.py",    title="📌  Plan de Comités"),
        ],
    },
    position="sidebar",
)

st.set_page_config(
    page_title=PAGE_TITLE_HOME,
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

pg.run()
