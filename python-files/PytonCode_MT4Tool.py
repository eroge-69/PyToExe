import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil

# === Benutzerdefinierte Pfade ===
ZIEL_VERZEICHNIS = r"C:\Users\sysan\Documents\ToolKitMT4Fix\Import"
ZULÄSSIGE_TYPEN = [".html", ".log"]

# === GUI Fenster ===
def importiere_dateien():
    dateien = filedialog.askopenfilenames(title="Wähle MT4-Dateien aus", 
                                          filetypes=[("Alle unterstützten Dateien", "*.html *.log"),
                                                     ("HTML-Dateien", "*.html"),
                                                     ("Log-Dateien", "*.log")])

    if not dateien:
        return

    fehlgeschlagen = []
    erfolgreich = []

    for dateipfad in dateien:
        try:
            dateiname = os.path.basename(dateipfad)
            ziel_pfad = os.path.join(ZIEL_VERZEICHNIS, dateiname)
            shutil.copy2(dateipfad, ziel_pfad)
            erfolgreich.append(dateiname)
        except Exception as e:
            fehlgeschlagen.append((dateiname, str(e)))

    # Rückmeldung anzeigen
    if erfolgreich:
        messagebox.showinfo("Import abgeschlossen", f"Erfolgreich importiert:\n" + "\n".join(erfolgreich))
    if fehlgeschlagen:
        messagebox.showerror("Fehler beim Import", f"Fehlgeschlagen:\n" + "\n".join([f"{f[0]}: {f[1]}" for f in fehlgeschlagen]))

# === Hauptfenster ===
fenster = tk.Tk()
fenster.title("MT4 Logbuch Import Tool")
fenster.geometry("450x250")
fenster.resizable(False, False)

tk.Label(fenster, text="Willkommen beim Logbuch Import Tool", font=("Arial", 14)).pack(pady=20)
tk.Label(fenster, text="Wähle deine MT4 HTML oder LOG Dateien\nund importiere sie in das Logbuch-Verzeichnis.", justify="center").pack(pady=10)

tk.Button(fenster, text="Dateien auswählen und importieren", font=("Arial", 12), command=importiere_dateien).pack(pady=20)

fenster.mainloop()
