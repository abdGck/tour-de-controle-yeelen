# Tour de Contrôle — Yeelen Consulting

Interface de suivi GPS des **box éducatives** Yeelen (Raspberry Pi déployés en Afrique).
Chaque box envoie automatiquement sa position GPS, sa température CPU, sa data consommée
et son IP Tailscale vers un serveur cloud, qui les affiche sur une carte mondiale.

> ⚠️ L'utilisateur est **novice en informatique**. Toujours expliquer pas à pas, avec le
> résultat attendu de chaque commande, et lui dire exactement où cliquer / quoi coller.

---

## Architecture (déployée, en production)

| Composant | Techno | Hébergement | URL |
|-----------|--------|-------------|-----|
| Backend API | Flask + gunicorn | **Render** (Starter, disque `/data`) | https://tour-de-controle-yeelen.onrender.com |
| Base de données | SQLite | disque persistant Render `/data/tourdecontrole.db` | — |
| Frontend | Streamlit | **Streamlit Community Cloud** | https://tour-de-controle-yeelen.streamlit.app |
| Code source | Git | **GitHub** | https://github.com/abdGck/tour-de-controle-yeelen |

**Déploiement** : `git push` sur `main` → Render + Streamlit redéploient automatiquement
(~3 min). Si Render ne redéploie pas : dashboard → **Manual Deploy → Deploy latest commit**.

---

## Fichiers

| Fichier | Rôle |
|---------|------|
| `app.py` | Serveur Flask : API JSON, réception données boxes, alertes email, sécurité |
| `database.py` | Couche SQLite : users, box_names, box_history (avec lat/lon), box_meta, logs, tokens |
| `streamlit_app.py` | Interface : Carte, Flotte, Historique, Rapports, Journal, Utilisateurs, Paramètres |
| `tracker_gps_TEMPLATE.py` | Script universel à mettre sur chaque box (seul `ID_BOX` change) |
| `requirements.txt` | Dépendances (flask, gunicorn, streamlit, plotly, folium, fpdf2, openpyxl…) |
| `Procfile` | Commande de démarrage gunicorn pour Render |
| `GUIDE_COMPLET_INSTALLATION.md` | Guide pas-à-pas pour ajouter une nouvelle box |
| `GUIDE_DEPLOIEMENT_CLOUD.md` | Guide de maintenance cloud (Render, Streamlit, sécurité, alertes) |

---

## Variables d'environnement

**Sur Render** : `DB_PATH=/data/tourdecontrole.db`, `SUPERADMIN_PASSWORD`,
`ALERT_EMAIL_FROM` / `ALERT_EMAIL_PASSWORD` (app password Gmail/Workspace) / `ALERT_EMAIL_TO`,
`ALERT_TEMP_THRESHOLD` (défaut 70), et `INTERNAL_API_KEY` (sécurité, optionnel).

**Sur Streamlit (Secrets)** : `FLASK_URL` (= URL Render), `INTERNAL_API_KEY` (la **même**
que Render, ou absente des deux).

> 🔒 `INTERNAL_API_KEY` : doit être **identique** des deux côtés, ou **absente** des deux.
> Définie d'un seul côté = l'interface affiche 0 box (erreur 403).

---

## Boxes connectées

| Nom | ID | IP Tailscale | User SSH | Script |
|-----|----|--------------|----------|--------|
| EduBox | `EDUBOX-001` | 100.89.175.28 | `admin` | `/home/admin/tracker_gps.py` |
| AgriBox | `AGRIBOX-001` | 100.66.117.83 | `pi` | `/home/pi/tracker_gps.py` |

Chaque box : Tailscale + GPSD + service systemd `tracker_gps.service`. Elle envoie son
`api_token` (stocké en DB). Envoi toutes les 5 min quand le GPS a un fix. Une box est
marquée « Hors-ligne » après 6 min sans signal.

---

## Conventions

- Marque Yeelen : Bleu `#2878BE`, Or `#F5C020`. **Thème clair uniquement.**
- Rôles : `superadmin` (tout + Paramètres), `admin` (gère viewers + boxes), `viewer` (lecture).
- Code et UI **en français**.
- Après modif Python : `python -m py_compile app.py database.py streamlit_app.py` pour valider.
- Sur Windows, lancer Streamlit avec `python -m streamlit run streamlit_app.py`.
