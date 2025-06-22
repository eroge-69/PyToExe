import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

DATEINAME = "werkzeuge.csv"

FELDER = [
    "Schublade", "Werkzeugnummer", "Typ", "Bezeichnung/Geometrie",
    "Durchmesser", "Eckenradius", "Zähnezahl", "Schneidstoff",
    "Beschichtung", "Artikelnummer", "Lieferant", "Ist-Bestand", "Mindestbestand"
]

# Startdaten, falls Datei noch nicht existiert
STARTWERKZEUGE = [
    [1, 1, "Wendeplatte", "CNMG 120416", "", 0.8, "", "HM", "HB7035-1", "250328 HB7035-1", "GARANT", 12, 4],
    [3, 2, "Bohrer", "Spiralbohrer HSS N", 15.25, "", "", "HSS", "unbeschichtet", "114150", "", 8, 2],
    [5, 3, "Fräser", "GARANT Master Steel PickPocket", 14, "", 3, "VHM", "", "202404", "GARANT", 5, 2]
]

def lade_werkzeuge():
    if os.path.isfile(DATEINAME):
        df = pd.read_csv(DATEINAME, dtype=str)
        df[FELDER[0]] = df[FELDER[0]].astype(int)  # Schublade als int
        df[FELDER[11]] = df[FELDER[11]].astype(int) # Ist-Bestand als int
        df[FELDER[12]] = df[FELDER[12]].astype(int) # Mindestbestand als int
        return df
    else:
        df = pd.DataFrame(STARTWERKZEUGE, columns=FELDER)
        df.to_csv(DATEINAME, index=False)
        return df

def speichere_werkzeuge(df):
    df.to_csv(DATEINAME, index=False)

class WerkzeugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Werkzeugverwaltung")
        self.df = lade_werkzeuge()

        # Schubladen-Filter
        filter_frame = tk.Frame(root)
        filter_frame.pack(pady=5)
        tk.Label(filter_frame, text="Schublade:").pack(side="left")
        self.schubladen_wert = tk.StringVar()
        self.schubladen_combo = ttk.Combobox(filter_frame, textvariable=self.schubladen_wert, width=5)
        self.schubladen_combo['values'] = ["Alle"] + sorted(self.df["Schublade"].unique(), key=lambda x: int(x))
        self.schubladen_combo.current(0)
        self.schubladen_combo.pack(side="left")
        tk.Button(filter_frame, text="Filtern", command=self.zeige_werkzeuge).pack(side="left", padx=8)

        # Tabelle
        self.tree = ttk.Treeview(root, columns=FELDER, show="headings")
        for col in FELDER:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col != "Bezeichnung/Geometrie" else 180)
        self.tree.pack(pady=5, fill="x")

        # +1/-1 Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=3)
        tk.Button(btn_frame, text="+1", command=self.bestand_plus).pack(side="left", padx=5)
        tk.Button(btn_frame, text="-1", command=self.bestand_minus).pack(side="left", padx=5)

        # Neueingabe
        add_frame = tk.LabelFrame(root, text="Neues Werkzeug hinzufügen")
        add_frame.pack(fill="x", padx=5, pady=7)
        self.eingabefelder = {}
        for i, feld in enumerate(FELDER):
            tk.Label(add_frame, text=feld, anchor="w").grid(row=0, column=i)
            entry = tk.Entry(add_frame, width=10)
            entry.grid(row=1, column=i)
            self.eingabefelder[feld] = entry
        tk.Button(add_frame, text="Hinzufügen", command=self.werkzeug_hinzufuegen).grid(row=2, column=len(FELDER)-2, columnspan=2, pady=4)

        self.zeige_werkzeuge()

    def zeige_werkzeuge(self):
        # Filter anwenden
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.schubladen_wert.get() and self.schubladen_wert.get() != "Alle":
            df = self.df[self.df["Schublade"] == int(self.schubladen_wert.get())]
        else:
            df = self.df
        for _, zeile in df.iterrows():
            farbe = ""
            try:
                if int(zeile["Ist-Bestand"]) <= int(zeile["Mindestbestand"]):
                    farbe = "#ff8888"
            except:
                pass
            self.tree.insert("", "end", values=[zeile[f] for f in FELDER], tags=("warnung",) if farbe else ())
            if farbe:
                self.tree.tag_configure("warnung", background=farbe)

    def bestand_plus(self):
        self._bestand_aendern(+1)

    def bestand_minus(self):
        self._bestand_aendern(-1)

    def _bestand_aendern(self, diff):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Hinweis", "Bitte ein Werkzeug in der Tabelle auswählen!")
            return
        index = self.tree.index(selected[0])
        df = self.df if self.schubladen_wert.get() == "Alle" or not self.schubladen_wert.get() else self.df[self.df["Schublade"] == int(self.schubladen_wert.get())]
        werkzeug = df.iloc[index]
        w_nummer = werkzeug["Werkzeugnummer"]
        row_idx = self.df.index[self.df["Werkzeugnummer"] == w_nummer].tolist()[0]
        # Bestand ändern
        ist_b = int(self.df.at[row_idx, "Ist-Bestand"])
        min_b = int(self.df.at[row_idx, "Mindestbestand"])
        if diff == -1 and ist_b == 0:
            return
        self.df.at[row_idx, "Ist-Bestand"] = ist_b + diff
        speichere_werkzeuge(self.df)
        if self.df.at[row_idx, "Ist-Bestand"] <= min_b:
            messagebox.showwarning("Achtung", "Mindestbestand erreicht oder unterschritten!")
        self.zeige_werkzeuge()

    def werkzeug_hinzufuegen(self):
        daten = {}
        for feld, entry in self.eingabefelder.items():
            daten[feld] = entry.get()
        # Prüfen & in DataFrame einfügen
        if not daten["Werkzeugnummer"]:
            messagebox.showinfo("Fehler", "Werkzeugnummer darf nicht leer sein.")
            return
        try:
            daten["Schublade"] = int(daten["Schublade"])
            daten["Ist-Bestand"] = int(daten["Ist-Bestand"])
            daten["Mindestbestand"] = int(daten["Mindestbestand"])
        except:
            messagebox.showinfo("Fehler", "Schublade, Ist-Bestand und Mindestbestand müssen Zahlen sein!")
            return
        self.df = self.df.append(daten, ignore_index=True)
        speichere_werkzeuge(self.df)
        self.zeige_werkzeuge()
        for entry in self.eingabefelder.values():
            entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = WerkzeugApp(root)
    root.mainloop()
