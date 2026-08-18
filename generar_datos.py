"""
generar_datos.py — PIE Oriental · Puebla
Genera data/secciones_itermc.csv con datos reales procesados.
Uso: python generar_datos.py
"""

import json, csv, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# ── Cargar GeoJSON ────────────────────────────────────────────────────────────
with open(os.path.join(DATA, "PIE_Oriental_manzanas.geojson")) as f:
    geo = json.load(f)

# ── LN por sección (de atributos del GeoJSON) ────────────────────────────────
ln = {}
seen = set()
for feat in geo["features"]:
    p = feat["properties"]
    s = p["SECCION"]
    if s not in seen:
        ln[s] = {
            "LN_total": p["LN_total_sec"],
            "LN_1839":  p["LN_1839_sec"],
            "LN_H":     p["LN_H_sec"],
            "LN_M":     p["LN_M_sec"],
        }
        seen.add(s)

# ── Resultados electorales por sección (hardcoded del CSV procesado) ──────────
# Fuente: Resultados_ayuntamiento.csv (elección ayuntamiento)
resultados = {
    875:  {"total": 1205, "morena_blq": 536, "pan_blq": 202, "pvem": 346, "nulos": 42},
    876:  {"total": 1107, "morena_blq": 371, "pan_blq": 294, "pvem": 328, "nulos": 38},
    877:  {"total": 2464, "morena_blq":1309, "pan_blq": 387, "pvem": 505, "nulos": 79},
    878:  {"total":  834, "morena_blq": 441, "pan_blq": 164, "pvem": 147, "nulos": 22},
    879:  {"total": 1125, "morena_blq": 616, "pan_blq": 176, "pvem": 226, "nulos": 42},
    880:  {"total":  711, "morena_blq": 317, "pan_blq": 123, "pvem": 198, "nulos": 21},
    881:  {"total":  868, "morena_blq": 262, "pan_blq": 172, "pvem": 233, "nulos": 28},
    882:  {"total": 1476, "morena_blq": 701, "pan_blq": 509, "pvem":  82, "nulos": 46},
    2747: {"total":  647, "morena_blq": 304, "pan_blq": 129, "pvem": 149, "nulos": 24},
}

# ── Calcular métricas ─────────────────────────────────────────────────────────
rows = {}
for s, r in resultados.items():
    l = ln[s]
    validos       = r["total"] - r["nulos"]
    pct_morena    = round(r["morena_blq"] / validos * 100, 1)
    pct_pan       = round(r["pan_blq"]    / validos * 100, 1)
    pct_pvem      = round(r["pvem"]       / validos * 100, 1)
    participacion = round(r["total"] / l["LN_total"] * 100, 1)
    pct_joven     = round(l["LN_1839"] / l["LN_total"] * 100, 1)
    abstencion    = round(100 - participacion, 1)

    rows[s] = {
        "seccion":        s,
        "LN_total":       l["LN_total"],
        "LN_1839":        l["LN_1839"],
        "LN_H":           l["LN_H"],
        "LN_M":           l["LN_M"],
        "pct_joven":      pct_joven,
        "total_votos":    r["total"],
        "pct_morena":     pct_morena,
        "pct_pan":        pct_pan,
        "pct_pvem":       pct_pvem,
        "participacion":  participacion,
        "abstencion":     abstencion,
        "voto_diferenciado": pct_pvem,
    }

# ── ITerMC — normalización min-max ───────────────────────────────────────────
secs = list(rows.keys())

def minmax_norm(vals):
    mn, mx = min(vals), max(vals)
    if mx == mn:
        return [50.0] * len(vals)
    return [(v - mn) / (mx - mn) * 100 for v in vals]

joven_vals = [rows[s]["pct_joven"] for s in secs]
comp_raw   = [(100 - rows[s]["pct_morena"]) * 0.65
              + rows[s]["voto_diferenciado"] * 0.35 for s in secs]
abst_vals  = [rows[s]["abstencion"] for s in secs]

joven_norm = dict(zip(secs, minmax_norm(joven_vals)))
comp_norm  = dict(zip(secs, minmax_norm(comp_raw)))
abst_norm  = dict(zip(secs, minmax_norm(abst_vals)))

for s in secs:
    itermc = round(
        joven_norm[s] * 0.40 +
        comp_norm[s]  * 0.35 +
        abst_norm[s]  * 0.25, 1
    )
    rows[s]["itermc"] = itermc
    rows[s]["itermc_joven"] = round(joven_norm[s], 1)
    rows[s]["itermc_comp"]  = round(comp_norm[s], 1)
    rows[s]["itermc_abst"]  = round(abst_norm[s], 1)

    if itermc >= 65:
        rows[s]["clasificacion"]       = "Alta prioridad"
        rows[s]["recomendacion"]       = "Primer comité seccional — máxima prioridad"
        rows[s]["prioridad_comite"]    = 1
    elif itermc >= 35:
        rows[s]["clasificacion"]       = "Oportunidad"
        rows[s]["recomendacion"]       = "Trabajo territorial — segundo nivel"
        rows[s]["prioridad_comite"]    = 2
    else:
        rows[s]["clasificacion"]       = "Terreno difícil"
        rows[s]["recomendacion"]       = "No priorizar en esta etapa"
        rows[s]["prioridad_comite"]    = 3

# Recomendaciones específicas por contexto
RECS = {
    876:  "Primer comité — mayor ITerMC del municipio. Instalar primero.",
    881:  "Sección más competitiva (Morena 30.9%) — alto potencial de arrastre.",
    877:  "Mayor padrón joven (2,000 en 18-39) — movilizar abstención.",
    882:  "Alta concentración de jóvenes (57.9%) — trabajo puerta a puerta.",
    875:  "Voto diferenciado (PVEM 29.9%) — explorar liderazgos locales.",
    880:  "PVEM fuerte (28.7%) — convertibles a MC con presencia directa.",
    878:  "Morena dominante — trabajo paciente de largo plazo.",
    879:  "Morena 56.8% — terreno adverso en esta etapa.",
    2747: "Sección pequeña — menor retorno por esfuerzo invertido.",
}
for s, rec in RECS.items():
    rows[s]["recomendacion"] = rec

# ── Exportar CSV ──────────────────────────────────────────────────────────────
cols = [
    "seccion", "LN_total", "LN_1839", "LN_H", "LN_M",
    "pct_joven", "total_votos", "pct_morena", "pct_pan", "pct_pvem",
    "participacion", "abstencion", "voto_diferenciado",
    "itermc", "itermc_joven", "itermc_comp", "itermc_abst",
    "clasificacion", "recomendacion", "prioridad_comite",
]

out = os.path.join(DATA, "secciones_itermc.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for s in sorted(rows):
        w.writerow({c: rows[s][c] for c in cols})

print(f"✅ Exportado: {out}")
print(f"   {len(rows)} secciones · ITerMC calculado")
for s in sorted(rows, key=lambda x: rows[x]["itermc"], reverse=True):
    r = rows[s]
    print(f"   §{s}: ITerMC={r['itermc']:5.1f} · {r['clasificacion']}")

# ── Punto de entrada para importación ─────────────────────────────────────────
def generar_si_necesario():
    """Genera secciones_itermc.csv si no existe. Se llama al arrancar la app."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "secciones_itermc.csv")
    if not os.path.exists(ruta):
        import runpy
        runpy.run_path(__file__)