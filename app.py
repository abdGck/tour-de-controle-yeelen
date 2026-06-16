"""
Tour de Contrôle — Serveur Flask
Yeelen Consulting · SchoolBox Africa

Reçoit les données des boxes via Tailscale.
Expose une API JSON sécurisée pour l'interface Streamlit.
Gère : authentification, users, historique, renommage, reset data.

Lancement : python app.py
"""

import os
import ssl
import time
import smtplib
import threading
from email.mime.text import MIMEText
from functools import wraps
from datetime import datetime, timedelta, timezone

from flask import (Flask, request, jsonify, session,
                   redirect, url_for, render_template)

from database import (
    init_db, init_default_names,
    login_user, get_users, create_user, delete_user, toggle_user, update_password,
    get_box_name, save_box_name,
    save_box_snapshot, get_box_history, get_gps_trail, get_box_stats,
    get_box_meta, get_all_box_meta, save_box_meta,
    get_logs, log_action,
    get_api_token, verify_api_token, regenerate_api_token,
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", os.urandom(32).hex())

TIMEOUT_MIN = 6

# ── Sécurité API interne ───────────────────────────────────────────────────────
# Clé partagée entre Streamlit (front) et Flask (back) pour protéger les routes
# sensibles maintenant que le serveur est public sur Internet. Si non définie →
# pas d'enforcement (mode développement local sans configuration).
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")


def require_internal(fn):
    """Protège une route : exige l'en-tête X-Internal-Key si INTERNAL_API_KEY est défini."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if INTERNAL_API_KEY:
            if request.headers.get("X-Internal-Key", "") != INTERNAL_API_KEY:
                return jsonify({"erreur": "Accès non autorisé"}), 403
        return fn(*args, **kwargs)
    return wrapper

# ── Initialisation DB ─────────────────────────────────────────────────────────
init_db()

# ── Données en mémoire (cache live des boxes) ─────────────────────────────────
_now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")

box_data: dict = {
    "EDUBOX_DEMO_01": {
        "lat": 14.6928, "lon": -17.4467, "status": "Connecté",
        "temperature": 45.2, "users": 12, "data_mb": 105.5, "raw_data_mb": 105.5,
        "ip_tailscale": "100.72.10.11", "last_seen": _now,
        "timestamp_interne": datetime.now(),
    },
    "EDUBOX_DEMO_02": {
        "lat": 12.6392, "lon": -8.0028, "status": "Hors-ligne",
        "temperature": 58.0, "users": 0, "data_mb": 852.1, "raw_data_mb": 852.1,
        "ip_tailscale": "100.72.10.18", "last_seen": "20/05/2026 18:30:00",
        "timestamp_interne": datetime.now() - timedelta(hours=2),
    },
    "BOX_DEMO_03": {
        "lat": 5.3600, "lon": -4.0083, "status": "Connecté",
        "temperature": 38.5, "users": 27, "data_mb": 44.2, "raw_data_mb": 44.2,
        "ip_tailscale": "100.72.10.22", "last_seen": _now,
        "timestamp_interne": datetime.now(),
    },
    "BOX_DEMO_04": {
        "lat": 6.1375, "lon": 1.2123, "status": "Connecté",
        "temperature": 73.4, "users": 8, "data_mb": 230.0, "raw_data_mb": 230.0,
        "ip_tailscale": "100.72.10.30", "last_seen": _now,
        "timestamp_interne": datetime.now(),
    },
}

init_default_names({
    "EDUBOX_DEMO_01": "SchoolBox Dakar 01",
    "EDUBOX_DEMO_02": "SchoolBox Bamako 01",
    "BOX_DEMO_03":    "AgriBox Abidjan 01",
    "BOX_DEMO_04":    "SchoolBox Lomé 01",
})

data_offsets: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def verifier_statuts() -> None:
    limite = datetime.now() - timedelta(minutes=TIMEOUT_MIN)
    for data in box_data.values():
        if data.get("timestamp_interne") and data["timestamp_interne"] < limite:
            data["status"] = "Hors-ligne"


def boxes_pour_api() -> dict:
    verifier_statuts()
    metas = get_all_box_meta()
    out = {}
    for id_mat, data in box_data.items():
        d = {k: v for k, v in data.items() if k != "timestamp_interne"}
        d["nom_affiche"] = get_box_name(id_mat, id_mat)
        meta = metas.get(id_mat, {"pays": "", "site": ""})
        d["pays"] = meta.get("pays", "")
        d["site"] = meta.get("site", "")
        out[id_mat] = d
    return out


# ══════════════════════════════════════════════════════════════════════════════
# SYSTÈME D'ALERTES EMAIL
# ══════════════════════════════════════════════════════════════════════════════

ALERT_FROM      = os.environ.get("ALERT_EMAIL_FROM", "")
ALERT_PASSWORD  = os.environ.get("ALERT_EMAIL_PASSWORD", "")
ALERT_TO        = os.environ.get("ALERT_EMAIL_TO", "")
ALERT_SMTP_HOST = os.environ.get("ALERT_SMTP_HOST", "smtp.gmail.com")
ALERT_SMTP_PORT = int(os.environ.get("ALERT_SMTP_PORT", "587"))
ALERT_TEMP_MAX  = float(os.environ.get("ALERT_TEMP_THRESHOLD", "70"))
ALERTS_ENABLED  = bool(ALERT_FROM and ALERT_PASSWORD and ALERT_TO)

# Mémoire anti-spam : ne pas renvoyer la même alerte en boucle
_alert_state: dict = {}   # box_id → {"offline": bool, "overheat": bool}


def _envoyer_email(sujet: str, corps: str) -> None:
    if not ALERTS_ENABLED:
        return
    try:
        msg = MIMEText(corps, "plain", "utf-8")
        msg["Subject"] = sujet
        msg["From"]    = ALERT_FROM
        msg["To"]      = ALERT_TO
        ctx = ssl.create_default_context()
        with smtplib.SMTP(ALERT_SMTP_HOST, ALERT_SMTP_PORT, timeout=15) as server:
            server.starttls(context=ctx)
            server.login(ALERT_FROM, ALERT_PASSWORD)
            server.sendmail(ALERT_FROM, [t.strip() for t in ALERT_TO.split(",")], msg.as_string())
        print(f"📧 Alerte envoyée : {sujet}")
    except Exception as e:
        print(f"❌ Échec envoi email : {e}")


def _verifier_alertes() -> None:
    """Vérifie chaque box et envoie un email si offline ou surchauffe (avec anti-spam)."""
    verifier_statuts()
    heure = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for box_id, data in box_data.items():
        if "DEMO" in box_id.upper():
            continue   # ne pas alerter sur les boxes de démonstration
        nom   = get_box_name(box_id, box_id)
        etat  = _alert_state.setdefault(box_id, {"offline": False, "overheat": False})

        # ── Hors-ligne ────────────────────────────────────────────────────────
        is_offline = data.get("status") != "Connecté"
        if is_offline and not etat["offline"]:
            _envoyer_email(
                f"🔴 Box HORS-LIGNE — {nom}",
                f"La box « {nom} » ({box_id}) ne répond plus.\n\n"
                f"Dernier signal : {data.get('last_seen', '?')}\n"
                f"IP Tailscale   : {data.get('ip_tailscale', '?')}\n"
                f"Détecté le     : {heure}\n\n"
                f"— Tour de Contrôle Yeelen",
            )
            etat["offline"] = True
        elif not is_offline and etat["offline"]:
            _envoyer_email(
                f"🟢 Box de retour EN LIGNE — {nom}",
                f"La box « {nom} » ({box_id}) a renvoyé un signal.\n"
                f"Rétabli le : {heure}\n\n— Tour de Contrôle Yeelen",
            )
            etat["offline"] = False

        # ── Surchauffe ────────────────────────────────────────────────────────
        temp = data.get("temperature")
        if temp is not None and not is_offline:
            if temp >= ALERT_TEMP_MAX and not etat["overheat"]:
                _envoyer_email(
                    f"🌡️ SURCHAUFFE — {nom} ({temp}°C)",
                    f"La box « {nom} » ({box_id}) dépasse le seuil de {ALERT_TEMP_MAX}°C.\n\n"
                    f"Température : {temp}°C\n"
                    f"Détecté le  : {heure}\n\n"
                    f"⚠️ Risque matériel. Vérifie la ventilation / l'emplacement.\n\n"
                    f"— Tour de Contrôle Yeelen",
                )
                etat["overheat"] = True
            elif temp < ALERT_TEMP_MAX - 5 and etat["overheat"]:
                etat["overheat"] = False   # hystérésis : revient sous seuil - 5°C


def _boucle_surveillance() -> None:
    """Thread de fond : vérifie les alertes toutes les 60 secondes."""
    while True:
        try:
            _verifier_alertes()
        except Exception as e:
            print(f"⚠️ Erreur surveillance alertes : {e}")
        time.sleep(60)


if ALERTS_ENABLED:
    threading.Thread(target=_boucle_surveillance, daemon=True).start()
    print(f"✅ Alertes email activées → {ALERT_TO}")


def _is_trusted(req) -> bool:
    """Fait confiance à localhost ET à tout le réseau Tailscale (100.x.x.x)."""
    ip = req.remote_addr or ""
    return ip in ("127.0.0.1", "::1") or ip.startswith("100.")


def _is_local(req) -> bool:
    return req.remote_addr in ("127.0.0.1", "::1")


# ══════════════════════════════════════════════════════════════════════════════
# API JSON — utilisée par Streamlit
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/boxes")
@require_internal
def api_boxes():
    return jsonify(boxes_pour_api())


@app.route("/api/login", methods=["POST"])
def api_login():
    body = request.get_json(silent=True) or {}
    user = login_user(body.get("identifiant", ""), body.get("mot_de_passe", ""))
    if user:
        return jsonify({
            "ok": True,
            "role": user["role"],
            "username": user["username"],
        }), 200
    return jsonify({"ok": False, "erreur": "Identifiant ou mot de passe incorrect"}), 401


# ── Boxes ─────────────────────────────────────────────────────────────────────

@app.route("/api/renommer_box", methods=["POST"])
@require_internal
def api_renommer():
    body = request.get_json(silent=True) or {}
    id_mat = body.get("id_materiel")
    nom    = body.get("nouveau_nom", "").strip()
    user   = body.get("username", "api")
    if id_mat and nom:
        save_box_name(id_mat, nom, user)
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 400


@app.route("/api/reset_data", methods=["POST"])
@require_internal
def api_reset_data():
    body   = request.get_json(silent=True) or {}
    id_mat = body.get("id_materiel")
    user   = body.get("username", "api")
    if id_mat and id_mat in box_data:
        data_offsets[id_mat] = box_data[id_mat].get("raw_data_mb", 0)
        box_data[id_mat]["data_mb"] = 0.0
        log_action(user, "RESET_DATA", f"Remise à zéro data — {id_mat}")
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 404


@app.route("/api/history/<box_id>")
@require_internal
def api_history(box_id):
    return jsonify(get_box_history(box_id))


@app.route("/api/gps_trail/<box_id>")
@require_internal
def api_gps_trail(box_id):
    return jsonify(get_gps_trail(box_id))


@app.route("/api/box_stats/<box_id>")
@require_internal
def api_box_stats(box_id):
    hours = int(request.args.get("hours", 168))
    return jsonify(get_box_stats(box_id, hours))


# ── Métadonnées (pays / site) ─────────────────────────────────────────────────

@app.route("/api/box_meta", methods=["POST"])
@require_internal
def api_box_meta():
    body = request.get_json(silent=True) or {}
    id_mat = body.get("id_materiel")
    if not id_mat:
        return jsonify({"ok": False}), 400
    save_box_meta(id_mat, body.get("pays", ""), body.get("site", ""),
                  body.get("done_by", "api"))
    return jsonify({"ok": True})


# ── Utilisateurs ──────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@require_internal
def api_get_users():
    return jsonify(get_users())


@app.route("/api/users", methods=["POST"])
@require_internal
def api_create_user():
    body = request.get_json(silent=True) or {}
    ok, err = create_user(
        body.get("username", ""),
        body.get("password", ""),
        body.get("role", "viewer"),
        body.get("created_by", "api"),
    )
    if ok:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "erreur": err}), 400


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@require_internal
def api_delete_user(user_id):
    body = request.get_json(silent=True, force=True) or {}
    delete_user(user_id, body.get("deleted_by", "api"))
    return jsonify({"ok": True})


@app.route("/api/users/<int:user_id>/toggle", methods=["POST"])
@require_internal
def api_toggle_user(user_id):
    body = request.get_json(silent=True) or {}
    toggle_user(user_id, body.get("active", True), body.get("done_by", "api"))
    return jsonify({"ok": True})


@app.route("/api/users/password", methods=["POST"])
@require_internal
def api_update_password():
    body = request.get_json(silent=True) or {}
    ok, err = update_password(
        body.get("username", ""),
        body.get("new_password", ""),
        body.get("done_by", "api"),
    )
    if ok:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "erreur": err}), 400


# ── Logs ──────────────────────────────────────────────────────────────────────

@app.route("/api/logs")
@require_internal
def api_logs():
    return jsonify(get_logs(150))


# ── Token API ─────────────────────────────────────────────────────────────────

@app.route("/api/token_info")
@require_internal
def api_token_info():
    return jsonify({"token": get_api_token()})


@app.route("/api/token_regenerate", methods=["POST"])
@require_internal
def api_token_regenerate():
    new_token = regenerate_api_token()
    return jsonify({"ok": True, "token": new_token})


# ── Réception données boxes ───────────────────────────────────────────────────

@app.route("/mise_a_jour_box", methods=["POST"])
def recevoir_donnees():
    token = (request.headers.get("X-API-Token")
             or (request.get_json(silent=True) or {}).get("api_token"))

    # Réseau Tailscale (100.x.x.x) = VPN privé → toujours autorisé sans token
    if not verify_api_token(token or "") and not _is_trusted(request):
        return jsonify({"erreur": "Token API invalide"}), 401

    donnees = request.get_json()
    if not donnees:
        return jsonify({"erreur": "Payload vide"}), 400

    id_mat   = donnees.get("id_materiel")
    raw_data = donnees.get("data_mb", 0)
    offset   = data_offsets.get(id_mat, 0)
    heure    = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")

    box_data[id_mat] = {
        "lat":           donnees.get("lat"),
        "lon":           donnees.get("lon"),
        "status":        "Connecté",
        "temperature":   donnees.get("temperature", 0),
        "users":         donnees.get("users", 0),
        "data_mb":       round(max(0.0, raw_data - offset), 2),
        "raw_data_mb":   raw_data,
        "ip_tailscale":  donnees.get("ip_tailscale", "Non communiquée"),
        "last_seen":     heure,
        "timestamp_interne": datetime.now(),
    }
    save_box_snapshot(id_mat, box_data[id_mat])
    return jsonify({"message": "OK"}), 200


# ══════════════════════════════════════════════════════════════════════════════
# Interface HTML Flask (conservée pour compatibilité)
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET", "POST"])
def connexion():
    erreur = None
    if request.method == "POST":
        user = login_user(request.form["identifiant"], request.form["mot_de_passe"])
        if user:
            session["est_connecte"] = True
            session["username"]     = user["username"]
            session["role"]         = user["role"]
            return redirect(url_for("afficher_carte"))
        erreur = "Identifiant ou mot de passe incorrect."
    return render_template("login.html", erreur=erreur)


@app.route("/carte")
def afficher_carte():
    if not session.get("est_connecte"):
        return redirect(url_for("connexion"))
    verifier_statuts()
    noms = {bid: get_box_name(bid, bid) for bid in box_data}
    return render_template("index.html", boxes=box_data, noms=noms)


@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("connexion"))


@app.route("/renommer_box", methods=["POST"])
def renommer_box():
    if not session.get("est_connecte"):
        return redirect(url_for("connexion"))
    id_mat = request.form.get("id_materiel")
    nom    = request.form.get("nouveau_nom")
    if id_mat and nom:
        save_box_name(id_mat, nom, session.get("username", "web"))
    return redirect(url_for("afficher_carte"))


@app.route("/reset_data", methods=["POST"])
def reset_data():
    if not session.get("est_connecte"):
        return redirect(url_for("connexion"))
    id_mat = request.form.get("id_materiel")
    if id_mat and id_mat in box_data:
        data_offsets[id_mat] = box_data[id_mat].get("raw_data_mb", 0)
        box_data[id_mat]["data_mb"] = 0.0
        log_action(session.get("username", "web"), "RESET_DATA", f"{id_mat}")
    return redirect(url_for("afficher_carte"))


if __name__ == "__main__":
    import socket
    # Récupérer toutes les IPs locales pour info
    hostname = socket.gethostname()
    try:
        local_ips = socket.getaddrinfo(hostname, None)
        ips = list({r[4][0] for r in local_ips if ':' not in r[4][0]})
    except Exception:
        ips = []

    print("\n" + "═"*60)
    print("  ✅  Tour de Contrôle v6 — Yeelen Consulting")
    print("═"*60)
    print(f"  Flask       → http://localhost:5000")
    print(f"  Streamlit   → python -m streamlit run streamlit_app.py")
    print(f"  Interface   → http://localhost:8501")
    print("─"*60)
    print("  📡  ENDPOINT pour les boxes :  /mise_a_jour_box")
    print("  🔑  Chaque box doit envoyer son champ 'api_token'")
    print(f"  🛡️   Sécurité API interne : {'ACTIVÉE' if INTERNAL_API_KEY else 'désactivée (INTERNAL_API_KEY non défini)'}")
    print(f"  📧  Alertes email        : {'ACTIVÉES → ' + ALERT_TO if ALERTS_ENABLED else 'désactivées'}")
    print("─"*60)
    print("  📦  Payload attendu de chaque box :")
    print('      { "id_materiel": "BOX_ID", "lat": 48.85, "lon": 2.35,')
    print('        "temperature": 45.2, "users": 12, "data_mb": 105.5,')
    print('        "ip_tailscale": "100.x.x.x", "api_token": "..." }')
    print("═"*60 + "\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
