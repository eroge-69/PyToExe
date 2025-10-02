# THEPLAN2.py — PLAN Offline App (Roster/Equipment, Assignments)
# Stdlib-only: Tkinter + sqlite3

import sqlite3, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import uuid, datetime

APP_NAME = "THE PLAN 2 (Offline)"
DB_PATH = Path("plan_app.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS investigations (
  id TEXT PRIMARY KEY,
  case_number TEXT,
  case_name TEXT,
  start_time TEXT,
  end_time TEXT,
  contact_name TEXT,
  contact_phone TEXT,
  contact_email TEXT,
  location_name TEXT,
  location_address TEXT,
  location_description TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS location_history (
  investigation_id TEXT PRIMARY KEY REFERENCES investigations(id) ON DELETE CASCADE,
  history TEXT,
  documentation TEXT,
  built_date TEXT,
  structures TEXT,
  rooms TEXT,
  paranormal_areas TEXT,
  renovated_recently INTEGER,
  blessed_before INTEGER
);

CREATE TABLE IF NOT EXISTS witnesses (
  id TEXT PRIMARY KEY,
  investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  name TEXT,
  phone TEXT,
  email TEXT,
  statement TEXT,
  recorded_at TEXT
);

CREATE TABLE IF NOT EXISTS investigation_log (
  investigation_id TEXT PRIMARY KEY REFERENCES investigations(id) ON DELETE CASCADE,
  lead_investigator TEXT,
  team TEXT,
  guests TEXT,
  equipment TEXT,
  weather TEXT,
  moon_cycle TEXT,
  start_time TEXT,
  end_time TEXT,
  observations TEXT
);

CREATE TABLE IF NOT EXISTS investigators (
  id TEXT PRIMARY KEY,
  name TEXT,
  role TEXT,
  phone TEXT,
  email TEXT,
  notes TEXT,
  active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS equipment (
  id TEXT PRIMARY KEY,
  name TEXT,
  type TEXT,
  serial TEXT,
  status TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS equipment_usage (
  id TEXT PRIMARY KEY,
  investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  equipment_id TEXT NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
  assigned_to TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS experiences (
  id TEXT PRIMARY KEY,
  investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  person TEXT,
  description TEXT,
  occurred_at TEXT,
  location_hint TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  type TEXT,
  file_path TEXT,
  description TEXT,
  captured_at TEXT
);

CREATE TABLE IF NOT EXISTS explanations (
  investigation_id TEXT PRIMARY KEY REFERENCES investigations(id) ON DELETE CASCADE,
  text TEXT
);

CREATE TABLE IF NOT EXISTS summation (
  investigation_id TEXT PRIMARY KEY REFERENCES investigations(id) ON DELETE CASCADE,
  conclusions TEXT,
  additional_comments TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
  id TEXT PRIMARY KEY,
  investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  text TEXT
);

CREATE TABLE IF NOT EXISTS letterhead (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT,
  contact_block TEXT,
  logo_path TEXT,
  logo_position TEXT
);

CREATE TABLE IF NOT EXISTS cover_letter (
  investigation_id TEXT PRIMARY KEY REFERENCES investigations(id) ON DELETE CASCADE,
  use_letterhead INTEGER,
  show_case_name INTEGER,
  show_case_number INTEGER,
  show_location INTEGER,
  show_date INTEGER,
  show_reporting_investigator INTEGER,
  intro TEXT,
  disclaimer TEXT
);
"""

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    cur = con.cursor()
    if not cur.execute("SELECT 1 FROM letterhead WHERE id=1").fetchone():
        cur.execute("INSERT INTO letterhead (id, name, contact_block, logo_path, logo_position) VALUES (1,'','','','TopLeft')")
    con.commit()
    con.close()

def uid(): return str(uuid.uuid4())

class OpenDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Open Investigation")
        self.geometry("820x480")
        self.result = None
        cols = ("id","case_number","case_name","start_time","created_at")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        widths = (260,120,200,120,140)
        for c,w in zip(cols,widths):
            self.tree.heading(c, text=c.replace("_"," ").title())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        btns = ttk.Frame(self); btns.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btns, text="Open", command=self._open).pack(side="right", padx=5)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")
        con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
        for r in con.execute("SELECT id, case_number, case_name, start_time, created_at FROM investigations ORDER BY datetime(created_at) DESC"):
            self.tree.insert("", "end", values=(r["id"], r["case_number"], r["case_name"], r["start_time"], r["created_at"]))
        con.close()
        self.tree.bind("<Double-1>", lambda e: self._open())

    def _open(self):
        sel = self.tree.focus()
        if not sel:
            return
        self.result = self.tree.item(sel)["values"][0]
        self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1250x850")
        self.minsize(1050, 720)
        init_db()
        self.current_id = None
        self._build_menu()
        self._build_tabs()
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=8, pady=(0,8))
        self.bind_all("<Control-s>", lambda e: self.save_all())
        self.bind_all("<Control-o>", lambda e: self.open_investigation())
        self.bind_all("<Control-n>", lambda e: self.new_investigation())

    # Menu
    def _build_menu(self):
        m = tk.Menu(self)
        f = tk.Menu(m, tearoff=0)
        f.add_command(label="New    Ctrl+N", command=self.new_investigation)
        f.add_command(label="Open   Ctrl+O", command=self.open_investigation)
        f.add_separator()
        f.add_command(label="Save   Ctrl+S", command=self.save_all)
        f.add_separator()
        f.add_command(label="Exit", command=self.quit)
        m.add_cascade(label="File", menu=f)
        self.config(menu=m)

    # Tabs
    def _build_tabs(self):
        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=True, padx=8, pady=8)
        self._tab_contact_location()
        self._tab_location_history()
        self._tab_witnesses()
        self._tab_investigation_log()
        self._tab_experiences()
        self._tab_evidence_explanations()
        self._tab_summation()
        self._tab_recommendations()
        self._tab_investigators()
        self._tab_equipment()
        self._tab_letterhead()
        self._tab_cover_letter()

    # Contact & Location
    def _tab_contact_location(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Contact & Location")
        box_inv = ttk.LabelFrame(f, text="Investigation"); box_inv.pack(fill="x", padx=8, pady=8)
        self.var_case_number = tk.StringVar()
        self.var_case_name   = tk.StringVar()
        self.var_start_time  = tk.StringVar(value=datetime.datetime.now().isoformat(timespec="minutes"))
        self.var_end_time    = tk.StringVar()
        ttk.Label(box_inv, text="Case Number").grid(row=0,column=0,sticky="e",padx=4,pady=4)
        ttk.Entry(box_inv, textvariable=self.var_case_number, width=24).grid(row=0,column=1,sticky="w",padx=4,pady=4)
        ttk.Label(box_inv, text="Case Name").grid(row=0,column=2,sticky="e",padx=4,pady=4)
        ttk.Entry(box_inv, textvariable=self.var_case_name, width=46).grid(row=0,column=3,sticky="w",padx=4,pady=4)
        ttk.Label(box_inv, text="Start").grid(row=1,column=0,sticky="e",padx=4,pady=4)
        ttk.Entry(box_inv, textvariable=self.var_start_time, width=24).grid(row=1,column=1,sticky="w",padx=4,pady=4)
        ttk.Label(box_inv, text="End").grid(row=1,column=2,sticky="e",padx=4,pady=4)
        ttk.Entry(box_inv, textvariable=self.var_end_time, width=24).grid(row=1,column=3,sticky="w",padx=4,pady=4)

        box_contact = ttk.LabelFrame(f, text="Client / Contact"); box_contact.pack(fill="x", padx=8, pady=8)
        self.var_contact_name  = tk.StringVar()
        self.var_contact_phone = tk.StringVar()
        self.var_contact_email = tk.StringVar()
        ttk.Label(box_contact, text="Name").grid(row=0,column=0,sticky="e",padx=4,pady=4)
        ttk.Entry(box_contact, textvariable=self.var_contact_name, width=28).grid(row=0,column=1,sticky="w",padx=4,pady=4)
        ttk.Label(box_contact, text="Phone").grid(row=0,column=2,sticky="e",padx=4,pady=4)
        ttk.Entry(box_contact, textvariable=self.var_contact_phone, width=20).grid(row=0,column=3,sticky="w",padx=4,pady=4)
        ttk.Label(box_contact, text="Email").grid(row=0,column=4,sticky="e",padx=4,pady=4)
        ttk.Entry(box_contact, textvariable=self.var_contact_email, width=30).grid(row=0,column=5,sticky="w",padx=4,pady=4)

        box_loc = ttk.LabelFrame(f, text="Location"); box_loc.pack(fill="both", expand=True, padx=8, pady=8)
        self.var_location_name = tk.StringVar()
        self.var_location_address = tk.StringVar()
        self.txt_location_desc = tk.Text(box_loc, height=4)
        self.txt_notes = tk.Text(box_loc, height=4)
        ttk.Label(box_loc, text="Name").grid(row=0,column=0,sticky="e",padx=4,pady=4)
        ttk.Entry(box_loc, textvariable=self.var_location_name, width=40).grid(row=0,column=1,sticky="w",padx=4,pady=4)
        ttk.Label(box_loc, text="Address").grid(row=0,column=2,sticky="e",padx=4,pady=4)
        ttk.Entry(box_loc, textvariable=self.var_location_address, width=40).grid(row=0,column=3,sticky="w",padx=4,pady=4)
        ttk.Label(box_loc, text="Description").grid(row=1,column=0,sticky="ne",padx=4,pady=4)
        self.txt_location_desc.grid(row=1,column=1,columnspan=3,sticky="we",padx=4,pady=4)
        ttk.Label(box_loc, text="Additional Notes / Directions").grid(row=2,column=0,sticky="ne",padx=4,pady=4)
        self.txt_notes.grid(row=2,column=1,columnspan=3,sticky="we",padx=4,pady=4)
        for i in range(4): box_loc.grid_columnconfigure(i, weight=1)

    # Location History
    def _tab_location_history(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Location History")
        self.txt_hist_history = tk.Text(f, height=8); self.txt_hist_history.pack(fill="x", padx=8, pady=(8,4))
        self.txt_hist_docs = tk.Text(f, height=4); self.txt_hist_docs.pack(fill="x", padx=8, pady=4)
        row = ttk.Frame(f); row.pack(fill="x", padx=8, pady=4)
        self.var_hist_built = tk.StringVar(); self.var_hist_structures = tk.StringVar(); self.var_hist_rooms = tk.StringVar()
        ttk.Label(row, text="Built/Age").grid(row=0,column=0,sticky="e"); ttk.Entry(row, textvariable=self.var_hist_built, width=20).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(row, text="Structures").grid(row=0,column=2,sticky="e"); ttk.Entry(row, textvariable=self.var_hist_structures, width=30).grid(row=0,column=3,sticky="w",padx=6)
        ttk.Label(row, text="Rooms").grid(row=0,column=4,sticky="e"); ttk.Entry(row, textvariable=self.var_hist_rooms, width=20).grid(row=0,column=5,sticky="w",padx=6)
        row2 = ttk.Frame(f); row2.pack(fill="x", padx=8, pady=4)
        self.txt_hist_paranormal_areas = tk.Text(row2, height=4, width=80); self.txt_hist_paranormal_areas.grid(row=0,column=0,sticky="w")
        self.var_hist_renovated = tk.BooleanVar(value=False); self.var_hist_blessed = tk.BooleanVar(value=False)
        col = ttk.Frame(row2); col.grid(row=0,column=1,sticky="nw",padx=12)
        ttk.Checkbutton(col, text="Renovated Recently", variable=self.var_hist_renovated).pack(anchor="w")
        ttk.Checkbutton(col, text="Blessed Before", variable=self.var_hist_blessed).pack(anchor="w")

    # Witnesses
    def _tab_witnesses(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Witnesses")
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=8)
        self.var_w_name  = tk.StringVar(); self.var_w_phone = tk.StringVar(); self.var_w_email = tk.StringVar()
        ttk.Label(top, text="Name").grid(row=0,column=0,sticky="e",padx=4); ttk.Entry(top,textvariable=self.var_w_name,width=24).grid(row=0,column=1,sticky="w")
        ttk.Label(top, text="Phone").grid(row=0,column=2,sticky="e",padx=4); ttk.Entry(top,textvariable=self.var_w_phone,width=16).grid(row=0,column=3,sticky="w")
        ttk.Label(top, text="Email").grid(row=0,column=4,sticky="e",padx=4); ttk.Entry(top,textvariable=self.var_w_email,width=28).grid(row=0,column=5,sticky="w")
        ttk.Label(top, text="Statement").grid(row=1,column=0,sticky="ne",padx=4,pady=(6,0))
        self.txt_w_stmt = tk.Text(top, height=4, width=80); self.txt_w_stmt.grid(row=1,column=1,columnspan=5,sticky="we",pady=(6,0))
        ttk.Button(top, text="Add Witness", command=self.add_witness).grid(row=2,column=1,sticky="w",pady=8)
        self.tree_w = ttk.Treeview(f, columns=("name","phone","email","statement"), show="headings", height=12)
        for c in ("name","phone","email","statement"):
            self.tree_w.heading(c, text=c.title()); self.tree_w.column(c, width=160 if c!="statement" else 500, anchor="w")
        self.tree_w.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_witness).pack(anchor="e", padx=8, pady=(0,8))

    def add_witness(self):
        n = self.var_w_name.get().strip()
        if not n:
            return messagebox.showerror("Witness","Name required")
        row = (n, self.var_w_phone.get().strip(), self.var_w_email.get().strip(), self.txt_w_stmt.get("1.0","end").strip())
        self.tree_w.insert("", "end", values=row)
        self.var_w_name.set(""); self.var_w_phone.set(""); self.var_w_email.set(""); self.txt_w_stmt.delete("1.0","end")

    def remove_selected_witness(self):
        sel = self.tree_w.focus()
        if sel: self.tree_w.delete(sel)

    # Investigation Log (+ Equipment Assigned)
    def _tab_investigation_log(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Investigation Log")
        grid = ttk.Frame(f); grid.pack(fill="x", padx=8, pady=8)
        self.var_log_lead = tk.StringVar(); self.var_log_team = tk.StringVar(); self.var_log_guests = tk.StringVar(); self.var_log_equipment = tk.StringVar()
        self.var_log_weather = tk.StringVar(); self.var_log_moon = tk.StringVar()
        self.var_log_start = tk.StringVar(); self.var_log_end = tk.StringVar()
        ttk.Label(grid, text="Lead Investigator").grid(row=0,column=0,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_lead, width=24).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(grid, text="Team").grid(row=0,column=2,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_team, width=36).grid(row=0,column=3,sticky="w",padx=6)
        ttk.Label(grid, text="Guests").grid(row=1,column=0,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_guests, width=24).grid(row=1,column=1,sticky="w",padx=6)
        ttk.Label(grid, text="Equipment (notes)").grid(row=1,column=2,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_equipment, width=36).grid(row=1,column=3,sticky="w",padx=6)
        ttk.Label(grid, text="Weather").grid(row=2,column=0,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_weather, width=24).grid(row=2,column=1,sticky="w",padx=6)
        ttk.Label(grid, text="Moon Cycle").grid(row=2,column=2,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_moon, width=24).grid(row=2,column=3,sticky="w",padx=6)
        ttk.Label(grid, text="Start Time").grid(row=3,column=0,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_start, width=24).grid(row=3,column=1,sticky="w",padx=6)
        ttk.Label(grid, text="End Time").grid(row=3,column=2,sticky="e"); ttk.Entry(grid, textvariable=self.var_log_end, width=24).grid(row=3,column=3,sticky="w",padx=6)
        ttk.Label(f, text="Observations").pack(anchor="w", padx=8)
        self.txt_log_observations = tk.Text(f, height=6); self.txt_log_observations.pack(fill="x", padx=8, pady=8)

        frame_eq = ttk.LabelFrame(f, text="Equipment Assigned (for this investigation)")
        frame_eq.pack(fill="both", expand=True, padx=8, pady=(0,8))
        row = ttk.Frame(frame_eq); row.pack(fill="x", padx=8, pady=8)
        self.var_assign_equipment = tk.StringVar()
        self.cbo_assign_equipment = ttk.Combobox(row, textvariable=self.var_assign_equipment, width=40, state="readonly")
        self.cbo_assign_equipment.grid(row=0, column=0, sticky="w")
        ttk.Button(row, text="Refresh List", command=self.refresh_equipment_combo).grid(row=0, column=1, padx=6)
        ttk.Label(row, text="Assigned To").grid(row=0, column=2, padx=(16,4))
        self.var_assign_to = tk.StringVar()
        ttk.Entry(row, textvariable=self.var_assign_to, width=24).grid(row=0, column=3)
        ttk.Label(row, text="Notes").grid(row=0, column=4, padx=(16,4))
        self.var_assign_notes = tk.StringVar()
        ttk.Entry(row, textvariable=self.var_assign_notes, width=36).grid(row=0, column=5)
        ttk.Button(row, text="Add Assignment", command=self.add_equipment_assignment).grid(row=0, column=6, padx=6)

        self.tree_usage = ttk.Treeview(frame_eq, columns=("equipment","assigned_to","notes"), show="headings", height=10)
        for c in ("equipment","assigned_to","notes"):
            self.tree_usage.heading(c, text=c.replace("_"," ").title())
            self.tree_usage.column(c, width=220 if c!="notes" else 420, anchor="w")
        self.tree_usage.pack(fill="both", expand=True, padx=8, pady=(0,8))
        ttk.Button(frame_eq, text="Remove Selected", command=self.remove_selected_assignment).pack(anchor="e", padx=8, pady=(0,8))

    # Experiences
    def _tab_experiences(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Personal Experiences")
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=8)
        self.var_exp_person = tk.StringVar(); self.var_exp_time = tk.StringVar(); self.var_exp_loc = tk.StringVar()
        ttk.Label(top, text="Person").grid(row=0,column=0,sticky="e"); ttk.Entry(top, textvariable=self.var_exp_person, width=24).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(top, text="When").grid(row=0,column=2,sticky="e"); ttk.Entry(top, textvariable=self.var_exp_time, width=24).grid(row=0,column=3,sticky="w",padx=6)
        ttk.Label(top, text="Where").grid(row=0,column=4,sticky="e"); ttk.Entry(top, textvariable=self.var_exp_loc, width=24).grid(row=0,column=5,sticky="w",padx=6)
        self.txt_exp_desc = tk.Text(f, height=4); self.txt_exp_desc.pack(fill="x", padx=8, pady=4)
        ttk.Button(f, text="Add Experience", command=self.add_experience).pack(anchor="w", padx=8, pady=6)
        self.tree_exp = ttk.Treeview(f, columns=("person","when","where","description"), show="headings", height=10)
        for c in ("person","when","where","description"):
            self.tree_exp.heading(c, text=c.title()); self.tree_exp.column(c, width=160 if c!="description" else 540, anchor="w")
        self.tree_exp.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_experience).pack(anchor="e", padx=8, pady=(0,8))

    def add_experience(self):
        person = self.var_exp_person.get().strip()
        desc = self.txt_exp_desc.get("1.0","end").strip()
        if not person and not desc:
            return
        self.tree_exp.insert("", "end", values=(person, self.var_exp_time.get().strip(), self.var_exp_loc.get().strip(), desc))
        self.var_exp_person.set(""); self.var_exp_time.set(""); self.var_exp_loc.set(""); self.txt_exp_desc.delete("1.0","end")

    def remove_selected_experience(self):
        sel = self.tree_exp.focus()
        if sel: self.tree_exp.delete(sel)

    # Evidence / Explanations
    def _tab_evidence_explanations(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Physical Evidence / Explanations")
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=8)
        self.var_e_type = tk.StringVar(value="photo"); self.var_e_file = tk.StringVar(); self.var_e_desc = tk.StringVar()
        ttk.Label(top, text="Type").grid(row=0,column=0,sticky="e"); ttk.Combobox(top, textvariable=self.var_e_type, values=["photo","evp","video","doc"], width=10, state="readonly").grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(top, text="File").grid(row=0,column=2,sticky="e"); ttk.Entry(top, textvariable=self.var_e_file, width=50).grid(row=0,column=3,sticky="we",padx=6)
        ttk.Button(top, text="Browse", command=self.pick_evidence_file).grid(row=0,column=4, padx=4)
        ttk.Label(top, text="Description").grid(row=1,column=0,sticky="e"); ttk.Entry(top, textvariable=self.var_e_desc, width=70).grid(row=1,column=1,columnspan=3,sticky="we",padx=6)
        ttk.Button(top, text="Add Evidence", command=self.add_evidence).grid(row=1,column=4)
        self.tree_e = ttk.Treeview(f, columns=("type","file","description"), show="headings", height=10)
        for c in ("type","file","description"):
            self.tree_e.heading(c, text=c.title()); self.tree_e.column(c, width=160 if c!="file" else 520, anchor="w")
        self.tree_e.pack(fill="both", expand=True, padx=8, pady=4)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_evidence).pack(anchor="e", padx=8, pady=(0,8))
        ttk.Label(f, text="Explanations (natural causes / analysis)").pack(anchor="w", padx=8)
        self.txt_explanations = tk.Text(f, height=6); self.txt_explanations.pack(fill="both", expand=False, padx=8, pady=(4,8))

    def pick_evidence_file(self):
        p = filedialog.askopenfilename(title="Choose evidence file",
            filetypes=[("All files","*.*"), ("Images","*.png;*.jpg;*.jpeg;*.bmp"), ("Audio","*.wav;*.mp3"), ("Video","*.mp4;*.mov;*.avi")])
        if p: self.var_e_file.set(p)

    def add_evidence(self):
        if not self.var_e_file.get().strip() and not self.var_e_desc.get().strip():
            return
        self.tree_e.insert("", "end", values=(self.var_e_type.get(), self.var_e_file.get().strip(), self.var_e_desc.get().strip()))
        self.var_e_file.set(""); self.var_e_desc.set("")

    def remove_selected_evidence(self):
        sel = self.tree_e.focus()
        if sel: self.tree_e.delete(sel)

    # Summation
    def _tab_summation(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Summation & Conclusions")
        ttk.Label(f, text="Conclusions").pack(anchor="w", padx=8, pady=(8,0))
        self.txt_sum_conclusions = tk.Text(f, height=8); self.txt_sum_conclusions.pack(fill="both", expand=True, padx=8, pady=4)
        ttk.Label(f, text="Additional Comments").pack(anchor="w", padx=8, pady=(8,0))
        self.txt_sum_additional = tk.Text(f, height=6); self.txt_sum_additional.pack(fill="both", expand=True, padx=8, pady=(4,8))

    # Recommendations
    def _tab_recommendations(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Recommendations")
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=8)
        self.var_rec = tk.StringVar()
        ttk.Entry(top, textvariable=self.var_rec, width=80).pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="Add Recommendation", command=self.add_recommendation).pack(side="left", padx=6)
        self.tree_rec = ttk.Treeview(f, columns=("text",), show="headings", height=12)
        self.tree_rec.heading("text", text="Recommendation"); self.tree_rec.column("text", width=900, anchor="w")
        self.tree_rec.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_recommendation).pack(anchor="e", padx=8, pady=(0,8))

    def add_recommendation(self):
        t = self.var_rec.get().strip()
        if t:
            self.tree_rec.insert("", "end", values=(t,))
            self.var_rec.set("")

    def remove_selected_recommendation(self):
        sel = self.tree_rec.focus()
        if sel: self.tree_rec.delete(sel)

    # Investigators
    def _tab_investigators(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Investigators")
        form = ttk.Frame(f); form.pack(fill="x", padx=8, pady=8)
        self.var_inv_name = tk.StringVar(); self.var_inv_role = tk.StringVar()
        self.var_inv_phone = tk.StringVar(); self.var_inv_email = tk.StringVar()
        self.var_inv_notes = tk.StringVar()
        ttk.Label(form, text="Name").grid(row=0,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_inv_name, width=28).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(form, text="Role").grid(row=0,column=2,sticky="e"); ttk.Entry(form, textvariable=self.var_inv_role, width=20).grid(row=0,column=3,sticky="w",padx=6)
        ttk.Label(form, text="Phone").grid(row=1,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_inv_phone, width=20).grid(row=1,column=1,sticky="w",padx=6)
        ttk.Label(form, text="Email").grid(row=1,column=2,sticky="e"); ttk.Entry(form, textvariable=self.var_inv_email, width=28).grid(row=1,column=3,sticky="w",padx=6)
        ttk.Label(form, text="Notes").grid(row=2,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_inv_notes, width=60).grid(row=2,column=1,columnspan=3,sticky="we",padx=6)
        ttk.Button(form, text="Add Investigator", command=self.add_investigator).grid(row=3,column=1,sticky="w",pady=6)
        self.tree_invest = ttk.Treeview(f, columns=("name","role","phone","email","notes"), show="headings", height=12)
        for c, w in zip(("name","role","phone","email","notes"), (200,120,120,220,360)):
            self.tree_invest.heading(c, text=c.title()); self.tree_invest.column(c, width=w, anchor="w")
        self.tree_invest.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_investigator).pack(anchor="e", padx=8, pady=(0,8))
        self.refresh_investigator_tree()

    def add_investigator(self):
        name = self.var_inv_name.get().strip()
        if not name:
            return messagebox.showerror("Investigators","Name required")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("INSERT INTO investigators (id, name, role, phone, email, notes, active) VALUES (?,?,?,?,?,?,1)",
                    (uid(), name, self.var_inv_role.get().strip(), self.var_inv_phone.get().strip(),
                     self.var_inv_email.get().strip(), self.var_inv_notes.get().strip()))
        con.commit(); con.close()
        self.var_inv_name.set(""); self.var_inv_role.set(""); self.var_inv_phone.set(""); self.var_inv_email.set(""); self.var_inv_notes.set("")
        self.refresh_investigator_tree()

    def remove_selected_investigator(self):
        sel = self.tree_invest.focus()
        if not sel: return
        vals = self.tree_invest.item(sel)["values"]
        name = vals[0]
        if not messagebox.askyesno("Remove", f"Remove investigator '{name}'?"):
            return
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("DELETE FROM investigators WHERE name=? AND phone=? AND email=?", (vals[0], vals[2], vals[3]))
        con.commit(); con.close()
        self.refresh_investigator_tree()

    def refresh_investigator_tree(self):
        for i in getattr(self, "tree_invest", []).get_children(): self.tree_invest.delete(i)
        con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM investigators WHERE active=1 ORDER BY name").fetchall()
        con.close()
        for r in rows:
            self.tree_invest.insert("", "end", values=(r["name"] or "", r["role"] or "", r["phone"] or "", r["email"] or "", r["notes"] or ""))

    # Equipment
    def _tab_equipment(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Equipment")
        form = ttk.Frame(f); form.pack(fill="x", padx=8, pady=8)
        self.var_eq_name = tk.StringVar(); self.var_eq_type = tk.StringVar()
        self.var_eq_serial = tk.StringVar(); self.var_eq_status = tk.StringVar(value="Available")
        self.var_eq_notes = tk.StringVar()
        ttk.Label(form, text="Name").grid(row=0,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_eq_name, width=28).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(form, text="Type").grid(row=0,column=2,sticky="e"); ttk.Entry(form, textvariable=self.var_eq_type, width=20).grid(row=0,column=3,sticky="w",padx=6)
        ttk.Label(form, text="Serial").grid(row=1,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_eq_serial, width=24).grid(row=1,column=1,sticky="w",padx=6)
        ttk.Label(form, text="Status").grid(row=1,column=2,sticky="e"); ttk.Combobox(form, textvariable=self.var_eq_status, values=["Available","In Use","Needs Repair"], width=18, state="readonly").grid(row=1,column=3,sticky="w",padx=6)
        ttk.Label(form, text="Notes").grid(row=2,column=0,sticky="e"); ttk.Entry(form, textvariable=self.var_eq_notes, width=60).grid(row=2,column=1,columnspan=3,sticky="we",padx=6)
        ttk.Button(form, text="Add Equipment", command=self.add_equipment).grid(row=3,column=1,sticky="w",pady=6)

        self.tree_equipment = ttk.Treeview(f, columns=("name","type","serial","status","notes"), show="headings", height=12)
        for c, w in zip(("name","type","serial","status","notes"), (220,140,180,120,420)):
            self.tree_equipment.heading(c, text=c.title()); self.tree_equipment.column(c, width=w, anchor="w")
        self.tree_equipment.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(f, text="Remove Selected", command=self.remove_selected_equipment).pack(anchor="e", padx=8, pady=(0,8))
        self.refresh_equipment_tree()

    def add_equipment(self):
        name = self.var_eq_name.get().strip()
        if not name:
            return messagebox.showerror("Equipment","Name required")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("INSERT INTO equipment (id, name, type, serial, status, notes) VALUES (?,?,?,?,?,?)",
                    (uid(), name, self.var_eq_type.get().strip(), self.var_eq_serial.get().strip(),
                     self.var_eq_status.get().strip(), self.var_eq_notes.get().strip()))
        con.commit(); con.close()
        self.var_eq_name.set(""); self.var_eq_type.set(""); self.var_eq_serial.set(""); self.var_eq_status.set("Available"); self.var_eq_notes.set("")
        self.refresh_equipment_tree()
        self.refresh_equipment_combo()

    def remove_selected_equipment(self):
        sel = self.tree_equipment.focus()
        if not sel: return
        vals = self.tree_equipment.item(sel)["values"]
        name = vals[0]
        if not messagebox.askyesno("Remove", f"Remove equipment '{name}'?"):
            return
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("DELETE FROM equipment WHERE name=? AND serial=?", (vals[0], vals[2]))
        con.commit(); con.close()
        self.refresh_equipment_tree()
        self.refresh_equipment_combo()

    def refresh_equipment_tree(self):
        for i in getattr(self, "tree_equipment", []).get_children(): self.tree_equipment.delete(i)
        con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM equipment ORDER BY name").fetchall(); con.close()
        for r in rows:
            self.tree_equipment.insert("", "end", values=(r["name"] or "", r["type"] or "", r["serial"] or "", r["status"] or "", r["notes"] or ""))

    # Letterhead
    def _tab_letterhead(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Letterhead")
        self.var_lh_name = tk.StringVar(); self.var_lh_logo = tk.StringVar(); self.var_lh_pos = tk.StringVar(value="TopLeft")
        row = ttk.Frame(f); row.pack(fill="x", padx=8, pady=8)
        ttk.Label(row, text="Letterhead Name").grid(row=0,column=0,sticky="e"); ttk.Entry(row, textvariable=self.var_lh_name, width=40).grid(row=0,column=1,sticky="w",padx=6)
        ttk.Label(row, text="Logo Path").grid(row=0,column=2,sticky="e"); ttk.Entry(row, textvariable=self.var_lh_logo, width=50).grid(row=0,column=3,sticky="we",padx=6)
        ttk.Button(row, text="Browse", command=self.pick_logo).grid(row=0,column=4, padx=4)
        ttk.Label(row, text="Logo Position").grid(row=1,column=0,sticky="e"); ttk.Combobox(row, textvariable=self.var_lh_pos, values=["TopLeft","TopCenter","TopRight"], width=12, state="readonly").grid(row=1,column=1,sticky="w",padx=6)
        ttk.Label(f, text="Contact Block").pack(anchor="w", padx=8)
        self.txt_lh_contact = tk.Text(f, height=6); self.txt_lh_contact.pack(fill="both", expand=True, padx=8, pady=(4,8))

    def pick_logo(self):
        p = filedialog.askopenfilename(title="Pick logo image", filetypes=[("Images","*.png;*.jpg;*.jpeg;*.bmp;*.ico"), ("All files","*.*")])
        if p: self.var_lh_logo.set(p)

    # Cover Letter
    def _tab_cover_letter(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Cover Letter")
        self.var_cov_use = tk.BooleanVar(value=True)
        self.var_cov_casename = tk.BooleanVar(value=True)
        self.var_cov_casenumber = tk.BooleanVar(value=True)
        self.var_cov_location = tk.BooleanVar(value=True)
        self.var_cov_date = tk.BooleanVar(value=True)
        self.var_cov_reporter = tk.BooleanVar(value=True)
        checks = ttk.Frame(f); checks.pack(fill="x", padx=8, pady=8)
        ttk.Checkbutton(checks, text="Use Letterhead", variable=self.var_cov_use).grid(row=0,column=0,sticky="w")
        ttk.Checkbutton(checks, text="Show Case Name", variable=self.var_cov_casename).grid(row=0,column=1,sticky="w")
        ttk.Checkbutton(checks, text="Show Case Number", variable=self.var_cov_casenumber).grid(row=0,column=2,sticky="w")
        ttk.Checkbutton(checks, text="Show Location", variable=self.var_cov_location).grid(row=0,column=3,sticky="w")
        ttk.Checkbutton(checks, text="Show Date", variable=self.var_cov_date).grid(row=1,column=0,sticky="w")
        ttk.Checkbutton(checks, text="Show Reporting Investigator", variable=self.var_cov_reporter).grid(row=1,column=1,sticky="w")
        ttk.Label(f, text="Intro").pack(anchor="w", padx=8)
        self.txt_cov_intro = tk.Text(f, height=6); self.txt_cov_intro.pack(fill="both", expand=True, padx=8, pady=(4,8))
        ttk.Label(f, text="Disclaimer").pack(anchor="w", padx=8)
        self.txt_cov_disclaimer = tk.Text(f, height=6); self.txt_cov_disclaimer.pack(fill="both", expand=True, padx=8, pady=(4,8))

    # ----- Assignments helpers -----
    def refresh_equipment_combo(self):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        rows = cur.execute("SELECT id, name, COALESCE(serial,'') FROM equipment ORDER BY name").fetchall()
        con.close()
        pretty = []
        self._equip_map = {}
        for eid, name, serial in rows:
            label = f"{name} ({serial})" if serial else name
            pretty.append(label)
            self._equip_map[label] = eid
        self.cbo_assign_equipment["values"] = pretty
        if pretty and not self.var_assign_equipment.get():
            self.var_assign_equipment.set(pretty[0])

    def add_equipment_assignment(self):
        if not self.current_id:
            return messagebox.showerror("Assignments","Save the investigation header first (case name).")
        label = self.var_assign_equipment.get()
        if not label or not hasattr(self, "_equip_map") or label not in self._equip_map:
            return messagebox.showerror("Assignments","Pick equipment from the list.")
        eq_id = self._equip_map[label]
        assigned_to = self.var_assign_to.get().strip()
        notes = self.var_assign_notes.get().strip()
        self.tree_usage.insert("", "end", values=(label, assigned_to, notes))
        self.var_assign_to.set(""); self.var_assign_notes.set("")

    def remove_selected_assignment(self):
        sel = self.tree_usage.focus()
        if sel: self.tree_usage.delete(sel)

    # Actions
    def new_investigation(self):
        if not self._confirm_discard():
            return
        self.current_id = None
        self._clear_all()
        self.status.set("New investigation started.")

    def open_investigation(self):
        dlg = OpenDialog(self); self.wait_window(dlg)
        if not dlg.result: return
        inv_id = dlg.result
        con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
        inv = con.execute("SELECT * FROM investigations WHERE id=?", (inv_id,)).fetchone()
        loc_hist = con.execute("SELECT * FROM location_history WHERE investigation_id=?", (inv_id,)).fetchone()
        log = con.execute("SELECT * FROM investigation_log WHERE investigation_id=?", (inv_id,)).fetchone()
        cov = con.execute("SELECT * FROM cover_letter WHERE investigation_id=?", (inv_id,)).fetchone()
        expl = con.execute("SELECT * FROM explanations WHERE investigation_id=?", (inv_id,)).fetchone()
        sumrow = con.execute("SELECT * FROM summation WHERE investigation_id=?", (inv_id,)).fetchone()
        witnesses = con.execute("SELECT * FROM witnesses WHERE investigation_id=?", (inv_id,)).fetchall()
        evidence = con.execute("SELECT * FROM evidence WHERE investigation_id=?", (inv_id,)).fetchall()
        exps = con.execute("SELECT * FROM experiences WHERE investigation_id=?", (inv_id,)).fetchall()
        recs = con.execute("SELECT * FROM recommendations WHERE investigation_id=?", (inv_id,)).fetchall()
        usage = con.execute("""
            SELECT eu.*, e.name, e.serial
            FROM equipment_usage eu
            JOIN equipment e ON e.id = eu.equipment_id
            WHERE eu.investigation_id=?
        """, (inv_id,)).fetchall()
        lh = con.execute("SELECT * FROM letterhead WHERE id=1").fetchone()
        con.close()

        self.current_id = inv_id
        self.var_case_number.set(inv["case_number"] or ""); self.var_case_name.set(inv["case_name"] or "")
        self.var_start_time.set(inv["start_time"] or ""); self.var_end_time.set(inv["end_time"] or "")
        self.var_contact_name.set(inv["contact_name"] or ""); self.var_contact_phone.set(inv["contact_phone"] or ""); self.var_contact_email.set(inv["contact_email"] or "")
        self.var_location_name.set(inv["location_name"] or ""); self.var_location_address.set(inv["location_address"] or "")
        self.txt_location_desc.delete("1.0","end"); self.txt_location_desc.insert("1.0", inv["location_description"] or "")
        self.txt_notes.delete("1.0","end"); self.txt_notes.insert("1.0", inv["notes"] or "")

        self.txt_hist_history.delete("1.0","end"); self.txt_hist_docs.delete("1.0","end"); self.txt_hist_paranormal_areas.delete("1.0","end")
        if loc_hist:
            self.txt_hist_history.insert("1.0", loc_hist["history"] or "")
            self.txt_hist_docs.insert("1.0", loc_hist["documentation"] or "")
            self.var_hist_built.set(loc_hist["built_date"] or ""); self.var_hist_structures.set(loc_hist["structures"] or ""); self.var_hist_rooms.set(loc_hist["rooms"] or "")
            self.txt_hist_paranormal_areas.insert("1.0", loc_hist["paranormal_areas"] or "")
            self.var_hist_renovated.set(bool(loc_hist["renovated_recently"])); self.var_hist_blessed.set(bool(loc_hist["blessed_before"]))
        else:
            self.var_hist_built.set(""); self.var_hist_structures.set(""); self.var_hist_rooms.set(""); self.var_hist_renovated.set(False); self.var_hist_blessed.set(False)

        self.var_log_lead.set(log["lead_investigator"] if log else "")
        self.var_log_team.set(log["team"] if log else "")
        self.var_log_guests.set(log["guests"] if log else "")
        self.var_log_equipment.set(log["equipment"] if log else "")
        self.var_log_weather.set(log["weather"] if log else "")
        self.var_log_moon.set(log["moon_cycle"] if log else "")
        self.var_log_start.set(log["start_time"] if log else "")
        self.var_log_end.set(log["end_time"] if log else "")
        self.txt_log_observations.delete("1.0","end"); self.txt_log_observations.insert("1.0", log["observations"] if log else "")

        for i in self.tree_w.get_children(): self.tree_w.delete(i)
        for w in witnesses:
            self.tree_w.insert("", "end", values=(w["name"] or "", w["phone"] or "", w["email"] or "", (w["statement"] or "")[:500]))

        for i in self.tree_e.get_children(): self.tree_e.delete(i)
        for e in evidence:
            self.tree_e.insert("", "end", values=(e["type"] or "", e["file_path"] or "", e["description"] or ""))

        self.txt_explanations.delete("1.0","end"); self.txt_explanations.insert("1.0", expl["text"] if expl else "")

        for i in self.tree_exp.get_children(): self.tree_exp.delete(i)
        for x in exps:
            self.tree_exp.insert("", "end", values=(x["person"] or "", x["occurred_at"] or "", x["location_hint"] or "", x["description"] or ""))

        for i in self.tree_rec.get_children(): self.tree_rec.delete(i)
        for r in recs:
            self.tree_rec.insert("", "end", values=(r["text"] or "",))

        for i in self.tree_usage.get_children(): self.tree_usage.delete(i)
        for u in usage:
            label = f"{u['name']} ({u['serial']})" if u["serial"] else (u["name"] or "")
            self.tree_usage.insert("", "end", values=(label, u["assigned_to"] or "", u["notes"] or ""))

        self.var_lh_name.set(lh["name"] or "")
        self.txt_lh_contact.delete("1.0","end"); self.txt_lh_contact.insert("1.0", lh["contact_block"] or "")
        self.var_lh_logo.set(lh["logo_path"] or ""); self.var_lh_pos.set(lh["logo_position"] or "TopLeft")

        self.var_cov_use.set(bool(cov["use_letterhead"]) if cov else True)
        self.var_cov_casename.set(bool(cov["show_case_name"]) if cov else True)
        self.var_cov_casenumber.set(bool(cov["show_case_number"]) if cov else True)
        self.var_cov_location.set(bool(cov["show_location"]) if cov else True)
        self.var_cov_date.set(bool(cov["show_date"]) if cov else True)
        self.var_cov_reporter.set(bool(cov["show_reporting_investigator"]) if cov else True)
        self.txt_cov_intro.delete("1.0","end"); self.txt_cov_intro.insert("1.0", cov["intro"] if cov else "")
        self.txt_cov_disclaimer.delete("1.0","end"); self.txt_cov_disclaimer.insert("1.0", cov["disclaimer"] if cov else "")
        self.status.set(f"Opened: {inv['case_name']}")

    def save_all(self):
        case_name = (self.var_case_name.get() or "").strip()
        if not case_name:
            return messagebox.showerror("Save","Case Name is required.")
        inv = dict(
            id=self.current_id or str(uuid.uuid4()),
            case_number=(self.var_case_number.get() or "").strip(),
            case_name=case_name,
            start_time=(self.var_start_time.get() or "").strip(),
            end_time=(self.var_end_time.get() or "").strip(),
            contact_name=(self.var_contact_name.get() or "").strip(),
            contact_phone=(self.var_contact_phone.get() or "").strip(),
            contact_email=(self.var_contact_email.get() or "").strip(),
            location_name=(self.var_location_name.get() or "").strip(),
            location_address=(self.var_location_address.get() or "").strip(),
            location_description=self.txt_location_desc.get("1.0","end").strip(),
            notes=self.txt_notes.get("1.0","end").strip(),
        )
        wit_rows = [self.tree_w.item(i)["values"] for i in self.tree_w.get_children()]
        ev_rows  = [self.tree_e.item(i)["values"] for i in self.tree_e.get_children()]
        exp_rows = [self.tree_exp.item(i)["values"] for i in self.tree_exp.get_children()]
        rec_rows = [self.tree_rec.item(i)["values"][0] for i in self.tree_rec.get_children()]
        usage_rows = [self.tree_usage.item(i)["values"] for i in self.tree_usage.get_children()]

        con = sqlite3.connect(DB_PATH); cur = con.cursor()
        cur.execute("""
            INSERT INTO investigations
              (id, case_number, case_name, start_time, end_time, contact_name, contact_phone, contact_email,
               location_name, location_address, location_description, notes, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
              case_number=excluded.case_number, case_name=excluded.case_name, start_time=excluded.start_time,
              end_time=excluded.end_time, contact_name=excluded.contact_name, contact_phone=excluded.contact_phone,
              contact_email=excluded.contact_email, location_name=excluded.location_name,
              location_address=excluded.location_address, location_description=excluded.location_description,
              notes=excluded.notes
        """, (inv["id"], inv["case_number"], inv["case_name"], inv["start_time"], inv["end_time"],
              inv["contact_name"], inv["contact_phone"], inv["contact_email"], inv["location_name"],
              inv["location_address"], inv["location_description"], inv["notes"]))

        cur.execute("""
            INSERT INTO location_history (investigation_id, history, documentation, built_date, structures, rooms, paranormal_areas, renovated_recently, blessed_before)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(investigation_id) DO UPDATE SET
              history=excluded.history, documentation=excluded.documentation, built_date=excluded.built_date,
              structures=excluded.structures, rooms=excluded.rooms, paranormal_areas=excluded.paranormal_areas,
              renovated_recently=excluded.renovated_recently, blessed_before=excluded.blessed_before
        """, (inv["id"], self.txt_hist_history.get("1.0","end").strip(), self.txt_hist_docs.get("1.0","end").strip(),
              self.var_hist_built.get().strip(), self.var_hist_structures.get().strip(), self.var_hist_rooms.get().strip(),
              self.txt_hist_paranormal_areas.get("1.0","end").strip(),
              int(self.var_hist_renovated.get()), int(self.var_hist_blessed.get())))

        cur.execute("""
            INSERT INTO investigation_log (investigation_id, lead_investigator, team, guests, equipment, weather, moon_cycle, start_time, end_time, observations)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(investigation_id) DO UPDATE SET
              lead_investigator=excluded.lead_investigator, team=excluded.team, guests=excluded.guests,
              equipment=excluded.equipment, weather=excluded.weather, moon_cycle=excluded.moon_cycle,
              start_time=excluded.start_time, end_time=excluded.end_time, observations=excluded.observations
        """, (inv["id"], self.var_log_lead.get().strip(), self.var_log_team.get().strip(), self.var_log_guests.get().strip(),
              self.var_log_equipment.get().strip(), self.var_log_weather.get().strip(), self.var_log_moon.get().strip(),
              self.var_log_start.get().strip(), self.var_log_end.get().strip(), self.txt_log_observations.get("1.0","end").strip()))

        cur.execute("DELETE FROM witnesses WHERE investigation_id=?", (inv["id"],))
        for w in wit_rows:
            name, phone, email, statement = w
            cur.execute("INSERT INTO witnesses (id, investigation_id, name, phone, email, statement, recorded_at) VALUES (?,?,?,?,?,?,datetime('now'))",
                        (str(uuid.uuid4()), inv["id"], name, phone, email, statement))

        cur.execute("DELETE FROM evidence WHERE investigation_id=?", (inv["id"],))
        for e in ev_rows:
            etype, fpath, desc = e
            cur.execute("INSERT INTO evidence (id, investigation_id, type, file_path, description, captured_at) VALUES (?,?,?,?,?,datetime('now'))",
                        (str(uuid.uuid4()), inv["id"], etype, fpath, desc))

        cur.execute("""
            INSERT INTO explanations (investigation_id, text)
            VALUES (?,?)
            ON CONFLICT(investigation_id) DO UPDATE SET text=excluded.text
        """, (inv["id"], self.txt_explanations.get("1.0","end").strip()))

        cur.execute("DELETE FROM experiences WHERE investigation_id=?", (inv["id"],))
        for x in exp_rows:
            person, when, where, desc = x
            cur.execute("INSERT INTO experiences (id, investigation_id, person, description, occurred_at, location_hint) VALUES (?,?,?,?,?,?)",
                        (str(uuid.uuid4()), inv["id"], person, desc, when, where))

        cur.execute("""
            INSERT INTO summation (investigation_id, conclusions, additional_comments)
            VALUES (?,?,?)
            ON CONFLICT(investigation_id) DO UPDATE SET conclusions=excluded.conclusions, additional_comments=excluded.additional_comments
        """, (inv["id"], self.txt_sum_conclusions.get("1.0","end").strip(), self.txt_sum_additional.get("1.0","end").strip()))

        cur.execute("DELETE FROM recommendations WHERE investigation_id=?", (inv["id"],))
        for t in rec_rows:
            cur.execute("INSERT INTO recommendations (id, investigation_id, text) VALUES (?,?,?)", (str(uuid.uuid4()), inv["id"], t))

        cur.execute("DELETE FROM equipment_usage WHERE investigation_id=?", (inv["id"],))
        for label, assigned_to, notes in usage_rows:
            eq_id = None
            if hasattr(self, "_equip_map") and label in self._equip_map:
                eq_id = self._equip_map[label]
            else:
                if label.endswith(")") and "(" in label:
                    nm = label[:label.rfind("(")].strip()
                    sn = label[label.rfind("(")+1:-1].strip()
                    cur.execute("SELECT id FROM equipment WHERE name=? AND COALESCE(serial,'')=?", (nm, sn))
                else:
                    cur.execute("SELECT id FROM equipment WHERE name=? ORDER BY id LIMIT 1", (label,))
                r = cur.fetchone()
                eq_id = r[0] if r else None
            if eq_id:
                cur.execute("INSERT INTO equipment_usage (id, investigation_id, equipment_id, assigned_to, notes) VALUES (?,?,?,?,?)",
                            (str(uuid.uuid4()), inv["id"], eq_id, assigned_to or "", notes or ""))

        cur.execute("UPDATE letterhead SET name=?, contact_block=?, logo_path=?, logo_position=? WHERE id=1",
                    (self.var_lh_name.get().strip(), self.txt_lh_contact.get("1.0","end").strip(), self.var_lh_logo.get().strip(), self.var_lh_pos.get().strip()))

        cur.execute("""
            INSERT INTO cover_letter (investigation_id, use_letterhead, show_case_name, show_case_number, show_location, show_date, show_reporting_investigator, intro, disclaimer)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(investigation_id) DO UPDATE SET
              use_letterhead=excluded.use_letterhead, show_case_name=excluded.show_case_name, show_case_number=excluded.show_case_number,
              show_location=excluded.show_location, show_date=excluded.show_date, show_reporting_investigator=excluded.show_reporting_investigator,
              intro=excluded.intro, disclaimer=excluded.disclaimer
        """, (inv["id"], int(self.var_cov_use.get()), int(self.var_cov_casename.get()), int(self.var_cov_casenumber.get()),
              int(self.var_cov_location.get()), int(self.var_cov_date.get()), int(self.var_cov_reporter.get()),
              self.txt_cov_intro.get("1.0","end").strip(), self.txt_cov_disclaimer.get("1.0","end").strip()))

        con.commit(); con.close()
        self.current_id = inv["id"]
        self.status.set(f"Saved: {inv['case_name']}")

    # Helpers
    def _clear_all(self):
        self.var_case_number.set(""); self.var_case_name.set("")
        self.var_start_time.set(datetime.datetime.now().isoformat(timespec="minutes")); self.var_end_time.set("")
        self.var_contact_name.set(""); self.var_contact_phone.set(""); self.var_contact_email.set("")
        self.var_location_name.set(""); self.var_location_address.set("")
        self.txt_location_desc.delete("1.0","end"); self.txt_notes.delete("1.0","end")
        self.txt_hist_history.delete("1.0","end"); self.txt_hist_docs.delete("1.0","end"); self.txt_hist_paranormal_areas.delete("1.0","end")
        self.var_hist_built.set(""); self.var_hist_structures.set(""); self.var_hist_rooms.set("")
        self.var_hist_renovated.set(False); self.var_hist_blessed.set(False)
        for i in getattr(self, "tree_w", []).get_children(): self.tree_w.delete(i)
        self.var_log_lead.set(""); self.var_log_team.set(""); self.var_log_guests.set(""); self.var_log_equipment.set("")
        self.var_log_weather.set(""); self.var_log_moon.set(""); self.var_log_start.set(""); self.var_log_end.set("")
        self.txt_log_observations.delete("1.0","end")
        for i in getattr(self, "tree_exp", []).get_children(): self.tree_exp.delete(i)
        self.var_exp_person.set(""); self.var_exp_time.set(""); self.var_exp_loc.set(""); self.txt_exp_desc.delete("1.0","end")
        for i in getattr(self, "tree_e", []).get_children(): self.tree_e.delete(i)
        self.var_e_file.set(""); self.var_e_desc.set(""); self.txt_explanations.delete("1.0","end")
        self.txt_sum_conclusions.delete("1.0","end"); self.txt_sum_additional.delete("1.0","end")
        for i in getattr(self, "tree_rec", []).get_children(): self.tree_rec.delete(i); self.var_rec.set("")
        for i in getattr(self, "tree_usage", []).get_children(): self.tree_usage.delete(i)
        self.var_cov_use.set(True); self.var_cov_casename.set(True); self.var_cov_casenumber.set(True)
        self.var_cov_location.set(True); self.var_cov_date.set(True); self.var_cov_reporter.set(True)
        self.txt_cov_intro.delete("1.0","end"); self.txt_cov_disclaimer.delete("1.0","end")

    def _confirm_discard(self):
        return messagebox.askyesno("Confirm", "Discard current changes?")

if __name__ == "__main__":
    App().mainloop()
