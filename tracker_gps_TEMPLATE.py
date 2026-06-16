"""
╔══════════════════════════════════════════════════════════════╗
║         TRACKER GPS — Yeelen Consulting / SchoolBox Africa   ║
║         Script universel pour toutes les boxes éducatives    ║
╠══════════════════════════════════════════════════════════════╣
║  INSTALLATION SUR UNE NOUVELLE BOX :                         ║
║                                                              ║
║  1. Copie ce fichier sur le Raspberry Pi :                   ║
║     scp tracker_gps_TEMPLATE.py pi@IP_BOX:/home/pi/tracker_gps.py
║                                                              ║
║  2. Modifie UNIQUEMENT la ligne ID_BOX ci-dessous            ║
║     (donne un nom unique à chaque box)                       ║
║                                                              ║
║  3. Installe le service automatique (voir GUIDE)             ║
╚══════════════════════════════════════════════════════════════╝
"""

import socket
import json
import time
import requests
import subprocess
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  ⚙️  CONFIGURATION — modifier UNIQUEMENT cette ligne
# ══════════════════════════════════════════════════════════════

ID_BOX = "MA_BOX_001"   # ← Nom unique de la box (ex: "EDUBOX-002", "AGRIBOX-003")
                         #   Pas d'espaces, pas d'accents, utilise des tirets

# ══════════════════════════════════════════════════════════════
#  🔒  NE PAS MODIFIER — paramètres du serveur Yeelen
# ══════════════════════════════════════════════════════════════

URL_TOUR_CONTROLE = "https://tour-de-controle-yeelen.onrender.com/mise_a_jour_box"
API_TOKEN         = "126e6f92caec167033897858a5429ed596d1b1493bb7ce4e9477304de21faeb3"
INTERVALLE_ENVOI  = 300   # secondes entre chaque envoi GPS (5 minutes)

# ══════════════════════════════════════════════════════════════
#  Fonctions — ne pas modifier
# ══════════════════════════════════════════════════════════════

def obtenir_ip_tailscale():
    """Récupère l'adresse IP Tailscale de la box."""
    try:
        return subprocess.check_output(
            ['tailscale', 'ip', '-4'], timeout=5
        ).decode('utf-8').strip()
    except Exception:
        return "Non communiquée"


def lire_temperature_cpu():
    """Lit la température du processeur (°C)."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(float(f.read()) / 1000.0, 1)
    except Exception:
        return 40.0


def lire_consommation_data():
    """Lit la consommation data réseau totale (Mo)."""
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
    except Exception:
        return 0.0


def lire_gps_officiel():
    """
    Lit la position GPS via GPSD (daemon GPS).
    Retourne (lat, lon, 'A')            → fix GPS valide, position connue
    Retourne (None, None, 'V:X')        → en attente de satellites (X = nb satellites vus)
    Retourne (None, None, 'Erreur:...') → GPSD inaccessible ou erreur
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)   # timeout pour éviter le blocage infini
        s.connect(('127.0.0.1', 2947))
        s.send(b'?WATCH={"enable":true,"json":true}\n')

        fin_chrono    = time.time() + 8   # lecture pendant 8 secondes max
        nb_satellites = 0

        while time.time() < fin_chrono:
            try:
                data = s.recv(4096).decode('utf-8', errors='replace')
            except socket.timeout:
                continue   # pas de données pendant 3s → on réessaie

            for ligne in data.split('\n'):
                ligne = ligne.strip()
                if not ligne.startswith('{'):
                    continue
                try:
                    msg    = json.loads(ligne)
                    classe = msg.get('class', '')

                    if classe == 'TPV':
                        lat  = msg.get('lat')
                        lon  = msg.get('lon')
                        mode = msg.get('mode', 0)
                        if mode >= 2 and lat and lon:   # mode 2 = 2D fix, mode 3 = 3D fix
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
            except Exception:
                pass


def envoyer_position(lat, lon):
    """Collecte toutes les données et les envoie au serveur Tour de Contrôle."""
    heure_actuelle = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ip_ts          = obtenir_ip_tailscale()

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
        "api_token":    API_TOKEN,   # ← authentification auprès du serveur cloud
    }

    try:
        r = requests.post(URL_TOUR_CONTROLE, json=donnees, timeout=10)
        if r.status_code == 200:
            print(f"✅ [{heure_actuelle}] Envoyé → lat={round(lat,5)} lon={round(lon,5)} "
                  f"| Temp={donnees['temperature']}°C | Data={donnees['data_mb']}Mo "
                  f"| IP={ip_ts}")
        elif r.status_code == 401:
            print(f"🔐 [{heure_actuelle}] Accès refusé (401) — vérifie le API_TOKEN dans ce script")
        else:
            print(f"⚠️  [{heure_actuelle}] Serveur a répondu {r.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ [{heure_actuelle}] Impossible de joindre {URL_TOUR_CONTROLE}")
        print(f"     → Vérifie la connexion Internet de la box")
    except requests.exceptions.Timeout:
        print(f"⏱  [{heure_actuelle}] Le serveur n'a pas répondu dans les 10s (timeout)")
    except Exception as e:
        print(f"❌ [{heure_actuelle}] Erreur envoi : {e}")


# ══════════════════════════════════════════════════════════════
#  Boucle principale
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print(f"  🚀 Traqueur GPS Yeelen — {ID_BOX}")
    print(f"  🔗 Serveur  : {URL_TOUR_CONTROLE}")
    print(f"  🌐 Tailscale: {obtenir_ip_tailscale()}")
    print("=" * 55)

    tentatives_sans_fix = 0

    while True:
        lat, lon, status = lire_gps_officiel()

        # ── Fix GPS obtenu → envoyer la position ─────────────
        if status == 'A':
            tentatives_sans_fix = 0
            envoyer_position(lat, lon)
            time.sleep(INTERVALLE_ENVOI)

        # ── En attente de satellites ──────────────────────────
        elif status.startswith('V'):
            tentatives_sans_fix += 1
            nb_sats = status.split(':')[1] if ':' in status else '0'
            print(f"⏳ Recherche satellites... ({nb_sats} utilisé(s)) "
                  f"— tentative {tentatives_sans_fix}")
            if tentatives_sans_fix == 1:
                print("   💡 Le GPS doit être dehors, ciel dégagé.")
                print("   💡 Premier fix : 1 à 15 min selon la météo.")
            time.sleep(15)

        # ── GPSD inaccessible ─────────────────────────────────
        else:
            detail = status.replace('Erreur:', '')
            print(f"🔴 GPSD inaccessible ({detail}) — nouvelle tentative dans 10s")
            print(f"     → Lance : sudo systemctl status gpsd")
            time.sleep(10)


if __name__ == '__main__':
    time.sleep(5)   # attendre que le réseau soit prêt au démarrage
    main()
