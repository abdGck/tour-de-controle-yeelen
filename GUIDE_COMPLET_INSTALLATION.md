# 📘 GUIDE COMPLET D'INSTALLATION
## Système de Suivi GPS — Tour de Contrôle Yeelen Consulting
### Pour une personne sans connaissance en informatique

---

> **Ce guide te permet de reproduire de zéro l'intégralité du système de géolocalisation des boxes éducatives Yeelen.**
> Chaque étape indique exactement ce que tu dois voir sur ton écran pour valider que tout s'est bien passé.
> **Ne saute aucune étape.** Elles sont dans l'ordre pour une raison.

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble — comprendre le système](#1-vue-densemble)
2. [Matériel nécessaire](#2-matériel-nécessaire)
3. [Logiciels à installer sur ton PC](#3-logiciels-à-installer-sur-ton-pc)
4. [Configurer le VPN Tailscale](#4-configurer-le-vpn-tailscale)
5. [Installer et lancer le serveur Flask](#5-installer-et-lancer-le-serveur-flask)
6. [Lancer l'interface Streamlit](#6-lancer-linterface-streamlit)
7. [Configurer chaque Raspberry Pi (Box)](#7-configurer-chaque-raspberry-pi-box)
8. [Connecter la Box au serveur](#8-connecter-la-box-au-serveur)
9. [Vérification finale — tout fonctionne ?](#9-vérification-finale)
10. [Dépannage — que faire si ça ne marche pas](#10-dépannage)

---

# 1. VUE D'ENSEMBLE

## 🧩 Comment le système fonctionne

```
┌─────────────────────────────────────────────────────────────┐
│                    TON PC (Serveur)                          │
│                  IP Tailscale: 100.x.x.x                    │
│                                                             │
│  ┌─────────────┐     ┌──────────────────────────────────┐   │
│  │  Flask      │     │  Interface Streamlit              │   │
│  │  Port 5000  │────▶│  Port 8501                       │   │
│  │  (reçoit    │     │  (carte + tableau de bord)        │   │
│  │  les données│     └──────────────────────────────────┘   │
│  │  des boxes) │                                            │
│  └─────────────┘                                            │
└────────────────────────────┬────────────────────────────────┘
                             │ Internet (VPN Tailscale)
              ┌──────────────┴──────────────┐
              │                             │
┌─────────────▼──────────┐   ┌─────────────▼──────────┐
│   EDUBOX                │   │   AGRIBOX               │
│   Raspberry Pi          │   │   Raspberry Pi          │
│   IP Tailscale: 100.x.x │   │   IP Tailscale: 100.x.x │
│                         │   │                         │
│   Antenne GPS (USB)     │   │   Antenne GPS (USB)     │
│   ↓                     │   │   ↓                     │
│   GPSD (logiciel)       │   │   GPSD (logiciel)       │
│   ↓                     │   │   ↓                     │
│   tracker_gps.py        │   │   tracker_gps.py        │
│   (envoie position      │   │   (envoie position      │
│    toutes les 5 min)    │   │    toutes les 5 min)    │
└─────────────────────────┘   └─────────────────────────┘
```

**En résumé :**
- Chaque **Raspberry Pi** a une antenne GPS branchée en USB
- Un script Python sur chaque Raspberry Pi lit le GPS et envoie la position à ton PC via Internet (VPN Tailscale)
- Ton **PC** reçoit ces données avec Flask et les affiche sur une carte dans l'interface Streamlit
- Toi tu accèdes à l'interface depuis un navigateur web : `http://localhost:8501`

---

# 2. MATÉRIEL NÉCESSAIRE

## 🖥️ Pour le serveur (ton PC)
- **Un PC Windows 10 ou 11** (toujours allumé quand tu veux surveiller les boxes)
- Connexion Internet

## 📦 Pour chaque Box éducative
| Composant | Description |
|-----------|-------------|
| **Raspberry Pi** | Modèle 3B+, 4 ou 5 (n'importe lequel) |
| **Carte microSD** | Minimum 16 Go (idéalement 32 Go) avec Raspberry Pi OS installé |
| **Antenne GPS USB** | Modèle recommandé : [GPS USB Amazon](https://www.amazon.fr/dp/B0GC6DMV6M) |
| **Câble USB** | Pour brancher l'antenne GPS au Raspberry Pi |
| **Alimentation** | Adaptateur officiel Raspberry Pi (5V 3A) |
| **Connexion Internet** | WiFi ou câble Ethernet (la box doit avoir accès à Internet) |

> ⚠️ **Important :** L'antenne GPS **doit être placée dehors** ou près d'une fenêtre avec vue sur le ciel. À l'intérieur d'un bâtiment, le GPS ne captera pas les satellites.

---

# 3. LOGICIELS À INSTALLER SUR TON PC

## 3.1 Installer Python

Python est le langage de programmation utilisé par le projet.

**👉 Étapes :**

1. Va sur le site : **https://www.python.org/downloads/**
2. Clique sur le gros bouton jaune **"Download Python 3.12.x"**
3. Ouvre le fichier téléchargé (ex: `python-3.12.x-amd64.exe`)
4. **TRÈS IMPORTANT** : coche la case **"Add python.exe to PATH"** en bas de la fenêtre avant de cliquer sur "Install Now"

   ```
   ┌─────────────────────────────────────────┐
   │  Install Python 3.12                    │
   │                                         │
   │  ○ Install Now                          │
   │  ○ Customize installation               │
   │                                         │
   │  ☑ Add python.exe to PATH  ← COCHER ça │
   └─────────────────────────────────────────┘
   ```

5. Clique sur **"Install Now"**
6. Attends la fin de l'installation
7. Clique sur **"Close"**

**✅ Vérification :**
Ouvre PowerShell (touche Windows → tape "PowerShell" → Entrée) et tape :
```
python --version
```
**Tu dois voir :**
```
Python 3.12.x
```
Si tu vois ça → ✅ Python est installé correctement.

---

## 3.2 Installer les bibliothèques Python nécessaires

Dans PowerShell, tape cette commande (en une seule ligne) et appuie sur Entrée :

```powershell
pip install flask streamlit plotly pandas werkzeug folium streamlit-folium requests
```

**Tu vas voir plein de lignes défiler pendant l'installation. Attends que ça se termine.**

**✅ Vérification — ce que tu dois voir à la fin :**
```
Successfully installed flask-3.x.x streamlit-1.x.x plotly-5.x.x pandas-2.x.x ...
```
Si tu vois `Successfully installed` → ✅ Les bibliothèques sont installées.

---

## 3.3 Installer Git (pour télécharger les fichiers du projet)

> Si tu as déjà les fichiers du projet sur ton PC, saute cette étape.

1. Va sur **https://git-scm.com/download/win**
2. Télécharge et installe avec les options par défaut (clique "Next" partout)

---

## 3.4 Récupérer les fichiers du projet

Si tu n'as pas encore le dossier `tour-v4` sur ton PC :

1. Crée un dossier sur ton Bureau, par exemple : `C:\Yeelen\tour-v4`
2. Copie-y ces fichiers (fournis séparément) :
   - `app.py`
   - `database.py`
   - `streamlit_app.py`
   - `requirements.txt`
   - `script_box.py`
   - Le dossier `templates/` (avec `login.html` et `index.html`)

**Structure attendue du dossier :**
```
tour-v4/
├── app.py
├── database.py
├── streamlit_app.py
├── requirements.txt
├── script_box.py
└── templates/
    ├── login.html
    └── index.html
```

---

# 4. CONFIGURER LE VPN TAILSCALE

Tailscale est un VPN qui crée un réseau privé entre ton PC et les Raspberry Pi, même s'ils sont à l'autre bout du monde. **C'est l'élément central du système.**

## 4.1 Installer Tailscale sur ton PC

1. Va sur **https://tailscale.com/download**
2. Clique sur **"Download for Windows"**
3. Lance l'installateur, clique "Install"
4. Une icône Tailscale apparaît dans la barre des tâches (en bas à droite, l'icône ressemble à un logo carré)
5. Clique dessus → **"Log in"**
6. Crée un compte gratuit avec ton adresse email ou un compte Google

**✅ Vérification :**
Clic droit sur l'icône Tailscale dans la barre → tu vois une adresse IP qui commence par `100.`
C'est **ton adresse Tailscale** (ex: `100.81.42.31`)

> 📝 **Note :** Retiens bien cette adresse IP. Tu devras la mettre dans les scripts des Raspberry Pi.

---

## 4.2 Ouvrir le port 5000 dans le pare-feu Windows

Le pare-feu de Windows bloque par défaut les connexions entrantes. Il faut lui dire d'accepter les connexions sur le port 5000 (utilisé par Flask).

**Ouvre PowerShell en tant qu'administrateur :**
- Touche Windows → tape "PowerShell"
- Clic droit sur "Windows PowerShell" → **"Exécuter en tant qu'administrateur"**

Tape cette commande et appuie sur Entrée :
```powershell
New-NetFirewallRule -DisplayName "Flask Tour de Controle" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

**✅ Ce que tu dois voir :**
```
Name                  : {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
DisplayName           : Flask Tour de Controle
Description           :
DisplayGroup          :
...
Enabled               : True
```

Si tu vois `Enabled : True` → ✅ Le pare-feu est configuré.

---

# 5. INSTALLER ET LANCER LE SERVEUR FLASK

Flask est le serveur qui reçoit les données envoyées par les boxes.

## 5.1 Premier lancement de Flask

1. Ouvre PowerShell
2. Va dans le dossier du projet avec cette commande (adapte le chemin si nécessaire) :
```powershell
cd "C:\Users\TON_NOM\Desktop\tour-v4"
```
> Remplace `TON_NOM` par ton nom d'utilisateur Windows (celui qui apparaît dans `C:\Users\...`)

3. Lance le serveur :
```powershell
python app.py
```

**✅ Ce que tu dois voir :**
```
════════════════════════════════════════════════════════════
  ✅  Tour de Contrôle v5 — Yeelen Consulting
════════════════════════════════════════════════════════════
  Flask       → http://localhost:5000
  Streamlit   → python -m streamlit run streamlit_app.py
  Interface   → http://localhost:8501
────────────────────────────────────────────────────────────
  📡  ENDPOINT pour les boxes :
      http://100.81.42.31:5000/mise_a_jour_box
  ✅  Réseau Tailscale (100.x.x.x) = accès autorisé sans token
────────────────────────────────────────────────────────────
  📦  Payload attendu de chaque box :
      { "id_materiel": "BOX_ID",
        "lat": 48.85, "lon": 2.35,
        "temperature": 45.2, "users": 12,
        "data_mb": 105.5, "ip_tailscale": "100.x.x.x" }
════════════════════════════════════════════════════════════

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

Si tu vois ces lignes → ✅ **Flask tourne correctement.**

> ⚠️ **Ne ferme pas cette fenêtre PowerShell.** Flask doit rester en marche. Si tu la fermes, le serveur s'arrête et les boxes ne peuvent plus envoyer leurs données.

---

## 5.2 Comprendre ce qui s'est créé automatiquement

Au premier démarrage, Flask a créé automatiquement une base de données `tour_controle.db` dans ton dossier avec :
- Un compte **superadmin** (utilisateur principal)
  - Identifiant : `superadmin`
  - Mot de passe : `Yeelen2024!`

> 🔐 **Change ce mot de passe** dès ta première connexion depuis l'interface Streamlit.

---

# 6. LANCER L'INTERFACE STREAMLIT

L'interface Streamlit est le tableau de bord visuel que tu utilises dans ton navigateur.

## 6.1 Ouvrir un second PowerShell

**Sans fermer** la fenêtre PowerShell qui fait tourner Flask, ouvre **une nouvelle fenêtre PowerShell** :
- Touche Windows → "PowerShell" → Entrée

## 6.2 Naviguer dans le dossier et lancer Streamlit

```powershell
cd "C:\Users\TON_NOM\Desktop\tour-v4"
python -m streamlit run streamlit_app.py
```

**✅ Ce que tu dois voir :**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Puis **ton navigateur s'ouvre automatiquement** sur `http://localhost:8501` et tu vois la page de connexion :

```
┌─────────────────────────────────────┐
│           [Logo Yeelen]              │
│                                     │
│    Tour de Contrôle                 │
│    SchoolBox Africa                 │
│                                     │
│  Identifiant : [____________]       │
│  Mot de passe : [____________]      │
│                                     │
│         [  Se connecter  ]          │
└─────────────────────────────────────┘
```

## 6.3 Se connecter pour la première fois

- **Identifiant :** `superadmin`
- **Mot de passe :** `Yeelen2024!`

Clique sur **"Se connecter"**

**✅ Ce que tu dois voir :**
L'interface s'ouvre avec la carte du monde et plusieurs boxes de démonstration visibles (EDUBOX_DEMO_01, etc.)

---

# 7. CONFIGURER CHAQUE RASPBERRY PI (BOX)

> **Répète les étapes 7.1 à 7.9 pour chaque Raspberry Pi que tu veux connecter.**
> Ces commandes sont à taper sur le Raspberry Pi lui-même (soit avec un clavier/écran branché dessus, soit en SSH depuis ton PC).

## 7.0 Se connecter au Raspberry Pi depuis ton PC (SSH)

SSH te permet de contrôler le Raspberry Pi à distance depuis ton PC, sans avoir besoin d'un écran branché dessus.

**Sur ton PC, ouvre PowerShell et tape :**
```powershell
ssh pi@ADRESSE_IP_LOCALE_DU_PI
```
> L'adresse IP locale (ex: `192.168.1.45`) se trouve dans les paramètres WiFi de ta box ou sur l'écran si tu en as un branché.

**Mot de passe par défaut du Raspberry Pi :** `raspberry`

**✅ Ce que tu dois voir une fois connecté :**
```
Linux raspberrypi 6.x.x #1 ...
...
pi@raspberrypi:~$
```
Le symbole `$` à la fin indique que tu es connecté et prêt à taper des commandes.

---

## 7.1 Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

**Ce que tu vas voir :** Plein de lignes qui défilent pendant quelques minutes.

**✅ Ce que tu dois voir à la fin :**
```
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```
(Les chiffres peuvent varier, c'est normal)

---

## 7.2 Brancher l'antenne GPS

Branche l'antenne GPS dans **un port USB du Raspberry Pi**.

**Vérifier que le système l'a détectée :**
```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

**✅ Ce que tu dois voir :**
```
/dev/ttyACM0
```
ou
```
/dev/ttyUSB0
```

Si tu ne vois rien → l'antenne n'est pas reconnue. Essaie un autre port USB et retape la commande.

---

## 7.3 Installer GPSD

GPSD est un logiciel qui lit les données GPS de l'antenne et les met à disposition des autres programmes.

```bash
sudo apt install gpsd gpsd-clients -y
```

**✅ Ce que tu dois voir à la fin :**
```
Setting up gpsd (3.xx) ...
Setting up gpsd-clients (3.xx) ...
```

---

## 7.4 Configurer GPSD pour ton antenne

Il faut dire à GPSD sur quel port USB se trouve ton antenne.

**Ouvre le fichier de configuration :**
```bash
sudo nano /etc/default/gpsd
```

> `nano` est un éditeur de texte simple dans le terminal. Les flèches du clavier permettent de se déplacer.

**Tu vas voir un fichier qui ressemble à ça :**
```
# Default settings for the gpsd init script and the hotplug wrapper.
START_DAEMON="true"
GPSD_OPTIONS="-n"
DEVICES=""
USBAUTO="true"
GPSD_SOCKET="/var/run/gpsd.sock"
```

**Modifie la ligne `DEVICES` pour mettre le port de ton antenne.** Avec les touches directionnelles, place ton curseur sur la ligne `DEVICES=""` et change-la en :

```
DEVICES="/dev/ttyACM0"
```

> Si ton antenne est sur `/dev/ttyUSB0` (tu l'as vu à l'étape 7.2), mets `/dev/ttyUSB0` à la place.

**Pour sauvegarder :** Appuie sur `Ctrl + X`, puis `Y` (Yes), puis `Entrée`.

---

## 7.5 Démarrer et activer GPSD

```bash
sudo systemctl enable gpsd
sudo systemctl start gpsd
```

**Vérifier que GPSD tourne :**
```bash
sudo systemctl status gpsd
```

**✅ Ce que tu dois voir :**
```
● gpsd.service - GPS (Global Positioning System) Daemon
     Loaded: loaded (/lib/systemd/system/gpsd.service; enabled; ...)
     Active: active (running) since ...
```

Le mot clé important : **`active (running)`** en vert.

---

## 7.6 Tester que GPSD lit bien le GPS

```bash
cgps -s
```

**✅ Ce que tu dois voir :**

Si l'antenne est dehors avec vue sur le ciel et qu'elle a capté des satellites :
```
┌───────────────────────────────────────────┐
│ Time:    2024-01-15T10:32:15.000Z         │
│ Latitude: 14.69280 N                      │
│ Longitude: -17.44670 W                    │
│ Speed:   0.00 kts                        │
│ ...                                       │
└───────────────────────────────────────────┘
```

Si l'antenne cherche encore les satellites :
```
┌───────────────────────────────────────────┐
│ Status: NO FIX (searching...)             │
│ ...                                       │
└───────────────────────────────────────────┘
```
→ C'est normal les premières minutes. **Place l'antenne dehors et attends 5-15 minutes.**

**Pour quitter cgps :** Appuie sur `Q`

---

## 7.7 Installer Tailscale sur le Raspberry Pi

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**Ce que tu vas voir :** Plein de lignes d'installation.

**✅ Ce que tu dois voir à la fin :**
```
Installation complete! Log in to start using Tailscale by running:
  sudo tailscale up
```

**Connecter le Raspberry Pi à ton réseau Tailscale :**
```bash
sudo tailscale up
```

**✅ Ce que tu dois voir :**
```
To authenticate, visit:

	https://login.tailscale.com/a/XXXXXXXXXXXXXXX
```

**Sur ton PC :**
1. Ouvre ce lien dans ton navigateur
2. Connecte-toi avec le **même compte Tailscale** que celui utilisé sur ton PC
3. Clique sur **"Connect"** ou **"Approve"**

**Vérifier l'IP Tailscale du Raspberry Pi :**
```bash
tailscale ip -4
```

**✅ Ce que tu dois voir :**
```
100.xx.xx.xx
```

> 📝 **Note cette adresse.** C'est l'adresse Tailscale de cette box (ex: `100.89.175.28`).

---

## 7.8 Vérifier que le Pi peut joindre ton PC

```bash
curl http://100.81.42.31:5000/api/boxes
```

> Remplace `100.81.42.31` par **l'adresse Tailscale de ton PC** (notée à l'étape 4.1).

**✅ Ce que tu dois voir :**
```json
{"EDUBOX_DEMO_01": {...}, "EDUBOX_DEMO_02": {...}, ...}
```

Si tu vois des données JSON → ✅ La box peut bien communiquer avec ton PC serveur.

Si tu vois `Connection refused` ou `Network unreachable` → Vérifie que :
- Flask tourne sur ton PC (étape 5)
- Tailscale est bien connecté sur les deux appareils
- Le pare-feu Windows est configuré (étape 4.2)

---

## 7.9 Installer les bibliothèques Python nécessaires

```bash
pip3 install requests
```

**✅ Ce que tu dois voir :**
```
Successfully installed requests-2.x.x
```

---

## 7.10 Créer le script GPS de la box

Ce script va lire la position GPS et l'envoyer à ton PC toutes les 5 minutes.

**Crée le fichier :**
```bash
nano /home/pi/tracker_gps.py
```

**Copie-colle exactement ce texte** (utilise le copier-coller de ton terminal SSH) :

```python
import socket
import json
import time
import requests
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
URL_TOUR_CONTROLE = "http://100.81.42.31:5000/mise_a_jour_box"
ID_BOX = "MA_BOX_001"
# ---------------------

def obtenir_ip_tailscale():
    try:
        return subprocess.check_output(['tailscale', 'ip', '-4']).decode('utf-8').strip()
    except:
        return "Non communiquée"

def lire_temperature_cpu():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(float(f.read()) / 1000.0, 1)
    except:
        return 40.0

def lire_consommation_data():
    try:
        with open("/proc/net/dev", "r") as f:
            lignes = f.readlines()
        total_octets = 0
        for ligne in lignes[2:]:
            parties = ligne.split()
            interface = parties[0].strip(':')
            if interface not in ['lo']:
                total_octets += int(parties[1]) + int(parties[9])
        return round(total_octets / (1024 * 1024), 2)
    except:
        return 0.0

def lire_gps_officiel():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect(('127.0.0.1', 2947))
        s.send(b'?WATCH={"enable":true,"json":true}\n')

        fin_chrono = time.time() + 8
        nb_satellites = 0

        while time.time() < fin_chrono:
            try:
                data = s.recv(4096).decode('utf-8', errors='replace')
            except socket.timeout:
                continue

            for ligne in data.split('\n'):
                ligne = ligne.strip()
                if not ligne.startswith('{'):
                    continue
                try:
                    msg = json.loads(ligne)
                    classe = msg.get('class', '')

                    if classe == 'TPV':
                        lat  = msg.get('lat')
                        lon  = msg.get('lon')
                        mode = msg.get('mode', 0)
                        if mode >= 2 and lat and lon:
                            s.close()
                            return lat, lon, 'A'

                    elif classe == 'SKY':
                        sats = msg.get('satellites', [])
                        nb_satellites = sum(1 for sat in sats if sat.get('used', False))

                except (json.JSONDecodeError, KeyError):
                    pass

        s.close()
        return None, None, f'V:{nb_satellites}'

    except ConnectionRefusedError:
        return None, None, 'Erreur:GPSD_hors_ligne'
    except Exception as e:
        return None, None, f'Erreur:{e}'
    finally:
        if s:
            try:
                s.close()
            except:
                pass


def main():
    print("=" * 50)
    print(f"Démarrage Traqueur GPS — {ID_BOX}")
    print(f"Serveur : {URL_TOUR_CONTROLE}")
    print(f"IP Tailscale : {obtenir_ip_tailscale()}")
    print("=" * 50)

    tentatives_sans_fix = 0

    while True:
        lat, lon, status = lire_gps_officiel()

        if status == 'A':
            tentatives_sans_fix = 0
            heure_actuelle = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ip_ts = obtenir_ip_tailscale()
            donnees = {
                "id_materiel": ID_BOX,
                "lat":          round(lat, 5),
                "lon":          round(lon, 5),
                "status":       "Connecté",
                "temperature":  lire_temperature_cpu(),
                "users":        1,
                "data_mb":      lire_consommation_data(),
                "ip_tailscale": ip_ts,
                "last_seen":    heure_actuelle,
            }
            try:
                r = requests.post(URL_TOUR_CONTROLE, json=donnees, timeout=5)
                if r.status_code == 200:
                    print(f"[{heure_actuelle}] Position envoyee lat={round(lat,5)} lon={round(lon,5)}")
                else:
                    print(f"[{heure_actuelle}] Serveur repond {r.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"[{heure_actuelle}] Impossible de joindre le serveur")
            except Exception as e:
                print(f"[{heure_actuelle}] Erreur envoi : {e}")

            time.sleep(300)

        elif status.startswith('V'):
            tentatives_sans_fix += 1
            nb_sats = status.split(':')[1] if ':' in status else '0'
            print(f"Recherche satellites... ({nb_sats} utilisé(s)) — tentative {tentatives_sans_fix}")
            if tentatives_sans_fix == 1:
                print("   Conseil : GPS doit être dehors, ciel dégagé.")
            time.sleep(15)

        else:
            detail = status.replace('Erreur:', '')
            print(f"GPSD inaccessible ({detail}) — retry dans 10s")
            time.sleep(10)


if __name__ == '__main__':
    time.sleep(5)
    main()
```

> ⚠️ **AVANT DE SAUVEGARDER**, modifie ces deux lignes :
> - `URL_TOUR_CONTROLE = "http://100.81.42.31:5000/mise_a_jour_box"` → remplace `100.81.42.31` par **l'IP Tailscale de ton PC**
> - `ID_BOX = "MA_BOX_001"` → mets un nom unique pour cette box (ex: `"EDUBOX-001"`, `"AGRIBOX-001"`)

**Pour sauvegarder :** `Ctrl + X` → `Y` → `Entrée`

---

## 7.11 Tester le script manuellement

Avant de le mettre en service automatique, teste-le :

```bash
python3 /home/pi/tracker_gps.py
```

**✅ Ce que tu dois voir :**
```
==================================================
Démarrage Traqueur GPS — MA_BOX_001
Serveur : http://100.81.42.31:5000/mise_a_jour_box
IP Tailscale : 100.xx.xx.xx
==================================================
Recherche satellites... (0 utilisé(s)) — tentative 1
   Conseil : GPS doit être dehors, ciel dégagé.
Recherche satellites... (3 utilisé(s)) — tentative 2
Recherche satellites... (7 utilisé(s)) — tentative 3
...
[25/05/2024 10:32:15] Position envoyee lat=14.69280 lon=-17.44670
```

Une fois que tu vois **"Position envoyée"**, retourne sur l'interface Streamlit dans ton navigateur (`http://localhost:8501`) → la box doit apparaître sur la carte ! 🎉

**Pour arrêter le test :** `Ctrl + C`

---

## 7.12 Créer le service automatique (démarrage au boot)

Le service systemd permet au script de démarrer automatiquement au démarrage du Raspberry Pi, sans que tu aies besoin de faire quoi que ce soit.

**Crée le fichier de service :**
```bash
sudo nano /etc/systemd/system/tracker_gps.service
```

**Copie-colle exactement ce texte :**
```ini
[Unit]
Description=Traqueur GPS Yeelen
After=network-online.target gpsd.service
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 -u /home/pi/tracker_gps.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Pour sauvegarder :** `Ctrl + X` → `Y` → `Entrée`

**Activer et démarrer le service :**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tracker_gps.service
sudo systemctl start tracker_gps.service
```

**✅ Vérifier que le service tourne :**
```bash
sudo systemctl status tracker_gps.service
```

**✅ Ce que tu dois voir :**
```
● tracker_gps.service - Traqueur GPS Yeelen
     Loaded: loaded (/etc/systemd/system/tracker_gps.service; enabled; ...)
     Active: active (running) since ...
    Process: ExecStart=/usr/bin/python3 -u /home/pi/tracker_gps.py
   Main PID: 1234 (python3)
```

Le mot **`active (running)`** en vert = ✅ Le service tourne.

**Voir les logs en direct :**
```bash
sudo journalctl -fu tracker_gps.service
```

> Pour quitter l'affichage des logs : `Ctrl + C`

---

# 8. CONNECTER LA BOX AU SERVEUR

## 8.1 Résumé de ce qui doit être en marche

Sur ton PC :
| Ce qui doit tourner | Où ? | Comment savoir |
|---------------------|------|----------------|
| Tailscale | Icône dans la barre des tâches | Icône verte |
| Flask (`app.py`) | Fenêtre PowerShell #1 | Affiche "Running on..." |
| Streamlit | Fenêtre PowerShell #2 | Navigateur ouvert sur :8501 |

Sur chaque Raspberry Pi :
| Ce qui doit tourner | Comment vérifier |
|---------------------|------------------|
| Tailscale | `tailscale ip -4` → affiche une IP en 100.x |
| GPSD | `sudo systemctl status gpsd` → "active (running)" |
| tracker_gps.service | `sudo systemctl status tracker_gps.service` → "active (running)" |

---

## 8.2 Ajouter un nom lisible à une box dans l'interface

Par défaut, la box apparaît avec son ID technique (ex: `AGRIBOX-001`). Tu peux lui donner un nom plus clair dans l'interface.

1. Connecte-toi à l'interface Streamlit (`http://localhost:8501`)
2. Va dans l'onglet **📋 Flotte**
3. Trouve la box et clique sur le crayon ✏️ pour la renommer
4. Entre un nom lisible, par exemple : `AgriBox Dakar 01`

---

# 9. VÉRIFICATION FINALE

## ✅ Checklist complète

Voici la liste de vérification pour confirmer que tout fonctionne :

### Sur ton PC
- [ ] Python installé → `python --version` affiche `Python 3.12.x`
- [ ] Flask tourne → la fenêtre PowerShell affiche "Running on all addresses"
- [ ] Streamlit tourne → l'interface s'ouvre dans le navigateur sur `:8501`
- [ ] Tailscale connecté → icône verte dans la barre des tâches
- [ ] Pare-feu configuré → règle "Flask Tour de Controle" créée

### Sur chaque Raspberry Pi
- [ ] GPSD installé et actif → `sudo systemctl status gpsd` = active
- [ ] Tailscale connecté → `tailscale ip -4` = IP en 100.x.x.x
- [ ] Connexion au serveur vérifiée → `curl http://TON_IP:5000/api/boxes` = JSON
- [ ] Script tracker_gps.py créé → `ls /home/pi/tracker_gps.py` = fichier présent
- [ ] Service activé → `sudo systemctl status tracker_gps.service` = active (enabled)
- [ ] Antenne GPS dehors et connectée → `ls /dev/ttyACM*` = /dev/ttyACM0

### Dans l'interface
- [ ] La box apparaît dans l'onglet Carte et Flotte
- [ ] Le statut est "Connecté" (en vert)
- [ ] La position s'affiche sur la carte

---

## 🗺️ Ce que tu vois sur la carte quand tout fonctionne

```
┌──────────────────────────────────────────────────────────┐
│  Tour de Contrôle Yeelen — SchoolBox Africa              │
├──────────────────────────────────────────────────────────┤
│  🗺️ Carte │ 📋 Flotte │ 📊 Historique │ 🗒️ Journal │ ...│
├──────────────────────────────────────────────────────────┤
│                                                          │
│   [Carte du monde avec des marqueurs bleus sur chaque    │
│    emplacement de box. Clic sur un marqueur = infos]     │
│                                                          │
│   📍 AgriBox Dakar 01                                    │
│   ├── 🌡️ Température : 45°C                            │
│   ├── 👥 Utilisateurs : 12                              │
│   ├── 📶 Data : 105 Mo                                  │
│   ├── 🌐 IP : 100.xx.xx.xx                              │
│   └── 🕐 Dernière mise à jour : il y a 2 min            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

# 10. DÉPANNAGE

## ❓ La box n'apparaît pas sur la carte

**Vérifie dans l'ordre :**

1. **Flask tourne-t-il sur ton PC ?**
   ```powershell
   # Sur ton PC dans PowerShell
   curl http://localhost:5000/api/boxes
   ```
   → Tu dois voir du JSON. Sinon, relance `python app.py`.

2. **La box peut-elle joindre ton PC ?**
   ```bash
   # Sur le Raspberry Pi
   curl http://IP_TAILSCALE_TON_PC:5000/api/boxes
   ```
   → Si "Connection refused" → Tailscale n'est peut-être pas connecté sur l'un des appareils.

3. **Le script GPS tourne-t-il ?**
   ```bash
   sudo systemctl status tracker_gps.service
   ```
   → Si "inactive" → `sudo systemctl start tracker_gps.service`

4. **Quel est le log du service ?**
   ```bash
   sudo journalctl -fu tracker_gps.service --lines=20
   ```

---

## ❓ "GPSD inaccessible" dans les logs

```bash
# Redémarre GPSD
sudo systemctl restart gpsd

# Vérifie que l'antenne est reconnue
ls /dev/ttyACM* /dev/ttyUSB*

# Vérification approfondie
sudo gpsd -N -D 3 /dev/ttyACM0
```

Si l'antenne n'est pas dans `/dev/ttyACM0`, modifie `/etc/default/gpsd` avec le bon port.

---

## ❓ Le GPS cherche les satellites depuis trop longtemps (> 20 min)

- Assure-toi que l'antenne est **à l'extérieur**, avec une vue dégagée sur le ciel (sans bâtiment, arbre ou toit au-dessus)
- Le premier fix ("cold start") peut prendre jusqu'à 15 minutes
- Une fois le premier fix obtenu, les suivants sont quasi instantanés
- Si après 30 minutes dehors il n'y a toujours rien → teste avec `cgps -s` pour voir ce que GPSD reçoit

---

## ❓ "streamlit : Le terme n'est pas reconnu" sur Windows

Utilise toujours cette commande à la place :
```powershell
python -m streamlit run streamlit_app.py
```

---

## ❓ Mot de passe oublié pour l'interface

Sur ton PC, dans le dossier du projet :
```powershell
python -c "from database import update_password; update_password('superadmin', 'NouveauMotDePasse123!', 'reset')"
```

---

## ❓ La box affiche "Hors-ligne" alors qu'elle tourne

Le système considère une box "hors-ligne" si elle n'a pas envoyé de données depuis 6 minutes. Vérifie que :
- Le script `tracker_gps.py` tourne bien (étape ci-dessus)
- Le GPS a un fix valide (les données ne sont envoyées que quand la position est connue)

---

# ANNEXE — PARAMÈTRES À RETENIR

| Paramètre | Valeur |
|-----------|--------|
| IP Tailscale PC serveur | `100.81.42.31` (la tienne peut être différente) |
| Port Flask | `5000` |
| Port Streamlit | `8501` |
| Identifiant superadmin | `superadmin` |
| Mot de passe par défaut | `Yeelen2024!` |
| Fréquence d'envoi GPS | Toutes les 5 minutes (300 secondes) |
| Délai "Hors-ligne" | 6 minutes sans données |
| Emplacement script sur Pi | `/home/pi/tracker_gps.py` |
| Emplacement service systemd | `/etc/systemd/system/tracker_gps.service` |

---

# ANNEXE — COMMANDES DE RÉFÉRENCE RAPIDE

## Sur ton PC (PowerShell)

```powershell
# Lancer Flask (serveur)
cd "C:\chemin\vers\tour-v4"
python app.py

# Lancer Streamlit (interface)
cd "C:\chemin\vers\tour-v4"
python -m streamlit run streamlit_app.py

# Voir l'IP Tailscale de ton PC
tailscale ip -4
```

## Sur le Raspberry Pi

```bash
# Voir l'IP Tailscale du Pi
tailscale ip -4

# Statut de tous les services GPS
sudo systemctl status gpsd tracker_gps.service

# Redémarrer tout
sudo systemctl restart gpsd tracker_gps.service

# Voir les logs GPS en direct
sudo journalctl -fu tracker_gps.service

# Voir les données GPS brutes
cgps -s

# Tester l'envoi au serveur manuellement
curl -X POST http://IP_PC:5000/mise_a_jour_box \
  -H "Content-Type: application/json" \
  -d '{"id_materiel":"TEST","lat":14.69,"lon":-17.44,"temperature":45,"users":1,"data_mb":10,"ip_tailscale":"100.x.x.x"}'
```

---

*Guide rédigé par Yeelen Consulting — Système Tour de Contrôle SchoolBox Africa*
*Version 1.0 — Mai 2026*
