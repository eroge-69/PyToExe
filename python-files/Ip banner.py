import re
import configparser
import sys

def open_file(name: str) -> str:
    """Ouvre un fichier et retourne son contenu sous forme de chaîne de caractères."""
    try:
        print(f"Ouverture du fichier : {name}")
        with open(name, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Lecture réussie ({len(content)} caractères).")
        return content
    except Exception as e:
        print(f"Erreur lors de l'ouverture du fichier {name} : {e}")
        return ""

def save_file(name: str, content: str):
    """Enregistre le contenu dans un fichier."""
    try:
        print(f"Enregistrement dans le fichier : {name}")
        with open(name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Enregistrement réussi ({len(content)} caractères).")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier {name} : {e}")

def extraire_ips(texte: str):
    """Extrait toutes les adresses IPv4 d'un texte."""
    try:
        motif_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(motif_ip, texte)
        print(f"{len(ips)} IP(s) extraite(s) : {ips}")
        return ips
    except Exception as e:
        print(f"Erreur lors de l'extraction des IPs : {e}")
        return []

exemple_ini = """
EXEMPLE DE .INI:
[files]
entry_file = input.txt
whitelist_file = whitelist.txt
output_file = ips_to_ban.txt
"""

# Lecture du fichier de configuration
config = configparser.ConfigParser()
try:
    print("Lecture du fichier de configuration : config.ini")
    files_read = config.read('config.ini')
    if not files_read:
        raise FileNotFoundError("Le fichier config.ini est introuvable.")
    if 'files' not in config or \
       not all(k in config['files'] for k in ('entry_file', 'whitelist_file', 'output_file')):
        raise KeyError("Section 'files' ou clés manquantes dans config.ini.")
    entry_file = config['files']['entry_file']
    whitelist_file = config['files']['whitelist_file']
    output_file = config['files']['output_file']
    print(f"Fichiers configurés :\n  Entrée : {entry_file}\n  Whitelist : {whitelist_file}\n  Sortie : {output_file}")
except Exception as e:
    print(f"Erreur lors de la lecture de la configuration : {e}")
    print(exemple_ini)
    input("Vous pouvez fermer cette fenêtre")
    sys.exit(1)

entry_content = open_file(entry_file)
whitelist_content = open_file(whitelist_file)

ips = extraire_ips(entry_content)
whitelisted_ips = extraire_ips(whitelist_content)

ips_uniques = list(set(ips))
print(f"Liste des IPs uniques trouvées dans l'entrée : {ips_uniques}")

ips_to_ban = [ip for ip in ips_uniques if ip not in whitelisted_ips]
print(f"IPs à bannir (hors whitelist) : {ips_to_ban}")

save_file(output_file, '\n'.join(ips_to_ban))
print("Traitement terminé.")

input("Vous pouvez fermer cette fenêtre")
