"""
Base de données SQLite — Tour de Contrôle Yeelen Consulting
Gestion : utilisateurs, noms de boxes, historique, logs, tokens API
"""

import sqlite3, secrets, os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

_db_raw = os.environ.get("DB_PATH", str(Path(__file__).parent / "tourdecontrole.db"))
# Nettoyage défensif : retire espaces, backticks et guillemets collés par erreur
_db_raw = _db_raw.strip().strip("`").strip('"').strip("'").strip()
DB_PATH = Path(_db_raw)


def get_db() -> sqlite3.Connection:
    # Crée le dossier parent si nécessaire (ex: /data sur Render)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role          TEXT NOT NULL DEFAULT 'viewer',
        created_by    TEXT DEFAULT 'system',
        created_at    TEXT DEFAULT (datetime('now')),
        last_login    TEXT,
        is_active     INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS box_names (
        box_id TEXT PRIMARY KEY,
        nom    TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS box_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        box_id      TEXT NOT NULL,
        timestamp   TEXT NOT NULL,
        temperature REAL,
        users       INTEGER DEFAULT 0,
        data_mb     REAL    DEFAULT 0,
        status      TEXT    DEFAULT 'Connecté',
        lat         REAL,
        lon         REAL
    );

    CREATE TABLE IF NOT EXISTS box_meta (
        box_id TEXT PRIMARY KEY,
        pays   TEXT DEFAULT '',
        site   TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS actions_log (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT (datetime('now')),
        username  TEXT,
        action    TEXT,
        details   TEXT
    );

    CREATE TABLE IF NOT EXISTS api_tokens (
        token       TEXT PRIMARY KEY,
        description TEXT,
        created_at  TEXT DEFAULT (datetime('now')),
        is_active   INTEGER DEFAULT 1
    );
    """)

    # ── Migration : ajouter lat/lon à box_history si base ancienne ────────────
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(box_history)").fetchall()]
    if "lat" not in cols:
        conn.execute("ALTER TABLE box_history ADD COLUMN lat REAL")
    if "lon" not in cols:
        conn.execute("ALTER TABLE box_history ADD COLUMN lon REAL")

    # ── Superadmin par défaut ─────────────────────────────────────────────────
    if not conn.execute("SELECT id FROM users WHERE username='superadmin'").fetchone():
        default_pw = os.environ.get("SUPERADMIN_PASSWORD", "Yeelen2024!")
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_by) VALUES (?,?,?,?)",
            ("superadmin", generate_password_hash(default_pw), "superadmin", "system"),
        )
        print(f"✅ Superadmin créé — mot de passe : {default_pw}")

    # ── Token API par défaut ──────────────────────────────────────────────────
    if not conn.execute("SELECT token FROM api_tokens WHERE description='default'").fetchone():
        token = secrets.token_hex(32)
        conn.execute(
            "INSERT INTO api_tokens (token, description) VALUES (?,?)",
            (token, "default"),
        )
        print(f"🔑 Token API boxes : {token}")

    conn.commit()
    conn.close()


# ── Authentification ──────────────────────────────────────────────────────────

def login_user(username: str, password: str) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
    ).fetchone()
    if row and check_password_hash(row["password_hash"], password):
        conn.execute(
            "UPDATE users SET last_login=? WHERE username=?",
            (datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S"), username),
        )
        conn.commit()
        conn.close()
        return dict(row)
    conn.close()
    return None


# ── Gestion utilisateurs ──────────────────────────────────────────────────────

def get_users() -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, username, role, created_by, created_at, last_login, is_active "
        "FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username: str, password: str, role: str, created_by: str) -> tuple[bool, str]:
    if role == "superadmin":
        return False, "Impossible de créer un autre superadmin"
    if len(password) < 6:
        return False, "Mot de passe trop court (min. 6 caractères)"
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_by) VALUES (?,?,?,?)",
            (username, generate_password_hash(password), role, created_by),
        )
        _log(conn, created_by, "CREATE_USER", f"Créé {username} (rôle: {role})")
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "Nom d'utilisateur déjà utilisé"
    finally:
        conn.close()


def update_password(username: str, new_password: str, done_by: str) -> tuple[bool, str]:
    if len(new_password) < 6:
        return False, "Mot de passe trop court (min. 6 caractères)"
    conn = get_db()
    conn.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (generate_password_hash(new_password), username),
    )
    _log(conn, done_by, "UPDATE_PASSWORD", f"Mot de passe changé pour {username}")
    conn.commit()
    conn.close()
    return True, ""


def delete_user(user_id: int, deleted_by: str) -> None:
    conn = get_db()
    row = conn.execute("SELECT username, role FROM users WHERE id=?", (user_id,)).fetchone()
    if row and row["role"] != "superadmin":
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        _log(conn, deleted_by, "DELETE_USER", f"Supprimé {row['username']}")
        conn.commit()
    conn.close()


def toggle_user(user_id: int, active: bool, done_by: str) -> None:
    conn = get_db()
    row = conn.execute("SELECT username, role FROM users WHERE id=?", (user_id,)).fetchone()
    if row and row["role"] != "superadmin":
        conn.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, user_id))
        action = "ACTIVATE_USER" if active else "DEACTIVATE_USER"
        _log(conn, done_by, action, row["username"])
        conn.commit()
    conn.close()


# ── Noms de boxes ─────────────────────────────────────────────────────────────

def get_box_name(box_id: str, fallback: str = "") -> str:
    conn = get_db()
    row = conn.execute("SELECT nom FROM box_names WHERE box_id=?", (box_id,)).fetchone()
    conn.close()
    return row["nom"] if row else (fallback or box_id)


def save_box_name(box_id: str, nom: str, done_by: str = "system") -> None:
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO box_names (box_id, nom) VALUES (?,?)", (box_id, nom))
    _log(conn, done_by, "RENAME_BOX", f"{box_id} → {nom}")
    conn.commit()
    conn.close()


def init_default_names(defaults: dict) -> None:
    conn = get_db()
    for box_id, nom in defaults.items():
        if not conn.execute("SELECT box_id FROM box_names WHERE box_id=?", (box_id,)).fetchone():
            conn.execute("INSERT INTO box_names (box_id, nom) VALUES (?,?)", (box_id, nom))
    conn.commit()
    conn.close()


# ── Historique boxes ──────────────────────────────────────────────────────────

def save_box_snapshot(box_id: str, data: dict) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO box_history (box_id, timestamp, temperature, users, data_mb, status, lat, lon) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            box_id,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            data.get("temperature"),
            data.get("users", 0),
            data.get("data_mb", 0),
            data.get("status", "Connecté"),
            data.get("lat"),
            data.get("lon"),
        ),
    )
    conn.commit()
    conn.close()


def get_box_history(box_id: str, limit: int = 288) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, temperature, users, data_mb, status, lat, lon "
        "FROM box_history WHERE box_id=? ORDER BY timestamp DESC LIMIT ?",
        (box_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_gps_trail(box_id: str, limit: int = 200) -> list[dict]:
    """Retourne les positions GPS successives (pour tracer le trajet)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, lat, lon FROM box_history "
        "WHERE box_id=? AND lat IS NOT NULL AND lon IS NOT NULL "
        "ORDER BY timestamp ASC LIMIT ?",
        (box_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_box_stats(box_id: str, hours: int = 168) -> dict:
    """
    Calcule les statistiques de santé d'une box sur les N dernières heures.
    Retourne : uptime (%), nb de relevés, temp moyenne/max, dernière activité.
    """
    conn = get_db()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT status, temperature FROM box_history "
        "WHERE box_id=? AND timestamp >= ?",
        (box_id, since),
    ).fetchall()
    conn.close()

    total = len(rows)
    if total == 0:
        return {"uptime": None, "releves": 0, "temp_moy": None, "temp_max": None}

    online = sum(1 for r in rows if r["status"] == "Connecté")
    temps  = [r["temperature"] for r in rows if r["temperature"] is not None]
    return {
        "uptime":   round(100.0 * online / total, 1),
        "releves":  total,
        "temp_moy": round(sum(temps) / len(temps), 1) if temps else None,
        "temp_max": round(max(temps), 1) if temps else None,
    }


# ── Métadonnées boxes (pays / site) ───────────────────────────────────────────

def get_box_meta(box_id: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT pays, site FROM box_meta WHERE box_id=?", (box_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"pays": "", "site": ""}


def get_all_box_meta() -> dict:
    conn = get_db()
    rows = conn.execute("SELECT box_id, pays, site FROM box_meta").fetchall()
    conn.close()
    return {r["box_id"]: {"pays": r["pays"], "site": r["site"]} for r in rows}


def save_box_meta(box_id: str, pays: str, site: str, done_by: str = "system") -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO box_meta (box_id, pays, site) VALUES (?,?,?)",
        (box_id, pays.strip(), site.strip()),
    )
    _log(conn, done_by, "EDIT_META", f"{box_id} → pays={pays}, site={site}")
    conn.commit()
    conn.close()


# ── Journal d'actions ─────────────────────────────────────────────────────────

def get_logs(limit: int = 150) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT timestamp, username, action, details FROM actions_log "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_action(username: str, action: str, details: str) -> None:
    conn = get_db()
    _log(conn, username, action, details)
    conn.commit()
    conn.close()


# ── Token API ─────────────────────────────────────────────────────────────────

def get_api_token() -> str | None:
    conn = get_db()
    row = conn.execute(
        "SELECT token FROM api_tokens WHERE is_active=1 LIMIT 1"
    ).fetchone()
    conn.close()
    return row["token"] if row else None


def verify_api_token(token: str) -> bool:
    if not token:
        return False
    conn = get_db()
    row = conn.execute(
        "SELECT token FROM api_tokens WHERE token=? AND is_active=1", (token,)
    ).fetchone()
    conn.close()
    return row is not None


def regenerate_api_token() -> str:
    new_token = secrets.token_hex(32)
    conn = get_db()
    conn.execute("UPDATE api_tokens SET is_active=0")
    conn.execute(
        "INSERT INTO api_tokens (token, description) VALUES (?,?)",
        (new_token, "regenerated"),
    )
    conn.commit()
    conn.close()
    return new_token


# ── Interne ───────────────────────────────────────────────────────────────────

def _log(conn: sqlite3.Connection, username: str, action: str, details: str) -> None:
    conn.execute(
        "INSERT INTO actions_log (username, action, details) VALUES (?,?,?)",
        (username, action, details),
    )
