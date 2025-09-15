import os
import re
import extract_msg
from datetime import datetime
from tkinter import Tk, filedialog, messagebox

# Ungültige Zeichen für Dateinamen ersetzen
def clean_filename(text):
    return re.sub(r'[<>:"/\\|?*]', "_")

# Nummer in Buchstaben umwandeln: a, b, c, ..., aa, ab, ...
def num_to_letters(num):
    letters = ""
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letters = chr(97 + remainder) + letters
    return letters

# Prüfen, ob Datei schon ein Datum im Namen hat
def has_date_prefix(filename):
    return re.match(r'^\d{4}-\d{2}-\d{2}[a-z]*_', filename) is not None

def main():
    # Ordnerauswahl
    root = Tk()
    root.withdraw()
    ordner = filedialog.askdirectory(title="Wähle den Ordner mit den .msg-Dateien")
    if not ordner:
        print("Kein Ordner gewählt. Abbruch.")
        return

    umbenannt = 0
    fehler = []

    for datei in os.listdir(ordner):
        if datei.lower().endswith(".msg") and not has_date_prefix(datei):
            pfad = os.path.join(ordner, datei)
            try:
                msg = extract_msg.Message(pfad)
                msg_date = msg.date
                msg_subject = msg.subject or "Ohne_Betreff"

                # Datum ins Format YYYY-MM-DD
                datum_str = "0000-00-00"
                if msg_date:
                    parsed = False
                    # Versuche Standardformat aus Outlook
                    for fmt in ["%a, %d %b %Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            datum = datetime.strptime(msg_date[:25], fmt)
                            datum_str = datum.strftime("%Y-%m-%d")
                            parsed = True
                            break
                        except:
                            continue
                    if not parsed:
                        # Falls alles scheitert, Standarddatum verwenden
                        datum_str = "0000-00-00"

                # Betreff bereinigen + kürzen
                subject_clean = clean_filename(msg_subject.strip())[:100]

                # Basisname
                basis_name = f"{datum_str}_{subject_clean}"
                neuer_name = f"{basis_name}.msg"
                neue
