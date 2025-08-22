#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gutty — Juristisches Gutachten Abtipper (UI + CLI)

Start:
  python gutty.py          # Tkinter-UI (Lückentext + Prüfung)
  python gutty.py --cli    # CLI-Blindmodus (ohne Lücken, ohne Prüfung)

Features:
- Mehrfachauswahl: mehrere PDF/MD/TXT zusammenführen
- Times New Roman in den Textfeldern (Fallback „Times“)
- Lückentext (Maskierung steuerbar), Vergleichsmodi (strict/loose/sem-light)
- Klausurmodus: Zeitablauf drückt automatisch „Weiter“; bei <85 % → gleicher Timer wird neu gestartet
- Punktesystem: 100 Punkte/Absatz; −5 je Nachkorrektur; zusätzlich −5 je Timeout-Nachkorrektur
- Diff-Ansicht (rot/grün), Export MD + optional PDF
"""

import re, sys, time, textwrap
from pathlib import Path
from dataclasses import dataclass
from typing import List

# ---------- optionale Abhängigkeiten ----------
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    REPORTLAB = True
except ImportError:
    REPORTLAB = False

# ---------- Profile ----------
@dataclass
class Profile:
    key: str
    name: str
    timer_factor: float

PROFILES = {
    "zivil": Profile("zivil", "Zivilrecht", 1.0),
    "straf": Profile("straf", "Strafrecht", 1.1),
    "oer":   Profile("oer",   "Öffentliches Recht", 1.2),
}

# ---------- Vergleich & Maskierung ----------
COMPARE_MODES = ["strict", "loose", "sem-light"]
MASK_LEVELS   = ["low", "medium", "high"]

# Zitate immer maskieren
MASK_ALWAYS = [
    r"§+\s*\d+[a-zA-Z]*\s*(Abs\.?\s*\d+)?\s*(S\.?\s*\d+)?\s*(Nr\.?\s*\d+)?\s*(BGB|StGB|VwGO|VwVfG|GG)?",
    r"Art\.?\s*\d+\s*(Abs\.?\s*\d+)?\s*(S\.?\s*\d+)?\s*(GG)",
]

# Juristische Schlüsselbegriffe (für sparsames Maskieren)
TRIGGERS = [
    # Zivil
    "Anspruch","Angebot","Annahme","invitatio","Anfechtung","Stellvertretung","AGB",
    "Pflichtverletzung","Vertretenmüssen","Verzug","Rücktritt","Schadensersatz",
    "Willenserklärung","Kaufvertrag",
    # Straf
    "Tatbestandsmäßigkeit","objektive","subjektive","Vorsatz","Fahrlässigkeit",
    "Rechtswidrigkeit","Notwehr","Schuld","Irrtum","Versuch","Täterschaft",
    "Teilnahme","Kausalität","Zurechnung",
    # ÖR
    "Verwaltungsrechtsweg","statthafte","Klageart","Klagebefugnis","Form","Frist",
    "Beteiligtenfähigkeit","Begründetheit","Eingriff","Schranke","Schranken-Schranke",
    "Ermessen","Bestandskraft","Verwaltungsakt","Verhältnismäßigkeit","Grundrechte",
]

# ---------- Punkte-System (anpassbar) ----------
SCORE_POINTS_PER_PARAGRAPH   = 100
SCORE_PENALTY_PER_CORRECTION = 25
SCORE_TIMEOUT_EXTRA_PENALTY  = 25   # Extra-Abzug, wenn Nachkorrektur durch Zeitablauf kam

# ---------- Normalisierung / Distanz ----------
def _stem_de(w: str) -> str:
    for suf in ["ungen","lich","keit","heit","chen","ung","en","ern","er","n","e","s"]:
        if len(w) > 5 and w.endswith(suf):
            return w[:-len(suf)]
    return w

def normalize_text(s: str, mode: str) -> str:
    s = s.strip()
    if mode in ("loose", "sem-light"):
        s = re.sub(r"\s+", " ", s).lower()
        s = re.sub(r"[\u2013\u2014]", "-", s)
        s = re.sub(r"[.,;:()\"'\[\]]", "", s)
    # Zitate kanonisieren
    s = re.sub(
        r"§\s*(\d+[a-zA-Z]*)\s*(Abs\.?\s*(\d+))?\s*(S\.?\s*(\d+))?\s*(Nr\.?\s*(\d+))?\s*(BGB|StGB|VwGO|VwVfG|GG)?",
        lambda m: f"§{m.group(1)}({m.group(3) or ''})({m.group(5) or ''})({m.group(7) or ''}){m.group(8) or ''}",
        s, flags=re.IGNORECASE,
    )
    s = re.sub(
        r"art\.?\s*(\d+)(?:\s*abs\.?\s*(\d+))?\s*(gg)",
        lambda m: f"art{m.group(1)}({m.group(2) or ''}){m.group(3)}",
        s, flags=re.IGNORECASE,
    )
    if mode == "sem-light":
        s = " ".join(_stem_de(w) for w in s.split())
    return s

def levenshtein(a: str, b: str) -> int:
    n, m = len(a), len(b)
    if n == 0: return m
    if m == 0: return n
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        ca = a[i - 1]
        for j in range(1, m + 1):
            cb = b[j - 1]
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (0 if ca == cb else 1))
        prev = cur
    return prev[m]

# ---------- Maskierung (Lückentext) ----------
def apply_masking(text: str, density: str, ratio: float = 0.22, keys_only: bool = False) -> str:
    """Erzeugt Lückentext mit Gewichtung; Zitate werden immer maskiert."""
    masked = text
    covered = [False] * len(text)
    for pat in MASK_ALWAYS:
        for m in re.finditer(pat, masked):
            s, e = m.start(), m.end()
            masked = masked[:s] + ("•" * (e - s)) + masked[e:]
            for i in range(s, e):
                if 0 <= i < len(covered):
                    covered[i] = True

    thresh = {"low": 10, "medium": 7, "high": 5}[density]
    tokens = list(re.finditer(r"\w+|\s+|\S", text))
    word_idxs = [i for i,t in enumerate(tokens) if t.group(0).isalnum()]
    candidates = []

    pos_in_sent = 0
    for i, t in enumerate(tokens):
        tok = t.group(0)
        if not tok.isalnum():
            if tok in ".!?":
                pos_in_sent = 0
            continue
        start, end = t.start(), t.end()
        if any(covered[start:end]):  # schon durch Zitat verdeckt
            continue

        word = tok
        cap_noun  = word[:1].isupper() and not word.isupper() and pos_in_sent > 0
        long_word = len(word) >= thresh
        is_trigger = any(word.lower().startswith(k.lower()) for k in TRIGGERS)

        if keys_only and not is_trigger:
            pos_in_sent += 1
            continue

        score = 0
        if is_trigger: score += 3
        if long_word:  score += 2
        if cap_noun:   score += 1
        if score > 0:
            candidates.append((score, i))
        pos_in_sent += 1

    max_masks = max(0, int(len(word_idxs) * ratio))
    candidates.sort(key=lambda x: (x[0], len(tokens[x[1]].group(0))), reverse=True)
    chosen = set(idx for _, idx in candidates[:max_masks])

    out = []
    pos_in_sent = 0
    for i, t in enumerate(tokens):
        tok = t.group(0)
        if tok.isalnum():
            s, e = t.start(), t.end()
            if any(covered[s:e]):
                out.append("•" * (e - s))
            elif i in chosen:
                out.append("•" * len(tok))
            else:
                out.append(tok)
            pos_in_sent += 1
        else:
            out.append(tok)
            if tok in ".!?":
                pos_in_sent = 0
    return "".join(out)

# ---------- Text laden ----------
def load_text_any(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        if PdfReader is None:
            raise RuntimeError("Für PDF bitte 'pip install pypdf'")
        reader = PdfReader(str(path))
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        return "\n\n".join(pages)
    elif ext in (".md", ".markdown", ".txt"):
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise RuntimeError("Unterstützt: .pdf, .md, .txt")

def load_texts(paths: List[str]) -> str:
    return "\n\n".join(load_text_any(Path(p)) for p in paths if p)

# ---------- Absatz-Split ----------
def split_paragraphs(text: str, min_words=160, max_words=480) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # Silbentrennung entfernen
    raw_blocks = [b for b in re.split(r"\n\s*\n+", text) if b.strip()]

    blocks = []
    for b in raw_blocks:
        lines = [ln.strip() for ln in b.strip().split("\n") if ln.strip()]
        # Wenn es keine Listen-/Gliederungslinien sind, zu einem Absatz zusammenziehen
        if all(not re.match(r"^([•*-]|\d+[\.)])\s+", ln) for ln in lines):
            blocks.append(re.sub(r"[ \t]+", " ", " ".join(lines)))
        else:
            blocks.append("\n".join(lines))

    paras, buf, buf_words = [], [], 0
    def flush_buf():
        nonlocal buf, buf_words
        if buf:
            paras.append(" ".join(buf).strip()); buf, buf_words = [], 0

    for b in blocks:
        w = len(b.split())
        if min_words <= w <= max_words and not buf:
            paras.append(b); continue
        if w > max_words and not buf:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", b) if s.strip()]
            acc, acc_w = [], 0
            for s in sentences:
                sw = len(s.split())
                if acc and acc_w + sw > max_words:
                    paras.append(" ".join(acc)); acc, acc_w = [s], sw
                else:
                    acc.append(s); acc_w += sw
            if acc: paras.append(" ".join(acc))
            continue
        if buf_words + w < min_words:
            buf.append(b); buf_words += w; continue
        buf.append(b); flush_buf()
    flush_buf()

    out = []
    for p in paras:
        if out and len(p.split()) < min_words:
            out[-1] = (out[-1] + " " + p).strip()
        else:
            out.append(p)
    return [p for p in out if p]

# ---------- Zeit & Export ----------
def seconds_for_paragraph(text: str, base_per_100w: int, profiles: List[Profile]) -> int:
    words = max(1, len(re.findall(r"\w+", text)))
    base = (words / 100.0) * base_per_100w
    prof_factor = sum(p.timer_factor for p in profiles) / (len(profiles) or 1)
    secs = int(round(base * prof_factor))
    return max(secs, 30)

def export_text_md(text: str, outpath: Path) -> None:
    outpath.write_text(text, encoding="utf-8")

def export_text_pdf(text: str, outpath: Path, title: str = "Dein Text") -> None:
    if not REPORTLAB:
        raise RuntimeError("reportlab ist nicht installiert.")
    c = canvas.Canvas(str(outpath), pagesize=A4)
    w, h = A4
    left = 2 * cm
    top = h - 2 * cm
    t = c.beginText(left, top)
    t.setFont("Times-Roman", 11)
    t.textLine(title)
    t.textLine("")
    for line in text.split("\n"):
        chunks = textwrap.wrap(line, width=95) if line else [""]
        for ch in chunks:
            t.textLine(ch)
    c.drawText(t); c.showPage(); c.save()

# ================= CLI-Blindmodus =================
def run_cli():
    print("=== Gutty CLI — Blindmodus ===")
    file_path = input("Pfad zur Vorlage (.pdf/.md/.txt): ").strip()
    if not file_path:
        print("Abbruch."); return
    try:
        text = load_text_any(Path(file_path))
    except Exception as e:
        print(f"Fehler: {e}"); return

    paras = split_paragraphs(text)
    typed = []
    print(f"{len(paras)} Absätze erkannt.\n")
    start_all = time.time()
    for idx, para in enumerate(paras, 1):
        print(f"[Absatz {idx}/{len(paras)}] — Tippe jetzt (Leere Zeile beendet den Absatz):")
        buf = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "":
                break
            buf.append(line)
        typed.append("\n".join(buf))
    total_time = int(time.time() - start_all)
    print("\n=== Auswertung ===")
    print(f"Gesamtzeit: {total_time}s")
    out_md = Path("ausgabe.md")
    export_text_md("\n\n".join(typed), out_md)
    print(f"Gespeichert als {out_md}")
    if REPORTLAB:
        out_pdf = Path("ausgabe.pdf")
        export_text_pdf("\n\n".join(typed), out_pdf)
        print(f"Auch als PDF gespeichert: {out_pdf}")

# ================= Tkinter-UI =================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

@dataclass
class ParaState:
    start_ts: float = 0.0
    budget: int = 0
    correction_mode: bool = False        # (nicht mehr genutzt für Freeze, behalten für Lesbarkeit)
    timed_out_handled: bool = False      # um wiederholte Auto-Weiter-Events zu entkoppeln

class GuttyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gutty — Gutachten-Typer")
        self.geometry("1100x740")
        self.minsize(980, 660)

        # State
        self.paragraphs: List[str] = []
        self.typed: List[str] = []
        self.per_para: List[ParaState] = []
        self.current_idx = 0

        # Settings
        self.timer_100w = tk.IntVar(value=90)
        self.min_words   = tk.IntVar(value=160)
        self.max_words   = tk.IntVar(value=480)
        self.mode        = tk.StringVar(value="training")
        self.var_zivil   = tk.BooleanVar(value=True)
        self.var_straf   = tk.BooleanVar(value=True)
        self.var_oer     = tk.BooleanVar(value=True)

        # Dateien (Mehrfachauswahl)
        self.file_paths: List[str] = []
        self.files_label = tk.StringVar(value="Keine Datei gewählt")

        # Vergleich & Maskierung
        self.compare_mode    = tk.StringVar(value="sem-light")
        self.mask_level      = tk.StringVar(value="medium")
        self.mask_ratio      = tk.IntVar(value=22)   # 0–60 %
        self.mask_keys_only  = tk.BooleanVar(value=False)

        # Punkte & UI
        self.time_lbl_var   = tk.StringVar(value="Zeit: 0/0s")
        self.absatz_lbl_var = tk.StringVar(value="Absatz –/–")
        self.points_lbl_var = tk.StringVar(value="Punkte: 0/0")
        self.pb_time_val    = tk.DoubleVar(value=0.0)
        self.pb_all_val     = tk.DoubleVar(value=0.0)
        self.corrections_total   = 0
        self.corrections_timeout = 0

        # Font
        try:
            self.ui_font = tkfont.Font(family="Times New Roman", size=13)
        except Exception:
            self.ui_font = tkfont.Font(family="Times", size=13)

        # UI bauen
        self._build_setup()
        self._build_training()
        self._show_setup()

        # Timer
        self._tick_handle = None

    # ---------- Setup-Ansicht ----------
    def _build_setup(self):
        self.setup = ttk.Frame(self); self.setup.pack(fill="both", expand=True)
        ttk.Label(self.setup, text="Vorlagen laden (Mehrfachauswahl)", font=("Segoe UI", 16, "bold")).pack(pady=(12,4))

        fr = ttk.Frame(self.setup); fr.pack(fill="x", padx=12)
        ttk.Button(fr, text="Dateien wählen…", command=self._choose_files).pack(side="left")
        ttk.Label(fr, textvariable=self.files_label).pack(side="left", padx=8)

        prof = ttk.LabelFrame(self.setup, text="Profile"); prof.pack(fill="x", padx=12, pady=8)
        ttk.Checkbutton(prof, text="Zivil", variable=self.var_zivil).pack(side="left", padx=(4,8))
        ttk.Checkbutton(prof, text="Straf", variable=self.var_straf).pack(side="left", padx=8)
        ttk.Checkbutton(prof, text="ÖR",   variable=self.var_oer).pack(side="left", padx=8)

        opts = ttk.Frame(self.setup); opts.pack(fill="x", padx=12, pady=4)
        ttk.Label(opts, text="Min Wörter/Abs.:").grid(row=0, column=0, sticky="w", padx=(0,6))
        ttk.Spinbox(opts, from_=60, to=1500, textvariable=self.min_words, width=6).grid(row=0, column=1, sticky="w")
        ttk.Label(opts, text="Max Wörter/Abs.:").grid(row=0, column=2, sticky="w", padx=(12,6))
        ttk.Spinbox(opts, from_=120, to=3000, textvariable=self.max_words, width=6).grid(row=0, column=3, sticky="w")
        ttk.Label(opts, text="Sek/100 Wörter:").grid(row=0, column=4, sticky="w", padx=(12,6))
        ttk.Spinbox(opts, from_=10, to=600, textvariable=self.timer_100w, width=6).grid(row=0, column=5, sticky="w")
        ttk.Radiobutton(opts, text="Training", variable=self.mode, value="training").grid(row=1, column=0, pady=(6,0), sticky="w")
        ttk.Radiobutton(opts, text="Klausur",  variable=self.mode, value="klausur").grid(row=1, column=1, pady=(6,0), sticky="w")

        ttk.Button(self.setup, text="Session starten", command=self._start).pack(pady=12)

    # ---------- Trainingsansicht ----------
    def _build_training(self):
        self.train = ttk.Frame(self)

        top = ttk.Frame(self.train); top.pack(fill="x", padx=12, pady=(10,4))
        ttk.Label(top, textvariable=self.absatz_lbl_var).pack(side="left")
        ttk.Label(top, textvariable=self.points_lbl_var).pack(side="right", padx=(0,12))
        ttk.Label(top, textvariable=self.time_lbl_var).pack(side="right")

        pbf = ttk.Frame(self.train); pbf.pack(fill="x", padx=12, pady=(0,8))
        ttk.Label(pbf, text="Zeit (Absatz):").grid(row=0, column=0, sticky="w")
        self.pb_time = ttk.Progressbar(pbf, maximum=100.0, variable=self.pb_time_val)
        self.pb_time.grid(row=0, column=1, sticky="ew", padx=(8,0)); pbf.columnconfigure(1, weight=1)
        ttk.Label(pbf, text="Fortschritt gesamt:").grid(row=1, column=0, sticky="w", pady=(6,0))
        self.pb_all = ttk.Progressbar(pbf, maximum=100.0, variable=self.pb_all_val)
        self.pb_all.grid(row=1, column=1, sticky="ew", padx=(8,0), pady=(6,0))

        ctrl = ttk.Frame(self.train); ctrl.pack(fill="x", padx=12, pady=(0,8))
        ttk.Label(ctrl, text="Vergleich:").pack(side="left")
        ttk.OptionMenu(ctrl, self.compare_mode, self.compare_mode.get(), *COMPARE_MODES).pack(side="left", padx=(4,12))
        ttk.Label(ctrl, text="Maskierung:").pack(side="left")
        ttk.OptionMenu(ctrl, self.mask_level, self.mask_level.get(), *MASK_LEVELS, command=lambda *_: self._remask()).pack(side="left", padx=(4,12))
        ttk.Label(ctrl, text="Mask %:").pack(side="left")
        ttk.Spinbox(ctrl, from_=0, to=60, textvariable=self.mask_ratio, width=4, command=lambda: self._remask()).pack(side="left", padx=(4,12))
        ttk.Checkbutton(ctrl, text="nur Schlüsselbegriffe", variable=self.mask_keys_only, command=self._remask).pack(side="left")

        ttk.Label(self.train, text="Maskierter Absatz").pack(anchor="w", padx=12)
        self.txt_para = tk.Text(self.train, height=14, wrap="word", font=self.ui_font)
        self.txt_para.pack(fill="both", expand=True, padx=12, pady=(0,8)); self.txt_para.configure(state="disabled")

        ttk.Label(self.train, text="Dein Text").pack(anchor="w", padx=12)
        self.txt_typed = tk.Text(self.train, height=14, wrap="word", font=self.ui_font)
        self.txt_typed.pack(fill="both", expand=True, padx=12, pady=(0,8))

        bottom = ttk.Frame(self.train); bottom.pack(fill="x", padx=12, pady=(0,10))
        ttk.Button(bottom, text="Weiter (Strg+Enter)", command=self._next).pack(side="left")
        ttk.Button(bottom, text="Fertig & Export", command=self._finish).pack(side="right")

        self.bind_all("<Control-Return>", lambda e: self._next())

    # ---------- View switch ----------
    def _show_setup(self):
        if hasattr(self, "train"):
            self.train.pack_forget()
        self.setup.pack(fill="both", expand=True)

    def _show_training(self):
        self.setup.pack_forget()
        self.train.pack(fill="both", expand=True)

    # ---------- Helpers ----------
    def _choose_files(self):
        paths = filedialog.askopenfilenames(filetypes=[
            ("Unterstützte Dateien", "*.pdf;*.md;*.markdown;*.txt"),
            ("PDF", "*.pdf"), ("Markdown", "*.md;*.markdown"), ("Text", "*.txt"), ("Alle", "*.*"),
        ])
        if paths:
            self.file_paths = list(paths)
            self.files_label.set(Path(paths[0]).name if len(paths)==1 else f"{len(paths)} Dateien gewählt")

    def _profiles(self) -> List[Profile]:
        keys = []
        if self.var_zivil.get(): keys.append("zivil")
        if self.var_straf.get(): keys.append("straf")
        if self.var_oer.get():   keys.append("oer")
        return [PROFILES[k] for k in keys]

    # ---------- Session ----------
    def _start(self):
        profs = self._profiles()
        if not profs:
            messagebox.showerror("Fehler", "Mindestens ein Profil wählen."); return
        if not self.file_paths:
            messagebox.showerror("Fehler", "Bitte mindestens eine Datei wählen."); return
        try:
            text = load_texts(self.file_paths)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", str(e)); return

        self.paragraphs = split_paragraphs(text, self.min_words.get(), self.max_words.get())
        if not self.paragraphs:
            messagebox.showerror("Fehler", "Keine Absätze erkannt."); return

        self.typed = ["" for _ in self.paragraphs]
        self.per_para = [ParaState() for _ in self.paragraphs]
        self.current_idx = 0
        self.corrections_total   = 0
        self.corrections_timeout = 0
        self._update_score()

        self._load_para()
        self._show_training()
        self._start_tick()

    def _load_para(self):
        i = self.current_idx
        para = self.paragraphs[i]
        ps = self.per_para[i]
        ps.timed_out_handled = False
        ps.budget   = seconds_for_paragraph(para, self.timer_100w.get(), self._profiles())
        ps.start_ts = time.time()
        self.absatz_lbl_var.set(f"Absatz {i+1}/{len(self.paragraphs)}")

        self._remask()
        self.txt_typed.configure(state="normal"); self.txt_typed.delete("1.0", "end")
        self._update_overall_progress()

    def _remask(self):
        if not self.paragraphs: return
        para = self.paragraphs[self.current_idx]
        masked = apply_masking(
            para,
            self.mask_level.get(),
            ratio=max(0.0, min(0.6, self.mask_ratio.get()/100.0)),
            keys_only=self.mask_keys_only.get()
        )
        self.txt_para.configure(state="normal"); self.txt_para.delete("1.0", "end")
        self.txt_para.insert("1.0", masked); self.txt_para.configure(state="disabled")

    def _show_diff(self, left_text: str, right_text: str):
        """Tokenbasierte Diff-Ansicht (rot/grün)."""
        import difflib
        top = tk.Toplevel(self); top.title("Diff-Ansicht"); top.geometry("1000x600")
        pan = ttk.Panedwindow(top, orient="horizontal"); pan.pack(fill="both", expand=True, padx=10, pady=8)
        f1, f2 = ttk.Frame(pan), ttk.Frame(pan); pan.add(f1, weight=1); pan.add(f2, weight=1)

        ttk.Label(f1, text="Original (normalisiert)").pack(anchor="w")
        t1 = tk.Text(f1, wrap="word"); sb1 = ttk.Scrollbar(f1, orient="vertical", command=t1.yview)
        t1.configure(yscrollcommand=sb1.set); t1.pack(side="left", fill="both", expand=True); sb1.pack(side="left", fill="y")

        ttk.Label(f2, text="Dein Text (normalisiert)").pack(anchor="w")
        t2 = tk.Text(f2, wrap="word"); sb2 = ttk.Scrollbar(f2, orient="vertical", command=t2.yview)
        t2.configure(yscrollcommand=sb2.set); t2.pack(side="left", fill="both", expand=True); sb2.pack(side="left", fill="y")

        t1.tag_config("bad", background="#ffe3e3"); t2.tag_config("add", background="#e6ffed")

        def tok(s: str):  # tokenisiere Wörter, Satzzeichen, Leerraum
            return re.findall(r"\w+|[^\w\s]+|\s+", s)
        A, B = tok(left_text), tok(right_text)
        sm = difflib.SequenceMatcher(a=A, b=B)
        for tag, a0, a1, b0, b1 in sm.get_opcodes():
            segA, segB = "".join(A[a0:a1]), "".join(B[b0:b1])
            if tag == "equal":
                t1.insert("end", segA); t2.insert("end", segB)
            elif tag == "delete":
                t1.insert("end", segA, "bad")
            elif tag == "insert":
                t2.insert("end", segB, "add")
            elif tag == "replace":
                t1.insert("end", segA, "bad"); t2.insert("end", segB, "add")

        ttk.Button(ttk.Frame(top), text="Schließen", command=top.destroy).pack(side="right", pady=8, padx=8)

    def _next(self, auto: bool = False):
        # Bewertung (Edit-Distanz)
        original  = self.paragraphs[self.current_idx]
        typed     = self.txt_typed.get("1.0", "end").strip()

        exp_norm   = normalize_text(original, self.compare_mode.get())
        typed_norm = normalize_text(typed,    self.compare_mode.get())
        dist = levenshtein(exp_norm, typed_norm)
        base_len = max(1, len(exp_norm))
        per_k = int(1000 * dist / base_len)
        accuracy = max(0.0, min(100.0, 100.0 * (1.0 - (dist / base_len))))

        # Feedback
        messagebox.showinfo(
            "Feedback",
            f"""Edit-Distanz: {dist}
Fehler/1000 Zeichen: {per_k}
Trefferquote: {accuracy:.1f}%
Vergleich: {self.compare_mode.get()}"""
        )

        # Diff
        self._show_diff(exp_norm, typed_norm)

        # Klausurmodus: Mindestquote 85 % → ggf. gleiche Zeit neu starten
        if self.mode.get() == "klausur" and accuracy < 85.0:
            ps = self.per_para[self.current_idx]
            ps.start_ts = time.time()  # Timer neu
            # Budget gleich lassen (optional neu berechnen, ergäbe idR den gleichen Wert):
            ps.budget = max(30, ps.budget // 4)  # halbe Restzeit, aber mindestens 30 Sekunden
            ps.timed_out_handled = False
            self.pb_time_val.set(0.0)

            # Punkte-Abzüge
            self.corrections_total += 1
            if auto:
                self.corrections_timeout += 1
            self._update_score()

            messagebox.showwarning(
                "Korrektur nötig",
                f"Trefferquote {accuracy:.1f}% < 85%. Die Zeit wurde neu gestartet – korrigiere und drücke erneut auf Weiter."
            )
            return  # Absatz bleibt aktiv

        # bestanden → speichern & weiter
        self.typed[self.current_idx] = typed
        ps = self.per_para[self.current_idx]
        ps.timed_out_handled = False

        if self.current_idx < len(self.paragraphs) - 1:
            self.current_idx += 1
            self._load_para()
        else:
            self._finish()

    def _finish(self):
        # Timer stoppen
        if getattr(self, "_tick_handle", None) is not None:
            try: self.after_cancel(self._tick_handle)
            except Exception: pass
            self._tick_handle = None

        out_text = "\n\n".join(self.typed)
        out_md = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
            title="Speichern als…"
        )
        if out_md:
            try:
                export_text_md(out_text, Path(out_md))
                messagebox.showinfo("Export", f"Gespeichert: {out_md}")
            except Exception as e:
                messagebox.showerror("Export fehlgeschlagen", str(e))

        if REPORTLAB and messagebox.askyesno("PDF", "Auch als PDF exportieren?"):
            out_pdf = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                title="PDF speichern als…"
            )
            if out_pdf:
                try:
                    export_text_pdf(out_text, Path(out_pdf), title="Dein Text — Gutty")
                    messagebox.showinfo("Export", f"PDF gespeichert: {out_pdf}")
                except Exception as e:
                    messagebox.showerror("PDF-Export fehlgeschlagen", str(e))

        # Ergebnisfenster mit Prozentanzeige
        total_max = len(self.paragraphs) * SCORE_POINTS_PER_PARAGRAPH
        current = max(
            0,
            total_max
            - self.corrections_total   * SCORE_PENALTY_PER_CORRECTION
            - self.corrections_timeout * SCORE_TIMEOUT_EXTRA_PENALTY
        )
        percent = (100.0 * current / total_max) if total_max else 0.0

        win = tk.Toplevel(self); win.title("Ergebnis & Punkte"); win.geometry("560x280")
        ttk.Label(
            win,
            text=f"Punkte gesamt: {current}/{total_max} (≈ {percent:.1f}%)",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(12,6))
        txt = tk.Text(win, height=8, wrap="word", font=self.ui_font)
        txt.pack(fill="both", expand=True, padx=12, pady=(0,10))
        txt.insert("1.0", (
            f"Absätze insgesamt: {len(self.paragraphs)}\n"
            f"Nachkorrekturen gesamt: {self.corrections_total}\n"
            f"…davon wegen Zeitablauf: {self.corrections_timeout} (Extra-Abzug je {SCORE_TIMEOUT_EXTRA_PENALTY})\n\n"
            f"Prozentsatz der Maximalpunkte: {percent:.1f}%\n"
        ))
        txt.configure(state="disabled")
        ttk.Button(win, text="Schließen", command=self.destroy).pack(pady=8)

    # ---------- Timer ----------
    def _start_tick(self):
        if getattr(self, "_tick_handle", None) is None:
            self._tick()

    def _tick(self):
        if not self.paragraphs:
            return
        i  = self.current_idx
        ps = self.per_para[i]
        elapsed = max(0, int(time.time() - ps.start_ts))
        budget  = max(1, ps.budget)
        percent = min(100.0, (elapsed / budget) * 100.0)

        self.pb_time_val.set(percent)
        self.time_lbl_var.set(f"Zeit: {elapsed}/{budget}s")

        # Auto-Weiter genau einmal pro Überschreiten
        if self.mode.get() == "klausur" and elapsed > budget and not ps.timed_out_handled:
            ps.timed_out_handled = True
            self._next(auto=True)
            # nächster Tick (neuer Timer oder nächster Absatz)
            self._tick_handle = self.after(300, self._tick)
            return

        # Eingabe immer möglich
        self.txt_typed.configure(state="normal")
        self._tick_handle = self.after(300, self._tick)

    def _update_overall_progress(self):
        total = len(self.paragraphs)
        done  = self.current_idx
        self.pb_all_val.set((done / total) * 100.0 if total else 0.0)
        self._update_score()

    def _update_score(self):
        total_max = len(self.paragraphs) * SCORE_POINTS_PER_PARAGRAPH if self.paragraphs else 0
        current = max(
            0,
            total_max
            - self.corrections_total   * SCORE_PENALTY_PER_CORRECTION
            - self.corrections_timeout * SCORE_TIMEOUT_EXTRA_PENALTY
        )
        self.points_lbl_var.set(f"Punkte: {current}/{total_max}")

# ---------- main ----------
if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        try:
            import tkinter  # noqa: F401
        except Exception:
            print("Tkinter nicht verfügbar. Starte stattdessen den CLI-Modus.")
            run_cli()
            sys.exit(0)
        app = GuttyApp()
        app.mainloop()
