"""
Script à installer sur chaque box éducative Yeelen
====================================================
Ce script envoie automatiquement les données de la box
au serveur Tour de Contrôle toutes les 60 secondes.

INSTALLATION sur la box :
1. Copier ce fichier sur la box (ex: /home/pi/script_box.py)
2. Modifier les 3 lignes de configuration ci-dessous (ID, LAT, LON)
3. Lancer : python3 script_box.py
4. Pour qu'il démarre automatiquement au boot, voir LANCEMENT.md
"""

import requests
import time
import subprocess
import os

# ══════════════════════════════════════════════════════════════
#  ⚙️  CONFIGURATION — à modifier pour chaque box
# ══════════════════════════════════════════════════════════════

ID_MATERIEL     = "EDUBOX_SENEGAL_01"   # ← Nom unique de cette box (pas d'espaces)
LATITUDE        = 14.6928              # ← Latitude GPS de l'emplacement de la box
LONGITUDE       = -17.4467             # ← Longitude GPS de l'emplacement de la box

SERVEUR_URL     = "http://100.81.42.31:5000/mise_a_jour_box"  # ← IP de ton PC serveur
INTERVALLE_SEC  = 60                   # ← Envoyer toutes les 60 secondes

# ══════════════════════════════════════════════════════════════
#  Fonctions — ne pas modifier
# ══════════════════════════════════════════════════════════════

def get_temperature():
    """Lit la température CPU du Raspberry Pi."""
    try:
        # Méthode 1 : fichier système Linux
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except Exception:
        pass
    try:
        # Méthode 2 : commande vcgencmd (Raspberry Pi)
        result = subprocess.check_output(["vcgencmd", "measure_temp"],
                                          text=True, timeout=5)
        return float(result.replace("temp=", "").replace("'C\n", ""))
    except Exception:
        return 0.0


def get_users_wifi():
    """Compte les appareils connectés en WiFi (hotspot)."""
    try:
        result = subprocess.check_output(
            ["iw", "dev", "wlan0", "station", "dump"],
            text=True, stderr=subprocess.DEVNULL, timeout=5
        )
        return result.count("Station")
    except Exception:
        return 0


def get_data_mb():
    """Lit la consommation data réseau en Mo (interface eth0 ou wwan0)."""
    interfaces = ["wwan0", "eth0", "usb0"]
    for iface in interfaces:
        try:
            path = f"/sys/class/net/{iface}/statistics/rx_bytes"
            if os.path.exists(path):
                with open(path) as f:
                    rx = int(f.read().strip())
                with open(f"/sys/class/net/{iface}/statistics/tx_bytes") as f:
                    tx = int(f.read().strip())
                return round((rx + tx) / (1024 * 1024), 2)
        except Exception:
            continue
    return 0.0


def get_ip_tailscale():
    """Récupère l'adresse IP Tailscale de cette box."""
    try:
        result = subprocess.check_output(
            ["tailscale", "ip", "-4"],
            text=True, stderr=subprocess.DEVNULL, timeout=5
        )
        return result.strip()
    except Exception:
        pass
    try:
        # Méthode alternative : lire les IPs réseau
        result = subprocess.check_output(["hostname", "-I"], text=True, timeout=5)
        ips = result.strip().split()
        for ip in ips:
            if ip.startswith("100."):
                return ip
    except Exception:
        pass
    return "Non communiquée"


def envoyer_donnees():
    """Collecte et envoie toutes les données au serveur."""
    temperature  = get_temperature()
    users        = get_users_wifi()
    data_mb      = get_data_mb()
    ip_tailscale = get_ip_tailscale()

    payload = {
        "id_materiel":  ID_MATERIEL,
        "lat":           LATITUDE,
        "lon":           LONGITUDE,
        "temperature":   temperature,
        "users":         users,
        "data_mb":       data_mb,
        "ip_tailscale":  ip_tailscale,
    }

    print(f"[{time.strftime('%H:%M:%S')}] Envoi → {ID_MATERIEL} | "
          f"Temp: {temperature}°C | Users: {users} | Data: {data_mb}Mo | IP: {ip_tailscale}")

    try:
        response = requests.post(SERVEUR_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Reçu par le serveur")
        else:
            print(f"  ⚠️  Réponse inattendue : {response.status_code} — {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Impossible de joindre le serveur ({SERVEUR_URL})")
        print(f"     → Vérifier que le serveur tourne et que Tailscale est connecté")
    except Exception as e:
        print(f"  ❌ Erreur : {e}")


# ══════════════════════════════════════════════════════════════
#  Démarrage
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print(f"  📡 Script box Yeelen — {ID_MATERIEL}")
    print(f"  🌍 Position : {LATITUDE}, {LONGITUDE}")
    print(f"  🔗 Serveur  : {SERVEUR_URL}")
    print(f"  ⏱  Intervalle : {INTERVALLE_SEC}s")
    print("=" * 55)

    # Premier envoi immédiat au démarrage
    envoyer_donnees()

    # Puis boucle toutes les X secondes
    while True:
        time.sleep(INTERVALLE_SEC)
        envoyer_donnees()
