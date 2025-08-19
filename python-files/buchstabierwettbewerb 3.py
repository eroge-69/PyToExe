import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random


class StartBildschirm:
    def __init__(self, master):
        self.master = master
        master.title("Buchstabierwettbewerb - Setup")
        master.geometry("1280x720")
        master.configure(bg="#00FF00")

        self.spieler_namen = []
        self.spieler_entries = []

        tk.Label(master, text="Anzahl Spieler:", font=("Arial", 12), bg="#00FF00").pack(pady=5)
        self.anzahl_var = tk.IntVar(value=2)
        tk.Spinbox(master, from_=2, to=6, textvariable=self.anzahl_var, width=5,
                   command=self.update_spielerfelder).pack()

        # Anzahl Wörter pro Runde
        tk.Label(master, text="Wörter pro Runde (max. 20):", font=("Arial", 12), bg="#00FF00").pack(pady=5)
        self.wortanzahl_var = tk.IntVar(value=10)
        tk.Spinbox(master, from_=1, to=20, textvariable=self.wortanzahl_var, width=5).pack()

        self.frame_spieler = tk.Frame(master, bg="#00FF00")
        self.frame_spieler.pack(pady=10)

        self.update_spielerfelder()

        tk.Button(master, text="Spiel starten", command=self.start_spiel, bg="#00FF00").pack(pady=10)

    def update_spielerfelder(self):
        for widget in self.frame_spieler.winfo_children():
            widget.destroy()
        self.spieler_entries.clear()
        for i in range(self.anzahl_var.get()):
            tk.Label(self.frame_spieler, text=f"Spieler {i+1} Name:", bg="#00FF00").grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(self.frame_spieler)
            entry.insert(0, f"Spieler {i+1}")
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.spieler_entries.append(entry)

    def start_spiel(self):
        self.spieler_namen = [entry.get().strip() for entry in self.spieler_entries]
        if any(not name for name in self.spieler_namen):
            messagebox.showerror("Fehler", "Bitte alle Spielernamen eingeben!")
            return
        wortanzahl = self.wortanzahl_var.get()
        self.master.destroy()
        root = tk.Tk()
        root.geometry("1280x720")
        root.configure(bg="#00FF00")
        BuchstabierWettbewerb(root, self.spieler_namen, wortanzahl)
        root.mainloop()


class BuchstabierWettbewerb:
    def __init__(self, master, spieler_namen, max_worte):
        self.master = master
        master.title("Buchstabierwettbewerb")
        master.configure(bg="#00FF00")

        self.max_worte_pro_runde = max_worte
        self.gespielte_worte = 0

        self.worte = []
        self.shuffle_worte = []
        self.verwendete_worte = []

        self.spieler = spieler_namen
        self.punkte = {spieler: 0 for spieler in self.spieler}
        self.aktueller_spieler_index = 0
        self.aktuelles_wort = None

        # --- Zentrales Layout ---
        self.frame_center = tk.Frame(master, bg="#00FF00")
        self.frame_center.pack(expand=True, fill="both")

        # Wortanzeige groß (100px), mittig
        self.label_wort = tk.Label(self.frame_center, text="", font=("Arial", 100), bg="#00FF00")
        self.label_wort.pack(expand=True)

        # Fortschrittsanzeige (unter dem Wort)
        self.label_fortschritt = tk.Label(master, text="", font=("Arial", 14), bg="#00FF00")
        self.label_fortschritt.pack(pady=5)

        self.progressbar = ttk.Progressbar(master, length=400, maximum=max_worte)
        self.progressbar.pack(pady=5)

        # Scoreboard
        self.score_frame = tk.Frame(master, bg="#00FF00")
        self.score_frame.pack(pady=10)
        tk.Label(self.score_frame, text="Spieler", font=("Arial", 14, "bold"), width=15, anchor="w", bg="#00FF00").grid(row=0, column=0)
        tk.Label(self.score_frame, text="Punkte", font=("Arial", 14, "bold"), width=8, bg="#00FF00").grid(row=0, column=1)

        self.score_labels = {}
        self.name_labels = {}
        for i, name in enumerate(self.spieler, start=1):
            name_label = tk.Label(self.score_frame, text=name, font=("Arial", 14), width=15, anchor="w", bg="#00FF00")
            name_label.grid(row=i, column=0)
            punkte_label = tk.Label(self.score_frame, text="0", font=("Arial", 14), width=8, bg="#00FF00")
            punkte_label.grid(row=i, column=1)
            self.score_labels[name] = punkte_label
            self.name_labels[name] = name_label

        # Datei laden Button
        self.btn_datei = tk.Button(master, text="Wortliste laden", command=self.lade_datei, bg="#00FF00")
        self.btn_datei.pack(pady=5)

        # --- Button-Leiste unten ---
        self.button_frame = tk.Frame(master, bg="#00FF00")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.btn_neues_wort = tk.Button(self.button_frame, text="Neues Wort", command=self.neues_wort, state=tk.DISABLED, bg="#00FF00")
        self.btn_neues_wort.pack(side=tk.LEFT, padx=10)

        self.btn_richtig = tk.Button(self.button_frame, text="Richtig", command=self.punkt_gewinnen, state=tk.DISABLED, bg="#00FF00")
        self.btn_richtig.pack(side=tk.LEFT, padx=10)

        self.btn_falsch = tk.Button(self.button_frame, text="Falsch", command=self.naechster_spieler, state=tk.DISABLED, bg="#00FF00")
        self.btn_falsch.pack(side=tk.LEFT, padx=10)

        self.btn_neustart = tk.Button(self.button_frame, text="Neustart", command=self.neustart, state=tk.DISABLED, bg="#00FF00")
        self.btn_neustart.pack(side=tk.LEFT, padx=10)

        self.highlight_aktueller_spieler()

    def lade_datei(self):
        dateipfad = filedialog.askopenfilename(title="Wortliste wählen", filetypes=[("Textdateien", "*.txt")])
        if dateipfad:
            try:
                with open(dateipfad, "r", encoding="utf-8") as f:
                    self.worte = [zeile.strip() for zeile in f if zeile.strip()]
                zufallsauswahl = min(self.max_worte_pro_runde, len(self.worte))
                self.shuffle_worte = random.sample(self.worte, zufallsauswahl)
                self.verwendete_worte.clear()
                self.gespielte_worte = 0
                self.progressbar["value"] = 0
                self.punkte = {spieler: 0 for spieler in self.spieler}
                self.update_scoreboard()
                self.update_fortschritt()
                self.btn_neues_wort.config(state=tk.NORMAL)
                self.btn_neustart.config(state=tk.NORMAL)
                self.label_wort.config(text="Datei geladen!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")

    def update_scoreboard(self):
        for spieler, punkte in self.punkte.items():
            self.score_labels[spieler].config(text=str(punkte))

    def update_fortschritt(self):
        self.label_fortschritt.config(
            text=f"Wort {self.gespielte_worte} von {self.max_worte_pro_runde}"
        )
        self.progressbar["value"] = self.gespielte_worte

    def highlight_aktueller_spieler(self):
        for name, label in self.name_labels.items():
            label.config(bg="#00FF00")
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.name_labels[aktueller_spieler].config(bg="yellow")

    def neues_wort(self):
        if not self.shuffle_worte:
            self.spiel_ende()
            return
        wort = self.shuffle_worte.pop(0)
        self.aktuelles_wort = wort
        self.verwendete_worte.append(wort)
        self.gespielte_worte += 1
        self.update_fortschritt()
        self.label_wort.config(text=wort)
        self.btn_richtig.config(state=tk.NORMAL)
        self.btn_falsch.config(state=tk.NORMAL)
        self.highlight_aktueller_spieler()

    def punkt_gewinnen(self):
        aktueller_spieler = self.spieler[self.aktueller_spieler_index]
        self.punkte[aktueller_spieler] += 1
        self.update_scoreboard()
        self.naechster_spieler()

    def naechster_spieler(self):
        self.aktueller_spieler_index = (self.aktueller_spieler_index + 1) % len(self.spieler)
        if not self.shuffle_worte:
            self.spiel_ende()
            return
        self.highlight_aktueller_spieler()
        self.btn_richtig.config(state=tk.DISABLED)
        self.btn_falsch.config(state=tk.DISABLED)
        self.label_wort.config(text=f"Nächster: {self.spieler[self.aktueller_spieler_index]}")
        self.master.after(1000, self.neues_wort)

    def spiel_ende(self):
        max_punkte = max(self.punkte.values())
        sieger = [s for s, p in self.punkte.items() if p == max_punkte]
        if len(sieger) > 1:
            nachricht = f"Unentschieden! Sieger: {', '.join(sieger)} mit {max_punkte} Punkten."
        else:
            nachricht = f"Sieger: {sieger[0]} mit {max_punkte} Punkten!"
        messagebox.showinfo("Spiel beendet", nachricht)
        self.label_wort.config(text="Spiel beendet!")
        self.btn_neues_wort.config(state=tk.DISABLED)
        self.btn_richtig.config(state=tk.DISABLED)
        self.btn_falsch.config(state=tk.DISABLED)

    def neustart(self):
        if not self.worte:
            return
        zufallsauswahl = min(self.max_worte_pro_runde, len(self.worte))
        self.shuffle_worte = random.sample(self.worte, zufallsauswahl)
        self.verwendete_worte.clear()
        self.gespielte_worte = 0
        self.progressbar["value"] = 0
        self.update_fortschritt()
        self.punkte = {spieler: 0 for spieler in self.spieler}
        self.update_scoreboard()
        self.aktueller_spieler_index = 0
        self.highlight_aktueller_spieler()
        self.label_wort.config(text="Neuer Durchgang gestartet!")
        self.btn_neues_wort.config(state=tk.NORMAL)
        self.btn_richtig.config(state=tk.DISABLED)
        self.btn_falsch.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1280x720")
    root.configure(bg="#00FF00")
    StartBildschirm(root)
    root.mainloop()
