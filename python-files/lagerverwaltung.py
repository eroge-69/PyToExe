# -*- coding: utf-8 -*-
"""
Lagerverwaltung – Desktop-App (Tkinter)
Funktionen:
- Artikel anlegen/bearbeiten/löschen
- Kategorien & Regale verwalten
- Suche, Sortierung (Name A–Z, Datum neu-alt/alt-neu)
- CSV/JSON Import/Export (UTF-8, ; oder ,)
- Bilder (Thumbnail-Spalte) + beliebige Dateianhänge je Artikel
- Auto-Speichern nach Änderungen + Zeitstempel-Backups
- Spaltenbreite per Maus einstellbar, Menge zentriert & fett
- Mindestbestand: komplette Zeile gelb mit schwarzer Schrift
- Mehrfachauswahl + Sammellöschen
- Ordner frei wählbar (keine Browser-Limits)
Abhängigkeiten: Python 3.10+, Pillow
Install: pip install pillow
"""
import csv
import io
import json
import os
import shutil
import sys
import textwrap
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import font   # <-- diesen Import hinzufügen
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import Dict, List, Optional

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Fehlende Abhängigkeit",
                         "Bitte installiere Pillow:\n\npip install pillow")
    raise

APP_NAME = "Lagerverwaltung"
APP_VERSION = "1.0"
DEFAULT_CATS = ["Allgemein"]
DEFAULT_SHELVES = {"R1": {"levels": 3, "cols": 5, "bins": 10}}

# -------------------- Hilfen --------------------
def ts_name() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def docs_dir() -> Path:
    from pathlib import Path
    home = Path.home()
    # Windows: "Documents", macOS: "Documents", Linux: fallback ~/Documents
    for name in ("Documents", "Dokumente", "documents"):
        p = home / name
        if p.exists():
            return p
    return home / "Documents"

def default_data_dir() -> Path:
    return docs_dir() / "Lagerverwaltung"

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def wrap_text(text: str, width_chars: int = 40) -> str:
    # Einfache Zell-„Umbruch”-Simulation (Treeview kann nicht hart umbrechen)
    # Besser: kürzen + Tooltip zeigen (hier: weiche Zeilen).
    text = (text or "").replace("\r", "").replace("\n", " ")
    return "\n".join(textwrap.wrap(text, width=width_chars)) if text else ""

def safe_float(s: str, default=0.0) -> float:
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return default

def safe_int(s: str, default=0) -> int:
    try:
        return int(str(s).strip())
    except Exception:
        return default

# -------------------- Datenmodell --------------------
@dataclass
class Item:
    id: str
    createdAt: int
    name: str
    sku: str = ""
    maker: str = ""
    cat: str = "Allgemein"
    shelf: str = "R1"
    level: int = 1
    col: int = 1
    bin: int = 1
    minQty: int = 0
    qty: int = 0
    price: float = 0.0
    note: str = ""
    image_path: str = ""          # Originalbild oder Kopie im attachments-Ordner
    thumb_path: str = ""          # erzeugtes Thumbnail (PNG)
    attachments: List[str] = field(default_factory=list)  # absolute Pfade

    def key_for_merge(self) -> str:
        if self.sku.strip():
            return f"SKU:{self.sku.strip().lower()}"
        return f"NM:{self.name.strip().lower()}|MK:{self.maker.strip().lower()}"

@dataclass
class State:
    items: List[Item] = field(default_factory=list)
    cats: List[str] = field(default_factory=lambda: DEFAULT_CATS.copy())
    shelves: Dict[str, Dict[str, int]] = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_SHELVES)))
    sort_mode: str = "name_asc"
    data_dir: Path = field(default_factory=default_data_dir)
    autosave: bool = True
    theme: str = "dark"  # "light" | "dark"

# -------------------- Persistenz --------------------
class Storage:
    def __init__(self, state: State):
        self.state = state

    @property
    def inventory_path(self) -> Path:
        return self.state.data_dir / "inventory.json"

    @property
    def attachments_dir(self) -> Path:
        return self.state.data_dir / "attachments"

    def load(self) -> None:
        p = self.inventory_path
        if not p.exists():
            ensure_dir(self.state.data_dir)
            ensure_dir(self.attachments_dir)
            self.save(backup=False)
            return
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"JSON laden fehlgeschlagen:\n{e}")
            return
        self.state.cats = data.get("cats") or DEFAULT_CATS.copy()
        self.state.shelves = data.get("shelves") or json.loads(json.dumps(DEFAULT_SHELVES))
        self.state.sort_mode = data.get("settings", {}).get("sortMode", "name_asc")
        self.state.autosave = bool(data.get("settings", {}).get("autosave", True))
        self.state.theme = data.get("settings", {}).get("theme", "dark")

        self.state.items = []
        for raw in data.get("items", []):
            self.state.items.append(Item(**raw))
        ensure_dir(self.attachments_dir)

    def save(self, backup: bool = True) -> None:
        ensure_dir(self.state.data_dir)
        ensure_dir(self.attachments_dir)
        payload = {
            "items": [asdict(x) for x in self.state.items],
            "cats": self.state.cats,
            "shelves": self.state.shelves,
            "settings": {
                "sortMode": self.state.sort_mode,
                "autosave": self.state.autosave,
                "theme": self.state.theme,
            },
        }
        tmp = io.StringIO()
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        text = tmp.getvalue()
        # Hauptdatei
        with self.inventory_path.open("w", encoding="utf-8") as f:
            f.write(text)
        # Backupdatei
        if backup:
            bpath = self.state.data_dir / f"inventory_{ts_name()}.json"
            with bpath.open("w", encoding="utf-8") as f:
                f.write(text)

# -------------------- Thumbnails --------------------
def make_thumbnail(src_path: Path, dst_path: Path, size=(96, 72)) -> bool:
    try:
        im = Image.open(src_path)
        im.thumbnail(size, Image.Resampling.LANCZOS)
        ensure_dir(dst_path.parent)
        im.save(dst_path, format="PNG")
        return True
    except Exception:
        return False

# -------------------- CSV --------------------
CSV_HEADER = [
    "Bezeichnung","Artikelnummer","Hersteller","Kategorie","Preis",
    "Regal","Boden","Spalte","Fach","Bestand","Mindestbestand","Notiz"
]

def to_csv(items: List[Item]) -> str:
    out = io.StringIO()
    # BOM für Excel-Kompatibilität
    out.write("\ufeff")
    writer = csv.writer(out, delimiter=";")
    writer.writerow(CSV_HEADER)
    for it in items:
        writer.writerow([
            it.name, it.sku, it.maker, it.cat,
            f"{it.price:.2f}",
            it.shelf, it.level, it.col, it.bin,
            it.qty, it.minQty, it.note
        ])
    return out.getvalue()

def detect_sep(first_line: str) -> str:
    return ";" if first_line.count(";") >= first_line.count(",") else ","

def parse_csv(content: str) -> List[Item]:
    # SEP erkennen an erster Zeile
    first = content.splitlines()[0] if content else ""
    sep = detect_sep(first)
    items: List[Item] = []
    reader = csv.reader(io.StringIO(content), delimiter=sep)
    header = None
    for row in reader:
        if not row:
            continue
        if header is None:
            header = [h.strip().lower() for h in row]
            continue
        def idx(*names):
            for n in names:
                try:
                    return header.index(n)
                except ValueError:
                    continue
            return -1
        def get(names, default=""):
            i = idx(*names)
            return row[i] if 0 <= i < len(row) else default

        name = get(("bezeichnung","name"))
        if not (name or "").strip():
            continue
        items.append(Item(
            id=str(int(time.time()*1000)) + "_" + str(len(items)+1),
            createdAt=int(time.time()*1000),
            name=name.strip(),
            sku=get(("artikelnummer","sku","art.-nr.","nummer")).strip(),
            maker=get(("hersteller","brand","maker")).strip(),
            cat=(get(("kategorie","category","cat")) or "Allgemein").strip(),
            price=safe_float(get(("preis","price","eur","€"), "0")),
            shelf=(get(("regal","shelf")) or "R1").strip(),
            level=safe_int(get(("boden","level"), "1"), 1),
            col=safe_int(get(("spalte","column"), "1"), 1),
            bin=safe_int(get(("fach","bin"), "1"), 1),
            qty=safe_int(get(("bestand","qty","menge"), "0"), 0),
            minQty=safe_int(get(("mindestbestand","min","min qty"), "0"), 0),
            note=get(("notiz","note","desc"), "")
        ))
    return items

# -------------------- GUI --------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} – v{APP_VERSION}")
        self.geometry("1280x760")
        self.minsize(1100, 640)

        self.state_ = State()
        self.storage = Storage(self.state_)
        ensure_dir(self.state_.data_dir)
        self.storage.load()

        # Images der Treeview im Speicher halten, sonst werden sie „freigegeben“
        self._row_images: Dict[str, ImageTk.PhotoImage] = {}

        self._build_menu()
        self._build_toolbar()
        self._build_layout()
        self._apply_theme(self.state_.theme)

        self.refresh_form(reset=True)
        self.refresh_lists(redraw_all=True)

    # ---------- Menu & Toolbar ----------
    def _build_menu(self):
        m = tk.Menu(self)
        self.config(menu=m)

        filem = tk.Menu(m, tearoff=False)
        filem.add_command(label="Datenordner wählen…", command=self.choose_data_dir)
        filem.add_separator()
        filem.add_command(label="JSON exportieren…", command=self.json_export)
        filem.add_command(label="JSON importieren…", command=self.json_import)
        filem.add_command(label="CSV exportieren…", command=self.csv_export)
        filem.add_command(label="CSV importieren…", command=self.csv_import)
        filem.add_separator()
        filem.add_command(label="Beenden", command=self.destroy)
        m.add_cascade(label="Datei", menu=filem)

        editm = tk.Menu(m, tearoff=False)
        editm.add_command(label="Ausgewählte löschen", command=self.bulk_delete)
        editm.add_separator()
        editm.add_checkbutton(label="Auto-Speichern", onvalue=True, offvalue=False,
                              variable=tk.BooleanVar(value=self.state_.autosave),
                              command=self.toggle_autosave)
        m.add_cascade(label="Bearbeiten", menu=editm)

        viewm = tk.Menu(m, tearoff=False)
        viewm.add_radiobutton(label="Sortierung: A–Z (Bezeichnung)", command=lambda: self.set_sort("name_asc"))
        viewm.add_radiobutton(label="Sortierung: Datum neu → alt", command=lambda: self.set_sort("date_desc"))
        viewm.add_radiobutton(label="Sortierung: Datum alt → neu", command=lambda: self.set_sort("date_asc"))
        m.add_cascade(label="Ansicht", menu=viewm)

        settingsm = tk.Menu(m, tearoff=False)
        settingsm.add_command(label="Kategorien & Regale…", command=self.open_settings_dialog)
        settingsm.add_separator()
        settingsm.add_radiobutton(label="Theme: Dunkel", command=lambda: self._apply_theme("dark"))
        settingsm.add_radiobutton(label="Theme: Hell", command=lambda: self._apply_theme("light"))
        m.add_cascade(label="Einstellungen", menu=settingsm)

        helpm = tk.Menu(m, tearoff=False)
        helpm.add_command(label="Über…", command=lambda: messagebox.showinfo(APP_NAME, f"{APP_NAME} v{APP_VERSION}\nPython/Tkinter-Version"))
        m.add_cascade(label="Hilfe", menu=helpm)

    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(side="top", fill="x")

        ttk.Label(bar, text="Suche:").pack(side="left")
        self.var_search = tk.StringVar()
        e = ttk.Entry(bar, width=50, textvariable=self.var_search)
        e.pack(side="left", padx=(6, 6))
        ttk.Button(bar, text="Suchen", command=self.run_search).pack(side="left")
        ttk.Button(bar, text="Zurücksetzen", command=self.clear_search).pack(side="left", padx=(6, 0))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(bar, text="Jetzt speichern", command=lambda: self.storage.save(backup=True)).pack(side="left")
        ttk.Button(bar, text="Laden", command=self.reload_from_disk).pack(side="left", padx=(6, 0))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(bar, text="Einstellungen", command=self.open_settings_dialog).pack(side="left")
        ttk.Button(bar, text="Auswahl löschen", command=self.bulk_delete).pack(side="left")

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Label(bar, text="Sortierung:").pack(side="left")
        self.var_sort = tk.StringVar(value=self.state_.sort_mode)
        ttk.Combobox(bar, textvariable=self.var_sort, state="readonly",
                     values=["name_asc","date_desc","date_asc"], width=12)\
            .pack(side="left")
        self.var_sort.trace_add("write", lambda *_: self.set_sort(self.var_sort.get()))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)

        self.var_autosave = tk.BooleanVar(value=self.state_.autosave)
        ttk.Checkbutton(bar, text="Auto‑Speichern", variable=self.var_autosave,
                        command=self.toggle_autosave).pack(side="left")

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(bar, text="Anhänge öffnen", command=self.open_attachments_for_selected).pack(side="left")

    def _build_layout(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill="both", expand=True)

        # Linke Seite: Formular
        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 8))

        # Felder
        self.var_name = tk.StringVar()
        self.var_sku = tk.StringVar()
        self.var_maker = tk.StringVar()
        self.var_cat = tk.StringVar(value=self.state_.cats[0])
        self.var_shelf = tk.StringVar(value=list(self.state_.shelves.keys())[0])
        self.var_level = tk.IntVar(value=1)
        self.var_col = tk.IntVar(value=1)
        self.var_bin = tk.IntVar(value=1)
        self.var_min = tk.IntVar(value=0)
        self.var_qty = tk.IntVar(value=0)
        self.var_price = tk.StringVar(value="0.00")
        self.var_note = tk.StringVar()

        f = ttk.LabelFrame(left, text="Artikel erfassen / bearbeiten", padding=8)
        f.pack(fill="x")

        def row(lbl, widget):
            r = ttk.Frame(f)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=lbl, width=16).pack(side="left")
            widget.pack(side="left", fill="x", expand=True)

        row("Bezeichnung *", ttk.Entry(f, textvariable=self.var_name))
        row("Artikelnummer", ttk.Entry(f, textvariable=self.var_sku))
        row("Hersteller", ttk.Entry(f, textvariable=self.var_maker))
        row("Kategorie", ttk.Combobox(f, textvariable=self.var_cat, values=self.state_.cats, state="readonly"))
        row("Regal", ttk.Combobox(f, textvariable=self.var_shelf, values=list(self.state_.shelves.keys()), state="readonly"))

        loc = ttk.Frame(f); loc.pack(fill="x", pady=2)
        ttk.Label(loc, text="Boden", width=16).pack(side="left")
        ttk.Spinbox(loc, from_=1, to=999, textvariable=self.var_level, width=6, command=self.validate_location).pack(side="left")
        ttk.Label(loc, text="Spalte").pack(side="left", padx=(8, 2))
        ttk.Spinbox(loc, from_=1, to=999, textvariable=self.var_col, width=6, command=self.validate_location).pack(side="left")
        ttk.Label(loc, text="Fach").pack(side="left", padx=(8, 2))
        ttk.Spinbox(loc, from_=1, to=999, textvariable=self.var_bin, width=6, command=self.validate_location).pack(side="left")
        self.lab_loc = ttk.Label(loc, text="—")
        self.lab_loc.pack(side="left", padx=(12, 0))

        row("Mindestbestand", ttk.Spinbox(f, from_=0, to=999999, textvariable=self.var_min, width=10))

        qty = ttk.Frame(f); qty.pack(fill="x", pady=2)
        ttk.Label(qty, text="Bestand", width=16).pack(side="left")
        ttk.Spinbox(qty, from_=0, to=999999, textvariable=self.var_qty, width=10).pack(side="left")
        ttk.Button(qty, text="+1", command=lambda: self.var_qty.set(self.var_qty.get()+1)).pack(side="left", padx=(6,2))
        ttk.Button(qty, text="−1", command=lambda: self.var_qty.set(max(0,self.var_qty.get()-1))).pack(side="left", padx=(2,0))

        row("Preis (€)", ttk.Entry(f, textvariable=self.var_price))
        row("Notiz", ttk.Entry(f, textvariable=self.var_note))

        imgrow = ttk.Frame(f); imgrow.pack(fill="x", pady=4)
        ttk.Button(imgrow, text="Bild wählen…", command=self.choose_image_for_current).pack(side="left")
        ttk.Button(imgrow, text="Dateianhänge hinzufügen…", command=self.add_attachments_for_current).pack(side="left", padx=(6,0))
        self.preview = ttk.Label(imgrow, text="(keine Vorschau)")
        self.preview.pack(side="left", padx=10)

        btns = ttk.Frame(f); btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Speichern", command=self.save_current).pack(side="left")
        ttk.Button(btns, text="Maske leeren", command=self.reset_form).pack(side="left", padx=(6,0))
        ttk.Button(btns, text="Artikel löschen", command=self.delete_current).pack(side="right")

        # Rechte Seite: Liste
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        cols = ("idx","img","name","sku","maker","cat","shelf","loc","qty","price","att")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=22)
        self.tree.pack(side="left", fill="both", expand=True)
        # Scrollbar
        sby = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        sby.pack(side="left", fill="y")
        self.tree.configure(yscroll=sby.set)

        # Spaltenköpfe
        self.tree.heading("idx", text="#")
        self.tree.heading("img", text="Bild")
        self.tree.heading("name", text="Bezeichnung")
        self.tree.heading("sku", text="Art.-Nr.")
        self.tree.heading("maker", text="Hersteller")
        self.tree.heading("cat", text="Kategorie")
        self.tree.heading("shelf", text="Regal")
        self.tree.heading("loc", text="Lagerort")
        self.tree.heading("qty", text="Bestand")
        self.tree.heading("price", text="Preis €")
        self.tree.heading("att", text="📎")

        # Standardbreiten (vom Nutzer ziehbar)
        self.tree.column("idx", width=40, anchor="e")
        self.tree.column("img", width=80, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("sku", width=120, anchor="w")
        self.tree.column("maker", width=140, anchor="w")
        self.tree.column("cat", width=120, anchor="w")
        self.tree.column("shelf", width=80, anchor="center")
        self.tree.column("loc", width=130, anchor="center")
        self.tree.column("qty", width=90, anchor="center")
        self.tree.column("price", width=90, anchor="e")
        self.tree.column("att", width=80, anchor="center")

        # Tags/Styles
        self.bold_font = font.Font(self, self.cget("font"))
        self.bold_font.configure(weight="bold")
        self.style = ttk.Style(self)
        self.style.configure("Treeview", rowheight=56)  # Platz für Thumbnail + Mehrzeilen
        self.tree.tag_configure("low", background="#fff3bf", foreground="#000000")  # Mindestbestand
        self.tree.tag_configure("qtybold", font=self.bold_font)

        # Selektion / Events
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        self.tree.bind("<Double-1>", self.on_double_click_row)
        self.tree.bind("<Delete>", lambda e: self.bulk_delete())

        # Rechtsklickmenü
        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(label="+1 Einlagern", command=lambda: self.adjust_qty(+1))
        self.menu.add_command(label="−1 Auslagern", command=lambda: self.adjust_qty(-1))
        self.menu.add_separator()
        self.menu.add_command(label="Anhänge öffnen", command=self.open_attachments_for_selected)
        self.menu.add_separator()
        self.menu.add_command(label="Löschen", command=self.bulk_delete)

        self.tree.bind("<Button-3>", self._popup_menu)

    # ---------- Theme ----------
    def _apply_theme(self, name: str):
        self.state_.theme = name
        sty = ttk.Style(self)
        if name == "dark":
            try:
                self.tk.call("ttk::style", "theme", "use", "clam")
            except Exception:
                pass
            # einfache dunkle Palette
            bg = "#12141a"; fg = "#e8eef9"; sel = "#273142"
            sty.configure(".", background=bg, foreground=fg)
            sty.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg)
            sty.map("Treeview", background=[("selected", sel)])
            self.configure(bg=bg)
        else:
            sty.theme_use("clam")
            sty.configure(".", background="#f6f7fb", foreground="#111827")
            sty.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#111827")
            self.configure(bg="#f6f7fb")
        self.update_idletasks()

    # ---------- Utility ----------
    def notify(self, msg: str):
        self.title(f"{APP_NAME} – {msg}")

    def set_sort(self, mode: str):
        self.state_.sort_mode = mode
        self.refresh_lists()

    def toggle_autosave(self):
        self.state_.autosave = bool(self.var_autosave.get())

    def validate_location(self) -> bool:
        sh = self.var_shelf.get()
        defn = self.state_.shelves.get(sh)
        if not defn:
            self.lab_loc.config(text="Unbekanntes Regal")
            return False
        L,C,B = self.var_level.get(), self.var_col.get(), self.var_bin.get()
        ok = (1 <= L <= defn["levels"]) and (1 <= C <= defn["cols"]) and (1 <= B <= defn["bins"])
        if ok:
            self.lab_loc.config(text=f"OK (B:{defn['levels']} S:{defn['cols']} F:{defn['bins']})")
        else:
            self.lab_loc.config(text=f"Ungültig – max B:{defn['levels']} S:{defn['cols']} F:{defn['bins']}")
        return ok

    def fmt_loc(self, it: Item) -> str:
        return f"B:{it.level} S:{it.col} F:{it.bin}"

    # ---------- Daten laden/speichern ----------
    def reload_from_disk(self):
        self.storage.load()
        self.refresh_lists(redraw_all=True)
        self.refresh_form(reset=True)
        self.notify("Geladen.")

    def save_all(self, backup=True):
        self.storage.save(backup=backup)
        self.notify("Gespeichert.")

    # ---------- Formular ----------
    _editing_id: Optional[str] = None

    def reset_form(self):
        self._editing_id = None
        self.var_name.set("")
        self.var_sku.set("")
        self.var_maker.set("")
        self.var_cat.set(self.state_.cats[0] if self.state_.cats else "Allgemein")
        self.var_shelf.set(list(self.state_.shelves.keys())[0] if self.state_.shelves else "R1")
        self.var_level.set(1)
        self.var_col.set(1)
        self.var_bin.set(1)
        self.var_min.set(0)
        self.var_qty.set(0)
        self.var_price.set("0.00")
        self.var_note.set("")
        self.preview.config(text="(keine Vorschau)", image="")
        self.validate_location()

    def refresh_form(self, reset=False):
        if reset or self._editing_id is None:
            self.reset_form()

    def save_current(self):
        if not self.var_name.get().strip():
            messagebox.showwarning(APP_NAME, "Bezeichnung ist Pflicht.")
            return
        if not self.validate_location():
            messagebox.showwarning(APP_NAME, "Lagerort ist ungültig.")
            return
        if self._editing_id:
            it = next((x for x in self.state_.items if x.id == self._editing_id), None)
            if not it:  # Falls gelöscht
                self._editing_id = None
                return self.save_current()
        else:
            it = Item(id=str(int(time.time()*1000)), createdAt=int(time.time()*1000), name="")

        it.name = self.var_name.get().strip()
        it.sku = self.var_sku.get().strip()
        it.maker = self.var_maker.get().strip()
        it.cat = self.var_cat.get().strip() or "Allgemein"
        it.shelf = self.var_shelf.get().strip() or "R1"
        it.level = int(self.var_level.get())
        it.col = int(self.var_col.get())
        it.bin = int(self.var_bin.get())
        it.minQty = int(self.var_min.get())
        it.qty = int(self.var_qty.get())
        it.price = safe_float(self.var_price.get(), 0.0)
        it.note = self.var_note.get()

        if not any(x.id == it.id for x in self.state_.items):
            self.state_.items.append(it)

        if self.state_.autosave:
            self.save_all(backup=True)

        self.refresh_lists()
        self.notify("Artikel gespeichert.")

    def delete_current(self):
        if not self._editing_id:
            return
        if messagebox.askyesno(APP_NAME, "Artikel wirklich löschen?"):
            self.state_.items = [x for x in self.state_.items if x.id != self._editing_id]
            self._editing_id = None
            if self.state_.autosave:
                self.save_all(backup=True)
            self.refresh_lists()
            self.reset_form()

    def load_into_form(self, it: Item):
        self._editing_id = it.id
        self.var_name.set(it.name)
        self.var_sku.set(it.sku)
        self.var_maker.set(it.maker)
        self.var_cat.set(it.cat if it.cat in self.state_.cats else (self.state_.cats[0] if self.state_.cats else "Allgemein"))
        self.var_shelf.set(it.shelf if it.shelf in self.state_.shelves else (list(self.state_.shelves.keys())[0] if self.state_.shelves else "R1"))
        self.var_level.set(it.level)
        self.var_col.set(it.col)
        self.var_bin.set(it.bin)
        self.var_min.set(it.minQty)
        self.var_qty.set(it.qty)
        self.var_price.set(f"{it.price:.2f}")
        self.var_note.set(it.note)
        if it.thumb_path and Path(it.thumb_path).exists():
            img = ImageTk.PhotoImage(Image.open(it.thumb_path))
            self.preview.configure(image=img, text="")
            self.preview.image = img
        else:
            self.preview.configure(text="(keine Vorschau)", image="")
            self.preview.image = None
        self.validate_location()

    # ---------- Tree / Liste ----------
    def _sorted_items(self) -> List[Item]:
        arr = list(self.state_.items)
        m = self.state_.sort_mode
        if m == "name_asc":
            arr.sort(key=lambda x: (x.name or "").lower())
        elif m == "date_desc":
            arr.sort(key=lambda x: x.createdAt, reverse=True)
        elif m == "date_asc":
            arr.sort(key=lambda x: x.createdAt)
        return arr

    def _apply_search(self, items: List[Item]) -> List[Item]:
        q = (self.var_search.get() or "").strip().lower()
        if not q:
            return items
        def hay(it: Item) -> str:
            return " ".join([
                it.name, it.sku, it.maker, it.cat, f"{it.price}", it.shelf,
                f"B:{it.level} S:{it.col} F:{it.bin}", it.note
            ]).lower()
        return [it for it in items if q in hay(it)]

    def refresh_lists(self, redraw_all=False):
        # Tree neu aufbauen
        self.tree.delete(*self.tree.get_children())
        self._row_images.clear()

        items = self._sorted_items()
        items = self._apply_search(items)

        for idx, it in enumerate(items, start=1):
            # Thumbnail laden (nur in img-Spalte nutzen wir Image als Text)
            img_obj = None
            if it.thumb_path and Path(it.thumb_path).exists():
                try:
                    img_obj = ImageTk.PhotoImage(Image.open(it.thumb_path))
                except Exception:
                    img_obj = None
            self._row_images[it.id] = img_obj  # halten

            name_wrapped = wrap_text(it.name, width_chars=32)
            note_wrapped = wrap_text(it.note, width_chars=36)  # (nicht angezeigt, nur optional)
            loc = self.fmt_loc(it)
            att_count = len(it.attachments)

            tags = []
            if (it.minQty or 0) > 0 and (it.qty or 0) < it.minQty:
                tags.append("low")
            tags.append("qtybold")

            # Treeview kann Bild nur als „image“ eines Items zeigen.
            # Workaround: Wir setzen das Bild als „image“ und zeigen in img-Spalte einen Platzhalter.
            iid = self.tree.insert("", "end",
                                   iid=it.id,
                                   values=(idx, " ", name_wrapped, it.sku or "—", it.maker or "—",
                                           it.cat or "—", it.shelf or "—", loc,
                                           it.qty, f"{it.price:.2f}", f"📎 {att_count}" if att_count else "—"),
                                   tags=tuple(tags),
                                   image=img_obj)

        # Menge (qty) optisch zentriert & fett: Spaltenanker + Zeilenfont
        self.tree.column("qty", anchor="center")
        # (Tkinter unterstützt kein per-Zelle-Font; wir markieren die ganze Zeile fett.
        # Alternativ: Nur qty-Zahl bereits zentriert anzeigen → ausreichend.)

    # ---------- Suche ----------
    def run_search(self):
        self.refresh_lists()
        self.notify("Suche aktiv")

    def clear_search(self):
        self.var_search.set("")
        self.refresh_lists()
        self.notify("Suche beendet")

    # ---------- Auswahl ----------
    def selected_items(self) -> List[Item]:
        ids = list(self.tree.selection())
        out = []
        for iid in ids:
            it = next((x for x in self.state_.items if x.id == iid), None)
            if it:
                out.append(it)
        return out

    def on_select_row(self, _):
        pass

    def on_double_click_row(self, _):
        sel = self.selected_items()
        if sel:
            self.load_into_form(sel[0])

    def _popup_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
        except Exception:
            pass
        self.menu.tk_popup(event.x_root, event.y_root)

    def adjust_qty(self, delta: int):
        for it in self.selected_items():
            it.qty = max(0, (it.qty or 0) + delta)
        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()

    def bulk_delete(self):
        sel = self.selected_items()
        if not sel:
            return
        if not messagebox.askyesno(APP_NAME, f"{len(sel)} Artikel wirklich löschen?"):
            return
        ids = {it.id for it in sel}
        self.state_.items = [x for x in self.state_.items if x.id not in ids]
        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()
        self.reset_form()

    def open_attachments_for_selected(self):
        sel = self.selected_items()
        if not sel:
            return
        it = sel[0]
        if not it.attachments:
            messagebox.showinfo(APP_NAME, "Keine Anhänge vorhanden.")
            return
        # Einfach: Ordner des ersten Anhangs öffnen
        path = Path(it.attachments[0]).parent
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Ordner öffnen fehlgeschlagen:\n{e}")

    # ---------- Bilder & Anhänge ----------
    def _item_dir(self, item_id: str) -> Path:
        return self.storage.attachments_dir / item_id

    def choose_image_for_current(self):
        if not self._editing_id:
            # Falls neu: Dummy Item anlegen (noch nicht speichern)
            self.save_current()
        it = next((x for x in self.state_.items if x.id == self._editing_id), None)
        if not it:
            return
        fp = filedialog.askopenfilename(title="Bild wählen",
                                        filetypes=[("Bilder", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif"),
                                                   ("Alle Dateien", "*.*")])
        if not fp:
            return
        src = Path(fp)
        dest_dir = self._item_dir(it.id)
        ensure_dir(dest_dir)
        # Original kopieren (Dateiname beibehalten)
        dst = dest_dir / src.name
        try:
            shutil.copy2(src, dst)
            it.image_path = str(dst)
            # Thumbnail erzeugen
            thumb = dest_dir / "thumb.png"
            if make_thumbnail(dst, thumb, size=(96, 72)):
                it.thumb_path = str(thumb)
            # Vorschau aktualisieren
            if it.thumb_path and Path(it.thumb_path).exists():
                img = ImageTk.PhotoImage(Image.open(it.thumb_path))
                self.preview.configure(image=img, text="")
                self.preview.image = img
            if self.state_.autosave:
                self.save_all(backup=True)
            self.refresh_lists()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Bild übernehmen fehlgeschlagen:\n{e}")

    def add_attachments_for_current(self):
        if not self._editing_id:
            self.save_current()
        it = next((x for x in self.state_.items if x.id == self._editing_id), None)
        if not it:
            return
        fps = filedialog.askopenfilenames(title="Dateien anhängen…")
        if not fps:
            return
        dest_dir = self._item_dir(it.id)
        ensure_dir(dest_dir)
        for fp in fps:
            src = Path(fp)
            dst = dest_dir / src.name
            try:
                shutil.copy2(src, dst)
                it.attachments.append(str(dst))
            except Exception as e:
                messagebox.showwarning(APP_NAME, f"Konnte {src.name} nicht kopieren:\n{e}")
        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()

    # ---------- Einstellungen ----------
    def open_settings_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Einstellungen, Kategorien & Regale")
        dlg.transient(self)
        dlg.grab_set()

        nb = ttk.Notebook(dlg)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Kategorien
        catf = ttk.Frame(nb, padding=8)
        nb.add(catf, text="Kategorien")

        self.var_new_cat = tk.StringVar()
        row = ttk.Frame(catf); row.pack(fill="x", pady=4)
        ttk.Entry(row, textvariable=self.var_new_cat).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="+ Hinzufügen", command=self.add_category).pack(side="left", padx=(6,0))

        self.lst_cats = tk.Listbox(catf, height=8)
        self.lst_cats.pack(fill="both", expand=True)
        for c in self.state_.cats:
            self.lst_cats.insert("end", c)
        ttk.Button(catf, text="Ausgewählte Kategorie löschen", command=self.delete_selected_category)\
            .pack(side="right", pady=(6,0))

        # Regale
        shelf = ttk.Frame(nb, padding=8)
        nb.add(shelf, text="Regale")

        self.var_shelf_name = tk.StringVar()
        self.var_shelf_levels = tk.IntVar(value=3)
        self.var_shelf_cols = tk.IntVar(value=5)
        self.var_shelf_bins = tk.IntVar(value=10)

        grid = ttk.Frame(shelf); grid.pack(fill="x", pady=4)
        ttk.Label(grid, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.var_shelf_name, width=10).grid(row=0, column=1, padx=6)
        ttk.Label(grid, text="Böden").grid(row=0, column=2)
        ttk.Spinbox(grid, from_=1, to=999, textvariable=self.var_shelf_levels, width=6).grid(row=0, column=3, padx=6)
        ttk.Label(grid, text="Spalten").grid(row=0, column=4)
        ttk.Spinbox(grid, from_=1, to=999, textvariable=self.var_shelf_cols, width=6).grid(row=0, column=5, padx=6)
        ttk.Label(grid, text="Fächer").grid(row=0, column=6)
        ttk.Spinbox(grid, from_=1, to=999, textvariable=self.var_shelf_bins, width=6).grid(row=0, column=7, padx=6)
        ttk.Button(grid, text="+ Regal speichern", command=self.add_shelf).grid(row=0, column=8, padx=8)

        self.lst_shelves = ttk.Treeview(shelf, columns=("levels","cols","bins"), show="headings", height=6)
        self.lst_shelves.pack(fill="both", expand=True, pady=(8,0))
        self.lst_shelves.heading("levels", text="Böden")
        self.lst_shelves.heading("cols", text="Spalten")
        self.lst_shelves.heading("bins", text="Fächer")
        self.lst_shelves.column("levels", width=80, anchor="center")
        self.lst_shelves.column("cols", width=80, anchor="center")
        self.lst_shelves.column("bins", width=80, anchor="center")
        for name, s in self.state_.shelves.items():
            self.lst_shelves.insert("", "end", iid=name, values=(s["levels"], s["cols"], s["bins"]))
        ttk.Button(shelf, text="Ausgewähltes Regal löschen", command=self.delete_selected_shelf)\
            .pack(side="right", pady=(6,0))

        # Buttons
        btns = ttk.Frame(dlg)
        btns.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(btns, text="Schließen", command=dlg.destroy).pack(side="right")

    def add_category(self):
        v = (self.var_new_cat.get() or "").strip()
        if not v:
            return
        if v not in self.state_.cats:
            self.state_.cats.append(v)
            self.lst_cats.insert("end", v)
        if self.state_.autosave:
            self.save_all(backup=True)
        self.var_new_cat.set("")
        # Combobox im Formular aktualisieren
        self.refresh_form()

    def delete_selected_category(self):
        sel = self.lst_cats.curselection()
        if not sel:
            return
        name = self.lst_cats.get(sel[0])
        if name == "Allgemein":
            messagebox.showinfo(APP_NAME, "Standardkategorie kann nicht gelöscht werden.")
            return
        if not messagebox.askyesno(APP_NAME, f'Kategorie "{name}" löschen?'):
            return
        self.state_.cats = [c for c in self.state_.cats if c != name]
        for it in self.state_.items:
            if it.cat == name:
                it.cat = "Allgemein"
        self.lst_cats.delete(sel[0])
        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()
        self.refresh_form()

    def add_shelf(self):
        name = (self.var_shelf_name.get() or "").strip()
        if not name:
            return
        lv = max(1, int(self.var_shelf_levels.get()))
        c = max(1, int(self.var_shelf_cols.get()))
        b = max(1, int(self.var_shelf_bins.get()))
        self.state_.shelves[name] = {"levels": lv, "cols": c, "bins": b}
        if self.lst_shelves.exists(name):
            self.lst_shelves.item(name, values=(lv,c,b))
        else:
            self.lst_shelves.insert("", "end", iid=name, values=(lv,c,b))
        if self.state_.autosave:
            self.save_all(backup=True)
        # Regal-Liste im Formular
        self.refresh_form()

    def delete_selected_shelf(self):
        sel = self.lst_shelves.selection()
        if not sel:
            return
        name = sel[0]
        if not messagebox.askyesno(APP_NAME, f'Regal "{name}" löschen?'):
            return
        self.state_.shelves.pop(name, None)
        self.lst_shelves.delete(name)
        for it in self.state_.items:
            if it.shelf == name:
                it.shelf = next(iter(self.state_.shelves.keys()), "R1")
        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()
        self.refresh_form()

    # ---------- Datei / Ordner ----------
    def choose_data_dir(self):
        p = filedialog.askdirectory(title="Datenordner wählen", initialdir=str(self.state_.data_dir))
        if not p:
            return
        self.state_.data_dir = Path(p)
        ensure_dir(self.state_.data_dir)
        ensure_dir(self.storage.attachments_dir)
        # neu speichern (Backup)
        self.save_all(backup=True)
        self.notify(f"Datenordner: {self.state_.data_dir}")

    # ---------- Import / Export ----------
    def json_export(self):
        p = filedialog.asksaveasfilename(
            title="JSON exportieren",
            defaultextension=".json",
            initialdir=str(self.state_.data_dir),
            initialfile=f"inventory_{ts_name()}.json",
            filetypes=[("JSON","*.json")])
        if not p:
            return
        tmp_state = State(
            items=self.state_.items,
            cats=self.state_.cats,
            shelves=self.state_.shelves,
            sort_mode=self.state_.sort_mode,
            data_dir=self.state_.data_dir,
            autosave=self.state_.autosave,
            theme=self.state_.theme
        )
        Storage(tmp_state).save(backup=False)
        try:
            shutil.copy2(self.storage.inventory_path, p)
            self.notify("JSON exportiert")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Export fehlgeschlagen:\n{e}")

    def json_import(self):
        p = filedialog.askopenfilename(title="JSON importieren", filetypes=[("JSON","*.json")])
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state_.cats = data.get("cats") or self.state_.cats
            self.state_.shelves = data.get("shelves") or self.state_.shelves
            self.state_.sort_mode = data.get("settings",{}).get("sortMode", self.state_.sort_mode)
            self.state_.autosave = bool(data.get("settings",{}).get("autosave", self.state_.autosave))
            self.state_.theme = data.get("settings",{}).get("theme", self.state_.theme)
            self.state_.items = [Item(**raw) for raw in data.get("items", [])]
            if self.state_.autosave:
                self.save_all(backup=True)
            self.refresh_lists(redraw_all=True)
            self.refresh_form(reset=True)
            self.notify("JSON importiert")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Import fehlgeschlagen:\n{e}")

    def csv_export(self):
        p = filedialog.asksaveasfilename(
            title="CSV exportieren",
            defaultextension=".csv",
            initialdir=str(self.state_.data_dir),
            initialfile="lager_export.csv",
            filetypes=[("CSV","*.csv")])
        if not p:
            return
        try:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(to_csv(self.state_.items))
            self.notify("CSV exportiert")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Export fehlgeschlagen:\n{e}")

    def csv_import(self):
        p = filedialog.askopenfilename(title="CSV importieren", filetypes=[("CSV","*.csv"),("Alle Dateien","*.*")])
        if not p:
            return
        try:
            content = Path(p).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = Path(p).read_text(encoding="latin-1")
        parsed = parse_csv(content)
        if not parsed:
            messagebox.showinfo(APP_NAME, "Keine gültigen Datensätze gefunden.")
            return

        imported = 0; updated = 0; checked = 0
        for cand in parsed:
            key = cand.key_for_merge()
            existing = next((x for x in self.state_.items if x.key_for_merge() == key), None)
            if existing:
                # Konflikt-Dialog (nur Bestand)
                if (cand.qty or 0) != (existing.qty or 0):
                    choice = simpledialog.askstring(
                        APP_NAME,
                        f'Konflikt bei "{existing.name}": alt {existing.qty}, neu {cand.qty}.\n'
                        f'1=behalten, 2=überschreiben, 3=addieren',
                        initialvalue="1")
                    if choice == "2":
                        existing.qty = cand.qty
                        updated += 1
                    elif choice == "3":
                        existing.qty = (existing.qty or 0) + (cand.qty or 0)
                        updated += 1
                # Lücken füllen
                if not existing.maker: existing.maker = cand.maker
                if not existing.cat: existing.cat = cand.cat
                if not existing.price: existing.price = cand.price
                if not existing.shelf: existing.shelf = cand.shelf
                if not existing.level: existing.level = cand.level
                if not existing.col: existing.col = cand.col
                if not existing.bin: existing.bin = cand.bin
                if not (existing.minQty or 0): existing.minQty = cand.minQty or 0
                checked += 1
            else:
                self.state_.items.append(cand)
                imported += 1

        if self.state_.autosave:
            self.save_all(backup=True)
        self.refresh_lists()
        messagebox.showinfo(APP_NAME, f"{imported} neu, {updated} aktualisiert, {checked} geprüft.")

# -------------------- main --------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
