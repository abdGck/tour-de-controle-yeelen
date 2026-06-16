# ☁️ GUIDE DÉPLOIEMENT CLOUD
## Système déjà en production — Informations & Maintenance
### Yeelen Consulting · Tour de Contrôle SchoolBox Africa

---

## 🟢 STATUT ACTUEL DU SYSTÈME

| Service | URL | Statut |
|---------|-----|--------|
| **Interface web** | https://tour-de-controle-yeelen.streamlit.app | ✅ En ligne |
| **Serveur Flask** | https://tour-de-controle-yeelen.onrender.com | ✅ En ligne |
| **GitHub (code)** | https://github.com/abdGck/tour-de-controle-yeelen | ✅ Synchronisé |

---

## 📋 COMPTES & ACCÈS

| Service | Identifiant | Mot de passe |
|---------|-------------|--------------|
| **Interface Streamlit** | `superadmin` | *(variable SUPERADMIN_PASSWORD sur Render)* |
| **Render.com** | compte email Yeelen | *(ton mot de passe Render)* |
| **Streamlit Cloud** | compte email Yeelen | *(ton mot de passe Streamlit)* |
| **GitHub** | compte email Yeelen | *(ton mot de passe GitHub)* |

**Token API des boxes :**
```
8ec8da953c6811952a0324be372d647dc54194920c29583e1762d07598ae2216
```
> Ce token est déjà intégré dans le fichier `tracker_gps_TEMPLATE.py`. Les boxes existantes l'utilisent déjà.

---

## 🏗️ ARCHITECTURE DÉPLOYÉE

```
Boxes Raspberry Pi
  └─ tracker_gps.py
       └─ POST https://tour-de-controle-yeelen.onrender.com/mise_a_jour_box
            + api_token: 8ec8da95...
                 │
                 ▼
         Render.com (Flask)
         app.py + database.py
         SQLite sur disque /data/tourdecontrole.db
                 │
                 ▼
      Streamlit Community Cloud
      streamlit_app.py
      Lit les données via l'API Flask
                 │
                 ▼
         Toi (navigateur)
         https://tour-de-controle-yeelen.streamlit.app
```

---

## 🆕 ACTIVER LES NOUVELLES FONCTIONNALITÉS (sécurité + alertes)

> Ces réglages se font **une seule fois**. Sans eux, l'interface fonctionne quand même,
> mais sans la protection de sécurité ni les emails d'alerte.

### A. 🔒 Sécuriser l'interface (clé interne) — FORTEMENT RECOMMANDÉ

Objectif : empêcher quiconque connaissant ton URL Render d'accéder à tes données.
Principe : une **clé secrète partagée** entre Render (serveur) et Streamlit (interface).

**1. Génère une clé** (n'importe quelle longue chaîne aléatoire). Par exemple sur ton PC :
```powershell
python -c "import secrets; print(secrets.token_hex(24))"
```
→ copie le résultat (ex: `4f8a9c2e1b...`).

**2. Sur Render** → ton service → **Environment** → Add Environment Variable :
| Key | Value |
|-----|-------|
| `INTERNAL_API_KEY` | *(la clé générée)* |

**3. Sur Streamlit Cloud** → ⋮ → Settings → **Secrets**, ajoute la **MÊME** clé :
```toml
FLASK_URL = "https://tour-de-controle-yeelen.onrender.com"
INTERNAL_API_KEY = "colle_ici_exactement_la_meme_cle"
```

> ⚠️ **RÈGLE D'OR :** la clé doit être **identique** des deux côtés.
> - Définie aux **deux** endroits → 🔒 sécurité activée, tout fonctionne.
> - Définie **nulle part** → ⚠️ ça marche mais sans protection (comme avant).
> - Définie d'un **seul** côté → ❌ l'interface affichera 0 box (erreur 403). À éviter.

L'onglet **⚙️ Paramètres** de l'interface affiche l'état : « Protection API interne ✅ Activée ».

---

### B. 📧 Activer les alertes email (box hors-ligne / surchauffe)

Tu recevras un email automatique quand une box tombe ou surchauffe (> 70°C).
On utilise Gmail (gratuit). Il faut un **mot de passe d'application** Gmail (pas ton mot de passe normal).

**1. Créer un mot de passe d'application Gmail :**
- Va sur **https://myaccount.google.com/security**
- Active la **validation en deux étapes** (obligatoire pour l'étape suivante)
- Va sur **https://myaccount.google.com/apppasswords**
- Crée un mot de passe d'application nommé « Yeelen Alertes »
- Google affiche un code de 16 lettres → **copie-le** (ex: `abcd efgh ijkl mnop`, retire les espaces)

**2. Sur Render** → ton service → **Environment** → ajoute ces variables :
| Key | Value | Exemple |
|-----|-------|---------|
| `ALERT_EMAIL_FROM` | l'adresse Gmail qui envoie | `tonadresse@gmail.com` |
| `ALERT_EMAIL_PASSWORD` | le mot de passe d'application (16 lettres, sans espaces) | `abcdefghijklmnop` |
| `ALERT_EMAIL_TO` | où recevoir les alertes (peut être la même) | `a.gackou02@gmail.com` |
| `ALERT_TEMP_THRESHOLD` | *(optionnel)* seuil surchauffe en °C | `70` |

> Pour envoyer à plusieurs personnes : sépare les emails par une virgule dans `ALERT_EMAIL_TO`.

**3. Render redémarre automatiquement.** Dans les logs tu verras :
```
✅ Alertes email activées → a.gackou02@gmail.com
```

L'alerte est envoyée **une seule fois** par incident (pas de spam), et un email
« de retour en ligne » est envoyé quand la box revient.

---

### C. Récapitulatif des nouveautés dans l'interface

| Fonctionnalité | Où la trouver |
|----------------|---------------|
| 🔒 Sécurité API | Onglet ⚙️ Paramètres → « Sécurité & alertes » |
| 📧 Alertes email | Automatique (configuré sur Render, section B) |
| 📄 Rapports PDF / Excel | Nouvel onglet **📄 Rapports** |
| 💚 Santé + disponibilité 7j | Onglet 📋 Flotte (badge sur chaque box) |
| 🔍 Filtres + pays | Onglet 📋 Flotte (menu déroulant pays) + carte (compteur par pays) |
| 🛰️ Trajet GPS | Onglet 🗺️ Carte → menu « Afficher le trajet GPS de… » |
| 📍 Pays / Site par box | Onglet 📋 Flotte → champ « Localisation » (admin) |

> 📦 **Après ce déploiement, pense à renseigner le pays et le site de chaque box**
> dans l'onglet Flotte — c'est ce qui alimente les filtres, la carte et les rapports.

---

## 🔄 COMMENT METTRE À JOUR LE CODE

Quand tu veux modifier quelque chose dans l'interface ou le serveur :

**Sur ton PC dans PowerShell :**
```powershell
cd "C:\Users\TON_NOM\Desktop\YEELEN CONSULTING\BOX EDUCATIVE\GPS\CLAUDE\INTERFACE GPS BOX EDUCATIVES\tour-v4"

# 1. Modifie les fichiers avec un éditeur de texte
# 2. Envoie les modifications sur GitHub
git add .
git commit -m "Description de ce que tu as changé"
git push
```

→ Render et Streamlit Cloud détectent le changement et se redéploient **automatiquement en 2-3 minutes**.

---

## 🔧 MAINTENANCE RENDER

### Voir les logs du serveur Flask

1. Va sur **https://dashboard.render.com**
2. Clique sur `tour-de-controle-yeelen`
3. Onglet **"Logs"**

### Forcer un redéploiement manuel

1. Dashboard Render → ton service
2. Bouton **"Manual Deploy"** → **"Deploy latest commit"**

### Vérifier les variables d'environnement

Dashboard Render → ton service → onglet **"Environment"**

| Variable | Valeur |
|----------|--------|
| `SUPERADMIN_PASSWORD` | Ton mot de passe admin |
| `DB_PATH` | `/data/tourdecontrole.db` |

### Vérifier le disque persistant (base de données)

Dashboard Render → ton service → onglet **"Disks"**

Tu dois voir un disque avec :
- **Name :** `database`
- **Mount Path :** `/data`
- **Size :** 1 GB

> ⚠️ Si le disque n'est pas là, la base de données se réinitialise à chaque redéploiement (perte des utilisateurs et de l'historique).

---

## 🔧 MAINTENANCE STREAMLIT CLOUD

### Voir les logs de l'interface

1. Va sur **https://share.streamlit.io**
2. Clique sur les `⋮` → **"Manage app"** → onglet **"Logs"**

### Modifier les secrets (variables de configuration)

1. **https://share.streamlit.io** → `⋮` → **"Settings"** → **"Secrets"**
2. Le contenu doit être :
```toml
FLASK_URL = "https://tour-de-controle-yeelen.onrender.com"
INTERNAL_API_KEY = "ta_cle_si_securite_activee"
```
> La ligne `INTERNAL_API_KEY` n'est nécessaire que si tu as activé la sécurité (section A).
> Si oui, elle doit être identique à celle définie sur Render.

### Redémarrer l'interface

1. **https://share.streamlit.io** → `⋮` → **"Reboot app"**

---

## 🔑 RÉGÉNÉRER LE TOKEN API (si compromis)

Si le token API a été exposé ou compromis :

1. Connecte-toi à l'interface : **https://tour-de-controle-yeelen.streamlit.app**
2. Onglet **⚙️ Paramètres**
3. Clique sur **"Régénérer le token"**
4. **Copie le nouveau token**
5. Mets à jour `API_TOKEN` dans le fichier `tracker_gps.py` de **chaque box** :
   ```bash
   # Sur chaque Raspberry Pi (SSH)
   nano /home/pi/tracker_gps.py
   # Modifie la ligne API_TOKEN = "..."
   sudo systemctl restart tracker_gps.service
   ```

---

## 🩺 DIAGNOSTIC RAPIDE — "les boxes n'apparaissent plus"

**Étape 1 — Le serveur Render tourne-t-il ?**
```
https://tour-de-controle-yeelen.onrender.com/api/boxes
```
→ Doit afficher du JSON. Si erreur → va sur Render dashboard et redémarre.

**Étape 2 — La box envoie-t-elle des données ?**
```bash
# SSH sur la box
sudo journalctl -fu tracker_gps.service --lines=20
```
→ Cherche "✅ Envoyé" ou "⚠️ 401" ou "❌ Impossible de joindre"

**Étape 3 — L'interface Streamlit est-elle à jour ?**
→ Rafraîchis la page. L'interface se met à jour toutes les 30 secondes.

---

## 📦 AJOUTER UNE NOUVELLE BOX

Pour connecter un nouveau Raspberry Pi au système :

1. Suis le **GUIDE_COMPLET_INSTALLATION.md** (étapes 3 à 8)
2. Le seul fichier à copier sur le Raspberry Pi est **`tracker_gps_TEMPLATE.py`**
3. Modifie uniquement `ID_BOX` dans ce fichier
4. La box apparaît automatiquement sur la carte dès qu'elle envoie sa première position

---

## 💰 COÛTS MENSUELS

| Service | Plan | Coût |
|---------|------|------|
| Render.com | Starter (Flask + disque 1GB) | ~7 $/mois |
| Streamlit Cloud | Free | 0 $/mois |
| GitHub | Free | 0 $/mois |
| **Total** | | **~7 $/mois (~6,50€)** |

Paiement Render : carte bancaire configurée dans **https://dashboard.render.com/billing**

---

*Yeelen Consulting — Documentation Cloud v2.0 — Mai 2026*
