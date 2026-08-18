"""
M3 · Plan de Comités — PIE Oriental
Mapa de priorización + proyección de alcance
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
    border-radius: 14px; padding: 28px 36px 22px; margin-bottom: 24px;
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
.comite-card {{
    background:#fff; border:1px solid #E2E8F0; border-radius:12px;
    padding:18px 20px; margin-bottom:10px;
    border-left:5px solid #FF8200;
}}
.comite-card.p2 {{ border-left-color:#FFB366; }}
.comite-card.p3 {{ border-left-color:#CBD5E0; }}
.comite-rank {{
    font-size:0.72rem; font-weight:700; color:#94a3b8;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;
}}
.comite-sec {{
    font-size:1.1rem; font-weight:700; color:#1e293b; margin-bottom:4px;
}}
.comite-score {{
    display:inline-block; background:#FF8200; color:#fff;
    border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:700;
    margin-left:6px; vertical-align:middle;
}}
.comite-score.p2 {{ background:#FFB366; color:#333; }}
.comite-score.p3 {{ background:#8B9299; }}
.comite-rec {{
    font-size:0.85rem; color:#FF8200; font-weight:600; margin-bottom:4px;
}}
.comite-rec.p2 {{ color:#CC6600; }}
.comite-rec.p3 {{ color:#8B9299; }}
.comite-stats {{
    font-size:0.78rem; color:#64748b; margin-top:4px;
    display:flex; gap:16px; flex-wrap:wrap;
}}
.comite-stat {{ white-space:nowrap; }}
.alcance-box {{
    background: linear-gradient(135deg, #1C2429 0%, #FF8200 100%);
    border-radius:14px; padding:28px 32px; color:#fff; margin-bottom:20px;
}}
.alcance-title {{ font-size:1.1rem; font-weight:700; color:#FFE4C4;
                  margin-bottom:16px; }}
.alcance-num {{ font-size:3.0rem; font-weight:700; color:#fff; line-height:1.1; }}
.alcance-sub {{ font-size:0.88rem; color:rgba(255,255,255,0.75); margin-top:4px; }}
.alcance-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px; }}
.alcance-item {{ background:rgba(255,255,255,0.10); border-radius:8px; padding:12px 14px; }}
.alcance-item-val {{ font-size:1.5rem; font-weight:700; color:#fff; }}
.alcance-item-lbl {{ font-size:0.76rem; color:rgba(255,255,255,0.70); margin-top:2px; }}
.narrativa-box {{
    background:#FFF4E6; border:1px solid #FFB366; border-radius:12px;
    padding:20px 24px; margin-bottom:16px;
    font-size:0.90rem; color:#8B4000; line-height:1.65;
}}
.narrativa-box strong {{ color:#FF8200; }}
.narrativa-box h4 {{ color:#333F48; margin-bottom:10px; font-size:1.0rem; }}
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

def centroide_seccion(geo, seccion):
    feats = [f for f in geo["features"] if f["properties"]["SECCION"] == seccion]
    all_coords = []
    for feat in feats:
        coords = feat["geometry"]["coordinates"][0]
        if isinstance(coords[0][0], list):
            coords = coords[0]
        all_coords.extend(coords)
    if not all_coords:
        return MAPA_LAT, MAPA_LON
    return (sum(c[1] for c in all_coords) / len(all_coords),
            sum(c[0] for c in all_coords) / len(all_coords))

def color_por_itermc(itermc):
    if itermc >= ITERMC_UMBRAL_ALTA:
        return COLOR_ALTA
    elif itermc >= ITERMC_UMBRAL_OPT:
        return COLOR_OPT
    else:
        return COLOR_DIFICIL

def construir_mapa_comites(sdf, geo, contornos, n_comites):
    """Mapa con secciones coloreadas + pins de comités."""
    m = folium.Map(location=[MAPA_LAT, MAPA_LON], zoom_start=MAPA_ZOOM,
                   tiles="CartoDB positron")

    itermc_map = dict(zip(sdf["seccion"], sdf["itermc"]))
    clasif_map = dict(zip(sdf["seccion"], sdf["clasificacion"]))
    rec_map    = dict(zip(sdf["seccion"], sdf["recomendacion"]))
    ln39_map   = dict(zip(sdf["seccion"], sdf["LN_1839"]))

    sdf_sorted = sdf.sort_values("itermc", ascending=False)
    comites_secs = set(sdf_sorted.head(n_comites)["seccion"].tolist())

    # Colorear manzanas por sección
    for feat in geo["features"]:
        p   = feat["properties"]
        sec = p["SECCION"]
        it  = itermc_map.get(sec, 35)
        es_comite = sec in comites_secs

        if es_comite:
            col  = "#FF8200"
            opac = 0.80
        elif it >= ITERMC_UMBRAL_OPT:
            col  = "#FFE4C4"
            opac = 0.50
        else:
            col  = "#CBD5E0"
            opac = 0.30

        tip = f"§{sec} · ITerMC {it:.1f}<br>{clasif_map.get(sec,'')}"
        if es_comite:
            tip += "<br>📌 <b>Comité recomendado</b>"

        folium.GeoJson(
            feat,
            style_function=lambda f, c=col, o=opac: {
                "fillColor": c, "color": "#fff", "weight": 0.8, "fillOpacity": o,
            },
            tooltip=folium.Tooltip(tip, sticky=True),
        ).add_to(m)

    # ── Contornos seccionales ────────────────────────────────────────────────
    sdf_sorted_local = sdf.sort_values("itermc", ascending=False)
    comites_set = set(sdf_sorted_local.head(n_comites)["seccion"].tolist())
    for feat in contornos["features"]:
        sec  = feat["properties"]["SECCION"]
        es_c = sec in comites_set
        folium.GeoJson(
            feat,
            style_function=lambda f, c=es_c: {
                "fillColor": "transparent",
                "fillOpacity": 0,
                "color": "#FF8200" if c else "#333F48",
                "weight": 3.5 if c else 1.5,
                "dashArray": None if c else "5 4",
            },
            tooltip=folium.Tooltip(
                f"§{sec}" + (" · 📌 Comité" if es_c else ""), sticky=False
            ),
        ).add_to(m)

    # Pins de comités
    for rank, (_, row) in enumerate(sdf_sorted.head(n_comites).iterrows(), 1):
        sec   = int(row["seccion"])
        clat, clon = centroide_seccion(geo, sec)
        ln_j = int(row["LN_1839"])

        folium.Marker(
            location=[clat, clon],
            icon=folium.DivIcon(
                html=f"""<div style='
                    background:#FF8200; color:#fff; font-weight:700;
                    font-size:13px; width:32px; height:32px;
                    border-radius:50%; display:flex; align-items:center;
                    justify-content:center; box-shadow:0 3px 8px rgba(0,0,0,0.35);
                    border:2px solid #fff; font-family:DM Sans,sans-serif;
                '>#{rank}</div>""",
                icon_size=(32, 32), icon_anchor=(16, 16),
            ),
            tooltip=folium.Tooltip(
                f"<b>Comité #{rank} · §{sec}</b><br>"
                f"ITerMC: {row['itermc']:.1f}<br>"
                f"LN 18–39: {ln_j:,}<br>"
                f"{rec_map.get(sec, '')}",
                sticky=True,
            ),
        ).add_to(m)

    return m

def main():
    st.set_page_config(page_title=PAGE_TITLE_M3, page_icon="📌",
                       layout="wide", initial_sidebar_state="collapsed")
    require_auth()
    st.markdown(CSS, unsafe_allow_html=True)

    sdf, geo, contornos = cargar_datos()
    sdf_sorted = sdf.sort_values("itermc", ascending=False)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-tag">M3 · Plan de Comités · {MUNICIPIO}, {ESTADO}</div>
        <div class="page-title">¿Dónde instalar los primeros comités de MC?</div>
        <div class="page-sub">
            Priorización territorial con base en ITerMC —
            con 5 comités bien ubicados, MC puede activar el mayor potencial
            de electores jóvenes del municipio.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Selector de comités ───────────────────────────────────────────────────
    col_ctrl, col_proj = st.columns([1, 2], gap="medium")

    with col_ctrl:
        n_comites = st.slider(
            "**Número de comités a instalar**",
            min_value=1, max_value=7, value=5,
            help="Ajusta cuántos comités deseas ver en el mapa y en la proyección"
        )

    comites_df = sdf_sorted.head(n_comites)
    ln_joven_activable = int(comites_df["LN_1839"].sum())
    alcance_directo    = ln_joven_activable
    alcance_red        = int(ln_joven_activable * 2.5)  # red de contacto estimada
    pct_padrón_joven   = round(ln_joven_activable / LN_JOVEN_TOTAL * 100, 1)

    with col_proj:
        st.markdown(f"""
        <div class="alcance-box">
            <div class="alcance-title">📊 Proyección de alcance · {n_comites} comités</div>
            <div class="alcance-num">{ln_joven_activable:,}</div>
            <div class="alcance-sub">electores 18–39 en zona de influencia directa</div>
            <div class="alcance-grid">
                <div class="alcance-item">
                    <div class="alcance-item-val">{pct_padrón_joven}%</div>
                    <div class="alcance-item-lbl">del padrón joven municipal</div>
                </div>
                <div class="alcance-item">
                    <div class="alcance-item-val">{alcance_red:,}</div>
                    <div class="alcance-item-lbl">alcance de red estimado (×2.5)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Layout: mapa + ranking ────────────────────────────────────────────────
    col_mapa, col_lista = st.columns([3, 2], gap="medium")

    with col_mapa:
        st.markdown(f'<div class="section-title">🗺️ Mapa · {n_comites} comités recomendados</div>',
                    unsafe_allow_html=True)
        with st.spinner("Generando mapa de comités…"):
            m = construir_mapa_comites(sdf, geo, contornos, n_comites)
            st_folium(m, width="100%", height=500, returned_objects=[])

    with col_lista:
        st.markdown('<div class="section-title">📋 Ranking de comités</div>',
                    unsafe_allow_html=True)

        for rank, (_, row) in enumerate(sdf_sorted.iterrows(), 1):
            clasif = row["clasificacion"]
            card_c = "" if clasif == "Alta prioridad" else ("p2" if clasif == "Oportunidad" else "p3")
            score_c = "" if clasif == "Alta prioridad" else card_c
            rec_c   = "" if clasif == "Alta prioridad" else card_c
            es_comite = rank <= n_comites
            opac_style = "" if es_comite else "opacity:0.45;"

            st.markdown(f"""
            <div class="comite-card {card_c}" style="{opac_style}">
                <div class="comite-rank">
                    {'📌 Comité #' + str(rank) if es_comite else f'#{rank} · No priorizado aún'}
                </div>
                <div class="comite-sec">
                    §{int(row['seccion'])}
                    <span class="comite-score {score_c}">ITerMC {row['itermc']:.1f}</span>
                </div>
                <div class="comite-rec {rec_c}">→ {row['recomendacion']}</div>
                <div class="comite-stats">
                    <span class="comite-stat">👥 LN 18–39: {int(row['LN_1839']):,}</span>
                    <span class="comite-stat">🗳️ Morena: {row['pct_morena']}%</span>
                    <span class="comite-stat">🔀 3ª vía: {row['pct_pvem']}%</span>
                    <span class="comite-stat">📊 Abst: {row['abstencion']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Narrativa estratégica ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">🎯 La narrativa estratégica para la dirigencia</div>',
                unsafe_allow_html=True)

    # Título
    st.markdown("""
    <div style="font-size:1.0rem; font-weight:700; color:#333F48;
                margin-bottom:12px;">
        ¿Por qué Oriental es viable para MC en 2027?
    </div>
    """, unsafe_allow_html=True)

    # Párrafo 1
    st.markdown("""
    <div style="background:#FFF4E6; border-left:4px solid #FF8200; border-radius:0 8px 8px 0;
                padding:14px 18px; margin-bottom:8px;
                font-size:0.90rem; color:#8B4000; line-height:1.65;">
        <span style="font-weight:700; color:#FF8200;">El electorado ya existe — nadie lo ha reclamado.</span>
        &nbsp;Oriental tiene 7,711 electores entre 18 y 39 años, que representan el 52% del padrón.
        En la última elección de ayuntamiento, MC no tuvo candidato.
        Eso no es un fracaso — es una oportunidad de primer acceso sin desgaste acumulado.
    </div>
    """, unsafe_allow_html=True)

    # Párrafo 2
    st.markdown("""
    <div style="background:#FFF4E6; border-left:4px solid #FF8200; border-radius:0 8px 8px 0;
                padding:14px 18px; margin-bottom:8px;
                font-size:0.90rem; color:#8B4000; line-height:1.65;">
        <span style="font-weight:700; color:#FF8200;">La competencia es débil donde más importa.</span>
        &nbsp;En §876 y §881, Morena ganó con apenas 1 de cada 3 votos.
        En 7 de 9 secciones, entre el 18% y el 31% del electorado eligió al PVEM como alternativa.
        Esos votantes rechazan el bipartidismo — son el electorado natural de MC en Oriental.
    </div>
    """, unsafe_allow_html=True)

    # Párrafo 3 — dinámico con n_comites
    st.markdown(f"""
    <div style="background:#FFF4E6; border-left:4px solid #FF8200; border-radius:0 8px 8px 0;
                padding:14px 18px; margin-bottom:8px;
                font-size:0.90rem; color:#8B4000; line-height:1.65;">
        <span style="font-weight:700; color:#FF8200;">Con {n_comites} comités bien ubicados,
        MC cubre {pct_padrón_joven}% del padrón joven ({ln_joven_activable:,} electores).</span>
        &nbsp;No se trata de cubrir todo el municipio desde el primer día —
        se trata de instalar presencia donde el retorno por esfuerzo es máximo.
        §876 primero. §877 y §882 en segundo nivel. La estrategia está en los datos.
    </div>
    """, unsafe_allow_html=True)

    # ── Gráfico: LN joven por sección con umbral comité ──────────────────────
    st.markdown('<div class="section-title">📊 LN 18–39 por sección · potencial activable</div>',
                unsafe_allow_html=True)

    fig = go.Figure()
    colors = ["#FF8200" if i < n_comites else "#CBD5E0"
              for i in range(len(sdf_sorted))]
    labels = [f"§{int(s)}" for s in sdf_sorted["seccion"]]

    fig.add_trace(go.Bar(
        x=labels, y=sdf_sorted["LN_1839"],
        marker_color=colors,
        marker_line_color="#fff", marker_line_width=1.5,
        text=sdf_sorted["LN_1839"],
        textposition="outside",
        textfont=dict(size=12, color="#333F48"),
    ))
    # Anotación acumulado
    acum = int(sdf_sorted.head(n_comites)["LN_1839"].sum())
    fig.add_annotation(
        x=labels[n_comites - 1],
        y=sdf_sorted.head(n_comites)["LN_1839"].max() + 100,
        text=f"Acumulado: {acum:,} jóvenes",
        showarrow=True, arrowhead=2, arrowcolor="#FF8200",
        font=dict(color="#FF8200", size=12, family="DM Sans"),
    )

    fig.update_layout(
        height=300,
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        yaxis=dict(title="LN 18–39", gridcolor="#F0F0F0"),
        xaxis=dict(title="Sección"),
        font=dict(family="DM Sans", color="#333F48"),
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟠 Naranja = secciones incluidas en el plan de comités seleccionado · ⬜ Gris = secciones fuera del plan")

    # ── Navegación ────────────────────────────────────────────────────────────
    st.markdown("<div class='nav-row'>", unsafe_allow_html=True)
    nav1, nav_mid, nav2 = st.columns([1, 4, 1])
    with nav1:
        if st.button("← Territorios", use_container_width=True):
            st.switch_page("pages/2_M2_Territorio.py")
    with nav2:
        if st.button("↩ Inicio", use_container_width=True):
            st.switch_page("Home.py")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="footer">{FOOTER_TEXTO}</div>', unsafe_allow_html=True)

main()