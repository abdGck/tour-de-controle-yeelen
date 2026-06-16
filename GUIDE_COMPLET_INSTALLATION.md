# 📘 GUIDE COMPLET D'INSTALLATION
## Système de Suivi GPS — Tour de Contrôle Yeelen Consulting
### Pour une personne sans connaissance en informatique

---

> **Ce guide te permet d'ajouter une nouvelle box éducative au système GPS Yeelen.**
> L'interface et le serveur sont déjà déployés dans le cloud — tu n'as qu'à configurer
> chaque nouveau Raspberry Pi pour qu'il envoie ses données automatiquement.

---

## 📋 INFORMATIONS DU SYSTÈME (à conserver précieusement)

| Élément | Valeur |
|---------|--------|
| 🌐 **Interface web** | https://tour-de-controle-yeelen.streamlit.app |
| 🔗 **Serveur Flask** | https://tour-de-controle-yeelen.onrender.com |
| 📡 **Endpoint boxes** | https://tour-de-controle-yeelen.onrender.com/mise_a_jour_box |
| 🔑 **Token API** | `8ec8da953c6811952a0324be372d647dc54194920c29583e1762d07598ae2216` |
| 👤 **Identifiant admin** | `superadmin` |
| 🔐 **Mot de passe admin** | *(celui défini sur Render → variable SUPERADMIN_PASSWORD)* |

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble — comprendre le système](#1-vue-densemble)
2. [Matériel nécessaire pour une box](#2-matériel-nécessaire)
3. [Configurer le Raspberry Pi](#3-configurer-le-raspberry-pi)
4. [Installer et configurer GPSD](#4-installer-et-configurer-gpsd)
5. [Installer Tailscale sur la box](#5-installer-tailscale)
6. [Installer le script GPS](#6-installer-le-script-gps)
7. [Créer le service automatique](#7-créer-le-service-automatique)
8. [Vérification finale](#8-vérification-finale)
9. [Dépannage](#9-dépannage)
10. [Commandes de référence rapide](#10-commandes-de-référence-rapide)

---

# 1. VUE D'ENSEMBLE

## 🧩 Comment le système fonctionne

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD (toujours actif)                        │
│                                                                 │
│  ┌─────────────────────────┐   ┌───────────────────────────┐   │
│  │  Serveur Flask          │   │  Interface Streamlit       │   │
│  │  (Render.com)           │──▶│  (Streamlit Cloud)         │   │
│  │  reçoit les données     │   │  carte + tableau de bord   │   │
│  │  des boxes              │   │  accessible partout        │   │
│  └──────────┬──────────────┘   └───────────────────────────┘   │
└─────────────┼───────────────────────────────────────────────────┘
              │ Internet (HTTPS sécurisé)
   ┌──────────┴──────────┬──────────────┐
   │                     │              │
┌──▼──────────┐  ┌───────▼─────┐  ┌────▼────────┐
│  EDUBOX-001 │  │ AGRIBOX-001 │  │  BOX-XXX    │
│  Raspberry  │  │  Raspberry  │  │  (nouvelle) │
│  Pi         │  │  Pi         │  │             │
│  GPS USB ↓  │  │  GPS USB ↓  │  │  GPS USB ↓  │
│  GPSD       │  │  GPSD       │  │  GPSD       │
│  tracker.py │  │  tracker.py │  │  tracker.py │
└─────────────┘  └─────────────┘  └─────────────┘
```

**En résumé :**
- Chaque **Raspberry Pi** a une antenne GPS branchée en USB
- Le script `tracker_gps.py` lit la position GPS et l'envoie au serveur cloud toutes les **5 minutes**
- Le serveur **Render** reçoit et stocke ces données (24h/24)
- L'**interface Streamlit** affiche tout sur une carte, accessible depuis n'importe où

---

# 2. MATÉRIEL NÉCESSAIRE

## 📦 Pour chaque nouvelle box éducative
| Composant | Description |
|-----------|-------------|
| **Raspberry Pi** | Modèle 3B+, 4 ou 5 — n'importe lequel |
| **Carte microSD** | Minimum 16 Go avec Raspberry Pi OS installé |
| **Antenne GPS USB** | Modèle : [GPS USB Amazon B0GC6DMV6M](https://www.amazon.fr/dp/B0GC6DMV6M) |
| **Câble USB** | Pour brancher l'antenne au Raspberry Pi |
| **Alimentation** | Adaptateur officiel Raspberry Pi (5V 3A) |
| **Internet** | WiFi ou câble Ethernet (connexion obligatoire) |

> ⚠️ **Important :** L'antenne GPS **doit être placée dehors** ou près d'une fenêtre avec vue dégagée sur le ciel.

---

# 3. CONFIGURER LE RASPBERRY PI

## 3.1 Se connecter à la box (SSH depuis ton PC)

SSH te permet de contrôler le Raspberry Pi à distance depuis ton PC Windows.

**Dans PowerShell sur ton PC :**
```powershell
ssh pi@ADRESSE_IP_LOCALE
```
> L'adresse IP locale du Raspberry Pi (ex: `192.168.1.45`) se trouve dans les paramètres WiFi de ta box ou dans l'interface de ton routeur.

**Mot de passe par défaut du Raspberry Pi :** `raspberry`

**✅ Ce que tu dois voir une fois connecté :**
```
Linux raspberrypi 6.x.x ...
pi@raspberrypi:~$
```

## 3.2 Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

Attends que tout se termine (quelques minutes).

**✅ Ce que tu dois voir à la fin :**
```
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

## 3.3 Vérifier que l'antenne GPS est détectée

Branche l'antenne GPS dans un port USB du Raspberry Pi, puis :

```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

**✅ Ce que tu dois voir :**
```
/dev/ttyACM0
```
ou `/dev/ttyUSB0` — c'est le port de ton antenne GPS.

Si tu ne vois rien → essaie un autre port USB et retape la commande.

---

# 4. INSTALLER ET CONFIGURER GPSD

GPSD est le logiciel qui lit l'antenne GPS et la met à disposition du script Python.

## 4.1 Installer GPSD

```bash
sudo apt install gpsd gpsd-clients -y
```

**✅ Ce que tu dois voir à la fin :**
```
Setting up gpsd ...
Setting up gpsd-clients ...
```

## 4.2 Configurer le port de l'antenne

```bash
sudo nano /etc/default/gpsd
```

Dans ce fichier, trouve la ligne `DEVICES=""` et modifie-la :
```
DEVICES="/dev/ttyACM0"
```
> Si ton antenne est sur `/dev/ttyUSB0`, mets `/dev/ttyUSB0`.

**Sauvegarde :** `Ctrl+X` → `Y` → `Entrée`

## 4.3 Activer GPSD

```bash
sudo systemctl enable gpsd
sudo systemctl start gpsd
sudo systemctl status gpsd
```

**✅ Ce que tu dois voir :**
```
● gpsd.service ...
     Active: active (running) since ...
```

**`active (running)`** en vert = ✅ GPSD tourne.

## 4.4 Tester la réception GPS

```bash
cgps -s
```

Si l'antenne est **dehors avec ciel dégagé** et a capté des satellites :
```
Latitude:  14.69280 N
Longitude: -17.44670 W
```

Si elle cherche encore :
```
Status: NO FIX (searching...)
```
→ Normal les premières minutes. Attends 5-15 min dehors.

**Pour quitter :** `Q`

---

# 5. INSTALLER TAILSCALE

Tailscale connecte la box à Internet de façon sécurisée.

## 5.1 Installer Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

## 5.2 Connecter la box au réseau Yeelen

```bash
sudo tailscale up
```

**✅ Ce que tu dois voir :**
```
To authenticate, visit:
    https://login.tailscale.com/a/XXXXXXXXXXXXXX
```

**Sur ton PC :** ouvre ce lien → connecte-toi avec le compte Tailscale Yeelen → clique **"Connect"**.

## 5.3 Vérifier l'IP Tailscale

```bash
tailscale ip -4
```

**✅ Ce que tu dois voir :**
```
100.xx.xx.xx
```

📝 Note cette adresse — c'est l'IP Tailscale de cette box.

## 5.4 Vérifier que la box joindra le serveur cloud

```bash
curl https://tour-de-controle-yeelen.onrender.com/api/boxes
```

**✅ Ce que tu dois voir :**
```json
{"EDUBOX_DEMO_01": {...}, "AGRIBOX-001": {...}}
```

Si tu vois du JSON → ✅ La box peut communiquer avec le serveur.

---

# 6. INSTALLER LE SCRIPT GPS

## 6.1 Installer la bibliothèque Python

```bash
pip3 install requests
```

## 6.2 Copier le script depuis ton PC

**Sur ton PC dans PowerShell** (pas sur la box) :

```powershell
scp "C:\Users\TON_NOM\Desktop\YEELEN CONSULTING\BOX EDUCATIVE\GPS\CLAUDE\INTERFACE GPS BOX EDUCATIVES\tour-v4\tracker_gps_TEMPLATE.py" pi@IP_TAILSCALE_BOX:/home/pi/tracker_gps.py
```

> Remplace `TON_NOM` par ton nom Windows et `IP_TAILSCALE_BOX` par l'IP Tailscale notée à l'étape 5.3

## 6.3 Modifier l'identifiant de la box

**Sur la box (SSH) :**
```bash
nano /home/pi/tracker_gps.py
```

Trouve cette ligne (en haut du fichier) :
```python
ID_BOX = "MA_BOX_001"
```

Change-la avec un nom unique pour cette box :
```python
ID_BOX = "EDUBOX-002"   # ou "AGRIBOX-002", "SCHOOLBOX-DAKAR-01", etc.
```

> ⚠️ **Règles pour le nom :**
> - Pas d'espaces → utilise des tirets : `EDUBOX-MALI-01` ✅ / `EduBox Mali 01` ❌
> - Pas d'accents ni de caractères spéciaux
> - Doit être **unique** (deux boxes ne peuvent pas avoir le même nom)

**Ne modifie rien d'autre dans le fichier.**

**Sauvegarde :** `Ctrl+X` → `Y` → `Entrée`

## 6.4 Tester manuellement le script

```bash
python3 /home/pi/tracker_gps.py
```

**✅ Ce que tu dois voir :**
```
=======================================================
  🚀 Traqueur GPS Yeelen — EDUBOX-002
  🔗 Serveur  : https://tour-de-controle-yeelen.onrender.com/mise_a_jour_box
  🌐 Tailscale: 100.xx.xx.xx
=======================================================
⏳ Recherche satellites... (0 utilisé(s)) — tentative 1
   💡 Le GPS doit être dehors, ciel dégagé.
⏳ Recherche satellites... (4 utilisé(s)) — tentative 2
⏳ Recherche satellites... (8 utilisé(s)) — tentative 3
✅ [25/05/2026 10:32:15] Envoyé → lat=14.69280 lon=-17.44670 | Temp=45.0°C | ...
```

Une fois que tu vois **"✅ Envoyé"**, vérifie l'interface :
**https://tour-de-controle-yeelen.streamlit.app** → la box apparaît sur la carte ! 🎉

**Pour arrêter le test :** `Ctrl+C`

---

# 7. CRÉER LE SERVICE AUTOMATIQUE

Le service systemd démarre le script automatiquement à chaque démarrage du Raspberry Pi.

## 7.1 Créer le fichier de service

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

**Sauvegarde :** `Ctrl+X` → `Y` → `Entrée`

## 7.2 Activer et démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable tracker_gps.service
sudo systemctl start tracker_gps.service
```

## 7.3 Vérifier que le service tourne

```bash
sudo systemctl status tracker_gps.service
```

**✅ Ce que tu dois voir :**
```
● tracker_gps.service - Traqueur GPS Yeelen
     Loaded: loaded (/etc/systemd/system/tracker_gps.service; enabled; ...)
     Active: active (running) since ...
```

**`enabled`** = démarre au boot ✅
**`active (running)`** = tourne maintenant ✅

## 7.4 Voir les logs en direct

```bash
sudo journalctl -fu tracker_gps.service
```

Pour quitter : `Ctrl+C`

---

# 8. VÉRIFICATION FINALE

## ✅ Checklist pour chaque nouvelle box

- [ ] Raspberry Pi à jour (`sudo apt update && sudo apt upgrade -y`)
- [ ] Antenne GPS détectée (`ls /dev/ttyACM*` → affiche `/dev/ttyACM0`)
- [ ] GPSD installé et actif (`sudo systemctl status gpsd` → `active (running)`)
- [ ] Tailscale connecté (`tailscale ip -4` → IP en `100.x.x.x`)
- [ ] Connexion serveur OK (`curl https://tour-de-controle-yeelen.onrender.com/api/boxes` → JSON)
- [ ] Script copié et `ID_BOX` modifié (`nano /home/pi/tracker_gps.py`)
- [ ] Test manuel réussi (`python3 /home/pi/tracker_gps.py` → "✅ Envoyé")
- [ ] Service activé (`sudo systemctl status tracker_gps.service` → `enabled` + `active`)
- [ ] Box visible sur l'interface (`https://tour-de-controle-yeelen.streamlit.app`)

---

# 9. DÉPANNAGE

## ❓ Le script envoie "401 Unauthorized"

Le token API dans le script ne correspond pas à celui du serveur.

**Vérifie le token actuel** sur l'interface Streamlit :
1. Connecte-toi → onglet **⚙️ Paramètres**
2. Copie le token affiché
3. Sur la box : `nano /home/pi/tracker_gps.py` → mets le bon token dans `API_TOKEN`
4. Redémarre : `sudo systemctl restart tracker_gps.service`

## ❓ "GPSD inaccessible" dans les logs

```bash
sudo systemctl restart gpsd
ls /dev/ttyACM* /dev/ttyUSB*   # vérifier que l'antenne est détectée
sudo systemctl status gpsd
```

## ❓ GPS cherche les satellites depuis plus de 20 minutes

- Antenne **dehors**, vue dégagée sur le ciel (pas de toit, pas d'arbre)
- Le premier démarrage ("cold start") peut prendre jusqu'à 15 min
- Teste : `cgps -s` → doit afficher des satellites

## ❓ La box apparaît "Hors-ligne" sur la carte

Le système marque une box "hors-ligne" si elle n'envoie pas de données depuis 6 minutes.
Vérifie que le service tourne et que le GPS a un fix valide.

## ❓ Impossible de faire SSH depuis mon PC

Vérifie que la box et ton PC sont sur le même réseau WiFi, ou utilise l'IP Tailscale :
```powershell
ssh pi@100.xx.xx.xx   # IP Tailscale de la box
```

---

# 10. COMMANDES DE RÉFÉRENCE RAPIDE

## Depuis ton PC (PowerShell)

```powershell
# Copier le script sur une box
scp "C:\...\tracker_gps_TEMPLATE.py" pi@IP_BOX:/home/pi/tracker_gps.py

# Se connecter en SSH
ssh pi@IP_TAILSCALE_BOX

# Voir l'interface
start https://tour-de-controle-yeelen.streamlit.app
```

## Sur le Raspberry Pi (après connexion SSH)

```bash
# Statut de tous les services
sudo systemctl status gpsd tracker_gps.service

# Redémarrer tout
sudo systemctl restart gpsd tracker_gps.service

# Voir les logs GPS en direct
sudo journalctl -fu tracker_gps.service

# Voir les données GPS brutes (appuie Q pour quitter)
cgps -s

# Voir l'IP Tailscale
tailscale ip -4

# Tester l'envoi au serveur manuellement
curl https://tour-de-controle-yeelen.onrender.com/api/boxes
```

---

## 📦 BOXES ACTUELLEMENT CONNECTÉES

| Nom | ID | IP Tailscale | Utilisateur SSH |
|-----|----|--------------|-----------------|
| EduBox | EDUBOX-001 | 100.89.175.28 | `admin` |
| AgriBox | AGRIBOX-001 | 100.66.117.83 | `pi` |

> Pour chaque nouvelle box à ajouter, répète les étapes 3 à 8 de ce guide.
> Le seul paramètre qui change d'une box à l'autre est `ID_BOX` dans le script.

---

*Yeelen Consulting — Guide Installation v2.0 — Mai 2026*
*Interface : https://tour-de-controle-yeelen.streamlit.app*
