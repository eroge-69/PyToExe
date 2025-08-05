
import sys
from pathlib import Path

def patch_file(file_path):
    # Charger le fichier
    with open(file_path, "rb") as f:
        data = bytearray(f.read())

    # Message personnalisé
    message = "Fichier protégé SH Préparation"
    message_bytes = message.encode("latin-1")

    # Réponse custom : 0x7F 0x23 0x33 + message ASCII
    custom_response = bytearray([0x7F, 0x23, 0x33]) + message_bytes

    # Rechercher toutes les occurrences de 0x23 (commande ReadMemoryByAddress)
    occurrences = [i for i, b in enumerate(data) if b == 0x23]

    if not occurrences:
        print("⚠️ Aucun offset 0x23 trouvé, fichier non modifié.")
        return

    print(f"🔎 Offsets trouvés : {occurrences[:5]}{'...' if len(occurrences) > 5 else ''}")

    # Appliquer le patch sur les 2 premières occurrences (suffisant sur EDC15P+)
    for offset in occurrences[:2]:
        data[offset:offset + len(custom_response)] = custom_response

    # Créer le nouveau fichier
    new_file = Path(file_path).with_name(Path(file_path).stem + "_PROTEGE.bin")
    with open(new_file, "wb") as f:
        f.write(data)

    print(f"✅ Patch appliqué avec succès : {new_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Glissez-déposez un fichier .bin sur ce programme pour le patcher.")
        sys.exit(1)

    file_path = sys.argv[1]
    patch_file(file_path)
