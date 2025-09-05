import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image, ImageTk

# Dateien
DATEI = "stempelzeiten.json"
PROJEKT_DATEI = "projekte.json"
ICON_DATEI = "logo.png"  # PNG oder JPG

# --- Helper: JSON laden und speichern ---
def lade_daten(datei):
    if os.path.exists(datei):
        with open(datei, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def speichere_daten(datei, daten):
    with open(datei, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)

# --- App ---
class StempelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lugges Zeiterfassung")
        self.root.geometry("800x520")
        self.root.configure(bg="#2b2b2b")

        # --- Header mit Logo ---
        frame_header = tk.Frame(root, bg="#2b2b2b")
        frame_header.pack(fill="x", pady=5)

        self.logo = None
        if os.path.exists(ICON_DATEI):
            try:
                bild = Image.open(ICON_DATEI).resize((60, 60))
                self.logo = ImageTk.PhotoImage(bild)
                tk.Label(frame_header, image=self.logo, bg="#2b2b2b").pack(side="left", padx=10)
            except Exception as e:
                print(f"Logo konnte nicht geladen werden: {e}")

        tk.Label(frame_header, text="Lugges Zeiterfassung", font=("Segoe UI", 16, "bold"),
                 bg="#2b2b2b", fg="white").pack(side="left", padx=10)

        # --- Style ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10,
                        background="#444", foreground="white")
        style.map("TButton",
                  background=[("active", "#666"), ("disabled", "#333")],
                  foreground=[("disabled", "#777")])
        style.configure("Treeview", font=("Segoe UI", 10),
                        background="#3c3f41", foreground="white", fieldbackground="#3c3f41")
        style.map("Treeview", background=[("selected", "#5c5cff")])
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"),
                        background="#2b2b2b", foreground="white")

        # --- Projektwahl ---
        self.projekte = lade_daten(PROJEKT_DATEI)
        if not self.projekte:
            self.projekte = ["Allgemein"]
            speichere_daten(PROJEKT_DATEI, self.projekte)

        self.auswahl_projekt = tk.StringVar(value=self.projekte[0])
        ttk.Label(root, text="Projekt auswählen:", background="#2b2b2b", foreground="white",
                  font=("Segoe UI", 11, "bold")).pack(pady=5)
        self.dropdown = ttk.Combobox(root, textvariable=self.auswahl_projekt,
                                     values=self.projekte, state="readonly", font=("Segoe UI", 11))
        self.dropdown.pack(pady=5)
        ttk.Button(root, text="Projekt hinzufügen", command=self.projekt_hinzufuegen).pack(pady=5)

        # --- Buttons ---
        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(pady=10)
        self.btn_ein = ttk.Button(frame_buttons, text="Einstempeln", command=self.einstempeln)
        self.btn_ein.grid(row=0, column=0, padx=10)
        self.btn_aus = ttk.Button(frame_buttons, text="Ausstempeln", command=self.ausstempeln, state="disabled")
        self.btn_aus.grid(row=0, column=1, padx=10)
        ttk.Button(frame_buttons, text="Export nach CSV", command=self.exportieren).grid(row=0, column=2, padx=10)

        # --- Tabelle ---
        ttk.Label(root, text="Bisherige Stempelungen:", background="#2b2b2b",
                  foreground="white", font=("Segoe UI", 11, "bold")).pack(pady=5)
        self.tree = ttk.Treeview(root, columns=("Projekt", "Aktion", "Zeit", "Pause", "Arbeitszeit"),
                                 show="headings", height=12)
        for col, w in zip(["Projekt","Aktion","Zeit","Pause","Arbeitszeit"], [160,120,160,120,120]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Rechtsklick-Menü
        self.menu = tk.Menu(root, tearoff=0, bg="#444", fg="white", activebackground="#666", activeforeground="white")
        self.menu.add_command(label="Eintrag ändern", command=self.eintrag_aendern)
        self.menu.add_command(label="Eintrag löschen", command=self.eintrag_loeschen)
        self.tree.bind("<Button-3>", self.rechtsklick)

        self.status = tk.Label(root, text="", bg="#2b2b2b", fg="#aaa", anchor="w")
        self.status.pack(fill="x", side="bottom")

        # Daten
        self.stempelzeiten = lade_daten(DATEI)
        self.offener_eintrag = self.pruefe_offenen_eintrag()
        self.lade_tree()

    # --- Projekt hinzufügen ---
    def projekt_hinzufuegen(self):
        neu = simpledialog.askstring("Projekt hinzufügen", "Projektname:")
        if neu and neu not in self.projekte:
            self.projekte.append(neu)
            speichere_daten(PROJEKT_DATEI, self.projekte)
            self.dropdown["values"] = self.projekte
            self.auswahl_projekt.set(neu)



    def pruefe_offenen_eintrag(self):
        for eintrag in self.stempelzeiten:
            # Fallback: wenn Key fehlt, setze auf None
            if "ausstempel" not in eintrag:
                eintrag["ausstempel"] = None
            if eintrag["ausstempel"] is None:
                # offener Eintrag gefunden
                self.btn_ein["state"] = "disabled"
                self.btn_aus["state"] = "normal"
                self.auswahl_projekt.set(eintrag.get("projekt", "Allgemein"))
                return eintrag
        # kein offener Eintrag
        self.btn_ein["state"] = "normal"
        self.btn_aus["state"] = "disabled"
        return None
    # --- Ausstempeln ---
    def ausstempeln(self):
        if not self.offener_eintrag:
            messagebox.showwarning("Fehler", "Kein offener Eintrag zum Ausstempeln.")
            return
        try:
            pause = simpledialog.askinteger("Pause", "Pause in Minuten:", minvalue=0, maxvalue=720)
            if pause is None:
                return
            zeit = datetime.now()
            ein = datetime.fromisoformat(self.offener_eintrag["einstempel"])
            arbeitszeit = (zeit - ein - timedelta(minutes=pause)).total_seconds()/3600
            self.offener_eintrag["ausstempel"] = zeit.isoformat(timespec="seconds")
            self.offener_eintrag["pause_min"] = pause
            self.offener_eintrag["arbeitszeit_h"] = round(arbeitszeit, 2)
            speichere_daten(DATEI, self.stempelzeiten)
            self.offener_eintrag = None
            self.btn_ein["state"] = "normal"
            self.btn_aus["state"] = "disabled"
            self.lade_tree()
            self.status["text"] = f"Ausgestempelt um {zeit.isoformat(timespec='seconds')} (Pause {pause} min)"
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
    # --- Einstempeln ---
    def einstempeln(self):
        projekt = self.auswahl_projekt.get()
        zeit = datetime.now().isoformat(timespec="seconds")
        eintrag = {
            "projekt": projekt,
            "einstempel": zeit,
            "ausstempel": None,
            "pause_min": None,
            "arbeitszeit_h": None
        }
        self.stempelzeiten.append(eintrag)
        speichere_daten(DATEI, self.stempelzeiten)
        self.offener_eintrag = eintrag
        self.btn_ein["state"] = "disabled"
        self.btn_aus["state"] = "normal"
        self.lade_tree()
        self.status["text"] = f"Eingestempelt um {zeit}"
    # --- Treeview laden ---
    def lade_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ein in self.stempelzeiten:
            zeit = ein["einstempel"]
            if ein["ausstempel"]:
                zeit += " → " + ein["ausstempel"]
            self.tree.insert("", "end", values=(ein["projekt"], "Eingestempelt" if ein["ausstempel"] is None else "Abgeschlossen",
                                                zeit,
                                                ein["pause_min"] if ein["pause_min"] is not None else "",
                                                ein["arbeitszeit_h"] if ein["arbeitszeit_h"] is not None else ""))

    # --- Export CSV ---
    def exportieren(self):
        import csv
        with open("stempel_export.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Projekt","Aktion","Zeit","Pause","Arbeitszeit"])
            for ein in self.stempelzeiten:
                zeit = ein["einstempel"]
                if ein["ausstempel"]:
                    zeit += " → " + ein["ausstempel"]
                writer.writerow([ein["projekt"], "Eingestempelt" if ein["ausstempel"] is None else "Abgeschlossen",
                                 zeit,
                                 ein["pause_min"] if ein["pause_min"] else "",
                                 ein["arbeitszeit_h"] if ein["arbeitszeit_h"] else ""])
        self.status["text"] = "Daten nach stempel_export.csv exportiert."

    # --- Rechtsklick ---
    def rechtsklick(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def eintrag_aendern(self):
        iid = self.tree.selection()[0]
        values = self.tree.item(iid)["values"]
        zeit_ein = values[2].split(" → ")[0]
        zeit_aus = values[2].split(" → ")[1] if "→" in values[2] else None

        # Einstempelzeit ändern
        neue_ein = simpledialog.askstring("Einstempelzeit ändern",
                                          f"Aktuelle Einstempelzeit: {zeit_ein}\nNeu (YYYY-MM-DD HH:MM:SS):",
                                          initialvalue=zeit_ein)
        if neue_ein is None:
            return

        neue_aus = zeit_aus
        if zeit_aus:
            # Ausstempelzeit ändern
            neue_aus = simpledialog.askstring("Ausstempelzeit ändern",
                                              f"Aktuelle Ausstempelzeit: {zeit_aus}\nNeu (YYYY-MM-DD HH:MM:SS):",
                                              initialvalue=zeit_aus)
        
        # In JSON suchen und ändern
        for ein in self.stempelzeiten:
            if ein["einstempel"] == zeit_ein:
                ein["einstempel"] = neue_ein
                ein["ausstempel"] = neue_aus
                # Arbeitszeit neu berechnen, nur wenn beide Zeiten vorhanden
                if neue_aus and ein.get("pause_min") is not None:
                    ein_ein_dt = datetime.fromisoformat(neue_ein)
                    ein_aus_dt = datetime.fromisoformat(neue_aus)
                    ein["arbeitszeit_h"] = round((ein_aus_dt - ein_ein_dt - timedelta(minutes=ein["pause_min"])).total_seconds()/3600, 2)
                break

        speichere_daten(DATEI, self.stempelzeiten)
        self.lade_tree()


    def eintrag_loeschen(self):
        iid = self.tree.selection()[0]
        zeit_str = self.tree.item(iid)["values"][2].split(" → ")[0]
        self.stempelzeiten = [ein for ein in self.stempelzeiten if ein["einstempel"] != zeit_str]
        speichere_daten(DATEI, self.stempelzeiten)
        self.lade_tree()

# --- Start ---
if __name__ == "__main__":
    root = tk.Tk()
    app = StempelApp(root)
    root.mainloop()
