"""
Tour de Contrôle — Yeelen Consulting · SchoolBox Africa
Design : Yeelen Brand (Bleu #2878BE · Or #F5C020) — Light Premium SaaS
Font   : Plus Jakarta Sans + JetBrains Mono
"""

import os
import time
import requests
import streamlit as st
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Tour de Contrôle · Yeelen",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _conf(key: str, default: str = "") -> str:
    """Lit une valeur depuis les secrets Streamlit, sinon les variables d'env."""
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)

FLASK_URL        = _conf("FLASK_URL", "http://localhost:5000")
INTERNAL_API_KEY = _conf("INTERNAL_API_KEY", "")

# En-têtes envoyés à Flask pour les routes protégées
API_HEADERS = {"X-Internal-Key": INTERNAL_API_KEY} if INTERNAL_API_KEY else {}

TAILSCALE_SERVER_IP = FLASK_URL.replace("https://","").replace("http://","").rstrip("/")
REFRESH_INTERVAL    = 30

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Yeelen Brand
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* ── Yeelen Brand ── */
  --blue:          #2878BE;
  --blue-dark:     #1C5A8A;
  --blue-mid:      #3D8FD1;
  --blue-light:    #EBF4FF;
  --blue-border:   #BFDBFE;
  --gold:          #F5C020;
  --gold-dark:     #D4A017;
  --gold-light:    #FEF9E7;
  --gold-border:   #FDE68A;

  /* ── Neutrals ── */
  --bg:            #F4F7FB;
  --surface:       #FFFFFF;
  --surface-alt:   #F8FAFC;
  --border:        #E2E8F0;
  --border-hover:  #CBD5E1;
  --text-primary:  #1A2A3A;
  --text-secondary:#4A5568;
  --text-muted:    #94A3B8;

  /* ── Semantic ── */
  --green:         #16A34A;
  --green-bg:      #F0FDF4;
  --green-border:  #BBF7D0;
  --red:           #DC2626;
  --red-bg:        #FFF1F1;
  --red-border:    #FECACA;
  --orange:        #EA580C;
  --orange-bg:     #FFF7ED;
  --orange-border: #FED7AA;

  /* ── Shadows ── */
  --shadow-sm:     0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:     0 4px 16px rgba(40,120,190,.10), 0 2px 4px rgba(0,0,0,.04);
  --shadow-blue:   0 4px 20px rgba(40,120,190,.18);

  /* ── Shape ── */
  --radius:        12px;
  --radius-sm:     8px;
  --radius-lg:     16px;
}

/* ── Base ── */
html, body, [class*="css"], .stApp {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background:  var(--bg) !important;
  color:       var(--text-primary) !important;
}
.block-container { padding: 1.6rem 2rem 2rem !important; max-width: 1440px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background:   var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background:    transparent !important;
  gap:           4px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
  background:    transparent !important;
  color:         var(--text-secondary) !important;
  font-family:   'Plus Jakarta Sans', sans-serif !important;
  font-size:     .84rem !important;
  font-weight:   600 !important;
  padding:       .55rem 1.1rem !important;
  border-radius: 8px 8px 0 0 !important;
  border-bottom: 2px solid transparent !important;
  transition:    color .15s, background .15s !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color:      var(--text-primary) !important;
  background: var(--blue-light) !important;
}
.stTabs [aria-selected="true"] {
  color:         var(--blue) !important;
  border-bottom: 2px solid var(--blue) !important;
  background:    transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem !important; }

/* ── Buttons — Default ── */
.stButton > button {
  font-family:   'Plus Jakarta Sans', sans-serif !important;
  font-weight:   600 !important;
  font-size:     .84rem !important;
  border-radius: var(--radius-sm) !important;
  border:        1px solid var(--border) !important;
  background:    var(--surface) !important;
  color:         var(--text-primary) !important;
  padding:       .5rem 1rem !important;
  transition:    all .15s ease !important;
  box-shadow:    var(--shadow-sm) !important;
}
.stButton > button:hover {
  border-color: var(--border-hover) !important;
  box-shadow:   var(--shadow-md) !important;
  transform:    translateY(-1px) !important;
}

/* ── Button — Primary (bleu) ── */
.btn-primary > button {
  background:    var(--blue) !important;
  color:         #fff !important;
  border-color:  var(--blue) !important;
  box-shadow:    var(--shadow-blue) !important;
}
.btn-primary > button:hover {
  background:   var(--blue-dark) !important;
  border-color: var(--blue-dark) !important;
}

/* ── Button — Gold ── */
.btn-gold > button {
  background:   var(--gold) !important;
  color:        var(--text-primary) !important;
  border-color: var(--gold-dark) !important;
}
.btn-gold > button:hover {
  background:   var(--gold-dark) !important;
  color:        #fff !important;
}

/* ── Button — Danger ── */
.btn-danger > button {
  background:   var(--red-bg) !important;
  color:        var(--red) !important;
  border-color: var(--red-border) !important;
}
.btn-danger > button:hover { background: #FECACA !important; }

/* ── Link button ── */
.stLinkButton a {
  font-family:   'Plus Jakarta Sans', sans-serif !important;
  font-weight:   600 !important;
  font-size:     .84rem !important;
  border-radius: var(--radius-sm) !important;
  background:    var(--blue-light) !important;
  color:         var(--blue) !important;
  border:        1px solid var(--blue-border) !important;
  padding:       .5rem 1rem !important;
  transition:    all .15s !important;
}
.stLinkButton a:hover {
  background:   #DBEAFE !important;
  border-color: var(--blue) !important;
}

/* ── Inputs ── */
input, textarea {
  font-family:   'Plus Jakarta Sans', sans-serif !important;
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color:         var(--text-primary) !important;
  transition:    border-color .15s, box-shadow .15s !important;
}
input:focus {
  border-color: var(--blue) !important;
  box-shadow:   0 0 0 3px rgba(40,120,190,.14) !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color:         var(--text-primary) !important;
  font-family:   'Plus Jakarta Sans', sans-serif !important;
}

/* ── Metrics natifs ── */
div[data-testid="metric-container"] {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding:       1rem 1.2rem !important;
  box-shadow:    var(--shadow-sm) !important;
}
div[data-testid="metric-container"] label {
  font-family:    'Plus Jakarta Sans', sans-serif !important;
  font-size:      .72rem !important;
  font-weight:    600 !important;
  color:          var(--text-muted) !important;
  text-transform: uppercase !important;
  letter-spacing: .06em !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size:   1.6rem !important;
  font-weight: 800 !important;
  color:       var(--text-primary) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding:       .85rem 1.1rem !important;
  font-family:   'Plus Jakarta Sans', sans-serif !important;
  font-weight:   600 !important;
  font-size:     .9rem !important;
  color:         var(--text-primary) !important;
  box-shadow:    var(--shadow-sm) !important;
  transition:    box-shadow .15s, border-color .15s !important;
}
.streamlit-expanderHeader:hover {
  border-color: var(--blue) !important;
  box-shadow:   var(--shadow-md) !important;
}
.streamlit-expanderContent {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-top:    none !important;
  border-radius: 0 0 var(--radius) var(--radius) !important;
  padding:       1.1rem !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: .8rem 0 !important; }

/* ── Toast ── */
div[data-testid="stToast"] {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow:    var(--shadow-md) !important;
  color:         var(--text-primary) !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: var(--radius) !important; overflow: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue-border); }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Alert banner ── */
.alert-warning {
  background: var(--orange-bg); border: 1px solid var(--orange-border);
  border-radius: var(--radius-sm); padding: .65rem .9rem;
  font-size: .82rem; color: var(--orange); font-weight: 600;
}
.alert-success {
  background: var(--green-bg); border: 1px solid var(--green-border);
  border-radius: var(--radius-sm); padding: .65rem .9rem;
  font-size: .82rem; color: var(--green); font-weight: 600;
}
.alert-info {
  background: var(--blue-light); border: 1px solid var(--blue-border);
  border-radius: var(--radius-sm); padding: .65rem .9rem;
  font-size: .82rem; color: var(--blue); font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPOSANTS HTML
# ══════════════════════════════════════════════════════════════════════════════

def badge_status(is_on: bool) -> str:
    if is_on:
        return ('<span style="display:inline-flex;align-items:center;gap:5px;'
                'background:#F0FDF4;border:1px solid #BBF7D0;border-radius:20px;'
                'padding:3px 10px;font-size:.74rem;font-weight:700;color:#16A34A">'
                '● Connecté</span>')
    return ('<span style="display:inline-flex;align-items:center;gap:5px;'
            'background:#FFF1F1;border:1px solid #FECACA;border-radius:20px;'
            'padding:3px 10px;font-size:.74rem;font-weight:700;color:#DC2626">'
            '● Hors-ligne</span>')


def badge_role(role: str) -> str:
    styles = {
        "superadmin": ("background:#FEF9E7;color:#D4A017;border:1px solid #FDE68A", "⭐ Superadmin"),
        "admin":      ("background:#EBF4FF;color:#2878BE;border:1px solid #BFDBFE", "🔧 Admin"),
        "viewer":     ("background:#F8FAFC;color:#64748B;border:1px solid #E2E8F0", "👁 Viewer"),
    }
    s, label = styles.get(role, styles["viewer"])
    return (f'<span style="{s};border-radius:20px;padding:2px 9px;'
            f'font-size:.72rem;font-weight:700">{label}</span>')


def kpi_card(icon: str, label: str, value: str, color: str = "#1A2A3A",
             accent: str = "", sublabel: str = "") -> str:
    bar = (f'<div style="height:3px;background:{accent};border-radius:2px;'
           f'margin-bottom:.9rem"></div>') if accent else ""
    sub = (f'<div style="font-size:.7rem;color:#94A3B8;margin-top:3px">{sublabel}</div>'
           ) if sublabel else ""
    return f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                padding:1.1rem 1.2rem;box-shadow:0 1px 3px rgba(0,0,0,.05);
                transition:box-shadow .15s;height:100%">
      {bar}
      <div style="font-size:.7rem;font-weight:600;color:#94A3B8;text-transform:uppercase;
                  letter-spacing:.07em;margin-bottom:.4rem">{icon}&nbsp;{label}</div>
      <div style="font-size:1.6rem;font-weight:800;color:{color};line-height:1.1">{value}</div>
      {sub}
    </div>"""


def info_row(label: str, value: str, mono: bool = False) -> str:
    val_style = (
        "font-family:'JetBrains Mono',monospace;font-size:.81rem;color:#2878BE;"
        "background:#EBF4FF;border:1px solid #BFDBFE;border-radius:5px;padding:2px 8px"
        if mono else "font-size:.84rem;font-weight:600;color:#1A2A3A"
    )
    return f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:.55rem 0;border-bottom:1px solid #F1F5F9">
      <span style="font-size:.76rem;font-weight:600;color:#94A3B8;
                   text-transform:uppercase;letter-spacing:.05em">{label}</span>
      <span style="{val_style}">{value}</span>
    </div>"""


def section_title(text: str, sub: str = "") -> str:
    s = f'<div style="font-size:.8rem;color:#94A3B8;font-weight:500;margin-top:.2rem">{sub}</div>' if sub else ""
    return f"""
    <div style="margin-bottom:1.2rem">
      <h2 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.1rem;
                 font-weight:800;color:#1A2A3A;margin:0;letter-spacing:-.02em">{text}</h2>
      {s}
    </div>"""


def temp_color(t) -> str:
    if t is None: return "#64748B"
    return "#16A34A" if t < 50 else ("#EA580C" if t < 70 else "#DC2626")


def data_color(mb) -> str:
    v = float(mb or 0)
    return "#16A34A" if v < 400 else ("#EA580C" if v < 800 else "#DC2626")


def admin_url(box_id: str, ip: str) -> str | None:
    if not ip or ip == "Non communiquée": return None
    return (f"http://{ip}/admin_login.php" if "EDUBOX" in box_id.upper()
            else f"http://{ip}:8080/")


def health_score(d: dict, uptime) -> tuple:
    """
    Calcule un score de santé global (0-100) à partir du statut, température et uptime.
    Retourne (score, couleur, emoji, libellé).
    """
    score = 100
    if d.get("status") != "Connecté":
        score -= 55
    t = d.get("temperature")
    if t is not None:
        if t >= 70:   score -= 30
        elif t >= 50: score -= 12
    if uptime is not None:
        score -= int((100 - uptime) * 0.30)
    score = max(0, min(100, score))

    if score >= 80:
        return score, "#16A34A", "🟢", "Bonne"
    if score >= 50:
        return score, "#EA580C", "🟡", "Moyenne"
    return score, "#DC2626", "🔴", "Critique"


def badge_health(score: int, color: str, emoji: str, label: str) -> str:
    return (f'<span style="display:inline-flex;align-items:center;gap:5px;'
            f'background:{color}1A;border:1px solid {color}55;border-radius:20px;'
            f'padding:3px 11px;font-size:.74rem;font-weight:700;color:{color}">'
            f'{emoji} Santé {label} · {score}%</span>')


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

_defaults = {
    "logged_in": False, "username": "", "role": "",
    "boxes": {}, "last_fetch": 0, "fetch_error": "", "prev_offline": 0,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _post(endpoint: str, payload: dict) -> dict:
    try:
        r = requests.post(f"{FLASK_URL}{endpoint}", json=payload,
                          headers=API_HEADERS, timeout=8)
        return r.json()
    except Exception as e:
        return {"ok": False, "erreur": str(e)}


def _get(endpoint: str) -> list | dict | None:
    try:
        r = requests.get(f"{FLASK_URL}{endpoint}", headers=API_HEADERS, timeout=8)
        return r.json()
    except:
        return None


def _delete(endpoint: str, payload: dict = None) -> dict:
    try:
        r = requests.delete(f"{FLASK_URL}{endpoint}", json=payload or {},
                            headers=API_HEADERS, timeout=8)
        return r.json()
    except Exception as e:
        return {"ok": False, "erreur": str(e)}


def fetch_boxes() -> dict:
    try:
        r = requests.get(f"{FLASK_URL}/api/boxes", headers=API_HEADERS, timeout=8)
        r.raise_for_status()
        st.session_state.fetch_error = ""
        return r.json()
    except Exception as e:
        st.session_state.fetch_error = str(e)
        return st.session_state.boxes


def do_login(identifiant: str, mdp: str) -> tuple:
    try:
        r = requests.post(f"{FLASK_URL}/api/login",
                          json={"identifiant": identifiant, "mot_de_passe": mdp}, timeout=5)
        d = r.json()
        return d.get("ok", False), d.get("erreur", ""), d.get("role", ""), d.get("username", "")
    except Exception as e:
        return False, f"Impossible de joindre Flask.\nLance d'abord : python app.py\n\n{e}", "", ""


def maybe_refresh():
    if time.time() - st.session_state.last_fetch > REFRESH_INTERVAL:
        boxes   = fetch_boxes()
        offline = sum(1 for b in boxes.values() if b.get("status") != "Connecté")
        if offline > st.session_state.prev_offline:
            diff = offline - st.session_state.prev_offline
            st.toast(f"⚠️ {diff} box(es) passée(s) hors-ligne", icon="🔴")
        st.session_state.prev_offline = offline
        st.session_state.boxes        = boxes
        st.session_state.last_fetch   = time.time()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE LOGIN
# ══════════════════════════════════════════════════════════════════════════════

def login_page():
    flask_ok = False
    try:
        requests.get(FLASK_URL, timeout=2)
        flask_ok = True
    except:
        pass

    _, col, _ = st.columns([1, 0.9, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # ── Logo Yeelen ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center;margin-bottom:2.2rem">
          <div style="display:inline-flex;align-items:center;justify-content:center;
                      width:72px;height:72px;background:#EBF4FF;border-radius:20px;
                      border:2px solid #BFDBFE;margin-bottom:.9rem">
            <svg width="40" height="40" viewBox="0 0 100 100" fill="none">
              <path d="M20 15 Q35 50 50 70 Q65 50 80 15" stroke="#F5C020" stroke-width="14"
                    stroke-linecap="round" fill="none"/>
              <path d="M50 70 Q50 85 50 95" stroke="#2878BE" stroke-width="14"
                    stroke-linecap="round" fill="none"/>
              <path d="M63 15 Q70 35 55 55" stroke="#2878BE" stroke-width="12"
                    stroke-linecap="round" fill="none"/>
            </svg>
          </div>
          <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.8rem;
                      font-weight:800;color:#1A2A3A;letter-spacing:-.03em;line-height:1">
            Tour de Contrôle</div>
          <div style="font-size:.8rem;font-weight:600;color:#2878BE;margin-top:.35rem;
                      letter-spacing:.02em">YEELEN CONSULTING · SchoolBox Africa</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Statut serveur ───────────────────────────────────────────────────
        if flask_ok:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:8px;background:#F0FDF4;
                        border:1px solid #BBF7D0;border-radius:8px;padding:.55rem .9rem;
                        margin-bottom:1.2rem">
              <span style="width:7px;height:7px;background:#16A34A;border-radius:50%;
                            display:inline-block;flex-shrink:0;
                            animation:pulse 2s infinite"></span>
              <span style="font-size:.78rem;font-weight:600;color:#16A34A">
                Serveur opérationnel</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#FFF1F1;border:1px solid #FECACA;border-radius:8px;
                        padding:.55rem .9rem;margin-bottom:1.2rem">
              <span style="font-size:.78rem;font-weight:600;color:#DC2626">
                ● Serveur non détecté — lance :
                <code style="background:#FFE4E4;padding:1px 5px;border-radius:3px;
                             font-family:monospace">python app.py</code>
              </span>
            </div>""", unsafe_allow_html=True)

        # ── Card formulaire ──────────────────────────────────────────────────
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;
                    padding:2rem 2rem 1.5rem;box-shadow:0 4px 24px rgba(40,120,190,.08)">
        """, unsafe_allow_html=True)

        with st.form("login"):
            st.markdown('<p style="font-size:.78rem;font-weight:600;color:#64748B;'
                        'margin-bottom:.3rem;margin-top:0">Identifiant</p>',
                        unsafe_allow_html=True)
            identifiant = st.text_input("id", label_visibility="collapsed",
                                        placeholder="superadmin")
            st.markdown('<p style="font-size:.78rem;font-weight:600;color:#64748B;'
                        'margin-bottom:.3rem;margin-top:.8rem">Mot de passe</p>',
                        unsafe_allow_html=True)
            mot_de_passe = st.text_input("pw", label_visibility="collapsed",
                                          type="password", placeholder="••••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Se connecter →", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not identifiant or not mot_de_passe:
                st.error("Remplis les deux champs.")
            else:
                with st.spinner("Vérification…"):
                    ok, err, role, username = do_login(identifiant, mot_de_passe)
                if ok:
                    st.session_state.logged_in  = True
                    st.session_state.username   = username
                    st.session_state.role       = role
                    st.session_state.boxes      = fetch_boxes()
                    st.session_state.last_fetch = time.time()
                    st.rerun()
                else:
                    st.error(err)

        st.markdown("""
        <div style="text-align:center;margin-top:1.2rem;font-size:.72rem;color:#94A3B8">
          Yeelen Consulting © 2026 · Tour de Contrôle v5
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(boxes: dict) -> None:
    online  = sum(1 for b in boxes.values() if b.get("status") == "Connecté")
    offline = len(boxes) - online
    total_u = sum(b.get("users",   0) for b in boxes.values())
    total_d = sum(b.get("data_mb", 0) for b in boxes.values())

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="padding:.4rem 0 .8rem">
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:40px;height:40px;background:linear-gradient(135deg,#EBF4FF,#FEF9E7);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;
                        border:1px solid #BFDBFE;flex-shrink:0">
              <svg width="22" height="22" viewBox="0 0 100 100" fill="none">
                <path d="M20 15 Q35 50 50 70 Q65 50 80 15" stroke="#F5C020" stroke-width="16"
                      stroke-linecap="round" fill="none"/>
                <path d="M50 70 Q50 85 50 95" stroke="#2878BE" stroke-width="16"
                      stroke-linecap="round" fill="none"/>
                <path d="M63 15 Q70 35 55 55" stroke="#2878BE" stroke-width="14"
                      stroke-linecap="round" fill="none"/>
              </svg>
            </div>
            <div>
              <div style="font-weight:800;font-size:.94rem;color:#1A2A3A">Tour de Contrôle</div>
              <div style="font-size:.68rem;color:#2878BE;font-weight:600;letter-spacing:.02em">
                YEELEN CONSULTING</div>
            </div>
          </div>
        </div>

        <!-- User badge -->
        <div style="background:#F4F7FB;border:1px solid #E2E8F0;border-radius:10px;
                    padding:.6rem .8rem;margin-bottom:.8rem;display:flex;
                    align-items:center;justify-content:space-between">
          <div>
            <div style="font-size:.82rem;font-weight:700;color:#1A2A3A">
              👤 {st.session_state.username}</div>
            <div style="margin-top:3px">{badge_role(st.session_state.role)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── KPIs sidebar ──────────────────────────────────────────────────────
        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                    padding:.7rem .6rem;text-align:center">
          <div style="font-size:.62rem;font-weight:600;color:#16A34A;text-transform:uppercase;
                      letter-spacing:.06em;margin-bottom:.25rem">En ligne</div>
          <div style="font-size:1.5rem;font-weight:800;color:#16A34A">{online}</div>
        </div>""", unsafe_allow_html=True)

        c2.markdown(f"""
        <div style="background:{'#FFF1F1' if offline else '#F8FAFC'};
                    border:1px solid {'#FECACA' if offline else '#E2E8F0'};
                    border-radius:10px;padding:.7rem .6rem;text-align:center">
          <div style="font-size:.62rem;font-weight:600;color:{'#DC2626' if offline else '#94A3B8'};
                      text-transform:uppercase;letter-spacing:.06em;margin-bottom:.25rem">Hors-ligne</div>
          <div style="font-size:1.5rem;font-weight:800;color:{'#DC2626' if offline else '#94A3B8'}">{offline}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        c3.markdown(f"""
        <div style="background:#EBF4FF;border:1px solid #BFDBFE;border-radius:10px;
                    padding:.7rem .6rem;text-align:center">
          <div style="font-size:.62rem;font-weight:600;color:#2878BE;text-transform:uppercase;
                      letter-spacing:.06em;margin-bottom:.25rem">Usagers</div>
          <div style="font-size:1.5rem;font-weight:800;color:#2878BE">{total_u}</div>
        </div>""", unsafe_allow_html=True)

        c4.markdown(f"""
        <div style="background:#FEF9E7;border:1px solid #FDE68A;border-radius:10px;
                    padding:.7rem .6rem;text-align:center">
          <div style="font-size:.62rem;font-weight:600;color:#D4A017;text-transform:uppercase;
                      letter-spacing:.06em;margin-bottom:.25rem">Data</div>
          <div style="font-size:1.3rem;font-weight:800;color:#D4A017">{total_d:.0f}<span style="font-size:.75rem"> Mo</span></div>
        </div>""", unsafe_allow_html=True)

        st.divider()

        # ── Refresh ───────────────────────────────────────────────────────────
        secs = max(0, REFRESH_INTERVAL - int(time.time() - st.session_state.last_fetch))
        last = time.strftime("%H:%M:%S", time.localtime(st.session_state.last_fetch))
        st.markdown(f"""
        <div style="font-size:.72rem;color:#94A3B8;margin:.2rem 0 .6rem">
          Actualisé à {last} · prochaine dans {secs}s
        </div>""", unsafe_allow_html=True)

        # Progress bar refresh
        progress = 1 - (secs / REFRESH_INTERVAL)
        st.markdown(f"""
        <div style="height:3px;background:#E2E8F0;border-radius:2px;margin-bottom:.8rem">
          <div style="height:3px;width:{int(progress*100)}%;background:#2878BE;
                      border-radius:2px;transition:width .5s"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("↻  Rafraîchir maintenant", use_container_width=True):
            st.session_state.boxes      = fetch_boxes()
            st.session_state.last_fetch = time.time()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.fetch_error:
            st.markdown("""
            <div class="alert-warning" style="margin-top:.6rem">
              ⚠ Mode démo — serveur injoignable
            </div>""", unsafe_allow_html=True)

        st.divider()

        if st.button("↩  Déconnexion", use_container_width=True):
            for k in list(_defaults.keys()):
                st.session_state.pop(k, None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB — CARTE
# ══════════════════════════════════════════════════════════════════════════════

def tab_carte(boxes: dict) -> None:
    if not boxes:
        st.info("En attente de signal des boxes…", icon="📡")
        return

    # ── Résumé par pays ───────────────────────────────────────────────────────
    pays_count: dict = {}
    for d in boxes.values():
        p = (d.get("pays") or "").strip() or "Non localisé"
        on = d.get("status") == "Connecté"
        pays_count.setdefault(p, {"total": 0, "on": 0})
        pays_count[p]["total"] += 1
        pays_count[p]["on"]    += 1 if on else 0

    if pays_count:
        chips = ""
        for p, c in sorted(pays_count.items(), key=lambda x: -x[1]["total"]):
            chips += (
                f'<span style="display:inline-flex;align-items:center;gap:6px;'
                f'background:#FFFFFF;border:1px solid #E2E8F0;border-radius:20px;'
                f'padding:4px 12px;font-size:.78rem;font-weight:600;color:#1A2A3A;'
                f'margin:0 6px 6px 0">🌍 {p}'
                f'<span style="color:#16A34A;font-weight:700">{c["on"]}</span>'
                f'<span style="color:#94A3B8">/ {c["total"]}</span></span>')
        st.markdown(f'<div style="margin-bottom:.9rem">{chips}</div>',
                    unsafe_allow_html=True)

    # ── Option : afficher le trajet GPS d'une box ─────────────────────────────
    trail_boxes = ["— Aucun —"] + [boxes[b].get("nom_affiche", b) for b in boxes]
    ct1, _ = st.columns([2, 3])
    trail_sel = ct1.selectbox("🛰️ Afficher le trajet GPS de :", trail_boxes,
                              key="carte_trail")

    m = folium.Map(
        location=[10.0, -5.0], zoom_start=5,
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        attr="© CartoDB Voyager",
    )

    # Tracer le trajet sélectionné
    if trail_sel != "— Aucun —":
        ids   = list(boxes.keys())
        noms  = [boxes[b].get("nom_affiche", b) for b in ids]
        bid   = ids[noms.index(trail_sel)]
        trail = _get(f"/api/gps_trail/{bid}") or []
        pts   = [[p["lat"], p["lon"]] for p in trail if p.get("lat") and p.get("lon")]
        if len(pts) >= 2:
            folium.PolyLine(pts, color="#2878BE", weight=3.5, opacity=.8,
                            dash_array="6,8").add_to(m)
            folium.CircleMarker(pts[0], radius=6, color="#16A34A",
                                fill=True, fill_opacity=1,
                                tooltip="Départ").add_to(m)
            m.location = pts[-1]
            m.zoom_start = 11
        elif len(pts) == 1:
            st.markdown('<div class="alert-info">📍 Une seule position connue — '
                        'pas encore de trajet à tracer.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">🛰️ Aucun historique GPS pour cette box '
                        'pour le moment.</div>', unsafe_allow_html=True)

    for box_id, d in boxes.items():
        if not d.get("lat") or not d.get("lon"):
            continue
        is_on = d.get("status") == "Connecté"
        nom   = d.get("nom_affiche", box_id)
        t     = d.get("temperature")
        tc    = temp_color(t)
        loc   = " · ".join(x for x in [(d.get("site") or "").strip(),
                                       (d.get("pays") or "").strip()] if x)

        popup_html = f"""
        <div style="font-family:'Plus Jakarta Sans',system-ui,sans-serif;
                    min-width:220px;padding:.3rem">
          <div style="font-size:.95rem;font-weight:700;color:#1A2A3A;
                      margin-bottom:.2rem">{nom}</div>
          {f'<div style="font-size:.74rem;color:#94A3B8;margin-bottom:.5rem">📍 {loc}</div>' if loc else ''}
          <div style="display:inline-flex;align-items:center;gap:5px;
                      background:{"#F0FDF4" if is_on else "#FFF1F1"};
                      border:1px solid {"#BBF7D0" if is_on else "#FECACA"};
                      border-radius:20px;padding:2px 9px;font-size:.72rem;
                      font-weight:700;color:{"#16A34A" if is_on else "#DC2626"};
                      margin-bottom:.7rem">
            ● {"Connecté" if is_on else "Hors-ligne"}
          </div><br>
          <table style="font-size:.82rem;width:100%;border-collapse:collapse">
            <tr><td style="color:#94A3B8;padding:3px 0">🌡️ Température</td>
                <td style="text-align:right;font-weight:700;color:{tc}">{t or "--"}°C</td></tr>
            <tr><td style="color:#94A3B8;padding:3px 0">👥 Usagers</td>
                <td style="text-align:right;font-weight:600;color:#1A2A3A">{d.get("users",0)}</td></tr>
            <tr><td style="color:#94A3B8;padding:3px 0">📶 Data 4G</td>
                <td style="text-align:right;font-weight:600;color:#1A2A3A">{d.get("data_mb","--")} Mo</td></tr>
            <tr><td style="color:#94A3B8;padding:3px 0">🔗 IP</td>
                <td style="text-align:right;font-family:monospace;font-size:.76rem;
                            color:#2878BE">{d.get("ip_tailscale","N/A")}</td></tr>
            <tr><td style="color:#94A3B8;padding:3px 0">🕐 Signal</td>
                <td style="text-align:right;color:#64748B;font-size:.74rem">
                  {d.get("last_seen","?")}</td></tr>
          </table>
        </div>"""

        folium.Marker(
            [d["lat"], d["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=nom,
            icon=folium.Icon(
                color="green" if is_on else "red",
                icon="signal", prefix="fa"
            ),
        ).add_to(m)

    st_folium(m, use_container_width=True, height=560)


# ══════════════════════════════════════════════════════════════════════════════
# TAB — FLOTTE
# ══════════════════════════════════════════════════════════════════════════════

def tab_flotte(boxes: dict) -> None:
    role = st.session_state.role
    can_edit = role in ("superadmin", "admin")

    # ── Pays disponibles pour le filtre ───────────────────────────────────────
    pays_set = sorted({(d.get("pays") or "").strip()
                       for d in boxes.values() if (d.get("pays") or "").strip()})
    pays_options = ["Tous pays"] + pays_set

    cs, cf, cp = st.columns([3, 1, 1])
    query   = cs.text_input("s", placeholder="🔍  Rechercher par nom, ID ou site…",
                            label_visibility="collapsed")
    filtre  = cf.selectbox("f", ["Tous", "Connecté", "Hors-ligne"],
                           label_visibility="collapsed")
    pays_f  = cp.selectbox("p", pays_options, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    sorted_boxes = dict(sorted(boxes.items(),
                                key=lambda x: x[1].get("status") != "Connecté"))
    has_results  = False

    for box_id, d in sorted_boxes.items():
        nom   = d.get("nom_affiche", box_id)
        is_on = d.get("status") == "Connecté"
        t     = d.get("temperature")
        ip    = d.get("ip_tailscale", "Non communiquée")
        mb    = d.get("data_mb", 0)
        pays  = (d.get("pays") or "").strip()
        site  = (d.get("site") or "").strip()

        if filtre != "Tous" and d.get("status") != filtre: continue
        if pays_f != "Tous pays" and pays != pays_f: continue
        if query and query.lower() not in (nom + box_id + pays + site).lower(): continue

        has_results = True
        dot   = "🟢" if is_on else "🔴"
        loc   = f"  ·  📍 {site or pays}" if (site or pays) else ""

        with st.expander(f"{dot}  {nom}  ·  {box_id}{loc}", expanded=False):
            # ── Santé + uptime (7 derniers jours) ──────────────────────────────
            stats  = _get(f"/api/box_stats/{box_id}") or {}
            uptime = stats.get("uptime")
            sc, scol, semoji, slabel = health_score(d, uptime)
            up_txt = f"{uptime}%" if uptime is not None else "—"
            st.markdown(
                f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;'
                f'margin-bottom:.8rem">{badge_health(sc, scol, semoji, slabel)}'
                f'<span style="background:#EBF4FF;border:1px solid #BFDBFE;border-radius:20px;'
                f'padding:3px 11px;font-size:.74rem;font-weight:700;color:#2878BE">'
                f'📈 Disponibilité 7j · {up_txt}</span></div>',
                unsafe_allow_html=True)

            mc1, mc2, mc3 = st.columns(3)
            tc = temp_color(t)
            mc1.markdown(f"""
            <div style="background:#FAFBFC;border:1px solid #E2E8F0;border-radius:10px;
                        padding:.85rem;text-align:center">
              <div style="font-size:.65rem;font-weight:600;color:#94A3B8;text-transform:uppercase;
                          letter-spacing:.06em;margin-bottom:.3rem">🌡️ Temp CPU</div>
              <div style="font-size:1.55rem;font-weight:800;color:{tc}">{t or "--"}°C</div>
            </div>""", unsafe_allow_html=True)

            mc2.markdown(f"""
            <div style="background:#FAFBFC;border:1px solid #E2E8F0;border-radius:10px;
                        padding:.85rem;text-align:center">
              <div style="font-size:.65rem;font-weight:600;color:#94A3B8;text-transform:uppercase;
                          letter-spacing:.06em;margin-bottom:.3rem">👥 Usagers</div>
              <div style="font-size:1.55rem;font-weight:800;color:#2878BE">{d.get("users",0)}</div>
            </div>""", unsafe_allow_html=True)

            dc = data_color(mb)
            mc3.markdown(f"""
            <div style="background:#FAFBFC;border:1px solid #E2E8F0;border-radius:10px;
                        padding:.85rem;text-align:center">
              <div style="font-size:.65rem;font-weight:600;color:#94A3B8;text-transform:uppercase;
                          letter-spacing:.06em;margin-bottom:.3rem">📶 Data 4G</div>
              <div style="font-size:1.55rem;font-weight:800;color:{dc}">{mb}<span style="font-size:.85rem"> Mo</span></div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                info_row("Statut",          badge_status(is_on)) +
                info_row("IP Tailscale",    ip, mono=True) +
                info_row("Dernier signal",  d.get("last_seen", "?")),
                unsafe_allow_html=True,
            )

            if can_edit:
                st.markdown("<br>", unsafe_allow_html=True)

                # ── Renommer ──────────────────────────────────────────────────
                st.markdown('<p style="font-size:.76rem;font-weight:600;color:#64748B;'
                            'margin-bottom:.3rem">Renommer la box</p>',
                            unsafe_allow_html=True)
                cr1, cr2 = st.columns([5, 1])
                new_name = cr1.text_input("n", value=nom, key=f"rn_{box_id}",
                                           label_visibility="collapsed")
                if cr2.button("✏️", key=f"btn_rn_{box_id}", help="Enregistrer"):
                    res = _post("/api/renommer_box", {
                        "id_materiel": box_id,
                        "nouveau_nom": new_name,
                        "username": st.session_state.username,
                    })
                    if res.get("ok"):
                        st.success("✅ Nom mis à jour")
                        st.session_state.boxes = fetch_boxes()
                        st.rerun()
                    else:
                        st.error(res.get("erreur", "Erreur"))

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Localisation (pays / site) ────────────────────────────────
                st.markdown('<p style="font-size:.76rem;font-weight:600;color:#64748B;'
                            'margin-bottom:.3rem">Localisation (pays · site)</p>',
                            unsafe_allow_html=True)
                cl1, cl2, cl3 = st.columns([2, 3, 1])
                new_pays = cl1.text_input("pays", value=pays, key=f"pays_{box_id}",
                                          placeholder="Pays", label_visibility="collapsed")
                new_site = cl2.text_input("site", value=site, key=f"site_{box_id}",
                                          placeholder="Ville / école / site",
                                          label_visibility="collapsed")
                if cl3.button("📍", key=f"btn_meta_{box_id}", help="Enregistrer la localisation"):
                    res = _post("/api/box_meta", {
                        "id_materiel": box_id,
                        "pays": new_pays, "site": new_site,
                        "done_by": st.session_state.username,
                    })
                    if res.get("ok"):
                        st.success("✅ Localisation enregistrée")
                        st.session_state.boxes = fetch_boxes()
                        st.rerun()
                    else:
                        st.error(res.get("erreur", "Erreur"))

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Reset data ────────────────────────────────────────────────
                ck = f"confirm_{box_id}"
                if ck not in st.session_state:
                    st.session_state[ck] = False

                if not st.session_state[ck]:
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("↺  Remettre data à zéro", key=f"reset_{box_id}",
                                 use_container_width=True):
                        st.session_state[ck] = True
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-warning">
                      ⚠️  Confirmer la remise à zéro pour <b>{nom}</b> ?
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    ca, cb = st.columns(2)
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if ca.button("Confirmer →", key=f"yes_{box_id}", use_container_width=True):
                        res = _post("/api/reset_data", {
                            "id_materiel": box_id,
                            "username": st.session_state.username,
                        })
                        st.session_state[ck] = False
                        if res.get("ok"):
                            st.success("✅ Data remise à zéro")
                            st.session_state.boxes = fetch_boxes()
                            st.rerun()
                        else:
                            st.error(res.get("erreur", "Erreur"))
                    st.markdown("</div>", unsafe_allow_html=True)
                    if cb.button("Annuler", key=f"no_{box_id}", use_container_width=True):
                        st.session_state[ck] = False
                        st.rerun()

            # ── Accès admin ───────────────────────────────────────────────────
            url = admin_url(box_id, ip)
            if url:
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("⚙️  Interface Admin →", url, use_container_width=True)

    if not has_results:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;color:#CBD2DA">
          <div style="font-size:1.5rem;margin-bottom:.5rem">🔍</div>
          <div style="font-size:.9rem;font-weight:500">Aucune box ne correspond</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB — HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════

def tab_historique(boxes: dict) -> None:
    if not boxes:
        st.info("Aucune box disponible.", icon="📊")
        return

    box_ids  = list(boxes.keys())
    box_noms = [boxes[b].get("nom_affiche", b) for b in box_ids]

    selected_nom = st.selectbox(
        "Sélectionner une box",
        box_noms,
        key="hist_select",
    )
    selected_id = box_ids[box_noms.index(selected_nom)]

    data = _get(f"/api/history/{selected_id}")

    if not data:
        st.markdown("""
        <div class="alert-info" style="margin-top:1rem">
          📊 Aucune donnée historique pour cette box — les données s'accumulent après chaque
          mise à jour reçue de la box physique.
        </div>""", unsafe_allow_html=True)
        return

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # ── Graphique température ─────────────────────────────────────────────────
    st.markdown(section_title("🌡️ Température CPU", "Évolution dans le temps"),
                unsafe_allow_html=True)

    fig_temp = px.area(
        df, x="timestamp", y="temperature",
        color_discrete_sequence=["#2878BE"],
        labels={"timestamp": "", "temperature": "°C"},
    )
    fig_temp.add_hline(y=50, line_dash="dot", line_color="#EA580C",
                       annotation_text="Seuil orange 50°C")
    fig_temp.add_hline(y=70, line_dash="dot", line_color="#DC2626",
                       annotation_text="Seuil rouge 70°C")
    fig_temp.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        font_family="Plus Jakarta Sans",
        yaxis=dict(gridcolor="#F1F5F9"),
        xaxis=dict(gridcolor="#F1F5F9"),
    )
    fig_temp.update_traces(fillcolor="rgba(40,120,190,.12)", line_width=2)
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphique usagers ─────────────────────────────────────────────────────
    col_u, col_d = st.columns(2)
    with col_u:
        st.markdown(section_title("👥 Usagers connectés"), unsafe_allow_html=True)
        fig_users = px.bar(
            df, x="timestamp", y="users",
            color_discrete_sequence=["#F5C020"],
            labels={"timestamp": "", "users": "Usagers"},
        )
        fig_users.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            font_family="Plus Jakarta Sans",
            yaxis=dict(gridcolor="#F1F5F9"),
            xaxis=dict(gridcolor="#F1F5F9"),
        )
        st.plotly_chart(fig_users, use_container_width=True)

    with col_d:
        st.markdown(section_title("📶 Consommation Data (Mo)"), unsafe_allow_html=True)
        fig_data = px.line(
            df, x="timestamp", y="data_mb",
            color_discrete_sequence=["#16A34A"],
            labels={"timestamp": "", "data_mb": "Mo"},
        )
        fig_data.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            font_family="Plus Jakarta Sans",
            yaxis=dict(gridcolor="#F1F5F9"),
            xaxis=dict(gridcolor="#F1F5F9"),
        )
        fig_data.update_traces(line_width=2.5)
        st.plotly_chart(fig_data, use_container_width=True)

    # ── Stats récap ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_title("📋 Statistiques résumées"), unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(kpi_card("🌡️", "Temp. max",
                          f"{df['temperature'].max():.1f}°C",
                          temp_color(df['temperature'].max())), unsafe_allow_html=True)
    s2.markdown(kpi_card("🌡️", "Temp. moy",
                          f"{df['temperature'].mean():.1f}°C", "#2878BE"), unsafe_allow_html=True)
    s3.markdown(kpi_card("👥", "Usagers max",
                          str(int(df['users'].max())), "#F5C020"), unsafe_allow_html=True)
    s4.markdown(kpi_card("📶", "Data max",
                          f"{df['data_mb'].max():.0f} Mo", "#16A34A"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB — RAPPORTS
# ══════════════════════════════════════════════════════════════════════════════

def _build_report_df(boxes: dict) -> pd.DataFrame:
    """Construit le tableau récapitulatif de la flotte (avec uptime 7j)."""
    rows = []
    for box_id, d in boxes.items():
        stats  = _get(f"/api/box_stats/{box_id}") or {}
        rows.append({
            "Box":           d.get("nom_affiche", box_id),
            "ID":            box_id,
            "Pays":          (d.get("pays") or "").strip() or "—",
            "Site":          (d.get("site") or "").strip() or "—",
            "Statut":        d.get("status", "?"),
            "Température °C": d.get("temperature", ""),
            "Usagers":       d.get("users", 0),
            "Data Mo":       d.get("data_mb", 0),
            "Disponibilité 7j %": stats.get("uptime", "—"),
            "Temp. moy 7j":  stats.get("temp_moy", "—"),
            "Dernier signal": d.get("last_seen", "?"),
        })
    return pd.DataFrame(rows)


def _excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Flotte Yeelen")
    return buf.getvalue()


def _pdf_bytes(df: pd.DataFrame, online: int, total: int,
               total_u: int, total_d: float) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    NL = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def s(txt) -> str:
        # Sécurité encodage latin-1 (police core fpdf)
        return str(txt).encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # En-tête bandeau bleu Yeelen
    pdf.set_fill_color(40, 120, 190)
    pdf.rect(0, 0, 297, 22, "F")
    pdf.set_xy(10, 6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, s("YEELEN CONSULTING  -  Rapport de flotte SchoolBox"), **NL)

    pdf.set_xy(10, 26)
    pdf.set_text_color(120, 120, 120)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, s(f"Genere le {time.strftime('%d/%m/%Y a %H:%M')}  -  "
                     f"Tour de Controle"), **NL)

    # Bandeau KPIs
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(26, 42, 58)
    kpi = (f"Total boxes : {total}      "
           f"En ligne : {online}      "
           f"Usagers : {total_u}      "
           f"Data totale : {total_d:.0f} Mo")
    pdf.cell(0, 7, s(kpi), **NL)
    pdf.ln(2)

    # Tableau
    cols   = ["Box", "Pays", "Site", "Statut", "Température °C",
              "Usagers", "Data Mo", "Disponibilité 7j %"]
    widths = [55, 32, 45, 26, 28, 22, 26, 34]

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(235, 244, 255)
    pdf.set_text_color(40, 120, 190)
    for c, w in zip(cols, widths):
        pdf.cell(w, 8, s(c.replace("°", "deg ").replace("é", "e")),
                 border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    for _, row in df.iterrows():
        on = row["Statut"] == "Connecté"
        for c, w in zip(cols, widths):
            val = row.get(c, "")
            if c == "Statut":
                pdf.set_text_color(22, 163, 74) if on else pdf.set_text_color(220, 38, 38)
                pdf.cell(w, 7, s("En ligne" if on else "Hors-ligne"), border=1, align="C")
                pdf.set_text_color(40, 40, 40)
            else:
                pdf.cell(w, 7, s(val), border=1, align="C")
        pdf.ln()

    out = pdf.output()
    return bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")


def tab_rapports(boxes: dict) -> None:
    st.markdown(section_title("📄 Rapports & exports",
                              "Documents prêts à partager avec tes partenaires"),
                unsafe_allow_html=True)

    if not boxes:
        st.info("Aucune box disponible pour générer un rapport.", icon="📄")
        return

    online   = sum(1 for b in boxes.values() if b.get("status") == "Connecté")
    total    = len(boxes)
    total_u  = sum(b.get("users", 0) for b in boxes.values())
    total_d  = sum(b.get("data_mb", 0) for b in boxes.values())

    st.markdown("""
    <div class="alert-info" style="margin-bottom:1.2rem">
      📊 Le rapport reprend l'état actuel de toute la flotte + le taux de disponibilité
      sur 7 jours de chaque box. Idéal pour un bilan mensuel aux bailleurs.
    </div>""", unsafe_allow_html=True)

    if st.button("⚙️  Générer le rapport de flotte", use_container_width=False):
        with st.spinner("Compilation des données…"):
            df = _build_report_df(boxes)
            st.session_state["report_df"]    = df
            try:
                st.session_state["report_xlsx"] = _excel_bytes(df)
            except Exception as e:
                st.session_state["report_xlsx"] = None
                st.warning(f"Excel indisponible : {e}")
            try:
                st.session_state["report_pdf"] = _pdf_bytes(df, online, total, total_u, total_d)
            except Exception as e:
                st.session_state["report_pdf"] = None
                st.warning(f"PDF indisponible : {e}")
        st.success("✅ Rapport généré.")

    if "report_df" in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(st.session_state["report_df"], use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        cdl1, cdl2 = st.columns(2)
        stamp = time.strftime("%Y%m%d_%H%M")
        if st.session_state.get("report_pdf"):
            with cdl1:
                st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
                st.download_button("⬇️  Télécharger le PDF",
                                   st.session_state["report_pdf"],
                                   file_name=f"Rapport_Yeelen_{stamp}.pdf",
                                   mime="application/pdf",
                                   use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.get("report_xlsx"):
            with cdl2:
                st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
                st.download_button("⬇️  Télécharger l'Excel",
                                   st.session_state["report_xlsx"],
                                   file_name=f"Rapport_Yeelen_{stamp}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB — JOURNAL
# ══════════════════════════════════════════════════════════════════════════════

def tab_journal() -> None:
    logs = _get("/api/logs")
    if not logs:
        st.info("Aucune action enregistrée.", icon="📋")
        return

    ACTION_ICONS = {
        "CREATE_USER":      "👤",  "DELETE_USER":    "🗑️",
        "ACTIVATE_USER":    "✅",  "DEACTIVATE_USER":"🚫",
        "UPDATE_PASSWORD":  "🔑",  "RENAME_BOX":     "✏️",
        "RESET_DATA":       "↺",   "REGENERATE_TOKEN":"🔑",
    }

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:1rem">
      <div style="font-size:.85rem;color:#64748B;font-weight:500">
        {len(logs)} entrée(s) · 150 dernières actions
      </div>
    </div>""", unsafe_allow_html=True)

    for log in logs:
        icon = ACTION_ICONS.get(log["action"], "📌")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:.6rem .8rem;
                    background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;
                    margin-bottom:.4rem;transition:border-color .15s">
          <div style="width:30px;height:30px;background:#F4F7FB;border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:.9rem;flex-shrink:0">{icon}</div>
          <div style="flex:1">
            <span style="font-size:.82rem;font-weight:700;color:#1A2A3A">
              {log['action'].replace('_',' ').title()}</span>
            <span style="font-size:.79rem;color:#64748B;margin-left:.5rem">
              {log['details'] or ''}</span>
          </div>
          <div style="text-align:right;flex-shrink:0">
            <div style="font-size:.73rem;font-weight:600;color:#2878BE">{log['username'] or '—'}</div>
            <div style="font-size:.69rem;color:#94A3B8">{log['timestamp'] or ''}</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB — UTILISATEURS
# ══════════════════════════════════════════════════════════════════════════════

def tab_utilisateurs() -> None:
    role = st.session_state.role
    me   = st.session_state.username

    if role not in ("superadmin", "admin"):
        st.markdown("""
        <div class="alert-warning">🔒 Accès réservé aux administrateurs.</div>
        """, unsafe_allow_html=True)
        return

    users = _get("/api/users") or []

    # ── Liste des utilisateurs ────────────────────────────────────────────────
    st.markdown(section_title("👥 Comptes utilisateurs",
                               f"{len(users)} compte(s) enregistré(s)"),
                unsafe_allow_html=True)

    for u in users:
        is_me = u["username"] == me
        is_sa = u["role"] == "superadmin"
        active = bool(u["is_active"])

        col_info, col_actions = st.columns([4, 2])
        with col_info:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:.65rem .9rem;
                        background:{'#FFFFFF' if active else '#F8FAFC'};
                        border:1px solid {'#E2E8F0' if active else '#F1F5F9'};
                        border-radius:10px;opacity:{'1' if active else '.6'}">
              <div style="width:34px;height:34px;background:{'#EBF4FF' if active else '#F1F5F9'};
                          border-radius:8px;display:flex;align-items:center;
                          justify-content:center;font-size:.9rem;flex-shrink:0">
                {'⭐' if is_sa else '🔧' if u['role']=='admin' else '👁'}
              </div>
              <div>
                <div style="font-size:.88rem;font-weight:700;color:#1A2A3A">
                  {u['username']} {'<span style="font-size:.7rem;color:#94A3B8">(vous)</span>' if is_me else ''}
                </div>
                <div style="display:flex;gap:6px;margin-top:3px;align-items:center">
                  {badge_role(u['role'])}
                  {'<span style="font-size:.68rem;color:#94A3B8">·</span>' if u.get('last_login') else ''}
                  {'<span style="font-size:.68rem;color:#94A3B8">Dernière connexion: '+u['last_login']+'</span>' if u.get('last_login') else ''}
                </div>
              </div>
              {'<span style="margin-left:auto;font-size:.68rem;background:#FFF1F1;color:#DC2626;'
               'border:1px solid #FECACA;padding:2px 8px;border-radius:10px;font-weight:600">'
               'Désactivé</span>' if not active else ''}
            </div>""", unsafe_allow_html=True)

        with col_actions:
            if not is_sa and not is_me:
                a1, a2 = st.columns(2)
                if active:
                    if a1.button("🚫", key=f"deact_{u['id']}", help="Désactiver"):
                        _post(f"/api/users/{u['id']}/toggle",
                              {"active": False, "done_by": me})
                        st.rerun()
                else:
                    if a1.button("✅", key=f"act_{u['id']}", help="Activer"):
                        _post(f"/api/users/{u['id']}/toggle",
                              {"active": True, "done_by": me})
                        st.rerun()

                if a2.button("🗑️", key=f"del_{u['id']}", help="Supprimer"):
                    _delete(f"/api/users/{u['id']}", {"deleted_by": me})
                    st.rerun()

        st.markdown("<div style='margin-bottom:.3rem'></div>", unsafe_allow_html=True)

    st.divider()

    # ── Créer un utilisateur ──────────────────────────────────────────────────
    st.markdown(section_title("➕ Créer un compte"), unsafe_allow_html=True)

    with st.form("create_user"):
        uc1, uc2 = st.columns(2)
        new_username = uc1.text_input("Identifiant", placeholder="prenom.nom")
        new_password = uc2.text_input("Mot de passe", type="password",
                                       placeholder="min. 6 caractères")

        # Rôles disponibles selon le rang
        if role == "superadmin":
            roles_dispo = ["viewer", "admin"]
        else:
            roles_dispo = ["viewer"]

        new_role = st.selectbox("Rôle", roles_dispo,
                                 format_func=lambda r: {
                                     "viewer": "👁  Viewer — lecture seule",
                                     "admin":  "🔧 Admin — toutes les actions",
                                 }[r])

        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        create_submitted = st.form_submit_button("Créer le compte →",
                                                  use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if create_submitted:
        if not new_username or not new_password:
            st.error("Identifiant et mot de passe requis.")
        else:
            res = _post("/api/users", {
                "username": new_username,
                "password": new_password,
                "role":     new_role,
                "created_by": me,
            })
            if res.get("ok"):
                st.success(f"✅ Compte **{new_username}** créé avec succès.")
                st.rerun()
            else:
                st.error(res.get("erreur", "Erreur lors de la création"))

    # ── Changer son propre mot de passe ───────────────────────────────────────
    st.divider()
    st.markdown(section_title("🔑 Changer mon mot de passe"), unsafe_allow_html=True)

    with st.form("change_pw"):
        pw1 = st.text_input("Nouveau mot de passe", type="password",
                             placeholder="min. 6 caractères")
        pw2 = st.text_input("Confirmer", type="password", placeholder="••••••••")
        st.markdown('<div class="btn-gold">', unsafe_allow_html=True)
        pw_submitted = st.form_submit_button("Mettre à jour →", use_container_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    if pw_submitted:
        if pw1 != pw2:
            st.error("Les mots de passe ne correspondent pas.")
        else:
            res = _post("/api/users/password",
                        {"username": me, "new_password": pw1, "done_by": me})
            if res.get("ok"):
                st.success("✅ Mot de passe mis à jour.")
            else:
                st.error(res.get("erreur", "Erreur"))


# ══════════════════════════════════════════════════════════════════════════════
# TAB — PARAMÈTRES
# ══════════════════════════════════════════════════════════════════════════════

def tab_parametres() -> None:
    role = st.session_state.role
    if role != "superadmin":
        st.markdown('<div class="alert-warning">🔒 Réservé au superadmin.</div>',
                    unsafe_allow_html=True)
        return

    st.markdown(section_title("⚙️ Paramètres système"), unsafe_allow_html=True)

    # ── Endpoint boxes ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid #2878BE;border-radius:12px;
                padding:1.3rem 1.4rem;margin-bottom:1.2rem">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:.6rem">
        <span style="font-size:1.1rem">📡</span>
        <div style="font-size:.9rem;font-weight:800;color:#1A2A3A">
          Adresse de réception — à configurer sur chaque box</div>
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;
                  color:#2878BE;background:#EBF4FF;border:1px solid #BFDBFE;
                  border-radius:8px;padding:.8rem 1rem;word-break:break-all;
                  margin-bottom:.7rem;font-weight:600">
        {FLASK_URL}/mise_a_jour_box
      </div>
      <div style="font-size:.78rem;color:#2878BE;font-weight:600;
                  background:#EBF4FF;border:1px solid #BFDBFE;
                  border-radius:6px;padding:.4rem .7rem">
        🔑 Chaque box doit envoyer son <b>api_token</b> (voir ci-dessous) pour être acceptée.
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Format JSON attendu ───────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                padding:1.2rem 1.4rem;margin-bottom:1.2rem">
      <div style="font-size:.84rem;font-weight:700;color:#1A2A3A;margin-bottom:.7rem">
        📦 Format JSON attendu (POST depuis chaque box)
      </div>
      <pre style="background:#F4F7FB;border:1px solid #E2E8F0;border-radius:8px;
                  padding:.9rem 1rem;font-family:'JetBrains Mono',monospace;
                  font-size:.78rem;color:#1A2A3A;overflow-x:auto;margin:0">{
  "id_materiel":  "EDUBOX_SENEGAL_01",
  "lat":           14.6928,
  "lon":           -17.4467,
  "temperature":   47.3,
  "users":         15,
  "data_mb":       125.4,
  "ip_tailscale":  "100.x.x.x",
  "api_token":     "votre_token_ci_dessous"
}</pre>
    </div>""", unsafe_allow_html=True)

    # ── Diagnostic boxes ──────────────────────────────────────────────────────
    boxes = st.session_state.get("boxes", {})
    real_boxes = {k: v for k, v in boxes.items() if "DEMO" not in k.upper()}
    demo_boxes = {k: v for k, v in boxes.items() if "DEMO" in k.upper()}

    st.markdown(section_title("🔍 Diagnostic connexion"), unsafe_allow_html=True)

    col_r, col_d = st.columns(2)
    col_r.markdown(f"""
    <div style="background:{'#F0FDF4' if real_boxes else '#FFF1F1'};
                border:1px solid {'#BBF7D0' if real_boxes else '#FECACA'};
                border-radius:10px;padding:1rem;text-align:center">
      <div style="font-size:2rem;font-weight:800;
                  color:{'#16A34A' if real_boxes else '#DC2626'}">{len(real_boxes)}</div>
      <div style="font-size:.75rem;font-weight:600;
                  color:{'#16A34A' if real_boxes else '#DC2626'}">Boxes réelles connectées</div>
    </div>""", unsafe_allow_html=True)

    col_d.markdown(f"""
    <div style="background:#F4F7FB;border:1px solid #E2E8F0;
                border-radius:10px;padding:1rem;text-align:center">
      <div style="font-size:2rem;font-weight:800;color:#94A3B8">{len(demo_boxes)}</div>
      <div style="font-size:.75rem;font-weight:600;color:#94A3B8">Boxes démo (à supprimer)</div>
    </div>""", unsafe_allow_html=True)

    if not real_boxes:
        st.markdown("""
        <div class="alert-warning" style="margin-top:1rem">
          ⚠️ Aucune box réelle détectée. Vérifie que :
          <ol style="margin:.5rem 0 0 1.2rem;font-size:.82rem">
            <li>Flask tourne bien sur ce PC : <code>python app.py</code></li>
            <li>Les boxes envoient un POST à l'adresse ci-dessus</li>
            <li>Le pare-feu Windows autorise le port 5000</li>
            <li>Tailscale est connecté sur les boxes ET ce PC</li>
          </ol>
        </div>""", unsafe_allow_html=True)
    else:
        for bid, d in real_boxes.items():
            is_on = d.get("status") == "Connecté"
            nom   = d.get("nom_affiche", bid)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:.6rem .9rem;
                        background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;
                        margin-top:.5rem">
              <span style="font-size:.85rem">{'🟢' if is_on else '🔴'}</span>
              <div style="flex:1">
                <div style="font-size:.85rem;font-weight:700">{nom}</div>
                <div style="font-size:.72rem;color:#94A3B8">{bid}</div>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;
                          color:#2878BE">{d.get('ip_tailscale','–')}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Sécurité & alertes ────────────────────────────────────────────────────
    st.markdown(section_title("🛡️ Sécurité & alertes"), unsafe_allow_html=True)
    sec_on   = bool(INTERNAL_API_KEY)
    st.markdown(
        info_row("Protection API interne",
                 ('<span style="color:#16A34A;font-weight:700">✅ Activée</span>' if sec_on
                  else '<span style="color:#DC2626;font-weight:700">⚠️ Désactivée — '
                       'définir INTERNAL_API_KEY</span>')) +
        info_row("Serveur",
                 ('🌐 Cloud (public)' if FLASK_URL.startswith("https")
                  else '💻 Local')),
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="alert-info" style="margin:.6rem 0 1.2rem">
      📧 Les alertes email (box hors-ligne / surchauffe) se configurent côté serveur Render
      via les variables <code>ALERT_EMAIL_FROM</code>, <code>ALERT_EMAIL_PASSWORD</code>,
      <code>ALERT_EMAIL_TO</code>. Voir le guide de déploiement.
    </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Token API ─────────────────────────────────────────────────────────────
    st.markdown(section_title("🔑 Token API des boxes"), unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:.8rem;color:#64748B;margin-bottom:.9rem">
      Ce token doit être présent dans chaque envoi des boxes (champ <code>api_token</code>).
      Le régénérer invalide immédiatement l'ancien — il faudra le mettre à jour sur chaque box.
    </div>""", unsafe_allow_html=True)

    token_data = _get("/api/token_info")
    current_token = token_data.get("token", "–") if token_data else "–"

    st.markdown(f"""
    <div style="background:#F4F7FB;border:1px solid #E2E8F0;border-radius:8px;
                padding:.7rem 1rem;font-family:'JetBrains Mono',monospace;
                font-size:.79rem;color:#2878BE;word-break:break-all;
                margin-bottom:.9rem">{current_token}</div>""", unsafe_allow_html=True)

    ck_token = "confirm_regen_token"
    if ck_token not in st.session_state:
        st.session_state[ck_token] = False

    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    if not st.session_state[ck_token]:
        if st.button("↻  Régénérer le token", help="Invalide l'ancien token immédiatement"):
            st.session_state[ck_token] = True
            st.rerun()
    else:
        st.warning("⚠️ Toutes les boxes utilisant l'ancien token cesseront d'envoyer "
                   "jusqu'à mise à jour de leur fichier tracker_gps.py.")
        ca, cb = st.columns(2)
        if ca.button("Confirmer régénération →", use_container_width=True):
            res = _post("/api/token_regenerate", {})
            st.session_state[ck_token] = False
            if res.get("ok"):
                st.success(f"✅ Nouveau token : `{res.get('token', '')}`")
                st.rerun()
        if cb.button("Annuler", use_container_width=True):
            st.session_state[ck_token] = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Infos système ─────────────────────────────────────────────────────────
    st.markdown(section_title("ℹ️ Informations système"), unsafe_allow_html=True)
    st.markdown(
        info_row("Version",            "Tour de Contrôle v5") +
        info_row("Serveur Flask",       FLASK_URL, mono=True) +
        info_row("Endpoint boxes",     f"{FLASK_URL}/mise_a_jour_box", mono=True) +
        info_row("Base de données",    "SQLite — tourdecontrole.db", mono=True) +
        info_row("Timeout hors-ligne", "6 minutes sans signal"),
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

def main_app() -> None:
    maybe_refresh()
    boxes   = st.session_state.boxes
    online  = sum(1 for b in boxes.values() if b.get("status") == "Connecté")
    offline = len(boxes) - online

    render_sidebar(boxes)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;
                margin-bottom:1.5rem">
      <div>
        <h1 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.55rem;
                   font-weight:800;color:#1A2A3A;margin:0;letter-spacing:-.025em">
          Tableau de bord</h1>
        <p style="font-size:.83rem;color:#94A3B8;margin:.3rem 0 0;font-weight:500">
          {len(boxes)} boxes · Afrique de l'Ouest · Yeelen Consulting</p>
      </div>
      <div style="display:flex;align-items:center;gap:7px;background:#F0FDF4;
                  border:1px solid #BBF7D0;border-radius:20px;padding:.35rem .9rem">
        <span style="width:7px;height:7px;background:#16A34A;border-radius:50%;
                      display:inline-block"></span>
        <span style="font-size:.78rem;font-weight:700;color:#16A34A">{online} en ligne</span>
        <span style="color:#BBF7D0;margin:0 2px">·</span>
        <span style="font-size:.78rem;font-weight:600;color:#64748B">{offline} hors-ligne</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    total_u = sum(b.get("users",   0) for b in boxes.values())
    total_d = sum(b.get("data_mb", 0) for b in boxes.values())

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi_card("📦", "Total boxes",    str(len(boxes)),
                          "#1A2A3A", "#E2E8F0"), unsafe_allow_html=True)
    k2.markdown(kpi_card("🟢", "En ligne",        str(online),
                          "#16A34A", "#BBF7D0"), unsafe_allow_html=True)
    k3.markdown(kpi_card("👥", "Usagers actifs",  str(total_u),
                          "#2878BE", "#2878BE",
                          f"sur {len(boxes)} boxes"), unsafe_allow_html=True)
    k4.markdown(kpi_card("📶", "Data consommée",  f"{total_d:.0f} Mo",
                          "#D4A017", "#F5C020"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Onglets ───────────────────────────────────────────────────────────────
    role = st.session_state.role

    # (libellé, fonction de rendu) — construit dynamiquement selon le rôle
    tab_defs = [
        ("🗺️  Carte",       lambda: tab_carte(boxes)),
        ("📋  Flotte",      lambda: tab_flotte(boxes)),
        ("📊  Historique",  lambda: tab_historique(boxes)),
        ("📄  Rapports",    lambda: tab_rapports(boxes)),
        ("🗒️  Journal",     tab_journal),
    ]
    if role in ("superadmin", "admin"):
        tab_defs.append(("👥  Utilisateurs", tab_utilisateurs))
    if role == "superadmin":
        tab_defs.append(("⚙️  Paramètres", tab_parametres))

    tabs = st.tabs([label for label, _ in tab_defs])
    for tab, (_, render) in zip(tabs, tab_defs):
        with tab:
            render()


# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.logged_in:
    main_app()
else:
    login_page()
