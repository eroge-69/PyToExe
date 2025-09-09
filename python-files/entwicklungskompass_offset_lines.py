from pathlib import Path
import os
import json
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- Für die Grafik ---
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure   # << WICHTIG: Figure statt plt verwenden

APP_TITLE = "Entwicklungskompass – Studienverlauf (Semester 1–6)"
LEVELS = [
    ("1: Orientieren & Erkennen", 1),
    ("2: Anwenden & Erproben", 2),
    ("3: Analysieren & Weiterentwickeln", 3),
    ("4: Gestalten & Innovieren", 4),
]

COMPETENCES = [
    "Fachlich-didaktische Kompetenz",
    "Reflexive Kompetenz",
    "Sozial-kommunikative Kompetenz",
    "Gestaltungskompetenz",
    "Entwicklungs- und Innovationskompetenz",
]

SEMESTERS = [1, 2, 3, 4, 5, 6]

SEMESTER_COLORS = {
    1: "#cfe8ff",
    2: "#d1ffd6",
    3: "#fff0c2",
    4: "#ffd6cc",
    5: "#e6d6ff",
    6: "#f2f2f2",
}

def default_data_dir():
    home = Path.home()
    docs = home / "Documents"
    base = docs if docs.exists() else home
    d = base / "Entwicklungskompass"
    d.mkdir(parents=True, exist_ok=True)
    return d

DEFAULT_SAVE_FILE = default_data_dir() / "entwicklungskompass_data.json"


class EntwicklungskompassApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x780")
        self.minsize(900, 640)

        self.data = self._new_empty_data()
        self.current_file = None

        self._build_menu()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

        self._autoload()

    # ---------- Data Model ----------
    def _new_empty_data(self):
        return {
            "person": {
                "Name": "",
                "Matrikelnummer": "",
                "Name PP": "",
                "Name LPS": "",
                "Name Mentor/in": "",
                "Studienbeginn (Jahr)": "",
            },
            "selections": {str(s): {c: None for c in COMPETENCES} for s in SEMESTERS},
            "notes": {c: "" for c in COMPETENCES},
        }

    # ---------- UI ----------
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Neu", command=self.on_new, accelerator="Strg+N")
        file_menu.add_command(label="Öffnen…", command=self.on_open, accelerator="Strg+O")
        file_menu.add_separator()
        file_menu.add_command(label="Speichern", command=self.on_save, accelerator="Strg+S")
        file_menu.add_command(label="Speichern unter…", command=self.on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export als CSV…", command=self.on_export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.on_quit, accelerator="Strg+Q")
        menubar.add_cascade(label="Datei", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Legende / Farben", command=self.show_legend)
        help_menu.add_command(label="Über", command=self.show_about)
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        self.config(menu=menubar)

        self.bind_all("<Control-n>", lambda e: self.on_new())
        self.bind_all("<Control-o>", lambda e: self.on_open())
        self.bind_all("<Control-s>", lambda e: self.on_save())
        self.bind_all("<Control-q>", lambda e: self.on_quit())

    def _build_header(self):
        frm = ttk.LabelFrame(self, text="Stammdaten (aus dem Dokumentkopf)")
        frm.pack(fill="x", padx=12, pady=8)

        labels = [
            "Name", "Matrikelnummer", "Name PP", "Name LPS",
            "Name Mentor/in", "Studienbeginn (Jahr)"
        ]

        self.person_vars = {k: tk.StringVar(value="") for k in labels}

        for i, key in enumerate(labels):
            ttk.Label(frm, text=key + ":").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=8, pady=6)
            ent = ttk.Entry(frm, textvariable=self.person_vars[key], width=35)
            ent.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="we", padx=8, pady=6)

        frm.grid_columnconfigure(1, weight=1)
        frm.grid_columnconfigure(3, weight=1)

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(expand=True, fill="both", padx=12, pady=(0, 8))

        self.semester_vars = {}
        self.semester_frames = {}

        for s in SEMESTERS:
            tab = ttk.Frame(self.nb)
            self.nb.add(tab, text=f"Semester {s}")
            self.semester_frames[s] = tab
            self._build_semester_tab(tab, s)

        self.overview_tab = ttk.Frame(self.nb)
        self.nb.add(self.overview_tab, text="Übersicht / Verlauf")
        self._build_overview_tab(self.overview_tab)

        self.notes_tab = ttk.Frame(self.nb)
        self.nb.add(self.notes_tab, text="Notizen")
        self._build_notes_tab(self.notes_tab)

        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_overview())

    def _build_semester_tab(self, parent, semester):
        hint = ttk.Label(
            parent,
            text=(f"Bitte wählen Sie für JEDE Kompetenz genau eine Stufe für Semester {semester}.\n"
                  "Die markierte Stufe wird farblich gekennzeichnet (Semester-Farbe).")
        )
        hint.pack(anchor="w", padx=8, pady=8)

        canvas = tk.Canvas(parent, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        inner = ttk.Frame(canvas)
        scroll_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")

        canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_configure)

        for i, comp in enumerate(COMPETENCES):
            lf = ttk.LabelFrame(inner, text=comp)
            lf.grid(row=i, column=0, sticky="nsew", padx=8, pady=6)

            var = tk.IntVar(value=0)
            self.semester_vars[(semester, comp)] = var

            for j, (label, value) in enumerate(LEVELS):
                btn = tk.Radiobutton(
                    lf, text=label, variable=var, value=value,
                    indicatoron=False, width=30, relief="raised", bd=2,
                    selectcolor=SEMESTER_COLORS[semester],
                    padx=8, pady=8, justify="left", anchor="w"
                )
                btn.grid(row=0, column=j, padx=6, pady=6, sticky="ew")

            for c in range(len(LEVELS)):
                lf.grid_columnconfigure(c, weight=1)

        inner.grid_columnconfigure(0, weight=1)

    def _build_overview_tab(self, parent):
        # Tabelle
        self.overview_tree = ttk.Treeview(parent, columns=[f"S{s}" for s in SEMESTERS],
                                          show="headings", height=12)
        for s in SEMESTERS:
            self.overview_tree.heading(f"S{s}", text=f"Sem {s}")
            self.overview_tree.column(f"S{s}", width=90, anchor="center")
        self.overview_tree.pack(fill="x", expand=False, padx=8, pady=8)

        for s in SEMESTERS:
            self.overview_tree.tag_configure(f"sem{s}", background=SEMESTER_COLORS[s])

        # --- Grafik stabil einbinden ---
        self.fig = Figure(figsize=(7, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Semester")
        self.ax.set_ylabel("Stufe")
        self.ax.set_xticks(SEMESTERS)
        self.ax.set_yticks([1, 2, 3, 4])
        self.ax.set_ylim(0.8, 4.2)
        self.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_plot.draw()  # << WICHTIG
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        self.refresh_overview()

    def _build_notes_tab(self, parent):
        self.notes_texts = {}
        for i, comp in enumerate(COMPETENCES):
            lf = ttk.LabelFrame(parent, text=f"Notizen/Ergänzungen – {comp}")
            lf.pack(fill="both", expand=True, padx=8, pady=6)
            txt = tk.Text(lf, height=4, wrap="word")
            txt.pack(fill="both", expand=True, padx=6, pady=6)
            self.notes_texts[comp] = txt

    # ---------- Übersicht ----------
    
    def refresh_overview(self):
        # Tabelle aktualisieren
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)

        for comp in COMPETENCES:
            row_vals = []
            tags = []
            for s in SEMESTERS:
                level = self.semester_vars[(s, comp)].get()
                label = next((lbl for (lbl, val) in LEVELS if val == level), "")
                short = label.split(":")[0] if label else ""
                row_vals.append(short)
                tags.append(f"sem{s}" if level else "")
            item_id = self.overview_tree.insert("", "end", values=row_vals)
            if any(tags):
                last_tag = [t for t in tags if t][-1]
                self.overview_tree.item(item_id, tags=(last_tag,))

        # Grafik aktualisieren (Linien mit X-Versatz, damit sie sich nicht überdecken)
        self.ax.clear()
        self.ax.set_xlabel("Semester")
        self.ax.set_ylabel("Stufe")
        self.ax.set_xticks(SEMESTERS)
        self.ax.set_yticks([1, 2, 3, 4])
        self.ax.set_ylim(0.8, 4.2)
        self.ax.grid(True, linestyle="--", alpha=0.6)

        import numpy as np
        x = np.array(SEMESTERS, dtype=float)
        n = len(COMPETENCES)
        offset_step = 0.08  # Horizontaler Versatz zwischen Linien

        for i, comp in enumerate(COMPETENCES):
            y_vals = []
            for s in SEMESTERS:
                val = self.semester_vars[(s, comp)].get()
                y_vals.append(val if val else None)
            if any(y_vals):
                x_offset = x + (i - n/2) * offset_step
                self.ax.plot(x_offset, y_vals, marker="o", label=comp)

        self.ax.legend(fontsize=8)
        self.canvas_plot.draw()


    # ---------- Status ----------
    def _build_statusbar(self):
        self.status = tk.StringVar(value="Bereit.")
        bar = ttk.Label(self, textvariable=self.status, anchor="w")
        bar.pack(fill="x", padx=12, pady=(0, 8))

    # ---------- Data IO ----------
    def collect_data_from_ui(self):
        for k, var in self.person_vars.items():
            self.data["person"][k] = var.get().strip()
        for comp, txt in self.notes_texts.items():
            self.data["notes"][comp] = txt.get("1.0", "end-1c")
        for s in SEMESTERS:
            for comp in COMPETENCES:
                val = self.semester_vars[(s, comp)].get()
                self.data["selections"][str(s)][comp] = int(val) if val else None

    def populate_ui_from_data(self):
        for k, var in self.person_vars.items():
            var.set(self.data["person"].get(k, ""))
        for comp, txt in self.notes_texts.items():
            txt.delete("1.0", "end")
            txt.insert("1.0", self.data["notes"].get(comp, ""))
        for s in SEMESTERS:
            for comp in COMPETENCES:
                val = self.data["selections"].get(str(s), {}).get(comp)
                self.semester_vars[(s, comp)].set(val if val in [1,2,3,4] else 0)
        self.refresh_overview()

    def _autoload(self):
        try:
            if DEFAULT_SAVE_FILE.exists():
                with open(DEFAULT_SAVE_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.populate_ui_from_data()
                self.current_file = DEFAULT_SAVE_FILE
                self._set_status(f"Automatisch geladen: {self.current_file}")
        except Exception as e:
            self._set_status(f"Autoladen fehlgeschlagen: {e}")

    def on_new(self):
        if not self._confirm_discard_changes():
            return
        self.data = self._new_empty_data()
        self.populate_ui_from_data()
        self.current_file = None
        self._set_status("Neues Dokument.")

    def on_open(self):
        if not self._confirm_discard_changes():
            return
        f = filedialog.askopenfilename(
            title="Öffnen",
            filetypes=[("JSON-Datei", "*.json"), ("Alle Dateien", "*.*")]
        )
        if not f:
            return
        try:
            with open(f, "r", encoding="utf-8") as fh:
                self.data = json.load(fh)
            self.populate_ui_from_data()
            self.current_file = Path(f)
            self._set_status(f"Geladen: {f}")
        except Exception as e:
            messagebox.showerror("Fehler beim Öffnen", str(e))

    def on_save(self, save_as_path: Path = None):
        self.collect_data_from_ui()
        path = save_as_path or self.current_file or DEFAULT_SAVE_FILE
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, ensure_ascii=False, indent=2)
            self.current_file = path
            self._set_status(f"Gespeichert: {path}")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

    def on_save_as(self):
        f = filedialog.asksaveasfilename(
            title="Speichern unter",
            defaultextension=".json",
            filetypes=[("JSON-Datei", "*.json")],
            initialfile="entwicklungskompass_data.json"
        )
        if not f:
            return
        self.on_save(Path(f))

    def on_export_csv(self):
        self.collect_data_from_ui()
        f = filedialog.asksaveasfilename(
            title="Export als CSV",
            defaultextension=".csv",
            filetypes=[("CSV-Datei", "*.csv")],
            initialfile="entwicklungskompass_export.csv"
        )
        if not f:
            return
        try:
            with open(f, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh, delimiter=";")
                writer.writerow(["Feld", "Wert"])
                for k, v in self.data["person"].items():
                    writer.writerow([k, v])
                writer.writerow([])
                writer.writerow(["Kompetenz"] + [f"Sem {s}" for s in SEMESTERS])
                for comp in COMPETENCES:
                    row = [comp]
                    for s in SEMESTERS:
                        val = self.data["selections"][str(s)][comp]
                        label = next((lbl for (lbl, v) in LEVELS if v == val), "")
                        row.append(label)
                    writer.writerow(row)
                writer.writerow([])
                writer.writerow(["Notizen/Ergänzungen"])
                for comp in COMPETENCES:
                    writer.writerow([comp])
                    writer.writerow([self.data["notes"][comp]])
                    writer.writerow([])
            self._set_status(f"CSV exportiert: {f}")
        except Exception as e:
            messagebox.showerror("Fehler beim Export", str(e))

    def on_quit(self):
        if not self._confirm_discard_changes():
            return
        self.destroy()

    def _confirm_discard_changes(self):
        return messagebox.askyesno("Fortfahren?", "Ungespeicherte Änderungen können verloren gehen. Fortfahren?")

    def _set_status(self, text):
        self.status.set(text)

    def show_legend(self):
        legend = "\n".join([f"Semester {s}: {SEMESTER_COLORS[s]}" for s in SEMESTERS])
        messagebox.showinfo("Farb-Legende", f"Jedes Semester hat seine Farbe:\n\n{legend}\n\n"
                                            "In den Semester-Reitern sind ausgewählte Stufen mit der jeweiligen Semesterfarbe hinterlegt.\n"
                                            "Die Übersicht fasst die Auswahl je Kompetenz zusammen.\n"
                                            "Zusätzlich wird der Verlauf in einer Grafik dargestellt.")

    def show_about(self):
        messagebox.showinfo("Über", f"{APP_TITLE}\n\n"
                                    "Dieses Tool ermöglicht die semestergenaue Markierung der Stufen je Kompetenz.\n"
                                    "Daten werden als JSON gespeichert und können als CSV exportiert werden.\n"
                                    "In der Übersicht wird eine Tabelle UND eine Verlaufsgrafik angezeigt.\n"
                                    "Erstellt für Windows (.exe) via PyInstaller.\n")


def main():
    app = EntwicklungskompassApp()
    app.mainloop()


if __name__ == "__main__":
    main()
