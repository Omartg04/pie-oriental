"""
DEMO_CONFIG.py — PIE · Oriental, Puebla
Data & AI Inclusion Technologies
Aspirante Karenth Vázquez · Movimiento Ciudadano 2027
"""

# ══════════════════════════════════════════════════════════════════════════════
# 1 · IDENTIDAD
# ══════════════════════════════════════════════════════════════════════════════
CANDIDATO_NOMBRE       = "Karenth Vázquez"
CANDIDATO_NOMBRE_CORTO = "Karenth"
PARTIDO                = "MC"
CARGO                  = "Presidenta Municipal"
MUNICIPIO              = "Oriental"
ESTADO                 = "Puebla"
ANIO_ELECCION          = 2027

DEMO_TAG       = f"Data & AI Inclusion Tech · Sistema de Inteligencia Electoral · {MUNICIPIO}, {ESTADO}"
DEMO_SUBTITULO = "Inteligencia territorial para construir presencia donde el electorado ya está esperando."

PAGE_TITLE_HOME = f"Inteligencia Electoral · {MUNICIPIO} {ANIO_ELECCION}"
PAGE_TITLE_M1   = f"M1 · Panorama Territorial | {MUNICIPIO}"
PAGE_TITLE_M2   = f"M2 · Territorios de Entrada | {MUNICIPIO}"
PAGE_TITLE_M3   = f"M3 · Plan de Comités | {MUNICIPIO}"

FOOTER_TEXTO = (
    f"Data & AI Inclusion Tech · {MUNICIPIO}, {ESTADO} · "
    f"{CANDIDATO_NOMBRE} · {PARTIDO} {ANIO_ELECCION} · Confidencial"
)

# ══════════════════════════════════════════════════════════════════════════════
# 2 · DATOS TERRITORIALES (reales · INE / INEGI 2020)
# ══════════════════════════════════════════════════════════════════════════════
N_SECCIONES_TOTAL  = 9
LN_TOTAL_MUNICIPAL = 14_836
LN_JOVEN_TOTAL     = 7_711
PCT_JOVEN_MUNICIPAL = 52.0

ELECCION_REFERENCIA = "Ayuntamiento"
MAPA_LAT  = 19.3615
MAPA_LON  = -97.6075
MAPA_ZOOM = 13

# ══════════════════════════════════════════════════════════════════════════════
# 3 · ÍNDICE ITerMC
# ══════════════════════════════════════════════════════════════════════════════
ITERMC_UMBRAL_ALTA = 65
ITERMC_UMBRAL_OPT  = 35

# ══════════════════════════════════════════════════════════════════════════════
# 4 · SECCIÓN ESTRELLA
# ══════════════════════════════════════════════════════════════════════════════
SECCION_ESTRELLA = 876

# ══════════════════════════════════════════════════════════════════════════════
# 5 · HALLAZGOS NARRATIVOS
# ══════════════════════════════════════════════════════════════════════════════
HALLAZGOS = [
    (
        "🟠",
        "MC no tuvo candidato en la última elección — el electorado nunca tuvo la opción.",
        "No hay voto perdido que recuperar. Hay voto disponible que nadie ha reclamado. "
        "La presencia de MC en 2027 es una oportunidad de primer acceso, no de reconquista.",
    ),
    (
        "👥",
        "52% del padrón de Oriental tiene entre 18 y 39 años — 7,711 electores jóvenes.",
        "Oriental es un municipio con mayoría de electores jóvenes. "
        "El perfil del electorado natural de MC ya está aquí. Falta quien lo active.",
    ),
    (
        "🔍",
        "En §876 y §881, Morena ganó con apenas 1 de cada 3 votos.",
        "Las secciones más competidas del municipio no son fortalezas de nadie. "
        "Son el punto de entrada con menor resistencia para instalar presencia.",
    ),
    (
        "🗳️",
        "PVEM independiente capturó entre 18% y 31% del voto en 7 de 9 secciones.",
        "Ese voto no fue a Morena ni a PAN. Fue a una tercera opción. "
        "Esos votantes son el proxy más claro del electorado natural de MC en Oriental.",
    ),
    (
        "📍",
        "§876: juventud alta (56.9%), Morena débil (34.7%), voto diferenciado (30.7%).",
        "El primer comité seccional debe instalarse aquí. "
        "Es el punto de máximo retorno para el trabajo territorial inicial.",
    ),
    (
        "📊",
        "§877 tiene 3,745 registros y 34% de abstención — el mayor potencial de movilización.",
        "Un tercio de su electorado no votó en la última elección. "
        "Movilizar ese voto abstencionista joven es el objetivo de segundo nivel.",
    ),
]

# ══════════════════════════════════════════════════════════════════════════════
# 6 · PALETA MC
# ══════════════════════════════════════════════════════════════════════════════
COLORES = {
    "naranja":        "#FF8200",
    "naranja_suave":  "#FFB366",
    "naranja_pale":   "#FFE4C4",
    "gris_oscuro":    "#333F48",
    "gris_sidebar":   "#1C2429",
    "gris_medio":     "#8B9299",
    "blanco":         "#FFFFFF",
    "alerta":         "#e63946",
    "fondo":          "#F8F9FA",
    "borde":          "#E2E8F0",
}

COLOR_ALTA    = "#FF8200"
COLOR_OPT     = "#FFB366"
COLOR_DIFICIL = "#CBD5E0"

GRADIENTE_HEADER  = "linear-gradient(135deg, #1C2429 0%, #333F48 55%, #FF8200 100%)"
