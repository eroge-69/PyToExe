#!/usr/bin/env python3
# SchoolBuddy - a simple study hub for Windows (.exe ready via PyInstaller)
# Single-file Tkinter app: Notes, Tasks, Timetable, Flashcards, Pomodoro, Shortcuts
# Data is saved under %APPDATA%\SchoolBuddy\
import os, sys, json, time, csv, webbrowser, datetime, threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "SchoolBuddy"
APP_VERSION = "1.0"
DATA_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / APP_NAME
NOTES_DIR = DATA_DIR / "notes"
DECKS_DIR = DATA_DIR / "decks"
FILES_JSON = DATA_DIR / "data.json"

def ensure_dirs():
    for p in [DATA_DIR, NOTES_DIR, DECKS_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    if not FILES_JSON.exists():
        save_data({"tasks": [], "timetable": {}, "shortcuts": []})

def load_data():
    try:
        with open(FILES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": [], "timetable": {}, "shortcuts": []}

def save_data(obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(FILES_JSON, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def human_date(d):
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return d

class Dashboard(ttk.Frame):
    def __init__(self, master, state):
        super().__init__(master)
        self.state = state
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=f"{APP_NAME} {APP_VERSION}", font=("Segoe UI", 16, "bold")).grid(sticky="w", padx=12, pady=(12,0))
        self.date_lbl = ttk.Label(self, font=("Segoe UI", 11))
        self.date_lbl.grid(sticky="w", padx=12)
        ttk.Separator(self, orient="horizontal").grid(sticky="ew", padx=12, pady=6)
        ttk.Label(self, text="À faire bientôt", font=("Segoe UI", 12, "bold")).grid(sticky="w", padx=12)
        self.tasks_box = tk.Listbox(self, height=8)
        self.tasks_box.grid(sticky="nsew", padx=12, pady=(0,12))
        self.rowconfigure(3, weight=1)
        ttk.Label(self, text="Prochain cours (emploi du temps)", font=("Segoe UI", 12, "bold")).grid(sticky="w", padx=12)
        self.next_class_lbl = ttk.Label(self, text="—")
        self.next_class_lbl.grid(sticky="w", padx=12, pady=(0,12))
        self.refresh()
        self.after(60_000, self.refresh)  # refresh every minute

    def refresh(self):
        today = datetime.date.today()
        now = datetime.datetime.now().strftime("%H:%M")
        self.date_lbl.config(text=f"Nous sommes le {today.strftime('%A %d %B %Y')} • {now}")
        # Upcoming tasks: sort by due date
        tasks = [t for t in self.state["tasks"] if not t.get("done")]
        def key(t):
            try:
                return datetime.datetime.strptime(t.get("due","9999-12-31"), "%Y-%m-%d")
            except Exception:
                return datetime.datetime(9999,12,31)
        tasks.sort(key=key)
        self.tasks_box.delete(0, tk.END)
        for t in tasks[:10]:
            due = human_date(t.get("due",""))
            subj = t.get("subject","")
            self.tasks_box.insert(tk.END, f"• {t.get('title','(sans titre)')} [{subj}] – {due}")
        # Next class (simple inference from timetable like 'HH:MM-HH:MM|Matière')
        today_key = today.strftime("%A")  # e.g., 'Monday' in English; we will support both
        # Normalize keys to French names if needed
        keys = list(self.state.get("timetable", {}).keys())
        # find today's entries
        entries = self.state.get("timetable", {}).get(today_key) or self.state.get("timetable", {}).get(self.to_en(today_key)) or []
        nxt = "—"
        now_minutes = today.hour * 60 + datetime.datetime.now().minute
        for s in entries:
            try:
                timepart, name = s.split("|", 1)
                start, end = timepart.split("-", 1)
                sm, em = self._to_minutes(start), self._to_minutes(end)
                if sm >= now_minutes:
                    nxt = f"{start}-{end} : {name.strip()}"
                    break
            except Exception:
                continue
        self.next_class_lbl.config(text=nxt)

    def _to_minutes(self, hhmm):
        h, m = hhmm.strip().split(":")
        return int(h)*60+int(m)

    def to_en(self, fr):
        # crude map French to English day names used by Python
        m = {"Lundi":"Monday","Mardi":"Tuesday","Mercredi":"Wednesday","Jeudi":"Thursday","Vendredi":"Friday","Samedi":"Saturday","Dimanche":"Sunday"}
        return m.get(fr, fr)

class NotesTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.notes_list = tk.Listbox(self, width=28)
        self.notes_list.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=8, pady=8)
        self.notes_list.bind("<<ListboxSelect>>", self.load_selected)
        btns = ttk.Frame(self)
        btns.grid(row=1, column=0, sticky="sw", padx=8, pady=(0,8))
        ttk.Button(btns, text="Nouveau", command=self.new_note).grid(row=0, column=0, padx=2)
        ttk.Button(btns, text="Renommer", command=self.rename_note).grid(row=0, column=1, padx=2)
        ttk.Button(btns, text="Supprimer", command=self.delete_note).grid(row=0, column=2, padx=2)
        self.text = tk.Text(self, wrap="word")
        self.text.grid(row=0, column=1, sticky="nsew", padx=(0,8), pady=8)
        self.text.bind("<KeyRelease>", lambda e: self.save_current())
        self.refresh_list()

    def refresh_list(self):
        self.notes_list.delete(0, tk.END)
        for f in sorted(NOTES_DIR.glob("*.txt")):
            self.notes_list.insert(tk.END, f.stem)
        if self.notes_list.size() and not self.text.get("1.0","end-1c"):
            self.notes_list.selection_set(0)
            self.load_selected()

    def selected_path(self):
        sel = self.notes_list.curselection()
        if not sel: return None
        name = self.notes_list.get(sel[0]) + ".txt"
        return NOTES_DIR / name

    def load_selected(self, *args):
        p = self.selected_path()
        if not p or not p.exists(): return
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)

    def save_current(self):
        p = self.selected_path()
        if not p: return
        with open(p, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0","end-1c"))

    def new_note(self):
        name = simple_prompt("Nom du fichier (sans .txt):", "nouvelle_note")
        if not name: return
        p = NOTES_DIR / f"{name}.txt"
        if p.exists():
            messagebox.showerror("Existe déjà", "Un fichier avec ce nom existe déjà.")
            return
        with open(p, "w", encoding="utf-8") as f:
            f.write("")
        self.refresh_list()

    def rename_note(self):
        p = self.selected_path()
        if not p: return
        name = simple_prompt("Nouveau nom:", p.stem)
        if not name: return
        newp = NOTES_DIR / f"{name}.txt"
        if newp.exists():
            messagebox.showerror("Existe déjà", "Un fichier avec ce nom existe déjà.")
            return
        p.rename(newp)
        self.refresh_list()

    def delete_note(self):
        p = self.selected_path()
        if not p: return
        if messagebox.askyesno("Confirmer", "Supprimer cette note ?"):
            try: p.unlink()
            except Exception as e: messagebox.showerror("Erreur", str(e))
            self.refresh_list()

class TasksTab(ttk.Frame):
    def __init__(self, master, state):
        super().__init__(master)
        self.state = state
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        cols = ("title","subject","due","priority","done")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for c, w in zip(cols, (220,120,100,80,60)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(sticky="nsew", padx=8, pady=8)
        btns = ttk.Frame(self)
        btns.grid(sticky="ew", padx=8, pady=(0,8))
        for i, (label, cmd) in enumerate([("Ajouter", self.add), ("Modifier", self.edit), ("Terminé", self.toggle_done), ("Supprimer", self.delete)]):
            ttk.Button(btns, text=label, command=cmd).grid(row=0, column=i, padx=4)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        tasks = list(self.state["tasks"])
        def k(t):
            try: return datetime.datetime.strptime(t.get("due","9999-12-31"), "%Y-%m-%d")
            except: return datetime.datetime(9999,12,31)
        for t in sorted(tasks, key=k):
            self.tree.insert("", tk.END, values=(t.get("title",""), t.get("subject",""), human_date(t.get("due","")), t.get("priority",""), "Oui" if t.get("done") else "Non"))

    def _selected_index(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.index(sel[0])
        return item

    def _edit_dialog(self, task=None):
        win = tk.Toplevel(self)
        win.title("Tâche")
        win.grab_set()
        entries = {}
        fields = [("Titre","title"),("Matière","subject"),("Échéance (YYYY-MM-DD)","due"),("Priorité (1-5)","priority")]
        for r,(lbl,key) in enumerate(fields):
            ttk.Label(win, text=lbl).grid(row=r, column=0, sticky="e", padx=6, pady=4)
            e = ttk.Entry(win, width=30)
            e.grid(row=r, column=1, padx=6, pady=4)
            entries[key] = e
        var_done = tk.BooleanVar(value=bool(task.get("done")) if task else False)
        chk = ttk.Checkbutton(win, text="Terminé", variable=var_done)
        chk.grid(row=len(fields), column=1, sticky="w", padx=6, pady=4)
        if task:
            for _,key in fields:
                entries[key].insert(0, task.get(key,""))
        res = {}
        def ok():
            for _,key in fields:
                res[key] = entries[key].get().strip()
            res["done"] = var_done.get()
            win.destroy()
        ttk.Button(win, text="OK", command=ok).grid(row=len(fields)+1, column=1, sticky="e", padx=6, pady=8)
        win.wait_window()
        return res if res else None

    def add(self):
        t = self._edit_dialog({})
        if not t: return
        self.state["tasks"].append(t)
        save_data(self.state)
        self.refresh()

    def edit(self):
        idx = self._selected_index()
        if idx is None: return
        t = self._edit_dialog(self.state["tasks"][idx])
        if not t: return
        self.state["tasks"][idx] = t
        save_data(self.state)
        self.refresh()

    def toggle_done(self):
        idx = self._selected_index()
        if idx is None: return
        self.state["tasks"][idx]["done"] = not self.state["tasks"][idx].get("done")
        save_data(self.state)
        self.refresh()

    def delete(self):
        idx = self._selected_index()
        if idx is None: return
        del self.state["tasks"][idx]
        save_data(self.state)
        self.refresh()

class TimetableTab(ttk.Frame):
    DAYS = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
    def __init__(self, master, state):
        super().__init__(master)
        self.state = state
        self.entries = {}
        ttk.Label(self, text="Format cellule: HH:MM-HH:MM|Matière (ex: 08:00-09:00|Maths)", foreground="#444").grid(row=0, column=0, columnspan=7, sticky="w", padx=8, pady=(8,0))
        for c, day in enumerate(self.DAYS):
            ttk.Label(self, text=day, font=("Segoe UI", 10, "bold")).grid(row=1, column=c, padx=6, pady=6)
        for r in range(8):  # 8 lines
            for c, day in enumerate(self.DAYS):
                e = tk.Entry(self, width=22)
                e.grid(row=r+2, column=c, padx=4, pady=4)
                self.entries[(day,r)] = e
        ttk.Button(self, text="Enregistrer", command=self.save).grid(row=20, column=6, sticky="e", padx=8, pady=8)
        self.load()

    def load(self):
        t = self.state.get("timetable", {})
        for day in self.DAYS:
            rows = t.get(day, [])
            for r, val in enumerate(rows[:8]):
                self.entries[(day,r)].insert(0, val)

    def save(self):
        t = {}
        for day in self.DAYS:
            rows = []
            for r in range(8):
                val = self.entries[(day,r)].get().strip()
                if val: rows.append(val)
            t[day] = rows
        self.state["timetable"] = t
        save_data(self.state)
        messagebox.showinfo("OK", "Emploi du temps enregistré.")

class FlashcardsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.deck = []
        self.index = 0
        self.quiz_mode = False
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ttk.Button(bar, text="Nouveau", command=self.new_deck).grid(row=0, column=0, padx=2)
        ttk.Button(bar, text="Ouvrir CSV", command=self.open_csv).grid(row=0, column=1, padx=2)
        ttk.Button(bar, text="Enregistrer CSV", command=self.save_csv).grid(row=0, column=2, padx=2)
        ttk.Button(bar, text="Ajouter", command=self.add_card).grid(row=0, column=3, padx=2)

        self.q = tk.Text(self, height=6, wrap="word")
        self.a = tk.Text(self, height=6, wrap="word")
        self.q.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,4))
        self.a.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0,8))

        nav = ttk.Frame(self)
        nav.grid(row=3, column=0, sticky="ew", padx=8, pady=(0,8))
        ttk.Button(nav, text="Précédent", command=self.prev_card).grid(row=0, column=0, padx=2)
        ttk.Button(nav, text="Suivant", command=self.next_card).grid(row=0, column=1, padx=2)
        ttk.Button(nav, text="Mode Quiz", command=self.toggle_quiz).grid(row=0, column=2, padx=2)
        self.status = ttk.Label(nav, text="0/0")
        self.status.grid(row=0, column=3, padx=6)

    def new_deck(self):
        self.deck = []
        self.index = 0
        self.render()

    def open_csv(self):
        f = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
        if not f: return
        with open(f, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            self.deck = [(r[0], r[1] if len(r)>1 else "") for r in reader]
        self.index = 0
        self.render()

    def save_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not f: return
        with open(f, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for q, a in self.deck: writer.writerow([q, a])
        messagebox.showinfo("OK", "Deck enregistré.")

    def add_card(self):
        q = self.q.get("1.0", "end-1c").strip()
        a = self.a.get("1.0", "end-1c").strip()
        if not q: return
        self.deck.append((q, a))
        self.index = len(self.deck)-1
        self.render()

    def render(self):
        total = len(self.deck)
        self.status.config(text=f"{self.index+1 if total else 0}/{total}")
        self.q.delete("1.0","end"); self.a.delete("1.0","end")
        if self.deck:
            q, a = self.deck[self.index]
            self.q.insert("1.0", q)
            if not self.quiz_mode:
                self.a.insert("1.0", a)

    def prev_card(self):
        if not self.deck: return
        self.index = (self.index - 1) % len(self.deck)
        self.render()

    def next_card(self):
        if not self.deck: return
        self.index = (self.index + 1) % len(self.deck)
        self.render()

    def toggle_quiz(self):
        self.quiz_mode = not self.quiz_mode
        self.render()

class PomodoroTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.running = False
        self.remaining = 25*60
        self.after_id = None

        self.time_lbl = ttk.Label(self, text=self._fmt(), font=("Segoe UI", 32, "bold"))
        self.time_lbl.pack(pady=12)
        controls = ttk.Frame(self)
        controls.pack()
        ttk.Button(controls, text="Démarrer", command=self.start).grid(row=0, column=0, padx=4)
        ttk.Button(controls, text="Pause", command=self.pause).grid(row=0, column=1, padx=4)
        ttk.Button(controls, text="Réinit 25/5", command=self.reset).grid(row=0, column=2, padx=4)

        self.phase = "focus"  # or "break"
        self.info = ttk.Label(self, text="Focus 25 min")
        self.info.pack(pady=6)

    def _fmt(self):
        m, s = divmod(self.remaining, 60)
        return f"{m:02d}:{s:02d}"

    def tick(self):
        if not self.running: return
        if self.remaining > 0:
            self.remaining -= 1
            self.time_lbl.config(text=self._fmt())
            self.after_id = self.after(1000, self.tick)
        else:
            self.running = False
            self.bell()
            if self.phase == "focus":
                self.phase = "break"
                self.remaining = 5*60
                self.info.config(text="Pause 5 min")
            else:
                self.phase = "focus"
                self.remaining = 25*60
                self.info.config(text="Focus 25 min")
            messagebox.showinfo("Terminé", f"Période {self.phase} prête !")

    def start(self):
        if not self.running:
            self.running = True
            self.tick()

    def pause(self):
        self.running = False
        if self.after_id: self.after_cancel(self.after_id); self.after_id=None

    def reset(self):
        self.pause()
        self.phase = "focus"
        self.remaining = 25*60
        self.time_lbl.config(text=self._fmt())
        self.info.config(text="Focus 25 min")

class ShortcutsTab(ttk.Frame):
    def __init__(self, master, state):
        super().__init__(master)
        self.state = state
        self.tree = ttk.Treeview(self, columns=("name","path"), show="headings")
        self.tree.heading("name", text="Nom")
        self.tree.heading("path", text="Chemin")
        self.tree.column("name", width=160); self.tree.column("path", width=420)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        bar = ttk.Frame(self); bar.pack(pady=(0,8))
        ttk.Button(bar, text="Ajouter", command=self.add).grid(row=0, column=0, padx=4)
        ttk.Button(bar, text="Ouvrir", command=self.open).grid(row=0, column=1, padx=4)
        ttk.Button(bar, text="Supprimer", command=self.delete).grid(row=0, column=2, padx=4)
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for it in self.state.get("shortcuts", []):
            self.tree.insert("", tk.END, values=(it.get("name",""), it.get("path","")))

    def add(self):
        p = filedialog.askopenfilename(title="Choisir un fichier")
        if not p: return
        name = simple_prompt("Nom à afficher:", Path(p).stem)
        if not name: return
        self.state["shortcuts"].append({"name": name, "path": p})
        save_data(self.state); self.refresh()

    def open(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        p = item["values"][1]
        try:
            os.startfile(p)  # Windows only
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        del self.state["shortcuts"][idx]
        save_data(self.state); self.refresh()

def simple_prompt(label, initial=""):
    win = tk.Toplevel()
    win.title("Entrée")
    ttk.Label(win, text=label).grid(row=0, column=0, padx=8, pady=8)
    e = ttk.Entry(win, width=40)
    e.grid(row=0, column=1, padx=8, pady=8)
    e.insert(0, initial)
    res = {"value": None}
    def ok():
        res["value"] = e.get().strip()
        win.destroy()
    ttk.Button(win, text="OK", command=ok).grid(row=1, column=1, sticky="e", padx=8, pady=8)
    e.focus_set()
    win.grab_set()
    win.wait_window()
    return res["value"]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_dirs()
        self.state = load_data()
        self.title(f"{APP_NAME}")
        self.geometry("980x640")
        try:
            self.iconbitmap(default="")  # no icon bundled by default
        except Exception:
            pass

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.dashboard = Dashboard(nb, self.state); nb.add(self.dashboard, text="Accueil")
        self.notes = NotesTab(nb); nb.add(self.notes, text="Notes")
        self.tasks = TasksTab(nb, self.state); nb.add(self.tasks, text="Tâches")
        self.timetable = TimetableTab(nb, self.state); nb.add(self.timetable, text="Emploi du temps")
        self.flash = FlashcardsTab(nb); nb.add(self.flash, text="Cartes mémoire")
        self.pomo = PomodoroTab(nb); nb.add(self.pomo, text="Pomodoro")
        self.shortcuts = ShortcutsTab(nb, self.state); nb.add(self.shortcuts, text="Raccourcis")

        # Menu
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Ouvrir dossier données", command=lambda: os.startfile(str(DATA_DIR)))
        filem.add_separator()
        filem.add_command(label="Quitter", command=self.destroy)
        menubar.add_cascade(label="Fichier", menu=filem)

        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="Aide/README", command=self.open_readme)
        helpm.add_command(label="Site Python", command=lambda: webbrowser.open("https://www.python.org/"))
        menubar.add_cascade(label="Aide", menu=helpm)
        self.config(menu=menubar)

        # Status bar
        self.status = ttk.Label(self, text=f"Données: {DATA_DIR}", anchor="w")
        self.status.pack(fill="x")

    def open_readme(self):
        readme_path = DATA_DIR / "README.txt"
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("Bienvenue sur SchoolBuddy ! Les données sont stockées dans ce dossier.\n")
            os.startfile(str(DATA_DIR))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
