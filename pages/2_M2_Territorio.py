"""
M2 · Territorios de Entrada — PIE Oriental
Drill-down a nivel manzana de la sección seleccionada
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json, os, sys
from shapely.geometry import shape, Point

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
.kpi-mini {{ background:#fff; border:1px solid #E2E8F0; border-radius:10px;
             padding:14px; border-top:3px solid #FF8200; margin-bottom:10px; }}
.kpi-mini.alt {{ border-top-color:#FFB366; }}
.kpi-mini.dim {{ border-top-color:#8B9299; }}
.kpi-mini-val {{ font-size:1.5rem; font-weight:700; color:#1e293b; }}
.kpi-mini-lbl {{ font-size:0.73rem; color:#64748b; margin-top:2px; }}
.insight-box {{
    background:#FFF4E6; border:1px solid #FFB366; border-radius:10px;
    padding:14px 16px; margin-bottom:10px;
    font-size:0.86rem; color:#8B4000; line-height:1.55;
}}
.insight-box strong {{ color:#FF8200; }}
.mza-row {{
    display:flex; align-items:center; gap:10px;
    padding:8px 12px; border-radius:8px; margin-bottom:4px;
    background:#F8F9FA; border-left:3px solid #FFB366;
}}
.mza-row.top {{ background:#FFF4E6; border-left-color:#FF8200; }}
.mza-num {{ font-size:0.88rem; font-weight:700; color:#333F48; min-width:48px; }}
.mza-bar-wrap {{ flex:1; height:8px; background:#E2E8F0; border-radius:4px; overflow:hidden; }}
.mza-bar {{ height:100%; border-radius:4px; }}
.mza-val {{ font-size:0.80rem; color:#475569; min-width:80px; text-align:right; }}
.legend-box {{
    background:#fff; border:1px solid #E2E8F0; border-radius:10px; padding:14px 16px;
}}
.legend-item {{ display:flex; align-items:center; gap:8px;
                font-size:0.82rem; color:#333F48; margin-bottom:6px; }}
.legend-dot {{ width:14px; height:14px; border-radius:3px; flex-shrink:0; }}
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

def color_por_percentil(valor, p25, p50, p75):
    """Coloriza por percentil interno — garantiza diferenciación visual en cualquier sección."""
    if valor >= p75:
        return "#CC5500"    # naranja oscuro — top 25%
    elif valor >= p50:
        return "#FF8200"    # naranja MC — 50-75%
    elif valor >= p25:
        return "#FFB366"    # naranja suave — 25-50%
    else:
        return "#FFE4C4"    # naranja pálido — bottom 25%

def construir_mapa_manzanas(geo, contornos, seccion_sel):
    """Mapa de manzanas de la sección seleccionada, coloreadas por % LN joven."""
    feats_sec = [f for f in geo["features"]
                 if f["properties"]["SECCION"] == seccion_sel]

    if not feats_sec:
        return None

    # Centroide aproximado
    all_coords = []
    for feat in feats_sec:
        coords = feat["geometry"]["coordinates"][0]
        if isinstance(coords[0][0], list):
            coords = coords[0]
        all_coords.extend(coords)
    clat = sum(c[1] for c in all_coords) / len(all_coords)
    clon = sum(c[0] for c in all_coords) / len(all_coords)

    m = folium.Map(location=[clat, clon], zoom_start=15,
                   tiles="CartoDB positron")

    # Calcular percentiles de LN 18-39 entre manzanas con datos
    valores_j = [f["properties"]["LN_1839_est"]
                 for f in feats_sec if f["properties"]["LN_estimada"] > 0]
    if len(valores_j) >= 4:
        valores_j_sorted = sorted(valores_j)
        n = len(valores_j_sorted)
        p25 = valores_j_sorted[n // 4]
        p50 = valores_j_sorted[n // 2]
        p75 = valores_j_sorted[3 * n // 4]
    else:
        p25, p50, p75 = 1, 2, 3

    for feat in feats_sec:
        p   = feat["properties"]
        mza = p["MZA"]
        ln_est  = p["LN_estimada"]
        ln_j    = p["LN_1839_est"]
        ln_h    = p["LN_H_est"]
        ln_m_v  = p["LN_M_est"]
        prior50 = p["prioridad_50"]

        pct_j = (ln_j / ln_est * 100) if ln_est > 0 else 0
        col   = color_por_percentil(ln_j, p25, p50, p75) if ln_est > 0 else "#E2E8F0"
        opac  = 0.80 if ln_est > 0 else 0.12

        tooltip_html = f"""
        <b>Manzana {mza} · §{seccion_sel}</b><br>
        LN estimada: <b>{ln_est}</b><br>
        18–39: <b>{ln_j}</b> ({pct_j:.0f}%)<br>
        Hombres 18–39: {ln_h} &nbsp;|&nbsp; Mujeres 18–39: {ln_m_v}<br>
        {'⭐ <b>Prioridad 50%</b>' if prior50 else ''}
        """

        folium.GeoJson(
            feat,
            style_function=lambda f, c=col, op=opac: {
                "fillColor": c,
                "color": "#ffffff",
                "weight": 1.0,
                "fillOpacity": op,
            },
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)

    # ── Contorno seccional encima ────────────────────────────────────────────
    for feat in contornos["features"]:
        sec    = feat["properties"]["SECCION"]
        es_sel = (sec == seccion_sel)
        folium.GeoJson(
            feat,
            style_function=lambda f, sel=es_sel: {
                "fillColor": "transparent",
                "fillOpacity": 0,
                "color": "#FF8200" if sel else "#333F48",
                "weight": 4.0 if sel else 2.0,
                "dashArray": None if sel else "6 4",
            },
        ).add_to(m)

    return m

def main():
    st.set_page_config(page_title=PAGE_TITLE_M2, page_icon="🏘️",
                       layout="wide", initial_sidebar_state="collapsed")
    require_auth()
    st.markdown(CSS, unsafe_allow_html=True)

    sdf, geo, contornos = cargar_datos()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-tag">M2 · Territorios de Entrada · {MUNICIPIO}, {ESTADO}</div>
        <div class="page-title">¿En qué manzanas llegar primero?</div>
        <div class="page-sub">
            Concentración de Lista Nominal 18–39 a nivel manzana —
            para planear trabajo de puerta en puerta con precisión quirúrgica.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Selector de sección ───────────────────────────────────────────────────
    secciones_ord = (sdf.sort_values("itermc", ascending=False)["seccion"]
                     .astype(int).tolist())
    # Mover sección estrella al inicio
    if SECCION_ESTRELLA in secciones_ord:
        secciones_ord = ([SECCION_ESTRELLA] +
                         [s for s in secciones_ord if s != SECCION_ESTRELLA])

    col_sel, col_info = st.columns([1, 2], gap="medium")
    with col_sel:
        itermc_labels = {int(r["seccion"]): f"§{int(r['seccion'])} · ITerMC {r['itermc']:.1f}"
                         for _, r in sdf.iterrows()}
        sec_options = [itermc_labels[s] for s in secciones_ord]
        sel_label = st.selectbox(
            "**Selecciona una sección**",
            options=sec_options,
            index=0,
            help="Ordenadas de mayor a menor ITerMC"
        )
        seccion_sel = secciones_ord[sec_options.index(sel_label)]

    row = sdf[sdf["seccion"] == seccion_sel].iloc[0]
    with col_info:
        clasif_col = {"Alta prioridad": "#FF8200",
                      "Oportunidad": "#FFB366",
                      "Terreno difícil": "#8B9299"}.get(row["clasificacion"], "#FF8200")
        st.markdown(f"""
        <div style="background:#fff; border:1px solid #E2E8F0; border-radius:10px;
                    padding:14px 18px; border-left:5px solid {clasif_col};">
            <span style="font-size:0.75rem; font-weight:700; color:#64748b;
                         text-transform:uppercase; letter-spacing:0.1em;">
                {row['clasificacion']}  ·  ITerMC {row['itermc']:.1f}
            </span><br>
            <span style="font-size:0.96rem; font-weight:700; color:#FF8200;">
                → {row['recomendacion']}
            </span><br>
            <span style="font-size:0.82rem; color:#475569;">
                LN Total: {int(row['LN_total']):,} &nbsp;|&nbsp;
                LN 18–39: {int(row['LN_1839']):,} ({row['pct_joven']}%) &nbsp;|&nbsp;
                Morena: {row['pct_morena']}% &nbsp;|&nbsp;
                PVEM 3ª vía: {row['pct_pvem']}%
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── Layout: mapa + sidebar ────────────────────────────────────────────────
    col_mapa, col_panel = st.columns([3, 1], gap="medium")

    feats_sec = [f for f in geo["features"]
                 if f["properties"]["SECCION"] == seccion_sel]
    mzas_con_ln = [f for f in feats_sec if f["properties"]["LN_estimada"] > 0]
    mzas_prior  = [f for f in feats_sec if f["properties"]["prioridad_50"]]

    with col_panel:
        st.markdown('<div class="section-title">📊 Resumen de sección</div>',
                    unsafe_allow_html=True)
        total_ln_est = sum(f["properties"]["LN_estimada"] for f in feats_sec)
        total_j_est  = sum(f["properties"]["LN_1839_est"] for f in feats_sec)
        pct_j_est    = round(total_j_est / total_ln_est * 100, 1) if total_ln_est else 0

        st.markdown(f"""
        <div class="kpi-mini">
            <div class="kpi-mini-val">{len(feats_sec)}</div>
            <div class="kpi-mini-lbl">Manzanas totales</div>
        </div>
        <div class="kpi-mini">
            <div class="kpi-mini-val">{len(mzas_con_ln)}</div>
            <div class="kpi-mini-lbl">Manzanas con electores</div>
        </div>
        <div class="kpi-mini alt">
            <div class="kpi-mini-val">{len(mzas_prior)}</div>
            <div class="kpi-mini-lbl">Manzanas prioritarias (top 50%)</div>
        </div>
        <div class="kpi-mini">
            <div class="kpi-mini-val">{total_j_est:,}</div>
            <div class="kpi-mini-lbl">LN 18–39 estimada en sección</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">🎨 Intensidad jóvenes</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="legend-box">
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">
                Concentración relativa dentro de la sección
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#CC5500;"></div>
                <span><b>Muy alta</b> — top 25%</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#FF8200;"></div>
                <span><b>Alta</b> — 50–75%</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#FFB366;"></div>
                <span><b>Media</b> — 25–50%</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#FFE4C4;"></div>
                <span><b>Baja</b> — bottom 25%</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#E2E8F0;"></div>
                <span><b>Sin datos</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_mapa:
        st.markdown(f'<div class="section-title">🏘️ Manzanas · §{seccion_sel} — haz clic en una manzana</div>',
                    unsafe_allow_html=True)
        with st.spinner("Cargando manzanas…"):
            m = construir_mapa_manzanas(geo, contornos, seccion_sel)
            if m:
                mapa_data = st_folium(
                    m, width="100%", height=500,
                    returned_objects=["last_clicked"],
                    key=f"mapa_m2_{seccion_sel}",
                )
            else:
                mapa_data = None
                st.warning("No hay geometría disponible para esta sección.")

    # ── Detectar manzana clickeada via point-in-polygon ───────────────────────
    mza_sel = None
    if mapa_data and mapa_data.get("last_clicked"):
        lc = mapa_data["last_clicked"]
        click_pt = Point(lc["lng"], lc["lat"])
        for feat in feats_sec:
            try:
                if shape(feat["geometry"]).contains(click_pt):
                    p = feat["properties"]
                    if p["LN_estimada"] > 0:
                        mza_sel = p
                    break
            except Exception:
                continue

    # ── Card de manzana seleccionada ──────────────────────────────────────────
    if mza_sel:
        p      = mza_sel
        ln_est = p["LN_estimada"]
        ln_j   = p["LN_1839_est"]
        ln_h   = p["LN_H_est"]
        ln_m   = p["LN_M_est"]
        pct_j  = round(ln_j / ln_est * 100, 1) if ln_est else 0
        pct_h  = round(ln_h / ln_j * 100, 1) if ln_j else 0
        pct_m  = round(ln_m / ln_j * 100, 1) if ln_j else 0
        prior  = "⭐ Prioridad top 50%" if p.get("prioridad_50") else ""

        c_mza1, c_mza2, c_mza3, c_mza4 = st.columns(4, gap="medium")
        with c_mza1:
            st.markdown(f"""
            <div style="background:#FF8200; border-radius:12px; padding:16px 18px; color:#fff;">
                <div style="font-size:0.72rem; font-weight:700; opacity:0.75;
                            text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">
                    Manzana seleccionada {prior}
                </div>
                <div style="font-size:2.0rem; font-weight:700; line-height:1.1;">
                    {p['MZA']}
                </div>
                <div style="font-size:0.78rem; opacity:0.80; margin-top:4px;">
                    §{seccion_sel}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_mza2:
            st.markdown(f"""
            <div style="background:#fff; border:1px solid #E2E8F0; border-radius:12px;
                        padding:16px 18px; border-top:4px solid #FF8200;">
                <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                            text-transform:uppercase; margin-bottom:4px;">LN Total estimada</div>
                <div style="font-size:1.8rem; font-weight:700; color:#1e293b;">{ln_est}</div>
                <div style="font-size:0.75rem; color:#94a3b8;">electores registrados</div>
            </div>
            """, unsafe_allow_html=True)
        with c_mza3:
            st.markdown(f"""
            <div style="background:#fff; border:1px solid #E2E8F0; border-radius:12px;
                        padding:16px 18px; border-top:4px solid #FF8200;">
                <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                            text-transform:uppercase; margin-bottom:4px;">LN 18–39 años</div>
                <div style="font-size:1.8rem; font-weight:700; color:#FF8200;">{ln_j}</div>
                <div style="font-size:0.75rem; color:#94a3b8;">{pct_j}% del total de la manzana</div>
            </div>
            """, unsafe_allow_html=True)
        with c_mza4:
            st.markdown(f"""
            <div style="background:#fff; border:1px solid #E2E8F0; border-radius:12px;
                        padding:16px 18px; border-top:4px solid #FFB366;">
                <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                            text-transform:uppercase; margin-bottom:4px;">Desglose por sexo</div>
                <div style="font-size:1.0rem; font-weight:700; color:#1e293b; margin-bottom:2px;">
                    👨 {ln_h} hombres
                    <span style="font-size:0.75rem; color:#94a3b8;">({pct_h}%)</span>
                </div>
                <div style="font-size:1.0rem; font-weight:700; color:#1e293b;">
                    👩 {ln_m} mujeres
                    <span style="font-size:0.75rem; color:#94a3b8;">({pct_m}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

    # ── Insight box ───────────────────────────────────────────────────────────
    if seccion_sel == 876:
        st.markdown("""
        <div class="insight-box">
            <strong>§876 · Sección estrella MC</strong> — Mayor ITerMC del municipio (70.2).
            Morena apenas superó el 34% de los votos en la última elección.
            El 30.7% eligió PVEM como alternativa — ese electorado está disponible para MC.
            Las <strong>45 manzanas prioritarias</strong> concentran el 50% del potencial joven de la sección.
            El trabajo de puerta en puerta aquí tiene el mayor retorno del municipio.
        </div>
        """, unsafe_allow_html=True)
    elif seccion_sel == 881:
        st.markdown("""
        <div class="insight-box">
            <strong>§881 · La sección más competitiva</strong> — Morena ganó con apenas 30.9% del voto.
            Es la sección donde el voto está más distribuido en todo Oriental.
            Instalar presencia aquí genera visibilidad política real — cualquier candidato con
            estructura puede competir con números reales.
        </div>
        """, unsafe_allow_html=True)
    elif seccion_sel == 877:
        st.markdown("""
        <div class="insight-box">
            <strong>§877 · Mayor potencial de movilización</strong> — Es la sección más grande:
            3,745 en Lista Nominal y <strong>2,000 jóvenes registrados</strong>.
            Con 34.2% de abstención, hay más de 1,200 electores que no votaron en la última elección.
            Movilizar ese universo abstencionista joven es el objetivo de segundo nivel de MC en Oriental.
        </div>
        """, unsafe_allow_html=True)
    else:
        rec_txt = row["recomendacion"]
        st.markdown(f"""
        <div class="insight-box">
            <strong>§{seccion_sel} · {row['clasificacion']}</strong> —
            {rec_txt}. &nbsp;
            LN 18–39: {int(row['LN_1839']):,} electores ({row['pct_joven']}% del padrón).
            Abstención disponible: {row['abstencion']}%.
        </div>
        """, unsafe_allow_html=True)

    # ── Top manzanas por LN joven ─────────────────────────────────────────────
    mza_sel_num = mza_sel["MZA"] if mza_sel else None
    st.markdown(f'<div class="section-title">📋 Top manzanas por concentración joven · §{seccion_sel}</div>',
                unsafe_allow_html=True)

    mzas_data = []
    for feat in mzas_con_ln:
        p = feat["properties"]
        ln_est = p["LN_estimada"]
        ln_j   = p["LN_1839_est"]
        pct_j  = round(ln_j / ln_est * 100, 1) if ln_est > 0 else 0
        mzas_data.append({
            "Manzana": p["MZA"],
            "LN estimada": ln_est,
            "LN 18–39": ln_j,
            "% Jóvenes": pct_j,
            "Hombres 18–39": p["LN_H_est"],
            "Mujeres 18–39": p["LN_M_est"],
            "Prior50": "⭐" if p["prioridad_50"] else "",
        })

    mzas_df = (pd.DataFrame(mzas_data)
               .sort_values("LN 18–39", ascending=False)
               .head(20)
               .reset_index(drop=True))

    # Gráfico horizontal top 15 — resalta manzana clickeada
    top15 = mzas_df.head(15)
    bar_colors = []
    for _, r in top15.iterrows():
        if mza_sel_num and r["Manzana"] == mza_sel_num:
            bar_colors.append("#333F48")
        elif r["Prior50"] == "⭐":
            bar_colors.append("#FF8200")
        else:
            bar_colors.append("#FFB366")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[f"Mzna {r['Manzana']}" for _, r in top15.iterrows()],
        x=top15["LN 18–39"],
        orientation="h",
        marker_color=bar_colors,
        marker_line_color="#ffffff", marker_line_width=1,
        text=top15["LN 18–39"], textposition="outside",
        textfont=dict(size=11, color="#333F48"),
    ))
    fig.update_layout(
        height=360, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        xaxis=dict(title="LN 18–39 estimada", gridcolor="#F0F0F0"),
        yaxis=dict(autorange="reversed"),
        font=dict(family="DM Sans", color="#333F48"),
        margin=dict(l=10, r=30, t=10, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla detalle
    with st.expander("📄 Ver tabla completa de manzanas"):
        st.dataframe(
            mzas_df.rename(columns={"Prior50": "⭐"}),
            use_container_width=True,
            hide_index=True,
        )

    # ── Navegación ────────────────────────────────────────────────────────────
    st.markdown("<div class='nav-row'>", unsafe_allow_html=True)
    nav1, nav_mid, nav2 = st.columns([1, 4, 1])
    with nav1:
        if st.button("← Panorama", use_container_width=True):
            st.switch_page("pages/1_M1_Panorama.py")
    with nav2:
        if st.button("Comités →", type="primary", use_container_width=True):
            st.switch_page("pages/3_M3_Comites.py")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="footer">{FOOTER_TEXTO}</div>', unsafe_allow_html=True)

main()