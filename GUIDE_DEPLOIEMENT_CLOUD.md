# ☁️ GUIDE DÉPLOIEMENT CLOUD
## Accéder à l'interface depuis n'importe où dans le monde
### Sans avoir besoin de ton PC allumé

---

> **Objectif :** Remplacer ton PC comme serveur par des services cloud gratuits ou peu coûteux,
> pour que l'interface soit accessible 24h/24 depuis ton téléphone, tablette ou n'importe quel ordinateur.

---

## 🗺️ LA NOUVELLE ARCHITECTURE

```
AVANT (local) :
  Boxes → [ton PC allumé] → Interface (accessible seulement sur ton PC)

APRÈS (cloud) :
  Boxes → [Render.com 24h/24] → Interface Streamlit Cloud (accessible partout)
                                           ↑
                               Toi depuis n'importe où
                               (téléphone, tablette, autre PC)
```

**Ce que tu vas utiliser :**

| Service | Rôle | Coût |
|---------|------|------|
| **GitHub** | Stocker le code (obligatoire pour déployer) | Gratuit |
| **Render.com** | Héberger le serveur Flask (reçoit les données des boxes) | ~7$/mois |
| **Streamlit Community Cloud** | Héberger l'interface (tu as déjà un compte) | Gratuit |

**Coût total : environ 7$/mois (~6,50€/mois)**

> 💡 Pourquoi Render est payant ? Le serveur Flask doit être **toujours actif** pour recevoir les données des boxes toutes les 5 minutes. Le forfait gratuit de Render "s'endort" après 15 minutes d'inactivité, ce qui ferait perdre des données. Le forfait Starter à 7$/mois garantit que le serveur ne dort jamais.

---

## ÉTAPE 1 — CRÉER UN COMPTE GITHUB

GitHub est un service qui stocke ton code en ligne. C'est lui qui fait le lien entre ton PC, Render et Streamlit Cloud.

### 1.1 Créer le compte

1. Va sur **https://github.com**
2. Clique sur **"Sign up"** (S'inscrire)
3. Entre ton adresse email, crée un mot de passe, choisis un nom d'utilisateur
4. Valide ton email
5. Sur la question "How many team members?" → choisis **"Just me"**
6. Sur la question "Are you a student or teacher?" → choisis **"Neither"**
7. Choisis le plan **gratuit (Free)**

✅ **Tu dois voir** un tableau de bord GitHub vide.

### 1.2 Installer Git sur ton PC

Git est le logiciel qui envoie ton code vers GitHub.

1. Va sur **https://git-scm.com/download/win**
2. Télécharge et installe (clique "Next" partout, laisse tout par défaut)
3. Ouvre PowerShell et tape :
```powershell
git --version
```
✅ **Tu dois voir :** `git version 2.xx.x`

### 1.3 Configurer Git avec ton identité

Dans PowerShell, tape ces deux commandes (remplace avec ton vrai email et nom) :
```powershell
git config --global user.email "ton@email.com"
git config --global user.name "Ton Nom"
```
Aucun message = ✅ c'est bon.

### 1.4 Créer le dépôt GitHub (repository)

1. Sur **github.com**, clique sur le **"+"** en haut à droite → **"New repository"**
2. Remplis :
   - **Repository name :** `tour-de-controle-yeelen`
   - **Description :** `Interface GPS Yeelen Consulting`
   - Choisis **Private** (privé — seul toi y as accès)
   - **Ne coche rien** d'autre (pas de README, pas de .gitignore)
3. Clique sur **"Create repository"**

Tu arrives sur une page avec des instructions. **Garde cette page ouverte**, tu en auras besoin.

---

## ÉTAPE 2 — ENVOYER LE CODE SUR GITHUB

### 2.1 Ouvre PowerShell et navigue dans le dossier du projet

```powershell
cd "C:\Users\TON_NOM\Desktop\YEELEN CONSULTING\BOX EDUCATIVE\GPS\CLAUDE\INTERFACE GPS BOX EDUCATIVES\tour-v4"
```
> Remplace `TON_NOM` par ton nom d'utilisateur Windows.

### 2.2 Initialise Git dans ce dossier

```powershell
git init
git add .
git commit -m "Premier envoi - Tour de Controle Yeelen"
```

✅ **Tu dois voir à la fin :**
```
[main (root-commit) xxxxxxx] Premier envoi - Tour de Controle Yeelen
 X files changed, X insertions(+)
```

### 2.3 Connecte ce dossier à ton dépôt GitHub

Sur la page GitHub que tu as gardée ouverte, tu vois une section **"…or push an existing repository from the command line"**.
Copie les 3 lignes qui ressemblent à ça et exécute-les dans PowerShell :

```powershell
git remote add origin https://github.com/TON_USERNAME/tour-de-controle-yeelen.git
git branch -M main
git push -u origin main
```

GitHub va te demander de te connecter. Une fenêtre de navigateur s'ouvre → connecte-toi avec ton compte GitHub.

✅ **Tu dois voir :**
```
Enumerating objects: XX, done.
...
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### 2.4 Vérification

Retourne sur la page GitHub de ton dépôt et actualise. Tu dois voir tous tes fichiers du projet listés (app.py, database.py, streamlit_app.py, etc.)

✅ **Si tu vois les fichiers → le code est sur GitHub.**

---

## ÉTAPE 3 — DÉPLOYER LE SERVEUR FLASK SUR RENDER

Render va faire tourner le serveur Flask à ta place, 24h/24, même quand ton PC est éteint.

### 3.1 Créer le compte Render

1. Va sur **https://render.com**
2. Clique sur **"Get Started for Free"**
3. Choisis **"Continue with GitHub"** → connecte-toi avec ton compte GitHub
4. Autorise Render à accéder à GitHub

✅ **Tu es dans le tableau de bord Render.**

### 3.2 Créer un nouveau service web

1. Clique sur **"New +"** en haut à droite
2. Choisis **"Web Service"**
3. Dans la section **"Connect a repository"**, tu vois ton dépôt `tour-de-controle-yeelen`
4. Clique sur **"Connect"** à côté de ce dépôt

### 3.3 Configurer le service

Tu arrives sur une page de configuration. Remplis les champs **exactement** comme ça :

| Champ | Valeur à entrer |
|-------|-----------------|
| **Name** | `yeelen-tour-controle` |
| **Region** | `Frankfurt (EU Central)` ← choisis EU pour la vitesse depuis l'Afrique |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |

**Plan :** Fais défiler vers le bas jusqu'à **"Instance Type"**. Choisis **"Starter"** ($7/month). C'est indispensable pour que le serveur ne s'endorme pas.

### 3.4 Ajouter les variables d'environnement

Toujours sur la même page de configuration, fais défiler vers **"Environment Variables"** et clique sur **"Add Environment Variable"**.

Ajoute ces variables une par une :

| Key (nom) | Value (valeur) |
|-----------|----------------|
| `SUPERADMIN_PASSWORD` | `TonMotDePasseSecurisé!` ← mets un vrai mot de passe |
| `DB_PATH` | `/data/tourdecontrole.db` |

### 3.5 Configurer le disque persistant

Le disque persistant assure que ta base de données (utilisateurs, historique) ne se réinitialise pas à chaque mise à jour.

1. Fais défiler vers **"Disks"**
2. Clique sur **"Add Disk"**
3. Remplis :
   - **Name :** `database`
   - **Mount Path :** `/data`
   - **Size :** `1 GB` (amplement suffisant)
4. Clique **"Save"**

### 3.6 Lancer le déploiement

Clique sur **"Create Web Service"** en bas de la page.

Render va maintenant télécharger ton code depuis GitHub et lancer le serveur. Ça prend **2-5 minutes**.

✅ **Tu dois voir une barre de progression**, puis :
```
==> Build successful 🎉
==> Starting service with 'gunicorn app:app...'
```

Et en haut de la page, le statut passe de **"Building"** à **"Live"** avec un point vert.

### 3.7 Récupérer l'URL de ton serveur

En haut de la page de ton service Render, tu vois une URL de cette forme :
```
https://yeelen-tour-controle.onrender.com
```
**📝 COPIE CETTE URL. Tu en auras besoin dans les étapes suivantes.**

### 3.8 Vérifier que Flask tourne

Dans ton navigateur, va sur :
```
https://yeelen-tour-controle.onrender.com/api/boxes
```
(remplace `yeelen-tour-controle` par le vrai nom de ton service)

✅ **Tu dois voir** du texte JSON qui ressemble à ça :
```json
{"EDUBOX_DEMO_01": {"lat": 14.6928, ...}, "EDUBOX_DEMO_02": {...}}
```

🎉 **Le serveur Flask tourne dans le cloud !**

### 3.9 Récupérer le Token API des boxes

Le token API est un code secret qui permet aux boxes de s'authentifier auprès du serveur cloud.

1. Va sur : `https://ton-url.onrender.com/api/token_info`
2. Tu vois quelque chose comme :
```json
{"token": "a3f8c9d2e1b4..."}
```
**📝 COPIE CE TOKEN. Tu en auras besoin pour les boxes (étape 5).**

---

## ÉTAPE 4 — DÉPLOYER L'INTERFACE SUR STREAMLIT CLOUD

### 4.1 Accéder à Streamlit Cloud

1. Va sur **https://share.streamlit.io**
2. Connecte-toi avec ton compte Streamlit
3. Clique sur **"New app"**

### 4.2 Connecter le dépôt GitHub

1. Choisis **"From existing repo"**
2. Dans **"Repository"**, sélectionne `ton-username/tour-de-controle-yeelen`
3. Dans **"Branch"**, mets `main`
4. Dans **"Main file path"**, mets `streamlit_app.py`
5. Dans **"App URL"** (optionnel), tu peux choisir un nom custom comme `yeelen-controle`

### 4.3 Configurer le secret FLASK_URL

Avant de déployer, clique sur **"Advanced settings"** (ou le bouton engrenage ⚙️).

Cherche la section **"Secrets"** et colle exactement ceci :
```toml
FLASK_URL = "https://yeelen-tour-controle.onrender.com"
```
> Remplace `yeelen-tour-controle` par l'URL exacte de **ton** service Render (celle copiée à l'étape 3.7).

Clique **"Save"**.

### 4.4 Déployer

Clique sur **"Deploy!"**

Streamlit va télécharger ton code et lancer l'interface. Ça prend **2-4 minutes**.

✅ **Tu dois voir l'interface de connexion Yeelen s'ouvrir dans le navigateur.**

### 4.5 Récupérer ton URL public permanent

En haut du navigateur, tu vois l'URL finale de ton interface, par exemple :
```
https://yeelen-controle.streamlit.app
```
**C'est ton URL permanent. Tu peux y accéder depuis n'importe où dans le monde.**

Teste sur ton téléphone : ouvre le navigateur et tape cette URL → tu dois voir la page de connexion.

---

## ÉTAPE 5 — METTRE À JOUR LES BOXES

Les boxes Raspberry Pi envoyaient leurs données à ton PC (`100.81.42.31`). Il faut maintenant les faire envoyer au serveur Render.

**Pour chaque Raspberry Pi (EduBox et AgriBox), répète ces étapes :**

### 5.1 Connexion SSH à la box

Sur ton PC dans PowerShell :
```powershell
# Pour EduBox :
ssh admin@100.89.175.28

# Pour AgriBox :
ssh pi@100.66.117.83
```

### 5.2 Modifier le script GPS

```bash
nano /home/pi/tracker_gps.py
```
> Pour l'EduBox, le fichier est à `/home/admin/tracker_gps.py`

**Modifie les deux premières lignes de configuration :**

Trouve :
```python
URL_TOUR_CONTROLE = "http://100.81.42.31:5000/mise_a_jour_box"
ID_BOX = "AGRIBOX-001"
```

Remplace par :
```python
URL_TOUR_CONTROLE = "https://yeelen-tour-controle.onrender.com/mise_a_jour_box"
API_TOKEN         = "COLLE_ICI_LE_TOKEN_COPIE_A_L_ETAPE_3_9"
ID_BOX = "AGRIBOX-001"
```

**Ensuite, trouve la ligne qui fait l'envoi (`requests.post`) et ajoute le token :**

Trouve :
```python
r = requests.post(URL_TOUR_CONTROLE, json=donnees, timeout=5)
```

Remplace par :
```python
r = requests.post(
    URL_TOUR_CONTROLE,
    json={**donnees, "api_token": API_TOKEN},
    timeout=10
)
```

> ⚠️ Maintenant le serveur est public (pas protégé par Tailscale), donc le token est **indispensable**.

**Sauvegarde :** `Ctrl+X` → `Y` → `Entrée`

### 5.3 Redémarrer le service

```bash
sudo systemctl restart tracker_gps.service
```

**Vérifier les logs :**
```bash
sudo journalctl -fu tracker_gps.service
```

✅ **Tu dois voir :**
```
Démarrage Traqueur GPS — AGRIBOX-001
Serveur : https://yeelen-tour-controle.onrender.com/mise_a_jour_box
IP Tailscale : 100.66.117.83
Recherche satellites... (4 utilisé(s)) — tentative 1
...
[25/05/2026 10:32:15] Position envoyee lat=14.69280 lon=-17.44670
```

---

## ÉTAPE 6 — VÉRIFICATION FINALE

### Checklist globale

- [ ] GitHub : dépôt créé avec tous les fichiers
- [ ] Render : service **"Live"** (point vert), URL accessible
- [ ] Streamlit Cloud : app déployée, interface accessible depuis ton téléphone
- [ ] Render : variable `FLASK_URL` correspond à l'URL Render dans Streamlit Cloud secrets
- [ ] Boxes : scripts mis à jour avec l'URL Render + token API
- [ ] Boxes : service redémarré
- [ ] Interface : les boxes apparaissent sur la carte avec statut "Connecté"

### Test depuis ton téléphone

1. Coupe le WiFi de ton téléphone (utilise la 4G)
2. Ouvre le navigateur et tape ton URL Streamlit Cloud
3. Connecte-toi avec `superadmin` et ton mot de passe
4. ✅ Tu dois voir la carte et les boxes

🎉 **Si tu vois ça → tout fonctionne ! Ton PC n'est plus nécessaire.**

---

## RÉSUMÉ DES 3 URLS À RETENIR

| URL | Usage |
|-----|-------|
| `https://yeelen-tour-controle.onrender.com` | Serveur Flask (boxes envoient ici) |
| `https://yeelen-controle.streamlit.app` | Interface (toi tu accèdes ici) |
| `https://github.com/TON_USERNAME/tour-de-controle-yeelen` | Code source |

---

## METTRE À JOUR LE CODE (pour les modifications futures)

Quand tu voudras modifier le code (changer un texte, ajouter une feature, etc.) :

1. Modifie les fichiers sur ton PC dans le dossier `tour-v4`
2. Ouvre PowerShell, va dans le dossier, puis :
```powershell
git add .
git commit -m "Description de ce que tu as changé"
git push
```
3. Render et Streamlit Cloud détectent automatiquement le nouveau code et se redéployent en **2-3 minutes**. Tu n'as rien d'autre à faire.

---

## DÉPANNAGE CLOUD

### ❓ "Application error" sur Streamlit Cloud

1. Va sur **share.streamlit.io** → clique sur ton app → **"Manage app"** → **"Logs"**
2. Lis l'erreur en rouge
3. Cause fréquente : `FLASK_URL` mal configuré dans les secrets → vérifie qu'il n'y a pas d'espace ou de `/` en trop à la fin

### ❓ Les boxes n'apparaissent plus sur la carte

1. Vérifie que le service Render est **"Live"** (pas "Suspended")
2. Sur ton PC : `curl https://ton-url.onrender.com/api/boxes` → doit afficher du JSON
3. Sur chaque box : `sudo journalctl -fu tracker_gps.service --lines=10` → cherche des erreurs

### ❓ "401 Unauthorized" dans les logs de la box

Le token API est incorrect. Retourne sur `https://ton-url.onrender.com/api/token_info` pour récupérer le bon token et mets-le à jour sur la box.

### ❓ Render affiche "Service Suspended"

Le forfait Starter facture à la consommation. Si la carte de paiement a expiré, le service se suspend. Mets à jour le moyen de paiement sur **https://dashboard.render.com/billing**.

### ❓ Je veux changer le mot de passe superadmin

Va sur Render → ton service → **"Environment"** → modifie la valeur de `SUPERADMIN_PASSWORD` → **"Save Changes"**. Le service redémarre et crée le nouveau mot de passe.

> ⚠️ Cela ne fonctionne que si le compte superadmin n'a jamais été créé. Si tu l'as déjà créé, utilise plutôt l'onglet **Utilisateurs** dans l'interface pour changer le mot de passe.

---

*Yeelen Consulting — Guide Déploiement Cloud v1.0 — Mai 2026*
