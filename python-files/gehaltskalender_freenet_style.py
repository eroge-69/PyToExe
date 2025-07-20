
import tkinter as tk
from tkinter import ttk
import calendar
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATEI = "work_data.json"
FREENET_GRUEN = "#8cc63f"
FREENET_BLAU = "#2c3e50"
HINTERGRUND = "#f2f4f8"

# Datenstruktur laden oder erstellen
if os.path.exists(DATEI):
    with open(DATEI, "r") as f:
        daten = json.load(f)
else:
    daten = {}

class Gehaltskalender:
    def __init__(self, root):
        self.root = root
        self.root.title("freenet Gehaltskalender")
        self.root.configure(bg=HINTERGRUND)
        self.theme = "hell"
        self.arbeitsstunden = 8
        self.tagessatz = 100
        self.monat = datetime.now().month
        self.jahr = datetime.now().year

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=HINTERGRUND, font=("Arial", 10))
        style.configure("TButton", background=FREENET_GRUEN, foreground="white", font=("Arial", 10, "bold"))
        style.configure("TCombobox", padding=5)

        self.frame_top = tk.Frame(self.root, bg=HINTERGRUND)
        self.frame_top.pack()
        self.frame_main = tk.Frame(self.root, bg=HINTERGRUND)
        self.frame_main.pack()

        self.build_settings()
        self.build_header()
        self.build_kalender()
        self.build_stats_tab()

    def build_settings(self):
        einstellungen = tk.LabelFrame(self.frame_top, text="⚙️ Einstellungen", bg=HINTERGRUND, fg=FREENET_BLAU)
        einstellungen.pack(pady=5)

        tk.Label(einstellungen, text="Arbeitsstunden/Tag:", bg=HINTERGRUND).grid(row=0, column=0)
        self.std_entry = tk.Entry(einstellungen, width=5)
        self.std_entry.insert(0, str(self.arbeitsstunden))
        self.std_entry.grid(row=0, column=1)

        tk.Label(einstellungen, text="Standard-Tagessatz (€):", bg=HINTERGRUND).grid(row=0, column=2)
        self.satz_entry = tk.Entry(einstellungen, width=7)
        self.satz_entry.insert(0, str(self.tagessatz))
        self.satz_entry.grid(row=0, column=3)

        self.theme_btn = ttk.Button(einstellungen, text="🌞 Hell/Dunkel", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=4, padx=10)

        ttk.Button(einstellungen, text="🔄 Neu laden", command=self.reload).grid(row=0, column=5)

    def build_header(self):
        header = tk.Frame(self.frame_main, bg=HINTERGRUND)
        header.pack()

        self.lbl_monat = tk.Label(header, text=self.monatsname(), font=("Arial", 14), bg=HINTERGRUND, fg=FREENET_BLAU)
        self.lbl_monat.grid(row=0, column=1, padx=10)

        ttk.Button(header, text="←", command=self.vorheriger_monat).grid(row=0, column=0)
        ttk.Button(header, text="→", command=self.naechster_monat).grid(row=0, column=2)

    def build_kalender(self):
        if hasattr(self, 'kalender_frame'):
            self.kalender_frame.destroy()

        self.kalender_frame = tk.Frame(self.frame_main, bg=HINTERGRUND)
        self.kalender_frame.pack()

        for i, wtag in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
            tk.Label(self.kalender_frame, text=wtag, bg=HINTERGRUND, font=("Arial", 10, "bold")).grid(row=0, column=i)

        month_data = daten.get(f"{self.jahr}-{self.monat:02d}", {})
        cal = calendar.Calendar(firstweekday=0)
        row = 1

        for day, weekday in cal.itermonthdays2(self.jahr, self.monat):
            if day == 0:
                continue
            col = (weekday - 1) % 7
            if col == 6:
                bg = "#e6e6e6"
                state = "disabled"
            else:
                bg = "#ffffff"
                state = "normal"

            frame = tk.LabelFrame(self.kalender_frame, text=f"{day:02d}", bg=bg, padx=5, pady=5, relief=tk.GROOVE)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="n")

            status = ttk.Combobox(frame, values=["arbeit", "frei"], state=state, width=8)
            status.set(month_data.get(str(day), {}).get("status", "frei"))
            status.pack()

            eintrag = tk.Entry(frame, width=10, state=state)
            eintrag.insert(0, str(month_data.get(str(day), {}).get("betrag", self.tagessatz)))
            eintrag.pack()

            self.save_widget(day, status, eintrag)

            if col == 6:
                row += 1

    def build_stats_tab(self):
        self.stats_btn = ttk.Button(self.root, text="📈 Statistik anzeigen", command=self.show_stats)
        self.stats_btn.pack(pady=5)

    def save_widget(self, day, status_widget, entry_widget):
        if not hasattr(self, 'widgets'):
            self.widgets = {}
        self.widgets[day] = (status_widget, entry_widget)

    def monatsname(self):
        return f"{calendar.month_name[self.monat]} {self.jahr}"

    def vorheriger_monat(self):
        if self.monat == 1:
            self.monat = 12
            self.jahr -= 1
        else:
            self.monat -= 1
        self.reload()

    def naechster_monat(self):
        if self.monat == 12:
            self.monat = 1
            self.jahr += 1
        else:
            self.monat += 1
        self.reload()

    def reload(self):
        self.arbeitsstunden = int(self.std_entry.get())
        self.tagessatz = float(self.satz_entry.get())
        self.build_kalender()

    def toggle_theme(self):
        if self.theme == "hell":
            self.root.configure(bg="#1e1e1e")
            self.theme = "dunkel"
        else:
            self.root.configure(bg=HINTERGRUND)
            self.theme = "hell"

    def show_stats(self):
        month_key = f"{self.jahr}-{self.monat:02d}"
        month_data = {}
        if hasattr(self, 'widgets'):
            for tag, (status_widget, betrag_entry) in self.widgets.items():
                status = status_widget.get()
                try:
                    betrag = float(betrag_entry.get())
                except:
                    betrag = 0
                month_data[str(tag)] = {"status": status, "betrag": betrag}
            daten[month_key] = month_data
            with open(DATEI, "w") as f:
                json.dump(daten, f, indent=4)

        tage = sorted(int(k) for k in month_data if month_data[k]["status"] == "arbeit")
        werte = [month_data[str(k)]["betrag"] for k in tage]

        fenster = tk.Toplevel(self.root)
        fenster.title("Statistik")

        fig, ax = plt.subplots(figsize=(6,3))
        ax.bar(tage, werte, color=FREENET_GRUEN)
        ax.set_title("Tagesverdienst")
        ax.set_xlabel("Tag")
        ax.set_ylabel("€")

        canvas = FigureCanvasTkAgg(fig, master=fenster)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = Gehaltskalender(root)
    root.mainloop()
