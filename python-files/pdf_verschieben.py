import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

ZIEL_ORDNER = r"W:\Schichtpläne"
ARCHIV_ORDNER = os.path.join(ZIEL_ORDNER, "Archiv")

def kopiere_mit_zeitstempel_und_aenderungsdatum():
    dateipfad = filedialog.askopenfilename(
        title="PDF-Datei auswählen",
        filetypes=[("PDF-Dateien", "*.pdf")],
        initialdir=os.getcwd()
    )

    if not dateipfad:
        return

    try:
        os.makedirs(ZIEL_ORDNER, exist_ok=True)
        os.makedirs(ARCHIV_ORDNER, exist_ok=True)

        # Vorhandene Dateien im Zielordner archivieren
        for datei in os.listdir(ZIEL_ORDNER):
            vollpfad = os.path.join(ZIEL_ORDNER, datei)
            if os.path.isfile(vollpfad):
                name, ext = os.path.splitext(datei)
                zeitstempel = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                archiv_name = f"{name}_{zeitstempel}{ext}"
                shutil.move(vollpfad, os.path.join(ARCHIV_ORDNER, archiv_name))

        # Neue Datei kopieren (Leerzeichen durch Unterstriche ersetzen)
        original_name = os.path.basename(dateipfad)
        bereinigt_name = original_name.replace(" ", "_")
        zielpfad = os.path.join(ZIEL_ORDNER, bereinigt_name)
        shutil.copy2(dateipfad, zielpfad)
        
        ## Neue Datei kopieren
        #dateiname = os.path.basename(dateipfad)
        #zielpfad = os.path.join(ZIEL_ORDNER, dateiname)
        #shutil.copy2(dateipfad, zielpfad)

        # Änderungsdatum auf aktuelle Zeit setzen
        jetzt = datetime.now().timestamp()
        os.utime(zielpfad, (jetzt, jetzt))

        messagebox.showinfo("Erfolg", f"Datei kopiert und aktualisiert:\n{zielpfad}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Kopieren:\n{str(e)}")

# GUI
fenster = tk.Tk()
fenster.title("PDF kopieren mit Archivierung")
fenster.geometry("400x150")
fenster.resizable(False, False)

button = tk.Button(fenster, text="PDF auswählen und kopieren", command=kopiere_mit_zeitstempel_und_aenderungsdatum, height=2, width=30)
button.pack(pady=30)

fenster.mainloop()
