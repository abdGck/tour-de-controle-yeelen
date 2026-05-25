# Tour de Contrôle v5 — Yeelen Consulting

## Installation (une seule fois)

```powershell
python -m pip install flask streamlit requests folium streamlit-folium plotly pandas werkzeug
```

## Lancer l'app (2 terminaux PowerShell)

> ⚠️ Sur Windows, utilise `python -m streamlit` (pas juste `streamlit`)

**Terminal 1 — Serveur Flask (reçoit les données des boxes)**
```powershell
python app.py
```

**Terminal 2 — Interface Streamlit**
```powershell
python -m streamlit run streamlit_app.py
```

Ouvrir → **http://localhost:8501**

---

## Connexion par défaut

| Identifiant  | Mot de passe  | Rôle        |
|-------------|---------------|-------------|
| `superadmin` | `Yeelen2024!` | Superadmin  |

> ⚠️ Changer le mot de passe après la première connexion (onglet Utilisateurs).

---

## Rôles & permissions

| Action                        | Superadmin | Admin | Viewer |
|-------------------------------|:----------:|:-----:|:------:|
| Voir la carte et la flotte    | ✅ | ✅ | ✅ |
| Voir l'historique             | ✅ | ✅ | ✅ |
| Voir le journal               | ✅ | ✅ | ✅ |
| Renommer une box              | ✅ | ✅ | ❌ |
| Remettre data à zéro          | ✅ | ✅ | ❌ |
| Créer des comptes utilisateurs| ✅ | ✅* | ❌ |
| Supprimer / désactiver users  | ✅ | ✅* | ❌ |
| Voir / régénérer token API    | ✅ | ❌ | ❌ |

*Admin peut créer/gérer les Viewers uniquement. Seul le Superadmin peut créer des Admins.

---

## Sécurité — variables d'environnement (optionnel)

Avant de lancer Flask, tu peux définir :

```powershell
$env:SUPERADMIN_PASSWORD = "MonSuperMotDePasse2025!"
$env:FLASK_SECRET        = "une_clé_aléatoire_longue"
```

Sans ces variables, Flask génère une clé aléatoire à chaque démarrage et utilise `Yeelen2024!` pour le superadmin.

---

## Envoi de données — format API (pour les boxes)

```http
POST http://<ip-serveur>:5000/mise_a_jour_box
X-API-Token: <token visible dans Paramètres>
Content-Type: application/json

{
  "id_materiel":  "EDUBOX_SENEGAL_01",
  "lat":           14.6928,
  "lon":           -17.4467,
  "temperature":   47.3,
  "users":         15,
  "data_mb":       125.4,
  "ip_tailscale":  "100.72.10.50"
}
```

Le token API est visible dans l'onglet **⚙️ Paramètres** (superadmin uniquement).

---

## Données démo

Flask démarre avec 4 boxes démo (Dakar, Bamako, Abidjan, Lomé).
Quand une vraie box se connecte, elle crée automatiquement son entrée.
