#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FiveM Cheat Detector with Learning (Drag&Drop + Hash learning + Custom strings)
Save as: fivem_cheat_detector_with_learning.py
Requires: requests
Optional: tkinterdnd2 for better drag-and-drop support
"""

import os
import sys
import time
import string
import threading
import requests
import json
import hashlib
import re
import shutil
import tempfile
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkFont

# ---------- Config / Filenames ----------
CUSTOM_STRINGS_FILE = "custom_cheat_strings.json"
CUSTOM_HASHES_FILE = "custom_cheat_hashes.json"

# Built-in detection strings and scores
fivem_cheat_strings = {
    "fivemcheat": 5,
    "triggerbot": 4,
    "aimbot": 5,
    "wallhack": 4,
    "noclip": 3,
    "speedhack": 3,
    "umbrella.exe": 10,
    "strawberry.exe": 10,
}

HARD_DETECTIONS = [
    "umbrella.exe",
    "strawberry.exe",
    "z7 Free Version 1.0.3.exe"
]

ALLOWED_EXTENSIONS = [".dll", ".asi", ".exe", ".lua", ".js"]

# Your discord webhook (left as you had it)
WEBHOOK_URL = "https://discord.com/api/webhooks/1404642769086976054/tnvRtA5RWD4rkQkOhsfteq7-JkMqrPfU5OWdATrlelFeWfCW80aomVZHmZun7LcP4-Hm"

# ---------- Helper functions to load/save json ----------
def load_json_file(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden {path}: {e}")
    return {}

def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern {path}: {e}")

def load_custom_strings():
    return load_json_file(CUSTOM_STRINGS_FILE)

def save_custom_strings(data):
    save_json_file(CUSTOM_STRINGS_FILE, data)

def load_custom_hashes():
    return load_json_file(CUSTOM_HASHES_FILE)

def save_custom_hashes(data):
    save_json_file(CUSTOM_HASHES_FILE, data)

# ---------- Utilities ----------
def safe_open_binary(path):
    """
    Versucht, eine Datei im Binary-Modus zu öffnen.
    Falls Öffnen fehlschlägt (z.B. Errno 22 oder Pfadlängenprobleme unter Windows),
    versucht es mit dem \\?\-Prefix (Windows).
    Liefert ein file-object oder wirft Exception.
    """
    try:
        return open(path, "rb")
    except Exception as e:
        # Try Windows extended path syntax if on nt
        if os.name == "nt":
            try:
                # If path already absolute, prefix with \\?\
                alt = path
                if not alt.startswith("\\\\?\\"):
                    alt = "\\\\?\\" + os.path.abspath(path)
                return open(alt, "rb")
            except Exception:
                raise
        else:
            raise

def compute_sha256(path):
    """
    Berechnet SHA256 eines Dateipfads robust.
    Gibt hex-String zurück oder None bei Fehler.
    """
    try:
        h = hashlib.sha256()
        # Use safe_open_binary helper to attempt robust open
        with safe_open_binary(path) as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"Fehler beim Berechnen Hash ({path}): {e}")
        return None

def extract_readable_strings_from_bytes(content_bytes, min_len=6):
    """
    Extrahiert lesbare strings aus Bytes (ähnlich Unix 'strings').
    Gibt deduplizierte Liste zurück.
    """
    try:
        text = content_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text = str(content_bytes)
    candidates = re.findall(r"[A-Za-z0-9_\-]{%d,}" % min_len, text)
    # dedupe while preserving order
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out

def sanitize_dropped_path(raw):
    """
    Reiniget raw drag data und liefert Liste von Pfaden.
    Unterstützt Formate wie:
      {C:\path with spaces\file.exe} oder C:\path\file.exe
      oder mehrere: {C:\a}{C:\b}
    """
    if not raw:
        return []
    raw = raw.strip()
    parts = []
    # If multiple braces
    if raw.startswith("{") and "}" in raw:
        cleaned = raw.strip("{}").split("}{")
        for p in cleaned:
            p = p.strip().strip('"').strip("{}").strip()
            if os.name == "nt":
                p = p.replace("/", "\\")
            if p:
                parts.append(p)
    else:
        for part in raw.split():
            part = part.strip().strip("{}").strip('"').strip()
            if os.name == "nt":
                part = part.replace("/", "\\")
            if part:
                parts.append(part)
    return parts

def send_discord_webhook(msg):
    try:
        r = requests.post(WEBHOOK_URL, json={"content": msg})
        return r.status_code, r.text
    except Exception as e:
        print("Fehler beim Senden an Discord:", e)
        return None, None

# ---------- Add detection display helper (mirrored from your code) ----------
def add_detection_to_display(self, detection, hard=False):
    file_path, strings = detection
    try:
        if hard:
            msg = f"🚨 HARTE DETECTION gefunden!\nPfad: `{file_path}`"
        else:
            msg = f"⚠️ Detection gefunden!\nPfad: `{file_path}`\nStrings: {', '.join(strings)}"
        print("DEBUG: Sende an Discord:", msg)
        status, resp = send_discord_webhook(msg)
        print("DEBUG: Discord Statuscode:", status, "Antwort:", resp)
    except Exception as e:
        print(f"Fehler beim Senden an Discord: {e}")

    if hard:
        try:
            self.results_text.insert(END, "🚨 [HARTE DETECTION] ", "hard")
            self.results_text.insert(END, f"{file_path}\n", "path")
            self.results_text.insert(END, "   Wahrscheinlichkeit: 100%\n\n", "hard")
            self.show_hard_detection_window(file_path)
        except Exception:
            pass
    else:
        try:
            self.results_text.insert(END, "⚠️  [DETECTION] ", "detection")
            self.results_text.insert(END, f"{file_path}\n", "path")
            self.results_text.insert(END, f"   Strings: {', '.join(strings)}\n\n", "detection")
        except Exception:
            pass
    try:
        self.results_text.see(END)
    except Exception:
        pass

# ---------- GUI Class ----------
class FiveMCheatDetectorGUI:
    def __init__(self, root):
        self.root = root

        # load learned data BEFORE creating widgets (so no race on refresh)
        self.custom_cheat_strings = load_custom_strings() or {}
        self.custom_cheat_hashes = load_custom_hashes() or {}
        # merged dict for string detection
        self.all_cheat_strings = {**fivem_cheat_strings, **self.custom_cheat_strings}

        # scanning state
        self.scan_thread = None
        self.is_scanning = False
        self.detections = []
        self.total_score = 0
        self.files_scanned = 0

        # Setup GUI
        self.setup_window()
        self.setup_styles()
        self.create_widgets()

        # Try enable drag & drop (if tkinterdnd2 installed)
        self.enable_drag_and_drop()

    def setup_window(self):
        self.root.title("FiveM Cheat Detector - Made by Jamil (mit Lernen)")
        width = 1000
        height = 760
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(True, True)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.style.configure('Title.TLabel', background="#1a1a1a", foreground="#ff3333", font=("Segoe UI", 22, "bold"))
        self.style.configure('Subtitle.TLabel', background="#1a1a1a", foreground="#cccccc", font=("Segoe UI", 10))
        self.style.configure('Section.TLabel', background="#2a2a2a", foreground="#66ccff", font=("Segoe UI", 12, "bold"))
        self.style.configure('Danger.TButton', background="#ff3333", foreground="white", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.configure('Primary.TButton', background="#66ccff", foreground="black", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.configure('Dark.TFrame', background="#2a2a2a", relief="ridge", borderwidth=1)
        self.style.configure('Stats.TLabel', background="#333333", foreground="#ff6666", font=("Segoe UI", 14, "bold"), anchor="center")
        self.style.configure('Red.Horizontal.TProgressbar', background='#ff3333', troughcolor='#1a1a1a', borderwidth=0, lightcolor='#ff6666', darkcolor='#cc0000')

    def create_widgets(self):
        main_frame = Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill=BOTH, expand=True, padx=12, pady=12)

        header_frame = Frame(main_frame, bg="#1a1a1a")
        header_frame.pack(fill=X, pady=(0, 12))
        title_label = ttk.Label(header_frame, text="🔍 FiveM Cheat Detector", style="Title.TLabel")
        title_label.pack()
        subtitle_label = ttk.Label(header_frame, text="Advanced Detection System - Lernmodus aktiviert", style="Subtitle.TLabel")
        subtitle_label.pack()

        top_frame = Frame(main_frame, bg="#1a1a1a")
        top_frame.pack(fill=X, pady=(8, 8))

        left_col = Frame(top_frame, bg="#1a1a1a")
        left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 8))
        right_col = Frame(top_frame, bg="#1a1a1a", width=360)
        right_col.pack(side=RIGHT, fill=Y, padx=(8, 0))

        # Drive frame
        drive_frame = ttk.Frame(left_col, style="Dark.TFrame")
        drive_frame.pack(fill=X, pady=(0, 8), padx=0, ipady=6)
        drive_title = ttk.Label(drive_frame, text="🔍 Laufwerk auswählen:", style="Section.TLabel")
        drive_title.pack(anchor=W, padx=10, pady=(6, 6))

        drives_container = Frame(drive_frame, bg="#2a2a2a")
        drives_container.pack(fill=X, padx=10, pady=(0, 8))

        self.drives = self.detect_drives()
        self.selected_drives = []
        self.drive_vars = {}
        for i, drive in enumerate(self.drives):
            var = BooleanVar(value=False)
            self.drive_vars[drive] = var
            cb = Checkbutton(drives_container, text=f"💾 {drive}", variable=var, bg="#2a2a2a", fg="#ffffff", selectcolor="#333333", activebackground="#404040", activeforeground="#ffffff", font=("Segoe UI", 10), command=self.update_selected_drives)
            row = i // 4
            col = i % 4
            cb.grid(row=row, column=col, sticky=W, padx=8, pady=4)

        button_frame = Frame(drive_frame, bg="#2a2a2a")
        button_frame.pack(fill=X, padx=10, pady=(0, 8))
        scan_btn = ttk.Button(button_frame, text="🔍 Scan starten", style="Danger.TButton", command=self.start_scan)
        scan_btn.pack(side=LEFT, padx=(0, 8))
        scan_all_btn = ttk.Button(button_frame, text="🔍 Alle Laufwerke", style="Primary.TButton", command=self.scan_all_drives)
        scan_all_btn.pack(side=LEFT, padx=(0, 8))
        stop_btn = ttk.Button(button_frame, text="⏹ Stop", command=self.stop_scan)
        stop_btn.pack(side=LEFT)

        # Progress & stats
        progress_frame = ttk.Frame(left_col, style="Dark.TFrame")
        progress_frame.pack(fill=X, pady=(0, 8), ipady=6)
        progress_title = ttk.Label(progress_frame, text="📊 Scan Status:", style="Section.TLabel")
        progress_title.pack(anchor=W, padx=10, pady=(6, 4))
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, style="Red.Horizontal.TProgressbar", length=420)
        self.progress_bar.pack(padx=10, pady=6)
        self.progress_label = ttk.Label(progress_frame, text="Bereit zum Scannen...", background="#2a2a2a", foreground="#cccccc")
        self.progress_label.pack(padx=10, pady=(0, 6))

        stats_frame = ttk.Frame(left_col, style="Dark.TFrame")
        stats_frame.pack(fill=X, pady=(0, 8), ipady=6)
        stats_title = ttk.Label(stats_frame, text="📈 Statistiken:", style="Section.TLabel")
        stats_title.pack(anchor=W, padx=10, pady=(6, 6))
        stats_container = Frame(stats_frame, bg="#2a2a2a")
        stats_container.pack(fill=X, padx=10, pady=(0, 8))
        stat_labels = ["Detections:", "Score:", "Wahrscheinlichkeit:", "Dateien:"]
        self.stat_values = []
        for i, label in enumerate(stat_labels):
            Label(stats_container, text=label, bg="#2a2a2a", fg="#cccccc", font=("Segoe UI", 10)).grid(row=0, column=i*2, sticky=W, padx=6)
            value_label = Label(stats_container, text="0", bg="#2a2a2a", fg="#ff6666", font=("Segoe UI", 12, "bold"))
            value_label.grid(row=0, column=i*2+1, sticky=W, padx=(6, 20))
            self.stat_values.append(value_label)

        # Right column: custom manager
        custom_frame = ttk.Frame(right_col, style="Dark.TFrame")
        custom_frame.pack(fill=BOTH, expand=True, padx=0, ipady=6)
        custom_title = ttk.Label(custom_frame, text="🧠 Gelernte Cheats / Strings", style="Section.TLabel")
        custom_title.pack(anchor=W, padx=10, pady=(8, 6))
        custom_btn_frame = Frame(custom_frame, bg="#2a2a2a")
        custom_btn_frame.pack(fill=X, padx=10)
        add_file_btn = ttk.Button(custom_btn_frame, text="➕ Datei hinzufügen", command=self.ask_add_file)
        add_file_btn.pack(side=LEFT, padx=(0, 6))
        export_btn = ttk.Button(custom_btn_frame, text="📤 Export", command=self.export_custom_data)
        export_btn.pack(side=LEFT, padx=(0, 6))
        import_btn = ttk.Button(custom_btn_frame, text="📥 Import", command=self.import_custom_data)
        import_btn.pack(side=LEFT, padx=(0, 6))
        remove_btn = ttk.Button(custom_btn_frame, text="🗑 Entfernen", command=self.remove_selected_custom)
        remove_btn.pack(side=LEFT, padx=(6, 0))

        lb_frame = Frame(custom_frame, bg="#2a2a2a")
        lb_frame.pack(fill=BOTH, expand=True, padx=10, pady=(8, 10))
        self.custom_listbox = Listbox(lb_frame, bg="#121212", fg="#ffffff", selectbackground="#333333", font=("Consolas", 10), height=12)
        self.custom_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.custom_scroll = Scrollbar(lb_frame, orient=VERTICAL, command=self.custom_listbox.yview)
        self.custom_scroll.pack(side=RIGHT, fill=Y)
        self.custom_listbox.config(yscrollcommand=self.custom_scroll.set)
        self._refresh_custom_listbox()

        dnd_frame = Frame(custom_frame, bg="#222222")
        dnd_frame.pack(fill=X, padx=10, pady=(4, 10))
        Label(dnd_frame, text="Ziehe hier Cheat-Dateien rein →", bg="#222222", fg="#cccccc", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=6, pady=6)
        self.dnd_hint = Label(dnd_frame, text="(Drag & Drop)", bg="#222222", fg="#888888", font=("Segoe UI", 9))
        self.dnd_hint.pack(side=LEFT, padx=6)

        # Middle results area
        results_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        results_frame.pack(fill=BOTH, expand=True, padx=0, pady=(6, 0))
        results_title = ttk.Label(results_frame, text="🚨 Detections:", style="Section.TLabel")
        results_title.pack(anchor=W, padx=10, pady=(8, 6))
        self.results_text = ScrolledText(results_frame, bg="#1a1a1a", fg="#ffffff", font=("Consolas", 10), wrap=WORD, height=18)
        self.results_text.pack(fill=BOTH, expand=True, padx=10, pady=(0, 12))
        self.results_text.tag_config("normal", foreground="#ffffff")
        self.results_text.tag_config("detection", foreground="#ff6666", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("hard", foreground="#ff0000", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("path", foreground="#ffcccc")
        self.results_text.tag_config("success", foreground="#66ff66", font=("Consolas", 10, "bold"))

        footer_frame = Frame(main_frame, bg="#1a1a1a")
        footer_frame.pack(fill=X, pady=(0, 4))
        footer_label = Label(footer_frame, text="Made by Jamil - FiveM Cheat Detection System (Lernmodus)", bg="#1a1a1a", fg="#888888", font=("Segoe UI", 9))
        footer_label.pack()

    # ---------- Custom listbox management ----------
    def _refresh_custom_listbox(self):
        self.custom_listbox.delete(0, END)
        # show hashes first
        for h in sorted(self.custom_cheat_hashes.keys()):
            meta = self.custom_cheat_hashes.get(h, {})
            names = meta.get("names", [])
            first = meta.get("first_seen", "")
            display_name = names[0] if names else "<unknown>"
            display = f"HASH {h[:10]}... | {display_name} | {first}"
            self.custom_listbox.insert(END, display)
        # then strings
        for s in sorted(self.custom_cheat_strings.keys()):
            score = self.custom_cheat_strings.get(s, 5)
            self.custom_listbox.insert(END, f"STR  {s} (score={score})")

    def ask_add_file(self):
        p = filedialog.askopenfilename(title="Wähle Cheat-Datei zum Lernen", filetypes=[("Executable files", "*.exe *.dll *.asi *.lua *.js"), ("All files", "*.*")])
        if p:
            ok = self._learn_file_as_cheat(p)
            if ok:
                messagebox.showinfo("Gelernte Datei", f"{os.path.basename(p)} wurde gelernt.")
                self._refresh_custom_listbox()
            else:
                messagebox.showinfo("Info", "Datei wurde nicht neu gelernt (evtl. bereits vorhanden).")

    def export_custom_data(self):
        out = filedialog.asksaveasfilename(title="Exportiere gelernte Daten", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not out:
            return
        data = {"hashes": self.custom_cheat_hashes, "strings": self.custom_cheat_strings}
        try:
            save_json_file(out, data)
            messagebox.showinfo("Export", f"Gelernte Daten exportiert nach:\n{out}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")

    def import_custom_data(self):
        inp = filedialog.askopenfilename(title="Importiere gelernte Daten (JSON)", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not inp:
            return
        try:
            data = load_json_file(inp)
            hashes = data.get("hashes", {})
            strings = data.get("strings", {})
            self.custom_cheat_hashes.update(hashes)
            self.custom_cheat_strings.update(strings)
            save_custom_hashes(self.custom_cheat_hashes)
            save_custom_strings(self.custom_cheat_strings)
            self.all_cheat_strings = {**fivem_cheat_strings, **self.custom_cheat_strings}
            self._refresh_custom_listbox()
            messagebox.showinfo("Import", "Daten importiert und gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def remove_selected_custom(self):
        sel = self.custom_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Bitte wähle einen Eintrag aus der Liste aus.")
            return
        idx = sel[0]
        value = self.custom_listbox.get(idx)
        if value.startswith("HASH"):
            # parse hash prefix
            hash_prefix = value.split()[1]
            # find full hash that starts with this prefix
            full = None
            for h in list(self.custom_cheat_hashes.keys()):
                if h.startswith(hash_prefix.replace("...", "")):
                    full = h
                    break
            if full:
                if messagebox.askyesno("Entfernen", f"Hash {full} löschen?"):
                    self.custom_cheat_hashes.pop(full, None)
                    save_custom_hashes(self.custom_cheat_hashes)
                    self._refresh_custom_listbox()
        elif value.startswith("STR"):
            m = re.match(r"STR\s+(.*?)\s+\(score=(\d+)\)", value)
            if m:
                s = m.group(1)
                if messagebox.askyesno("Entfernen", f"String '{s}' löschen?"):
                    self.custom_cheat_strings.pop(s, None)
                    save_custom_strings(self.custom_cheat_strings)
                    self.all_cheat_strings = {**fivem_cheat_strings, **self.custom_cheat_strings}
                    self._refresh_custom_listbox()
        else:
            if messagebox.askyesno("Entfernen", f"Eintrag entfernen?\n{value}"):
                # naive attempt
                if " (score=" in value:
                    key = value.split(" (score=")[0].replace("STR  ", "").strip()
                    if key in self.custom_cheat_strings:
                        self.custom_cheat_strings.pop(key, None)
                        save_custom_strings(self.custom_cheat_strings)
                        self.all_cheat_strings = {**fivem_cheat_strings, **self.custom_cheat_strings}
                self._refresh_custom_listbox()

    # ---------- Drag & Drop ----------
    def enable_drag_and_drop(self):
        try:
            from tkinterdnd2 import DND_FILES
            # Bind to custom_listbox and results_text (visible target)
            widgets_to_bind = [self.custom_listbox, self.results_text, self.root]
            for w in widgets_to_bind:
                try:
                    w.drop_target_register(DND_FILES)
                    w.dnd_bind('<<Drop>>', self.on_file_drop)
                except Exception:
                    pass
            self.dnd_hint.config(text="Drag & Drop verfügbar ✅")
        except Exception:
            self.dnd_hint.config(text="Drag & Drop nicht installiert (pip install tkinterdnd2)")

    def on_file_drop(self, event):
        raw = getattr(event, "data", None)
        paths = sanitize_dropped_path(raw)
        if not paths:
            messagebox.showinfo("Info", "Keine gültigen Pfade erkannt.")
            return
        added = 0
        added_names = []
        for p in paths:
            p = p.strip().strip('"').strip()
            if os.path.isfile(p):
                ok = self._learn_file_as_cheat_via_temp_copy(p)
                if ok:
                    added += 1
                    added_names.append(os.path.basename(p))
            else:
                # try if temporary browsers provide file:// uri
                if p.startswith("file://"):
                    try:
                        candidate = p[len("file://"):]
                        if os.path.isfile(candidate):
                            ok = self._learn_file_as_cheat_via_temp_copy(candidate)
                            if ok:
                                added += 1
                                added_names.append(os.path.basename(candidate))
                    except Exception:
                        pass
                else:
                    print(f"Dropped path nicht lesbar: {p}")
        if added > 0:
            messagebox.showinfo("Erfolg", f"{added} Datei(en) gelernt:\n" + "\n".join(added_names))
            self._refresh_custom_listbox()
        else:
            messagebox.showinfo("Info", "Keine neuen Daten hinzugefügt (evtl. bereits vorhanden).")

    def _learn_file_as_cheat_via_temp_copy(self, path):
        """
        Kopiert die gedroppte Datei in temp und ruft _learn_file_as_cheat auf der Kopie.
        Dies umgeht Zugriffsprobleme bei Browser-temporären Pfaden.
        """
        try:
            base = os.path.basename(path)
            dst = os.path.join(tempfile.gettempdir(), f"learn_{int(time.time())}_{base}")
            try:
                shutil.copy2(path, dst)
            except Exception as e:
                # try a simpler copy if copy2 fails
                try:
                    shutil.copy(path, dst)
                except Exception as e2:
                    print("Kopie fehlgeschlagen:", e, e2)
                    return False
            return self._learn_file_as_cheat(dst)
        except Exception as e:
            print("Fehler beim lernen via temp copy:", e)
            return False

    def _learn_file_as_cheat(self, file_path):
        """
        Lernt Datei: speichert Hash & extrahiert Strings.
        Gibt True zurück, wenn neu gespeichert wurde.
        """
        try:
            file_path = os.path.abspath(file_path)
            if not os.path.exists(file_path):
                print("File nicht gefunden:", file_path)
                return False
            file_hash = compute_sha256(file_path)
            if not file_hash:
                return False
            filename = os.path.basename(file_path)
            now = datetime.utcnow().isoformat()
            changed = False
            meta = self.custom_cheat_hashes.get(file_hash)
            if meta:
                names = meta.get("names", [])
                if filename not in names:
                    names.insert(0, filename)
                    meta["names"] = names
                    meta["last_seen"] = now
                    changed = True
            else:
                # Read file and extract strings
                try:
                    with safe_open_binary(file_path) as f:
                        content = f.read()
                except Exception as e:
                    print("Fehler beim Lesen Datei:", e)
                    content = b""
                sigs = extract_readable_strings_from_bytes(content, min_len=5)
                meta = {"names": [filename], "first_seen": now, "last_seen": now, "strings": sigs}
                self.custom_cheat_hashes[file_hash] = meta
                changed = True
                # add top strings to strings db
                top_to_add = sigs[:20]
                added_strings = 0
                for s in top_to_add:
                    if s and s not in self.custom_cheat_strings:
                        self.custom_cheat_strings[s] = 5
                        added_strings += 1
                if added_strings:
                    save_custom_strings(self.custom_cheat_strings)
            if changed:
                save_custom_hashes(self.custom_cheat_hashes)
            self.all_cheat_strings = {**fivem_cheat_strings, **self.custom_cheat_strings}
            return changed
        except Exception as e:
            print("Fehler beim Lernen:", e)
            return False

    # ---------- Scan functions ----------
    def detect_drives(self):
        drives = []
        # Try Windows style A:\ .. Z:\ and also Unix root
        if os.name == "nt":
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # add root
            drives.append("/")
        # remove duplicates and sort
        return sorted(list(dict.fromkeys(drives)))

    def update_selected_drives(self):
        self.selected_drives = [d for d, v in self.drive_vars.items() if v.get()]

    def scan_all_drives(self):
        for var in self.drive_vars.values():
            var.set(True)
        self.update_selected_drives()
        self.start_scan()

    def start_scan(self):
        if self.is_scanning:
            messagebox.showwarning("Warnung", "Ein Scan läuft bereits!")
            return
        # update selected drives
        self.update_selected_drives()
        if not self.selected_drives:
            messagebox.showerror("Fehler", "Bitte wähle mindestens ein Laufwerk aus!")
            return
        self.is_scanning = True
        self.detections = []
        self.total_score = 0
        self.files_scanned = 0
        try:
            self.results_text.delete(1.0, END)
            self.results_text.insert(END, "🔍 Starte Scan...\n\n", "normal")
        except Exception:
            pass
        self.scan_thread = threading.Thread(target=self.run_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def stop_scan(self):
        self.is_scanning = False
        if self.scan_thread and self.scan_thread.is_alive():
            try:
                self.progress_label.config(text="Scan wird gestoppt...")
            except Exception:
                pass

    def run_scan(self):
        try:
            for drive in self.selected_drives:
                if not self.is_scanning:
                    break
                self.root.after(0, lambda d=drive: self.progress_label.config(text=f"Scanne {d}..."))
                drive_detections = self.scan_drive(drive)
                self.detections.extend(drive_detections)
                # If any hard detection, stop
                for detection in drive_detections:
                    if "HARTE DETECTION" in detection[1] or "KNOWN_CHEAT_HASH" in detection[1]:
                        self.root.after(0, self.scan_completed)
                        return
            self.root.after(0, self.scan_completed)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Scan-Fehler: {str(e)}"))
        finally:
            self.is_scanning = False

    def scan_drive(self, start_path):
        all_files = []
        detections = []
        for root, dirs, files in os.walk(start_path):
            if not self.is_scanning:
                break
            if self.is_path_excluded(root):
                continue
            for file in files:
                lower = file.lower()
                if any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    all_files.append(os.path.join(root, file))
        total_files = len(all_files)
        if total_files == 0:
            return []
        for idx, file_path in enumerate(all_files, 1):
            if not self.is_scanning:
                break
            file_name = os.path.basename(file_path)
            progress = (idx / total_files) * 100
            try:
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda i=idx, t=total_files, f=file_name: self.progress_label.config(text=f"Datei {i}/{t}: {f[:40]}..."))
            except Exception:
                pass

            # Hard filename list
            try:
                if file_name.lower() in (n.lower() for n in HARD_DETECTIONS):
                    detection = (file_path, ["HARTE DETECTION"])
                    detections.append(detection)
                    self.files_scanned = idx
                    self.root.after(0, lambda d=detection: add_detection_to_display(self, d, hard=True))
                    return detections
            except Exception:
                pass

            # Compute hash with fallback (may be slow)
            file_hash = compute_sha256(file_path)
            if file_hash and file_hash in self.custom_cheat_hashes:
                meta = self.custom_cheat_hashes.get(file_hash, {})
                detection = (file_path, ["KNOWN_CHEAT_HASH"] + meta.get("strings", [])[:4])
                detections.append(detection)
                self.total_score += 100
                self.files_scanned = idx
                self.root.after(0, lambda d=detection: add_detection_to_display(self, d, hard=True))
                return detections

            # Search for strings (both built-in and custom)
            found = self.scan_file_for_cheat_strings(file_path)
            if found:
                detection = (file_path, found)
                detections.append(detection)
                try:
                    max_score = max((self.all_cheat_strings.get(s, 0) for s in found), default=0)
                except Exception:
                    max_score = 0
                self.total_score += max_score
                self.root.after(0, lambda d=detection: add_detection_to_display(self, d, hard=False))

            self.files_scanned = idx
        return detections

    def is_path_excluded(self, path):
        path_lower = path.lower()
        for exclude in [
            "c:\\windows",
            "c:\\program files",
            "c:\\program files (x86)",
            "c:\\users\\default",
            "c:\\users\\public",
        ]:
            if path_lower.startswith(exclude):
                return True
        return False

    def scan_file_for_cheat_strings(self, file_path):
        try:
            with safe_open_binary(file_path) as f:
                content = f.read().lower()
                found_strings = []
                for cheat_str in fivem_cheat_strings.keys():
                    try:
                        if cheat_str.encode() in content:
                            found_strings.append(cheat_str)
                    except Exception:
                        pass
                for cheat_str in self.custom_cheat_strings.keys():
                    try:
                        if cheat_str.encode() in content:
                            found_strings.append(cheat_str)
                    except Exception:
                        pass
                return list(dict.fromkeys(found_strings))
        except Exception:
            return []

    # ---------- Utilities ----------
    def open_file_location(self, file_path):
        try:
            import subprocess
            subprocess.Popen(f'explorer /select,"{file_path}"')
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {str(e)}")

    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Erfolg", "Text wurde in die Zwischenablage kopiert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Kopieren fehlgeschlagen: {str(e)}")

    def show_hard_detection_window(self, file_path):
        try:
            hard_window = Toplevel(self.root)
            hard_window.title("🚨 KRITISCHE BEDROHUNG ERKANNT!")
            hard_window.geometry("700x500")
            hard_window.configure(bg="#1a0000")
            hard_window.resizable(True, True)
            hard_window.grab_set()
            hard_window.update_idletasks()
            x = (hard_window.winfo_screenwidth() // 2) - (700 // 2)
            y = (hard_window.winfo_screenheight() // 2) - (500 // 2)
            hard_window.geometry(f"700x500+{x}+{y}")
            try:
                hard_window.iconbitmap('warning.ico')
            except Exception:
                pass
            main_container = Frame(hard_window, bg="#1a0000")
            main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
            header_frame = Frame(main_container, bg="#330000", relief="raised", bd=3)
            header_frame.pack(fill=X, pady=(0, 20))
            warning_frame = Frame(header_frame, bg="#330000")
            warning_frame.pack(pady=15)
            warning_icon = Label(warning_frame, text="⚠️🚨⚠️", bg="#330000", fg="#ff0000", font=("Segoe UI", 32, "bold"))
            warning_icon.pack()
            title_label = Label(warning_frame, text="HARTE DETECTION GEFUNDEN!", bg="#330000", fg="#ffffff", font=("Segoe UI", 18, "bold"))
            title_label.pack(pady=(5, 0))
            subtitle_label = Label(warning_frame, text="Kritische Bedrohung erkannt - Sofortige Maßnahmen erforderlich", bg="#330000", fg="#ffcccc", font=("Segoe UI", 11))
            subtitle_label.pack(pady=(2, 0))
            info_frame = Frame(main_container, bg="#2a0000", relief="sunken", bd=2)
            info_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
            info_title = Label(info_frame, text="🔍 Details der Bedrohung:", bg="#2a0000", fg="#ff6666", font=("Segoe UI", 14, "bold"))
            info_title.pack(anchor=W, padx=15, pady=(15, 10))
            file_info_frame = Frame(info_frame, bg="#2a0000")
            file_info_frame.pack(fill=X, padx=15, pady=(0, 15))
            Label(file_info_frame, text="Datei:", bg="#2a0000", fg="#cccccc", font=("Segoe UI", 11, "bold")).pack(anchor=W)
            file_label = Label(file_info_frame, text=file_path, bg="#2a0000", fg="#ffffff", font=("Consolas", 10), wraplength=600, justify=LEFT)
            file_label.pack(anchor=W, padx=(0, 0), pady=(2, 10))
            Label(file_info_frame, text="Bedrohungstyp:", bg="#2a0000", fg="#cccccc", font=("Segoe UI", 11, "bold")).pack(anchor=W)
            threat_label = Label(file_info_frame, text="Bekannter FiveM Cheat/Hack - Susano Detection", bg="#2a0000", fg="#ff4444", font=("Segoe UI", 11, "bold"))
            threat_label.pack(anchor=W, pady=(2, 10))
            Label(file_info_frame, text="Risikostufe:", bg="#2a0000", fg="#cccccc", font=("Segoe UI", 11, "bold")).pack(anchor=W)
            risk_label = Label(file_info_frame, text="🔴 KRITISCH (100%)", bg="#2a0000", fg="#ff0000", font=("Segoe UI", 12, "bold"))
            risk_label.pack(anchor=W, pady=(2, 10))
            recommendations_frame = Frame(info_frame, bg="#2a0000")
            recommendations_frame.pack(fill=X, padx=15, pady=(0, 15))
            Label(recommendations_frame, text="⚡ Empfohlene Maßnahmen:", bg="#2a0000", fg="#ff6666", font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=(0, 5))
            recommendations = [
                "• Datei sofort löschen oder in Quarantäne verschieben",
                "• Vollständigen Antivirus-Scan durchführen",
                "• FiveM Cache leeren und neu installieren",
                "• Passwörter ändern (falls Keylogger vermutet)",
                "• System-Neustart nach Bereinigung",
            ]
            for rec in recommendations:
                rec_label = Label(recommendations_frame, text=rec, bg="#2a0000", fg="#ffcccc", font=("Segoe UI", 10), wraplength=600, justify=LEFT)
                rec_label.pack(anchor=W, pady=1)
            button_frame = Frame(main_container, bg="#1a0000")
            button_frame.pack(fill=X, pady=(10, 0))
            open_folder_btn = Button(button_frame, text="📁 Datei-Ordner öffnen", bg="#4a4a00", fg="white", font=("Segoe UI", 10, "bold"), command=lambda: self.open_file_location(file_path), relief="raised", bd=2)
            open_folder_btn.pack(side=LEFT, padx=(0, 10))
            copy_path_btn = Button(button_frame, text="📋 Pfad kopieren", bg="#004a4a", fg="white", font=("Segoe UI", 10, "bold"), command=lambda: self.copy_to_clipboard(file_path), relief="raised", bd=2)
            copy_path_btn.pack(side=LEFT, padx=(0, 10))
            continue_btn = Button(button_frame, text="▶️ Scan fortsetzen", bg="#4a0000", fg="white", font=("Segoe UI", 10, "bold"), command=hard_window.destroy, relief="raised", bd=2)
            continue_btn.pack(side=LEFT, padx=(0, 10))
            stop_scan_btn = Button(button_frame, text="🛑 Scan stoppen", bg="#aa0000", fg="white", font=("Segoe UI", 10, "bold"), command=lambda: [self.stop_scan(), hard_window.destroy()], relief="raised", bd=2)
            stop_scan_btn.pack(side=RIGHT)
            self.blink_warning(warning_icon, 0)
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass
        except Exception as e:
            print("Fehler beim Anzeigen Hard Detection Window:", e)

    def blink_warning(self, widget, state):
        try:
            if state == 0:
                widget.config(fg="#ff0000")
                self.root.after(500, lambda: self.blink_warning(widget, 1))
            else:
                widget.config(fg="#ffaaaa")
                self.root.after(500, lambda: self.blink_warning(widget, 0))
        except Exception:
            pass

    def scan_completed(self):
        self.is_scanning = False
        try:
            self.progress_var.set(100)
        except Exception:
            pass
        if not self.detections:
            try:
                self.results_text.insert(END, "✅ Keine verdächtigen Dateien gefunden!\n", "success")
            except Exception:
                pass
            probability = 0
        else:
            has_hard = any("HARTE DETECTION" in det[1] or "KNOWN_CHEAT_HASH" in det[1] for det in self.detections)
            if has_hard:
                probability = 100
                try:
                    self.progress_label.config(text="HARTE DETECTION gefunden! Scan beendet.")
                except Exception:
                    pass
            else:
                max_score = sum(fivem_cheat_strings.values()) * 10 if fivem_cheat_strings else 1
                probability = min(100, int((self.total_score / max_score) * 100)) if max_score else 0
                try:
                    self.progress_label.config(text="Scan abgeschlossen!")
                except Exception:
                    pass
        try:
            self.stat_values[0].config(text=str(len(self.detections)))
            self.stat_values[1].config(text=str(self.total_score))
            self.stat_values[2].config(text=f"{probability}%")
            self.stat_values[3].config(text=str(self.files_scanned))
        except Exception:
            pass
        try:
            if probability >= 80:
                self.stat_values[2].config(fg="#ff0000")
            elif probability >= 50:
                self.stat_values[2].config(fg="#ff6666")
            else:
                self.stat_values[2].config(fg="#66ff66")
        except Exception:
            pass

# ---------- main ----------
def main():
    root = Tk()
    app = FiveMCheatDetectorGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()

if __name__ == "__main__":
    main()
