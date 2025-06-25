import os
import re
import shutil
from docx import Document

# Setări directoare pe Desktop
user = os.getlogin()
desktop = os.path.join("C:\Users", user, "Desktop")
folder_sursa = os.path.join(desktop, "DeSortat")
folder_destinatie = os.path.join(desktop, "Sortate")

# Mapare lună abreviată -> lună completă
luni = {
    "Ian.": "Ianuarie", "Feb.": "Februarie", "Mar.": "Martie", "Apr.": "Aprilie",
    "Mai.": "Mai", "Iun.": "Iunie", "Iul.": "Iulie", "Aug.": "August",
    "Sep.": "Septembrie", "Oct.": "Octombrie", "Nov.": "Noiembrie", "Dec.": "Decembrie"
}

# Parcurge fișierele Word
for fisier in os.listdir(folder_sursa):
    if fisier.lower().endswith(".docx"):
        cale_fisier = os.path.join(folder_sursa, fisier)
        try:
            doc = Document(cale_fisier)
            paragrafe = [p.text for p in doc.paragraphs[:11]]
            text_comb = " ".join(paragrafe)

            # Detectează anul
            an_match = re.search(r"\b(2023|2024|2025)\b", text_comb)
            if not an_match:
                continue
            an = an_match.group(1)

            # Detectează luna și ziua
            data_match = re.search(
                r"\b(" + "|".join(re.escape(luna) for luna in luni.keys()) + r")\s?(\d{1,2})\b",
                text_comb
            )
            if not data_match:
                continue

            luna_abrev = data_match.group(1)
            zi = data_match.group(2).zfill(2)
            luna_lunga = luni[luna_abrev]

            # Creează folder destinație
            cale_dest = os.path.join(folder_destinatie, f"Lucrari {an}", f"CTC_{zi}_{luna_lunga}")
            os.makedirs(cale_dest, exist_ok=True)

            # Copiază fișierul
            shutil.copy2(cale_fisier, os.path.join(cale_dest, fisier))
            print(f"✔️ {fisier} -> {cale_dest}")

        except Exception as e:
            print(f"❌ Eroare la {fisier}: {e}")