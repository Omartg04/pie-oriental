"""
auth.py — PIE Oriental · Autenticación por sesión
Credenciales configuradas en .streamlit/secrets.toml (nunca en el código)
"""

import streamlit as st

def _check_credentials(username: str, password: str) -> bool:
    try:
        users = st.secrets["users"]
        stored = users.get(username.strip().lower())
        return stored is not None and stored == password
    except Exception:
        return False

def login_screen():
    """Renderiza pantalla de login con paleta MC. Retorna False mientras no autenticado."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1C2429 0%, #333F48 60%, #FF8200 100%);
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent; }
    .login-wrap {
        max-width: 400px; margin: 80px auto 0; padding: 0 16px;
    }
    .login-card {
        background: #ffffff; border-radius: 18px;
        padding: 40px 36px 32px; box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    }
    .login-logo {
        font-size: 2.6rem; text-align: center; margin-bottom: 8px;
    }
    .login-title {
        font-size: 1.3rem; font-weight: 700; color: #333F48;
        text-align: center; margin-bottom: 4px;
    }
    .login-sub {
        font-size: 0.82rem; color: #94a3b8; text-align: center;
        margin-bottom: 28px;
    }
    .login-footer {
        font-size: 0.70rem; color: rgba(255,255,255,0.4);
        text-align: center; margin-top: 24px;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px !important; border: 1.5px solid #E2E8F0 !important;
        padding: 10px 14px !important; font-family: 'DM Sans', sans-serif !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #FF8200 !important; box-shadow: 0 0 0 3px rgba(255,130,0,0.15) !important;
    }
    div[data-testid="stForm"] { background: transparent; border: none; padding: 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="login-card">
        <div class="login-logo">🟠</div>
        <div class="login-title">Plataforma de Inteligencia Electoral</div>
        <div class="login-sub">Oriental, Puebla · Movimiento Ciudadano 2027</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        usuario = st.text_input("Usuario", placeholder="tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submitted = st.form_submit_button(
            "Ingresar →", use_container_width=True,
            type="primary"
        )

    if submitted:
        if _check_credentials(usuario, password):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario.strip().lower()
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown("""
    <div class="login-footer">
        Data &amp; AI Inclusion Technologies · Acceso restringido · Confidencial
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def require_auth():
    """
    Llama esto al inicio de cada página.
    Si no está autenticado, muestra el login y detiene la ejecución.
    """
    if not st.session_state.get("autenticado"):
        login_screen()
        st.stop()
