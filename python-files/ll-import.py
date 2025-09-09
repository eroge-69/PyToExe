import os
import re
import pdfplumber
import pandas as pd

# 🔧 Pfad zum Ordner mit deinen PDFs
pdf_ordner = r"D:\auftraege\MurnigKG\SCH\ladelisten"  # ← hier anpassen
output_datei = "versanddaten.xlsx"

# 📦 Versandcodes, die extrahiert werden sollen
codes = ["PLK", "BND", "PLE", "LBUN", "PKT", "KPKT", "GCOL", "SONC", "VER2"]

# 📋 Ergebnisliste
alle_daten = []

# 📂 Alle PDFs im Ordner durchgehen
for datei in os.listdir(pdf_ordner):
    if datei.lower().endswith(".pdf"):
        pfad = os.path.join(pdf_ordner, datei)
        with pdfplumber.open(pfad) as pdf:
            text = "\n".join([seite.extract_text() for seite in pdf.pages if seite.extract_text()])

        # 🕒 Druckzeitpunkt extrahieren
        druckzeit = re.search(r"Druck:\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", text)
        druckzeit = druckzeit.group(1) if druckzeit else ""

        # 🚚 Tournummer extrahieren
        tournummer = re.search(r"Tournummer:\s*(\d+)", text)
        tournummer = tournummer.group(1) if tournummer else ""

        # 📦 Versandeinheiten extrahieren
        versand = {code: 0 for code in codes}
        matches = re.findall(r"(\d+)\s+(" + "|".join(codes) + r")", text)
        for menge, code in matches:
            versand[code] += int(menge)

        # 🧾 Zeile zusammenbauen
        zeile = [druckzeit, tournummer] + [versand[code] for code in codes]
        alle_daten.append(zeile)

# 🧮 Excel schreiben
spalten = ["Druckzeitpunkt", "Tournummer"] + codes
df = pd.DataFrame(alle_daten, columns=spalten)
df.to_excel(output_datei, index=False)

print(f"✅ Fertig! Daten gespeichert in: {output_datei}")