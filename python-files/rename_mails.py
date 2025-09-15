import os
import re
import extract_msg
from datetime import datetime
from tkinter import Tk, filedialog, messagebox

# Ungültige Zeichen für Dateinamen ersetzen
def clean_filename(text):
    return re.sub(r'[<>:"/\\|?*]', "_")

# Hilfsfunktion: Nummer in a, b, c ... umwandeln (Excel-Style)
def num_to_letters(num):
    letters = ""
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letters = chr(97 + remainder) + letters  # 97 = 'a'
    return letters

# Prüfen, ob Dateiname schon ein Datum hat
def has_date_prefix(filename):
    return re.match(r'^\d{4}-\d{2}-\d{2}[a-z]*_', filename) is not None

def main():
    # Ordnerauswahl-Dialog
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

                # Datum ins Format YYYY-MM-DD bringen
                datum_str = "0000-00-00"
                if msg_date:
                    try:
                        datum = datetime.strptime(msg_date[:25], "%a, %d %b %Y %H:%M:%S")
                        datum_str = datum.strftime("%Y-%m-%d")
                    except:
                        try:
                            datum = datetime.strptime(msg_date, "%Y-%m-%d %H:%M:%S")
                            datum_str = datum.strftime("%Y-%m-%d")
                        except:
                            pass

                # Betreff bereinigen + kürzen
                subject_clean = clean_filename(msg_subject.strip())[:100]

                # Basis-Name ohne Buchstaben
                basis_name = f"{datum_str}_{subject_clean}"
                neuer_name = f"{basis_name}.msg"
                neuer_pfad = os.path.join(ordner, neuer_name)

                # Bei Namenskonflikt Buchstaben direkt nach Datum einfügen
                counter = 1
                while os.path.exists(neuer_pfad):
                    letters = num_to_letters(counter)
                    basis_name = f"{datum_str}{letters}_{subject_clean}"
                    neuer_name = f"{basis_name}.msg"
                    neuer_pfad = os.path.join(ordner, neuer_name)
                    counter += 1

                os.rename(pfad, neuer_pfad)
                umbenannt += 1

            except Exception as e:
                fehler.append(f"{datei}: {e}")

    # Ende-Meldung
    if fehler:
        messagebox.showwarning("Fertig mit Fehlern",
                               f"{umbenannt} Dateien umbenannt.\n{len(fehler)} Fehler aufgetreten.\nSiehe Konsole.")
        for f in fehler:
            print("Fehler:", f)
    else:
        messagebox.showinfo("Fertig", f"{umbenannt} Dateien erfolgreich umbenannt.")

if __name__ == "__main__":
    main()
