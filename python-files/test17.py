import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = "ernaehrung_daten.csv"

class ErnaehrungsTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Ernährungs- und Beschwerdetracker")
        self.create_widgets()

        # Menü hinzufügen
        self.create_menu()

    # Menü 
    def create_menu(self):
        menuleiste = tk.Menu(self.root)
        self.root.config(menu=menuleiste)

        # Hilfe-Menü
        hilfe_menu = tk.Menu(menuleiste, tearoff=0)
        hilfe_menu.add_command(label="Hilfe anzeigen", command=self.hilfe_anzeigen)
        menuleiste.add_cascade(label="Hilfe", menu=hilfe_menu)

        # Info-Menü
        info_menu = tk.Menu(menuleiste, tearoff=0)
        info_menu.add_command(label="Info anzeigen", command=self.info_anzeigen)
        menuleiste.add_cascade(label="Info", menu=info_menu)
    
    def hilfe_anzeigen(self):
        hilfe_fenster = tk.Toplevel(self.root)
        hilfe_fenster.title("Hilfe")

        frame = tk.Frame(hilfe_fenster)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        textfeld = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, width=80, height=30)

        hilfetext = """
Hinweise & Hilfe zur Nutzung des Programms:
-------------------------------------------

Der Ernährungs- und Beschwerdetracker soll der besseren Identifikation von
ernährungsbasierten Problemen dienen. Im Fokus liegt dabei die Ermittlung
der Beschwerdeursachen. Als Leitfaden kann hierzu der "Beschwerden-Parameter"
genommen werden; er ist zusammen mit dem Stimmungs- und Stressparameter ein
Pflichtfeld, das aus diesem Grund bei jedem neuen Eintrag ausgefüllt werden 
muss. Liegen somit mehrere Datensätze vor, so kann mittels des Buttons
"Daten anzeigen" eine Visualisierung über den zeitlichen Verlauf vorgenommen
werden. Nun kann bei zunehmenden oder anhaltenden Beschwerden gleichzeitig 
abgeglichen werden, ob womöglich Stress ein begünstigender Faktor für diese
sein könnte. 
    Selbstverständlich lassen sich - sofern ausgefüllt - jetzt auch anhand 
der Zeitpunkte (Datum / Uhrzeit) die gespeicherten Daten der Ernährung
tiefer auswerten, um möglicherweise Zusammenhänge zwischen den Beschwerden 
und der aufgenommenen Nahrung aufzuzeigen.

Tipp: Wenn kein explizites Filter-Datum für die Anzeige eingegeben wird, so
      werden alle gespeicherten Daten abgerufen und angezeigt! 

Was dieses Programm nicht kann:
-------------------------------
Es kann keinen ärztlichen oder ernährungswissenschaftlichen Rat ersetzen. Es
eigent sich jedoch dazu, die aufbereiteten Daten mit Hilfe eines Arztes oder
einer Ernährungsberaterin zu besprechen, um so mögliche Ursache für etwaige
Beschwerden ausfindig zu machen.

Auch ist dieses Programm nicht dazu konzipiert ein explizites Fitnesstracking
zu ermöglichen, da zum aktuellen Zeitpunkt keine Funktionalität zur
Ermittlung der kcal implementiert ist. Änderungen hierzu behalte ich mir vor.
        """
        textfeld.insert("1.0", hilfetext)
        textfeld.config(state="disabled")
        textfeld.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=textfeld.yview)

    def info_anzeigen(self):
        info_fenster = tk.Toplevel(self.root)
        info_fenster.title("Info")

        frame = tk.Frame(info_fenster)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        textfeld = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, width=60, height=15)

        infotext = """Informationen über dieses Programm:

Ernährungs- und Beschwerdetracker
Version: 1.2b
Autor: Daniel Schmäh
Webseite: www.daniel-schmaeh.de
Email: info@daniel-schmaeh.de

Haben Sie Fragen oder Anregungen? 
Kontaktieren Sie mich gern!


Copyright:

Copyright (c) 2025 by Daniel Schmäh Permission is hereby
granted, free of charge, to any person obtaining a copy
of this software and associated documentation files
(the “Software”), to deal in the Software without 
restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the 
following conditions:

The above copyright notice and this permission notice 
shall be included in all copies or substantial portions of
the Software.

The Software is provided “as is”, without warranty of any 
kind, express or implied,including but not limited to the
warranties of merchantability, fitness for a particular
purpose and noninfringement. In no event shall the authors
or copyright holders be liable for any claim, damages or 
other liability, whether in an action of contract,tort or
otherwise, arising from, out of or in connection with the
software or the use or other dealings in the Software.
"""
        textfeld.insert("1.0", infotext)
        textfeld.config(state="disabled")
        textfeld.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=textfeld.yview)

    def create_widgets(self):
        # Datum
        tk.Label(self.root, text="Datum (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(self.root)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="nw")
        
        # Uhrzeit
        tk.Label(self.root, text="Uhrzeit (HH:MM)").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.time_entry = tk.Entry(self.root)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.grid(row=1, column=1, padx=5, pady=5, sticky="nw")

        # Essen Kategorie
        tk.Label(self.root, text="Essenskategorie").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.essen_kategorien = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
        self.essen_var = tk.StringVar()
        self.essen_combo = ttk.Combobox(self.root, textvariable=self.essen_var, values=self.essen_kategorien, state="readonly", width=40)
        self.essen_combo.grid(row=2, column=1, padx=5, pady=5, sticky="nw")

        # Essen Details (kurz)
        tk.Label(self.root, text="Gericht").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.essen_detail = tk.Entry(self.root, width=40)
        self.essen_detail.grid(row=3, column=1, padx=5, pady=5, sticky="nw")

        # Essen Zutaten (mehrzeilig)
        tk.Label(self.root, text="Zutaten + Menge (g) / Portionen").grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        # Frame für Textfeld + Scrollbar
        essen_zutaten_frame = tk.Frame(self.root)
        essen_zutaten_frame.grid(row=4, column=1, padx=5, pady=5, columnspan=3, sticky="nw")
        # Scrollbar
        essen_zutaten_scrollbar = tk.Scrollbar(essen_zutaten_frame)
        essen_zutaten_scrollbar.pack(side="right", fill="y")
        # Textfeld
        self.essen_zutaten = tk.Text(essen_zutaten_frame, width=40, height=4, yscrollcommand=essen_zutaten_scrollbar.set)
        self.essen_zutaten.pack(side="left", fill="both", expand=True)
        # Scrollbar mit Textfeld verbinden
        essen_zutaten_scrollbar.config(command=self.essen_zutaten.yview)

        # Trinken Kategorie
        tk.Label(self.root, text="Trinkkategorie").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.trinken_kategorien = ["Wasser", "Kaffee", "Tee", "Saft", "Softdrink", "Alkohol"]
        self.trinken_var = tk.StringVar()
        self.trinken_combo = ttk.Combobox(self.root, textvariable=self.trinken_var, values=self.trinken_kategorien, state="readonly", width=40)
        self.trinken_combo.grid(row=5, column=1, padx=5, pady=5, sticky="nw")

        # Trinken Details (kurz)
        tk.Label(self.root, text="Getränk").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.trinken_detail = tk.Entry(self.root, width=40)
        self.trinken_detail.grid(row=7, column=1, padx=5, pady=5, sticky="nw")

        # Trinken Zutaten (mehrzeilig)
        tk.Label(self.root, text="Zutaten + Menge (ml)").grid(row=8, column=0, padx=5, pady=5, sticky="ne")
        # Frame für Textfeld + Scrollbar
        trinken_zutaten_frame = tk.Frame(self.root)
        trinken_zutaten_frame.grid(row=8, column=1, padx=5, pady=5, columnspan=3, sticky="nw")
        # Scrollbar
        trinken_zutaten_scrollbar = tk.Scrollbar(trinken_zutaten_frame)
        trinken_zutaten_scrollbar.pack(side="right", fill="y")
        # Textfeld
        self.trinken_zutaten = tk.Text(trinken_zutaten_frame, width=40, height=4, yscrollcommand=trinken_zutaten_scrollbar.set)
        self.trinken_zutaten.pack(side="left", fill="both", expand=True)
        # Scrollbar mit Textfeld verbinden
        trinken_zutaten_scrollbar.config(command=self.trinken_zutaten.yview)

        # Stimmung, Stress, Beschwerden + Beschwerden Details
        tk.Label(self.root, text="Stimmung (1-10)*").grid(row=9, column=0, padx=5, pady=5, sticky="e")
        tk.Label(self.root, text="(1= sehr gut, 10= extrem schlecht)").grid(row=9, column=1, padx=60, pady=5, sticky="w")
        self.stimmung_entry = tk.Entry(self.root, width=5)
        self.stimmung_entry.grid(row=9, column=1, padx=5, pady=5, sticky="nw")

        tk.Label(self.root, text="Stresslevel (1-10)*").grid(row=10, column=0, padx=5, pady=5, sticky="e")
        tk.Label(self.root, text="(1= keinen, 10= extrem)").grid(row=10, column=1, padx=60, pady=5, sticky="w")
        self.stress_entry = tk.Entry(self.root, width=5)
        self.stress_entry.grid(row=10, column=1, padx=5, pady=5,  sticky="nw")

        tk.Label(self.root, text="Beschwerden-Intensität (1-10)*").grid(row=11, column=0, padx=5, pady=5, sticky="e")
        tk.Label(self.root, text="(1= keine, 10= extrem)").grid(row=11, column=1, padx=60, pady=5, sticky="w")
        self.beschwerden_entry = tk.Entry(self.root, width=5)
        self.beschwerden_entry.grid(row=11, column=1, padx=5, pady=5, sticky="nw")

        tk.Label(self.root, text="Beschwerden-Details (Was? Wo?)").grid(row=12, column=0, padx=5, pady=5, sticky="e")
        self.beschwerden_detail = tk.Entry(self.root, width=40)
        self.beschwerden_detail.grid(row=12, column=1, padx=5, pady=5, sticky="nw")

        # Körpergewicht
        tk.Label(self.root, text="Körpergewicht (kg)").grid(row=13, column=0, padx=5, pady=5, sticky="e")
        self.gewicht_entry = tk.Entry(self.root, width=5)
        self.gewicht_entry.grid(row=13, column=1, padx=5, pady=5, sticky="nw")

        # Stuhlkonsistenz
        STUHL_TYPEN = [
            "Typ 1 Einzelne, feste Klümpchen, schwer auszuscheiden",
            "Typ 2 Wurstartig, klumpig",
            "Typ 3 Wurstartig mit rissiger Oberfläche",
            "Typ 4 Wurstartig mit glatter Oberfläche",
            "Typ 5 Einzelne, weiche, glattrandige Klümpchen, leicht auszuscheiden",
            "Typ 6 Einzelne, weiche Klümpchen mit unregelmäßigem Rand",
            "Typ 7 Flüssig, ohne feste Bestandteile"
        ]
        tk.Label(self.root, text="Stuhlkonsistenz").grid(row=14, column=0, padx=5, pady=5, sticky="e")
        self.stuhl_var = tk.StringVar()
        self.stuhl_combo = ttk.Combobox(self.root, textvariable=self.stuhl_var, values=STUHL_TYPEN, state="readonly", width=55)
        self.stuhl_combo.grid(row=14, column=1, padx=5, pady=5, sticky="w")

        # Stuhl Details
        tk.Label(self.root, text="Stuhl Details").grid(row=15, column=0, padx=5, pady=5, sticky="e")
        self.stuhl_detail = tk.Entry(self.root, width=40)
        self.stuhl_detail.grid(row=15, column=1, padx=5, pady=5, sticky="nw")

        # Medikation
        tk.Label(self.root, text="Medikation (Medikament + Dosierung)").grid(row=16, column=0, padx=5, pady=5, sticky="e")
        self.medikation = tk.Entry(self.root, width=40)
        self.medikation.grid(row=16, column=1, padx=5, pady=5, sticky="nw")

        # Buttons
        tk.Button(self.root, text="Eintrag speichern   ", command=self.save_entry).grid(row=19, column=0, columnspan=1, pady=10)
        tk.Button(self.root, text="Felder leeren           ", command=self.clear_fields).grid(row=20, column=1, columnspan=1, pady=10)
        tk.Button(self.root, text="Daten anzeigen      ", command=self.plot_data).grid(row=19, column=1, columnspan=1, pady=10)
        tk.Button(self.root, text="Einträge verwalten", command=self.manage_entries_window).grid(row=20, column=0, columnspan=1, pady=10)
        tk.Button(self.root, text="Datei auswählen     ", command=self.load_file).grid(row=21, column=0, pady=10)

        # Filter für Anzeige
        tk.Label(self.root, text="Filter-Datum für Anzeige (YYYY-MM-DD)").grid(row=17, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_entry = tk.Entry(self.root)
        self.filter_date_entry.grid(row=17, column=1, padx=5, pady=5, sticky="nw")
 
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV-Dateien", "*.csv")])
        if file_path:
            global DATA_FILE
            DATA_FILE = file_path
            messagebox.showinfo("Datei geladen", f"Neue Datei geladen:\n{file_path}")

    def save_entry(self):
        datum = self.date_entry.get()
        gewicht_eingabe = self.gewicht_entry.get().strip()
        vorhandenes_gewicht = None

        # Pflichtfelder prüfen
        if not self.stimmung_entry.get().strip():
            messagebox.showwarning("Pflichtfeld fehlt", "Bitte geben Sie einen Wert für Stimmung (1-10) ein.")
            return
        if not self.stress_entry.get().strip():
            messagebox.showwarning("Pflichtfeld fehlt", "Bitte geben Sie einen Wert für Stresslevel (1-10) ein.")
            return
        if not self.beschwerden_entry.get().strip():
            messagebox.showwarning("Pflichtfeld fehlt", "Bitte geben Sie einen Wert für Beschwerden (1-10) ein.")
            return

        # Gewicht prüfen
        if not gewicht_eingabe:
            if os.path.isfile(DATA_FILE):
                with open(DATA_FILE, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("datum") == datum and row.get("gewicht"):
                            vorhandenes_gewicht = row.get("gewicht")
                            break
            if vorhandenes_gewicht:
                gewicht = vorhandenes_gewicht
            else:
                messagebox.showwarning("Pflichtfeld fehlt", "Bitte geben Sie ein Gewicht ein.")
                return
        else:
            try:
                gewicht = float(gewicht_eingabe)
            except ValueError:
                messagebox.showwarning("Ungültiges Gewicht", "Bitte geben Sie eine gültige Zahl für das Gewicht ein.")
                return

        # Alle Werte auslesen
        daten = {
            "datum": datum,
            "time": self.time_entry.get(),
            "essen_kategorie": self.essen_var.get(),
            "essen_detail": self.essen_detail.get(),
            "essen_zutaten": self.essen_zutaten.get("1.0", tk.END).strip().replace("\n", "; "),
            "trinken_kategorie": self.trinken_var.get(),
            "trinken_detail": self.trinken_detail.get(),
            "trinken_zutaten": self.trinken_zutaten.get("1.0", tk.END).strip().replace("\n", "; "),
            "stimmung": self.stimmung_entry.get(),
            "stress": self.stress_entry.get(),
            "beschwerden": self.beschwerden_entry.get(),
            "beschwerden_detail": self.beschwerden_detail.get(),
            "stuhl_typ": self.stuhl_var.get(),
            "stuhl_detail": self.stuhl_detail.get(),
            "medikation": self.medikation.get(),
            "gewicht": gewicht,
        }

        # Datei schreiben
        file_exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
            fieldnames = list(daten.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(daten)

        messagebox.showinfo("Gespeichert", "Der Eintrag wurde gespeichert.")
        self.clear_fields()

    def clear_fields(self):
        self.essen_var.set("")
        self.essen_detail.delete(0, tk.END)
        self.essen_zutaten.delete("1.0", tk.END)
        self.trinken_var.set("")
        self.trinken_detail.delete(0, tk.END)
        self.trinken_zutaten.delete("1.0", tk.END)
        self.stimmung_entry.delete(0, tk.END)
        self.stress_entry.delete(0, tk.END)
        self.beschwerden_entry.delete(0, tk.END)
        self.beschwerden_detail.delete(0, tk.END)
        self.stuhl_var.set("")
        self.stuhl_detail.delete(0, tk.END)
        self.medikation.delete(0, tk.END)
        self.gewicht_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))

    def plot_data(self):
        filter_datum = self.filter_date_entry.get().strip()

        if not os.path.isfile(DATA_FILE):
            messagebox.showwarning("Keine Datei", "Keine gespeicherte Datei gefunden.")
            return

        # Fenster für Auswahl der Parameter
        options_win = tk.Toplevel(self.root)
        options_win.title("Parameter auswählen")
        options_win.geometry("300x180+800+400")  # Größe und Position anpassen ("BreitexHöhe+X+Y") X: Abstand v. linken Bildschirmrand Y: Abstand oberer Bildschirmrand

        var_stimmung = tk.BooleanVar(value=True)
        var_stress = tk.BooleanVar(value=True)
        var_beschwerden = tk.BooleanVar(value=True)
        var_gewicht = tk.BooleanVar(value=True)
        var_stuhl = tk.BooleanVar(value=True)

        tk.Checkbutton(options_win, text="Stimmung", variable=var_stimmung).pack(anchor="w")
        tk.Checkbutton(options_win, text="Stresslevel", variable=var_stress).pack(anchor="w")
        tk.Checkbutton(options_win, text="Beschwerden", variable=var_beschwerden).pack(anchor="w")
        tk.Checkbutton(options_win, text="Gewicht", variable=var_gewicht).pack(anchor="w")
        tk.Checkbutton(options_win, text="Stuhlkonsistenz", variable=var_stuhl).pack(anchor="w")

        def do_plot():
            selected = {
                "stimmung": var_stimmung.get(),
                "stress": var_stress.get(),
                "beschwerden": var_beschwerden.get(),
                "gewicht": var_gewicht.get(),
                "stuhl": var_stuhl.get(),
            }
            if not any(selected.values()):
                messagebox.showwarning("Auswahl fehlt", "Bitte mindestens einen Parameter auswählen.")
                return

            options_win.destroy()

            times = []
            stimmung = []
            stress = []
            beschwerden = []
            gewicht = []
            stuhl = []
            details = []

            stuhl_mapping = {
            "Typ 1 Einzelne, feste Klümpchen, schwer auszuscheiden": 1,
            "Typ 2 Wurstartig, klumpig": 2,
            "Typ 3 Wurstartig mit rissiger Oberfläche": 3,
            "Typ 4 Wurstartig mit glatter Oberfläche": 4,
            "Typ 5 Einzelne, weiche, glattrandige Klümpchen, leicht auszuscheiden": 5,
            "Typ 6 Einzelne, weiche Klümpchen mit unregelmäßigem Rand": 6,
            "Typ 7 Flüssig, ohne feste Bestandteile": 7,
            }

            with open(DATA_FILE, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if filter_datum and row["datum"] != filter_datum:
                        continue

                    timestamp = f"{row['datum']} {row['time']}"
                    times.append(timestamp)

                    try:
                        stimmung_val = int(row.get("stimmung", 0))
                    except:
                        stimmung_val = 0
                    stimmung.append(stimmung_val)

                    try:
                        stress_val = int(row.get("stress", 0))
                    except:
                        stress_val = 0
                    stress.append(stress_val)

                    try:
                        beschwerden_val = int(row.get("beschwerden", 0))
                    except:
                        beschwerden_val = 0
                    beschwerden.append(beschwerden_val)

                    try:
                        gewicht_val = float(row.get("gewicht", 0))
                    except:
                        gewicht_val = 0
                    gewicht.append(gewicht_val)

                    try:
                        stuhl_beschr = row.get("stuhl_typ", "")
                        # Falls kein gültiger Wert vorhanden ist, setze stuhl_val auf None
                        stuhl_val = stuhl_mapping.get(stuhl_beschr, None)
                    except:
                        stuhl_val = None
                    stuhl.append(stuhl_val)

                    details.append(
                        f"{timestamp}:\n"
                        f"  Essen: {row.get('essen_kategorie', '')} – {row.get('essen_detail', '')}\n"
                        f"  Essen Zutaten: {row.get('essen_zutaten', '')}\n"
                        f"  Trinken: {row.get('trinken_kategorie', '')} – {row.get('trinken_detail', '')}\n"
                        f"  Trinken Zutaten: {row.get('trinken_zutaten', '')}\n"
                        f"  Stimmung: {row.get('stimmung', '')}/10\n"
                        f"  Stresslevel: {row.get('stress', '')}/10\n"
                        f"  Beschwerden-Intensität: {row.get('beschwerden', '')}/10\n"
                        f"  Beschwerden Detail: {row.get('beschwerden_detail', '')}\n"
                        f"  Stuhlkonsistenz: {row.get('stuhl_typ', '')} – {row.get('stuhl_detail', '')}\n"
                        f"  Medikation: {row.get('medikation', '')}\n"
                        f"  Gewicht: {row.get('gewicht', '')} kg\n"
                    )

            if not times:
                messagebox.showinfo("Keine Daten", "Für das gewählte Datum wurden keine Daten gefunden.")
                return

            plt.figure(figsize=(10, 6))
            if selected["stimmung"]:
                plt.plot(times, stimmung, label="Stimmung")
            if selected["stress"]:
                plt.plot(times, stress, label="Stresslevel")
            if selected["beschwerden"]:
                plt.plot(times, beschwerden, label="Beschwerden")
            if selected["gewicht"]:
                plt.plot(times, gewicht, label="Gewicht (kg)")
            if selected["stuhl"]:
                plt.plot(times, stuhl, label="Stuhl-Typ")

            # Beispiel: Maximal 20 Ticks anzeigen
            ax = plt.gca()
            ax.xaxis.set_major_locator(plt.MaxNLocator(10))  # max. 20 Ticks
            # Beispiel: Ende

            # Beispiel: Nur jeden 2 Tick anzeigen
            # ax = plt.gca()
            # ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
            # Beispiel: Ende

            # x-Achsen Ticks Ausrichtung
            plt.xticks(rotation=45, ha="right")

            plt.xlabel("Zeit")
            plt.ylabel("Wert")
            plt.title(f"Parameter für {filter_datum if filter_datum else 'jedes Datum'}")
            plt.legend()
            plt.tight_layout()

            if selected["stuhl"] and not any([selected["stimmung"], selected["stress"], selected["beschwerden"], selected["gewicht"]]):
                stuhl_labels = {
                    1: "1: Feste Klümpchen",
                    2: "2: Wurstartig, klumpig",
                    3: "3: Wurstartig mit rissiger Oberfläche",
                    4: "4: Wurstartig mit glatter Oberfläche",
                    5: "5: Einzelne, glattrandige Klümpchen",
                    6: "6: Einzelne, unregelmäßige Klümpchen",
                    7: "7: Flüssig"
                }
                plt.title(f"Stuhlkonsistenz für {filter_datum if filter_datum else 'jedes Datum'}")

                # Achsenbeschriftung mit Text ersetzen
                plt.yticks(ticks=list(stuhl_labels.keys()), labels=list(stuhl_labels.values()))
                plt.ylabel("Stuhlkonsistenz")
                plt.subplots_adjust(left=0.3)  # 0.3 statt Standard ~0.125
            else:
                plt.ylabel("Wert")

            plt.show()

            # Details anzeigen im Textfenster nur wenn Datum eingegeben wurde
            if filter_datum and details:
                # Details anzeigen im Textfenster
                detail_window = tk.Toplevel(self.root)
                detail_window.title("Details zu Einträgen")

                text = tk.Text(detail_window, width=80, height=20)
                text.pack(padx=10, pady=10)
                text.insert(tk.END, "\n\n".join(details))
                text.config(state=tk.DISABLED)

        tk.Button(options_win, text="Plot anzeigen", command=do_plot).pack(pady=10)


    def manage_entries_window(self):
        if not os.path.isfile(DATA_FILE):
            messagebox.showwarning("Keine Datei", "Keine gespeicherte Datei gefunden.")
            return

        window = tk.Toplevel(self.root)
        window.title("Einträge verwalten")
        window.geometry("900x500")

        filter_label = tk.Label(window, text="Filter Datum (YYYY-MM-DD)")
        filter_label.pack()
        filter_entry = tk.Entry(window)
        filter_entry.pack()

        # Frame für Listbox + Scrollbar
        list_frame = tk.Frame(window)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar erstellen
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox erstellen & Scrollbar verbinden
        listbox = tk.Listbox(list_frame, width=120, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        matching_rows = []

        def load_entries():
            listbox.delete(0, tk.END)
            matching_rows.clear()
            with open(DATA_FILE, mode="r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                filter_text = filter_entry.get().strip()
                for i, row in enumerate(reader):
                    if filter_text and row["datum"] != filter_text:
                        continue
                    display_text = (
                        f"{row['datum']} {row['time']} | "
                        f"Essen: {row.get('essen_kategorie','')} {row.get('essen_detail','')} | "
                        f"Essen Zutaten: {row.get('essen_zutaten','')} | "
                        f"Trinken: {row.get('trinken_kategorie','')} {row.get('trinken_detail','')} | "
                        f"Trinken Zutaten: {row.get('trinken_zutaten','')} | "
                        f"Stimmung: {row.get('stimmung','')} | Stress: {row.get('stress','')} | Beschwerden: {row.get('beschwerden','')}"
                    )
                    listbox.insert(tk.END, display_text)
                    matching_rows.append((i, row))

        def delete_entry():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("Auswahl fehlt", "Bitte einen Eintrag zum Löschen auswählen.")
                return

            index_in_file, _ = matching_rows[selected[0]]

            with open(DATA_FILE, mode="r", encoding="utf-8") as f:
                lines = list(csv.DictReader(f))

            # Letzten Eintrag nicht löschen, da dann die Header-Formatierung der CSV-Datei kaputt ist! Später besser lösen
            if len(lines) <= 1:
                messagebox.showwarning("Nicht erlaubt", "Der letzte Eintrag darf nicht gelöscht werden. Um ihn zu ändern, editiere ihn.")
                return

            del lines[index_in_file]

            with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=lines[0].keys())
                writer.writeheader()
                writer.writerows(lines)

            messagebox.showinfo("Gelöscht", "Eintrag wurde gelöscht.")
            load_entries()


        def edit_entry():
            LABELS = {
                "datum": "Datum (YYYY-MM-DD)",
                "time": "Uhrzeit (HH:MM)",
                "essen_kategorie": "Essen Kategorie",
                "essen_detail": "Gericht",
                "essen_zutaten": "Zutaten + Menge (g) / Portionen",
                "trinken_kategorie": "Trinken Kategorie",
                "trinken_detail": "Getränk",
                "trinken_zutaten": "Zutaten + Menge (ml)",
                "stimmung": "Stimmung (1-10)",
                "stress": "Stress (1-10)",
                "beschwerden": "Beschwerden-Intensität (1-10)",
                "beschwerden_detail": "Beschwerden-Details (Was? Wo?)",
                "stuhl_typ": "Stuhlkonsistenz",
                "stuhl_detail": "Stuhl Details",
                "gewicht": "Körpergewicht (kg)",
                "medikation": "Medikation (Medikament + Dosierung)",
            }

            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("Auswahl fehlt", "Bitte einen Eintrag zum Bearbeiten auswählen.")
                return

            index_in_file, data = matching_rows[selected[0]]

            edit_win = tk.Toplevel(window)
            edit_win.title("Eintrag bearbeiten")

            fields = {}
            row_idx = 0
            for key, value in data.items():
                label_text = LABELS.get(key, key)  # fallback: zeigt key, falls kein Mapping vorhanden
                tk.Label(edit_win, text=label_text).grid(row=row_idx, column=0, sticky="e", padx=5, pady=2)
                if key in ("essen_kategorie", "trinken_kategorie", "stuhl_typ"):
                    if key == "essen_kategorie":
                        combo = ttk.Combobox(edit_win, values=self.essen_kategorien, state="readonly", width=40)
                        combo.set(value)
                        combo.grid(row=row_idx, column=1, padx=5, pady=2)
                        fields[key] = combo
                    elif key == "trinken_kategorie":
                        combo = ttk.Combobox(edit_win, values=self.trinken_kategorien, state="readonly", width=40)
                        combo.set(value)
                        combo.grid(row=row_idx, column=1, padx=5, pady=2)
                        fields[key] = combo
                    elif key == "stuhl_typ":
                        STUHL_TYPEN = [
                            "Typ 1 Einzelne, feste Klümpchen, schwer auszuscheiden",
                            "Typ 2 Wurstartig, klumpig",
                            "Typ 3 Wurstartig mit rissiger Oberfläche",
                            "Typ 4 Wurstartig mit glatter Oberfläche",
                            "Typ 5 Einzelne, weiche, glattrandige Klümpchen, leicht auszuscheiden",
                            "Typ 6 Einzelne, weiche Klümpchen mit unregelmäßigem Rand",
                            "Typ 7 Flüssig, ohne feste Bestandteile"
                        ]
                        combo = ttk.Combobox(edit_win, values=STUHL_TYPEN, state="readonly", width=40)
                        combo.set(value)
                        combo.grid(row=row_idx, column=1, padx=5, pady=2)
                        fields[key] = combo
                elif key in ("essen_zutaten", "trinken_zutaten"):
                    # Frame für Textfeld + Scrollbar
                    text_frame = tk.Frame(edit_win)
                    text_frame.grid(row=row_idx, column=1, padx=5, pady=2)
                    text_widget = tk.Text(text_frame, width=40, height=4, wrap="word")
                    text_widget.insert("1.0", value.replace("; ", "\n"))
                    text_widget.pack(side="left", fill="both", expand=True)
                    scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
                    scrollbar.pack(side="right", fill="y")
                    text_widget.config(yscrollcommand=scrollbar.set)
                    fields[key] = text_widget
                else:
                    entry = tk.Entry(edit_win, width=50)
                    entry.insert(0, value)
                    entry.grid(row=row_idx, column=1, padx=5, pady=2)
                    fields[key] = entry
                row_idx += 1

            def save_changes():
                for key in data.keys():
                    widget = fields.get(key)
                    if isinstance(widget, ttk.Combobox) or isinstance(widget, tk.Entry):
                        data[key] = widget.get()
                    elif isinstance(widget, tk.Text):
                        data[key] = widget.get("1.0", tk.END).strip().replace("\n", "; ")
                    else:
                        data[key] = widget.get()

                with open(DATA_FILE, mode="r", encoding="utf-8") as f:
                    lines = list(csv.DictReader(f))
                    fieldnames = lines[0].keys() if lines else data.keys()

                lines[index_in_file] = data

                with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(lines)

                messagebox.showinfo("Gespeichert", "Eintrag wurde aktualisiert.")
                edit_win.destroy()
                load_entries()

            tk.Button(edit_win, text="Änderungen speichern", command=save_changes).grid(row=row_idx, column=0, columnspan=2, pady=10)

        # Buttons für Verwaltung
        btn_frame = tk.Frame(window)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Einträge laden", command=load_entries).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Ausgewählten Eintrag löschen", command=delete_entry).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Ausgewählten Eintrag bearbeiten", command=edit_entry).grid(row=0, column=2, padx=5)

        load_entries()

if __name__ == "__main__":
    root = tk.Tk()
    app = ErnaehrungsTracker(root)
    root.mainloop()
