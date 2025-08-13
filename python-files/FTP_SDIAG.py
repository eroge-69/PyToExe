import os
import re
import tarfile
import tempfile
from collections import defaultdict
import paramiko

# === CONFIGURATION SFTP ===
SFTP_HOST = "172.16.28.1"
SFTP_PORT = 22
SFTP_USER = "MaintenanceMR"
SFTP_PASS = "MRftp@Lxt2017"
REMOTE_DIR = "remote_reg"

# === SORTIE LOCALE ===
LOCAL_DIR = "logs_par_rame"
os.makedirs(LOCAL_DIR, exist_ok=True)

# === COFFRES ATTENDUS ===
COFFRES_ATTENDUS = {
    "ACR": ["C1", "C2", "S3"],
    "TCU": ["C1", "C2", "S3"],
    "HMI": ["1", "2"],
    # "MON_ACR": ["C1", "C2", "S3"],  # prêt mais désactivé
    # "MON_TCU": ["C1", "C2", "S3"],  # prêt mais désactivé
}

# === PATTERNS (corrigés pour inclure M3) ===
PATTERNS = {
    "ACR": r"^(?P<rame>\d{3})_CPU_DSP_ACR_(?P<coffre>C\d|S3|M3)_(?P<date>\d{8})_\d{6}\.tar\.gz$",
    "TCU": r"^(?P<rame>\d{3})_CPU_DSP_TCU_(?P<coffre>C\d|S3|M3)_(?P<date>\d{8})_\d{6}\.tar\.gz$",
    "HMI": r"^(?P<rame>\d{3})_HMI(?P<coffre>[12])_(?P<date>\d{8})_\d{6}\.tar\.gz$",
    # "MON": r"^(?P<rame>\d{3})_MON_(?P<famille>ACR|TCU)_(?P<coffre>C\d|S3|M3)_(?P<date>\d{8})_\d{6}\.tar\.gz$",  # prêt mais désactivé
}

def connect_sftp():
    """Connexion SFTP (nouvelle connexion à chaque transfert pour robustesse)."""
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def lister_fichiers():
    sftp, transport = connect_sftp()
    try:
        sftp.chdir(REMOTE_DIR)
        files = sftp.listdir()
        return files
    finally:
        sftp.close()
        transport.close()

def organiser_fichiers(files):
    """
    Indexe les archives par rame/famille/coffre et ne garde que la plus récente (par date dans le nom).
    Normalise 'M3' -> 'S3'. HMI1/HMI2 mis en familles distinctes 'HMI' mais coffres '1'/'2'.
    """
    mapping = defaultdict(lambda: defaultdict(dict))  # mapping[rame][famille][coffre] = {"date": d, "filename": f}
    for name in files:
        # Ignore tout sauf .tar.gz
        if not name.endswith(".tar.gz"):
            continue

        # Ignorer MON (préparé mais désactivé)
        if "_MON_" in name or name.startswith(tuple([f"{i}_MON_" for i in range(100, 1000)])):
            # # Pour activer un jour, gérer via PATTERNS["MON"] et stocker famille MON_ACR / MON_TCU
            continue

        matched = False

        # ACR / TCU
        for famille in ("ACR", "TCU"):
            m = re.match(PATTERNS[famille], name)
            if m:
                d = m.groupdict()
                rame = int(d["rame"])
                coffre = d["coffre"].upper()
                if coffre == "M3":
                    coffre = "S3"
                date = d["date"]
                current = mapping[rame][famille].get(coffre)
                if (current is None) or (date > current["date"]):
                    mapping[rame][famille][coffre] = {"date": date, "filename": name}
                matched = True
                break

        if matched:
            continue

        # HMI1 / HMI2
        m = re.match(PATTERNS["HMI"], name)
        if m:
            d = m.groupdict()
            rame = int(d["rame"])
            coffre = d["coffre"]  # "1" ou "2"
            date = d["date"]
            current = mapping[rame]["HMI"].get(coffre)
            if (current is None) or (date > current["date"]):
                mapping[rame]["HMI"][coffre] = {"date": date, "filename": name}
            continue

        # Non reconnu -> on ignore silencieusement
    return mapping

def telecharger_et_extraire(remote_name, rame, famille, coffre):
    """
    Télécharge dans un fichier temporaire (en fermant avant extraction pour éviter WinError 32),
    puis extrait vers logs_par_rame/<rame>/<FamilleCoffre>/.
    """
    sous_dossier = f"{famille}{coffre}" if famille != "HMI" else f"HMI{coffre}"
    dest_dir = os.path.join(LOCAL_DIR, str(rame), sous_dossier)
    os.makedirs(dest_dir, exist_ok=True)

    remote_path = f"{REMOTE_DIR}/{remote_name}"
    sftp, transport = connect_sftp()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp:
            tmp_path = tmp.name  # fermé à la sortie du with
        # Télécharger *après* la fermeture du handle pour éviter les verrous Windows
        sftp.get(remote_path, tmp_path)
    finally:
        sftp.close()
        transport.close()

    try:
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(path=dest_dir)
        print(f"  ↳ Téléchargement : {remote_path}")
    except Exception as e:
        print(f"  ❌ Erreur pour {remote_name} : {e}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

def main():
    files = lister_fichiers()
    mapping = organiser_fichiers(files)

    # Traitement rame par rame (101..133)
    for rame in range(101, 134):
        familles = mapping.get(rame, {})
        if not familles:
            # Pas d'archives pour cette rame dans le listing -> log manquants complet
            rame_dir = os.path.join(LOCAL_DIR, str(rame))
            os.makedirs(rame_dir, exist_ok=True)
            tous_manquants = []
            for fam, coffs in COFFRES_ATTENDUS.items():
                for c in coffs:
                    tous_manquants.append(f"{fam}{c}")
            if tous_manquants:
                with open(os.path.join(rame_dir, f"manquant_{rame}.txt"), "w") as f:
                    f.write("\n".join(tous_manquants))
            print(f"\n🟦 Traitement de la rame {rame}\n  ❗ Coffres manquants pour rame {rame} : {', '.join(tous_manquants)}")
            continue

        print(f"\n🟦 Traitement de la rame {rame}")
        rame_dir = os.path.join(LOCAL_DIR, str(rame))
        os.makedirs(rame_dir, exist_ok=True)

        manquants = []
        for famille, coffres in COFFRES_ATTENDUS.items():
            dispo = familles.get(famille, {})
            for coffre in coffres:
                info = dispo.get(coffre)
                if not info:
                    manquants.append(f"{famille}{coffre}")
                    continue
                telecharger_et_extraire(info["filename"], rame, famille, coffre)

        if manquants:
            with open(os.path.join(rame_dir, f"manquant_{rame}.txt"), "w") as f:
                f.write("\n".join(manquants))
            print(f"  ❗ Coffres manquants pour rame {rame} : {', '.join(manquants)}")
        else:
            print(f"  ✅ Tous les coffres ont été traités pour rame {rame}")

if __name__ == "__main__":
    main()
