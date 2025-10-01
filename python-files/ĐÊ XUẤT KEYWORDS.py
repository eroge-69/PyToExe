# keyword_exporter_gui_plus.py
# Keyword Exporter for Stock Footage — GUI with persistent memory (SQLite)
# IMPROVED: clipboard copy, mark-used-on-copy, editable blocklist (DB), hotkeys, and quality-of-life UI tweaks
# - Generate English keywords from seed words + WordNet (synonyms/hypernyms/hyponyms)
# - Curated "style packs" for camera / lighting / mood / time / weather / motion / framing / color
# - Persistent memory: once exported / copied / marked-as-used, keywords won't be suggested again
# - New: One-click Copy (All / Selected) with selectable formats, optional auto mark-used on copy
# - New: Editable blocklist stored in DB (import/export/add/remove) and used during generation & input cleaning
# - New: Hotkeys (Ctrl+G Generate, Ctrl+Shift+C Copy All, Ctrl+Shift+S Copy Selected)
# - Robust Tkinter UI (no external GUI deps). Optional WordNet; graceful fallback if not installed.
# - Exports CSV or TXT (one-per-line or comma-separated)
#
# By ChatGPT — 2025-09-12

import os
import re
import csv
import json
import random
import sqlite3
from datetime import datetime
from collections import defaultdict
from typing import List, Set, Tuple, Dict

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- Optional WordNet ----------
WN_AVAILABLE = True
try:
    from nltk.corpus import wordnet as wn
except Exception:
    WN_AVAILABLE = False

APP_NAME = "Trình Xuất Keyword+"
DB_PATH = os.path.join(os.path.dirname(__file__), "keywords_memory.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "keywords_gui.log")

# ---------- Helpers ----------
DEFAULT_BLOCKLIST = {
    # Avoid trademarks / brands / risky generic terms
    "google", "facebook", "instagram", "tiktok", "twitter", "apple", "microsoft", "adobe", "netflix",
    "uber", "tesla", "coca", "cola", "nike", "adidas", "spacex", "lego", "disney",
    # Too-generic / low-signal words
    "thing", "stuff", "nice", "good", "bad", "object", "item", "concept",
}

STYLE_PACKS = {
    "camera": [
        "wide shot", "close-up", "macro", "overhead", "low angle", "high angle", "dutch tilt", "handheld",
        "tripod", "tracking", "dolly", "gimbal", "drone", "crane", "slider", "pan", "tilt",
        "static", "rack focus", "deep focus"
    ],
    "lighting": [
        "soft light", "hard light", "backlight", "rim light", "golden hour", "blue hour", "neon-lit",
        "tungsten", "daylight", "overcast", "high key", "low key", "silhouette", "bokeh", "prism flare"
    ],
    "mood": [
        "serene", "dramatic", "moody", "uplifting", "playful", "minimal", "vibrant", "nostalgic",
        "cinematic", "elegant", "energetic", "mellow", "mysterious", "dreamy"
    ],
    "time": [
        "sunrise", "morning", "noon", "afternoon", "sunset", "twilight", "night"
    ],
    "weather": [
        "clear sky", "cloudy", "overcast", "foggy", "misty", "rainy", "snowy", "windy", "stormy"
    ],
    "motion": [
        "time-lapse", "hyperlapse", "slow motion", "fast motion", "freeze frame", "speed ramp"
    ],
    "framing": [
        "rule of thirds", "centered", "symmetry", "leading lines", "negative space", "framed subject"
    ],
    "color": [
        "monochrome", "pastel", "vivid", "duotone", "teal and orange", "earth tones", "neon",
        "warm tones", "cool tones", "high contrast"
    ],
}

# NEW: Seed suggestion pools (bổ sung được tuỳ ý)
SUGGEST_SEED_POOLS: Dict[str, List[str]] = {
    "nature": [
        "forest", "meadow", "mountain", "valley", "desert", "oasis", "reef", "glacier", "canyon",
        "waterfall", "river", "stream", "lake", "pond", "beach", "coast", "shore", "cliff", "cave",
        "savanna", "jungle", "rainforest", "mangrove", "wetland", "marsh", "bog", "dune"
    ],
    "urban": [
        "alley", "boulevard", "plaza", "bridge", "skyscraper", "subway", "crosswalk", "intersection",
        "neon", "billboard", "warehouse", "rooftop", "parking lot", "tunnel", "overpass", "underpass",
        "roundabout", "tram", "station", "harbor", "market", "arcade"
    ],
    "abstract": [
        "geometry", "pattern", "gradient", "noise", "fluid", "smoke", "particle", "wave", "glow",
        "nebula", "fractal", "plasma", "bokeh", "texture", "refraction", "reflection", "diffraction",
        "silhouette", "shadow", "overlay", "displacement", "caustics"
    ],
    "technology": [
        "circuit", "motherboard", "microchip", "server", "datacenter", "cloud", "satellite", "antenna",
        "robotics", "hologram", "interface", "dashboard", "hud", "network", "algorithm", "encryption",
        "sensor", "fiber optic", "battery", "solar panel", "wind turbine"
    ],
    "materials": [
        "glass", "metal", "steel", "copper", "aluminum", "wood", "marble", "granite", "concrete",
        "asphalt", "ceramic", "fabric", "linen", "wool", "silk", "paper", "cardboard", "leather",
        "plastic", "acrylic", "resin"
    ],
    "colors": [
        "red", "crimson", "scarlet", "orange", "amber", "gold", "yellow", "lime", "green", "emerald",
        "teal", "cyan", "blue", "navy", "indigo", "violet", "magenta", "pink", "fuchsia", "beige",
        "ivory", "white", "gray", "black", "monochrome", "pastel", "neon", "duotone"
    ],
    "shapes": [
        "circle", "sphere", "cube", "square", "triangle", "pyramid", "prism", "torus", "hexagon",
        "octagon", "grid", "mesh", "lattice", "spiral", "helix", "waveform", "ring", "arc", "line", "curve"
    ],
    "actions": [
        "splash", "ripples", "swirl", "sparkle", "drift", "shatter", "melt", "ignite", "glide", "pulse",
        "flicker", "flutter", "oscillate", "rotate", "spin", "zoom", "pan", "tilt", "vibrate", "expand",
        "contract"
    ],
    "light": [
        "spotlight", "backlight", "rim light", "sunbeam", "flare", "glare", "glitter", "glow", "haze",
        "mist", "volumetric light"
    ],
    "weather": [
        "fog", "mist", "rain", "drizzle", "snow", "hail", "storm", "lightning", "wind", "overcast",
        "clear sky"
    ],
    "time": [
        "sunrise", "morning", "noon", "afternoon", "sunset", "twilight", "midnight", "night",
        "golden hour", "blue hour", "dawn", "dusk"
    ],
    "water": [
        "ocean", "sea", "lake", "river", "stream", "tide", "wave", "foam", "bubble", "droplet", "rainfall"
    ],
    "textures": [
        "grain", "grit", "pebble", "sand", "velvet", "satin", "matte", "glossy", "rough", "smooth",
        "brushed metal", "polished stone", "weathered wood"
    ],
    "scenes": [
        "studio", "workbench", "laboratory", "kitchen", "greenhouse", "workstation", "office", "library",
        "gallery", "museum", "workshop"
    ],
    "food": [
        "coffee", "tea", "chocolate", "honey", "spice", "citrus", "lemon", "orange", "berry",
        "strawberry", "raspberry", "blueberry", "grape", "mango", "avocado", "almond", "wheat", "rice",
        "noodle", "bread", "pastry"
    ],
}

POS_MAP = {
    "noun": "n",
    "verb": "v",
    "adj": "a",
    "adv": "r",
}

# ---------- DB ----------

def init_db(db_path: str = DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS used_keywords (
            keyword TEXT PRIMARY KEY,
            first_seen TEXT NOT NULL,
            source_context TEXT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS blocklist (
            keyword TEXT PRIMARY KEY,
            first_seen TEXT NOT NULL,
            source_context TEXT
        );
        """
    )
    con.commit()

    # Seed DB blocklist if empty with defaults
    cur.execute("SELECT COUNT(*) FROM blocklist")
    if cur.fetchone()[0] == 0:
        ts = datetime.utcnow().isoformat()
        cur.executemany(
            "INSERT OR IGNORE INTO blocklist (keyword, first_seen, source_context) VALUES (?, ?, ?)",
            [(kw, ts, "seed:DEFAULT_BLOCKLIST") for kw in sorted(DEFAULT_BLOCKLIST)]
        )
        con.commit()
    return con


def log_audit(con: sqlite3.Connection, action: str, details: str = ""):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO audit_log (ts, action, details) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), action, details)
    )
    con.commit()


# ---------- Text cleaning ----------
_whitespace = re.compile(r"\s+")
_non_alpha_space = re.compile(r"[^a-zA-Z\s]+")


def clean_phrase(s: str) -> str:
    s = s.strip().lower()
    s = _non_alpha_space.sub(" ", s)
    s = _whitespace.sub(" ", s)
    return s.strip()


# ---------- WordNet expansion ----------

def expand_wordnet(seed: str, pos_tags: Set[str]) -> Tuple[List[str], List[str], List[str]]:
    """Return (synonyms, hyponyms, hypernyms) lists for seed using WordNet.
    If WordNet not available, return empty lists.
    """
    if not WN_AVAILABLE:
        return [], [], []

    syns = set()
    hypos = set()
    hypers = set()

    for pos_name in pos_tags:
        pos = POS_MAP.get(pos_name)
        if not pos:
            continue
        try:
            for synset in wn.synsets(seed, pos=pos):
                # synonyms
                for lemma in synset.lemmas():
                    syns.add(lemma.name().replace('_', ' '))
                # hyponyms
                for h in synset.hyponyms():
                    for lemma in h.lemmas():
                        hypos.add(lemma.name().replace('_', ' '))
                # hypernyms
                for h in synset.hypernyms():
                    for lemma in h.lemmas():
                        hypers.add(lemma.name().replace('_', ' '))
        except Exception:
            continue

    def cleaned(lst: Set[str]) -> List[str]:
        out = []
        for w in lst:
            cw = clean_phrase(w)
            if cw:
                out.append(cw)
        return out

    return cleaned(syns), cleaned(hypos), cleaned(hypers)


# ---------- Candidate assembly & ranking ----------

def assemble_candidates(
    seeds: List[str],
    pos_tags: Set[str],
    include: Set[str],
    exclude: Set[str],
    packs_selected: Set[str],
    allow_phrases: bool,
    used: Set[str],
    blocklist: Set[str],
    max_items: int,
) -> Tuple[List[str], Dict[str, int]]:
    """Build a ranked, de-duplicated keyword list, skipping already-used.
    Returns (candidates, stats) where stats counts how many filtered by reason.
    """
    stats = defaultdict(int)
    seen: Set[str] = set()
    results: List[Tuple[int, str]] = []  # (score, keyword)

    # 1) From seeds via WordNet
    for raw_seed in seeds:
        seed = clean_phrase(raw_seed)
        if not seed:
            continue
        if seed not in used and seed not in blocklist:
            if (allow_phrases or ' ' not in seed):
                if seed not in seen:
                    seen.add(seed)
                    results.append((1000, seed))  # highest priority
        syns, hypos, hypers = expand_wordnet(seed, pos_tags)
        for w in syns:
            _push(results, seen, used, blocklist, w, 900, allow_phrases, stats)
        for w in hypos:
            _push(results, seen, used, blocklist, w, 800, allow_phrases, stats)
        for w in hypers:
            _push(results, seen, used, blocklist, w, 700, allow_phrases, stats)

    # 2) Include manual 'include' list (high priority)
    for w in include:
        w = clean_phrase(w)
        _push(results, seen, used, blocklist, w, 950, allow_phrases, stats)

    # 3) Style packs
    for pack in packs_selected:
        for w in STYLE_PACKS.get(pack, []):
            w = clean_phrase(w)
            _push(results, seen, used, blocklist, w, 600, allow_phrases, stats)

    # 4) Exclude filters (apply at the end to remove any that slipped in)
    final = []
    for score, w in results:
        if w in exclude or w in blocklist:
            stats['blocked_exclude_or_blocklist'] += 1
            continue
        final.append((score, w))

    # 5) Sort by score desc, then alphabetically for stability
    final.sort(key=lambda x: (-x[0], x[1]))

    # 6) Limit
    limited = [w for _, w in final[:max_items]]
    return limited, stats


def _push(results, seen, used, blocklist, w, score, allow_phrases, stats):
    if not w:
        return
    if not allow_phrases and (' ' in w):
        stats['filtered_phrases'] += 1
        return
    if w in seen:
        stats['filtered_dupe_session'] += 1
        return
    if w in used:
        stats['filtered_used_memory'] += 1
        return
    if w in blocklist:
        stats['filtered_blocklist'] += 1
        return
    seen.add(w)
    results.append((score, w))


# ---------- DB I/O ----------

def load_used_keywords(con: sqlite3.Connection) -> Set[str]:
    cur = con.cursor()
    cur.execute("SELECT keyword FROM used_keywords")
    return {row[0] for row in cur.fetchall()}


def mark_used(con: sqlite3.Connection, keywords: List[str], context: str = ""):
    cur = con.cursor()
    ts = datetime.utcnow().isoformat()
    for kw in keywords:
        try:
            cur.execute(
                "INSERT OR IGNORE INTO used_keywords (keyword, first_seen, source_context) VALUES (?, ?, ?)",
                (kw, ts, context)
            )
        except Exception:
            pass
    con.commit()
    log_audit(con, "mark_used", json.dumps({"count": len(keywords)}))


def import_used_from_file(con: sqlite3.Connection, path: str) -> int:
    added = 0
    cur = con.cursor()
    ts = datetime.utcnow().isoformat()

    def insert_kw(kw: str):
        nonlocal added
        kwc = clean_phrase(kw)
        if not kwc:
            return
        try:
            cur.execute(
                "INSERT OR IGNORE INTO used_keywords (keyword, first_seen, source_context) VALUES (?, ?, ?)",
                (kwc, ts, f"import:{os.path.basename(path)}")
            )
            if cur.rowcount:
                added += 1
        except Exception:
            pass

    if path.lower().endswith(".csv"):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'keyword' in reader.fieldnames:
                for row in reader:
                    insert_kw(row.get('keyword', ''))
            else:
                f.seek(0)
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        insert_kw(row[0])
    else:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        parts = re.split(r"[\n,]", text)
        for p in parts:
            insert_kw(p)
    con.commit()
    log_audit(con, "import_used", json.dumps({"path": path, "added": added}))
    return added


def export_used_to_file(con: sqlite3.Connection, path: str) -> int:
    cur = con.cursor()
    cur.execute("SELECT keyword, first_seen, source_context FROM used_keywords ORDER BY keyword")
    rows = cur.fetchall()
    if path.lower().endswith('.csv'):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["keyword", "first_seen", "source_context"])
            for r in rows:
                writer.writerow(list(r))
    else:
        with open(path, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(r[0] + "\n")
    log_audit(con, "export_used", json.dumps({"path": path, "count": len(rows)}))
    return len(rows)


# ---- Blocklist I/O ----

def load_blocklist(con: sqlite3.Connection) -> Set[str]:
    cur = con.cursor()
    cur.execute("SELECT keyword FROM blocklist")
    return {row[0] for row in cur.fetchall()} | set(DEFAULT_BLOCKLIST)


def add_blocklist_keywords(con: sqlite3.Connection, kws: List[str], context: str = "manual") -> int:
    cur = con.cursor()
    ts = datetime.utcnow().isoformat()
    added = 0
    for kw in kws:
        c = clean_phrase(kw)
        if not c:
            continue
        try:
            cur.execute(
                "INSERT OR IGNORE INTO blocklist (keyword, first_seen, source_context) VALUES (?, ?, ?)",
                (c, ts, context)
            )
            if cur.rowcount:
                added += 1
        except Exception:
            pass
    con.commit()
    log_audit(con, "blocklist_add", json.dumps({"count": added}))
    return added


def delete_blocklist_keywords(con: sqlite3.Connection, kws: List[str]) -> int:
    cur = con.cursor()
    deleted = 0
    for kw in kws:
        try:
            cur.execute("DELETE FROM blocklist WHERE keyword=?", (kw,))
            deleted += cur.rowcount
        except Exception:
            pass
    con.commit()
    log_audit(con, "blocklist_delete", json.dumps({"count": deleted}))
    return deleted


def import_blocklist_from_file(con: sqlite3.Connection, path: str) -> int:
    ts = datetime.utcnow().isoformat()
    cur = con.cursor()
    added = 0

    def insert_kw(kw: str):
        nonlocal added
        k = clean_phrase(kw)
        if not k:
            return
        try:
            cur.execute(
                "INSERT OR IGNORE INTO blocklist (keyword, first_seen, source_context) VALUES (?, ?, ?)",
                (k, ts, f"import:{os.path.basename(path)}")
            )
            if cur.rowcount:
                added += 1
        except Exception:
            pass

    if path.lower().endswith('.csv'):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'keyword' in reader.fieldnames:
                for row in reader:
                    insert_kw(row.get('keyword', ''))
            else:
                f.seek(0)
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        insert_kw(row[0])
    else:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        parts = re.split(r"[\n,]", text)
        for p in parts:
            insert_kw(p)

    con.commit()
    log_audit(con, "blocklist_import", json.dumps({"path": path, "added": added}))
    return added


def export_blocklist_to_file(con: sqlite3.Connection, path: str) -> int:
    cur = con.cursor()
    cur.execute("SELECT keyword, first_seen, source_context FROM blocklist ORDER BY keyword")
    rows = cur.fetchall()
    if path.lower().endswith('.csv'):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["keyword", "first_seen", "source_context"])
            for r in rows:
                writer.writerow(list(r))
    else:
        with open(path, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(r[0] + "\n")
    log_audit(con, "blocklist_export", json.dumps({"path": path, "count": len(rows)}))
    return len(rows)


# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1120x760")
        self.minsize(980, 680)

        self.con = init_db(DB_PATH)
        self.used_cache = load_used_keywords(self.con)
        self.blocklist = load_blocklist(self.con)

        self._build_ui()
        self._refresh_stats()
        self._bind_hotkeys()

    # UI construction
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        self.page_generate = ttk.Frame(nb)
        self.page_memory = ttk.Frame(nb)
        self.page_about = ttk.Frame(nb)
        nb.add(self.page_generate, text="Tạo từ khoá")
        nb.add(self.page_memory, text="Bộ nhớ")
        nb.add(self.page_about, text="Giới thiệu")

        self._build_generate()
        self._build_memory()
        self._build_about()

    def _build_generate(self):
        root = self.page_generate

        # Top: inputs (left/right columns)
        top = ttk.Frame(root)
        top.pack(fill=tk.X, padx=12, pady=8)

        left = ttk.Frame(top)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        right = ttk.Frame(top)
        right.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # Seeds
        ttk.Label(left, text="Từ gốc (seed) — ngăn cách bằng dấu phẩy hoặc xuống dòng").pack(anchor=tk.W)
        self.txt_seeds = tk.Text(left, height=5)
        self.txt_seeds.pack(fill=tk.BOTH, expand=True)

        # NEW: Seed Suggest Toolbar
        sugbar = ttk.Frame(left)
        sugbar.pack(fill=tk.X, pady=(6, 2))
        ttk.Label(sugbar, text="Đề xuất seed:").pack(side=tk.LEFT)
        ttk.Label(sugbar, text="Số lượng").pack(side=tk.LEFT, padx=(8, 2))
        self.var_suggest_count = tk.IntVar(value=20)
        tk.Spinbox(sugbar, from_=1, to=200, width=5, textvariable=self.var_suggest_count).pack(side=tk.LEFT)

        ttk.Label(sugbar, text="Nhóm").pack(side=tk.LEFT, padx=(8, 2))
        self.var_suggest_category = tk.StringVar(value="all")
        categories = ["all"] + sorted(SUGGEST_SEED_POOLS.keys())
        self.cmb_suggest_cat = ttk.Combobox(sugbar, values=categories, textvariable=self.var_suggest_category, width=14, state="readonly")
        self.cmb_suggest_cat.pack(side=tk.LEFT)

        self.var_suggest_unique = tk.BooleanVar(value=True)
        ttk.Checkbutton(sugbar, text="Không trùng (đã dùng/blocklist)", variable=self.var_suggest_unique).pack(side=tk.LEFT, padx=8)

        self.var_suggest_mode = tk.StringVar(value="append")
        ttk.Radiobutton(sugbar, text="Thêm", variable=self.var_suggest_mode, value="append").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(sugbar, text="Thay thế", variable=self.var_suggest_mode, value="replace").pack(side=tk.LEFT, padx=4)

        ttk.Button(sugbar, text="Đề xuất ngay", command=self.on_suggest_seeds).pack(side=tk.RIGHT)

        # Include / Exclude
        cols = ttk.Frame(left)
        cols.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        col1 = ttk.Frame(cols)
        col2 = ttk.Frame(cols)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        ttk.Label(col1, text="Bắt buộc thêm (Include)").pack(anchor=tk.W)
        self.txt_include = tk.Text(col1, height=5)
        self.txt_include.pack(fill=tk.BOTH, expand=True)

        ttk.Label(col2, text="Loại trừ (Exclude)").pack(anchor=tk.W)
        self.txt_exclude = tk.Text(col2, height=5)
        self.txt_exclude.pack(fill=tk.BOTH, expand=True)

        # Right side: options
        opt = ttk.LabelFrame(right, text="Tuỳ chọn")
        opt.pack(fill=tk.BOTH, expand=True)

        # Packs
        self.pack_vars: Dict[str, tk.BooleanVar] = {}
        packs_frame = ttk.Frame(opt)
        packs_frame.pack(fill=tk.X, pady=(8, 4))
        ttk.Label(packs_frame, text="Gói phong cách (footage):").pack(anchor=tk.W)
        packs1 = ttk.Frame(packs_frame); packs1.pack(fill=tk.X)
        packs2 = ttk.Frame(packs_frame); packs2.pack(fill=tk.X)
        half = (len(STYLE_PACKS) + 1) // 2
        pack_names = list(STYLE_PACKS.keys())
        for i, name in enumerate(pack_names):
            var = tk.BooleanVar(value=(name in {"camera", "lighting", "mood"}))
            self.pack_vars[name] = var
            parent = packs1 if i < half else packs2
            ttk.Checkbutton(parent, text=name, variable=var).pack(side=tk.LEFT, padx=4, pady=2)

        # POS
        self.pos_vars: Dict[str, tk.BooleanVar] = {
            "noun": tk.BooleanVar(value=True),
            "adj": tk.BooleanVar(value=True),
            "verb": tk.BooleanVar(value=False),
            "adv": tk.BooleanVar(value=False),
        }
        pos_frame = ttk.Frame(opt)
        pos_frame.pack(fill=tk.X, pady=(8, 4))
        ttk.Label(pos_frame, text="Từ loại (WordNet):").pack(anchor=tk.W)
        for name, var in self.pos_vars.items():
            ttk.Checkbutton(pos_frame, text=name, variable=var).pack(side=tk.LEFT, padx=4)

        # Misc toggles
        toggles = ttk.Frame(opt)
        toggles.pack(fill=tk.X, pady=(8, 4))
        self.var_allow_phrases = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggles, text="Cho phép cụm từ nhiều từ (multi-word)", variable=self.var_allow_phrases).pack(side=tk.LEFT, padx=4)
        self.var_mark_used_on_export = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggles, text="Đánh dấu đã dùng khi xuất", variable=self.var_mark_used_on_export).pack(side=tk.LEFT, padx=4)
        self.var_mark_used_on_copy = tk.BooleanVar(value=True)
        ttk.Checkbutton(toggles, text="Đánh dấu đã dùng khi COPY", variable=self.var_mark_used_on_copy).pack(side=tk.LEFT, padx=4)

        # Output/Clipboard format
        fmt = ttk.LabelFrame(opt, text="Định dạng (Xuất / Clipboard)")
        fmt.pack(fill=tk.X, pady=(8, 4))
        self.var_format = tk.StringVar(value="csv")
        rb1 = ttk.Radiobutton(fmt, text="CSV (1 cột: keyword)", variable=self.var_format, value="csv")
        rb2 = ttk.Radiobutton(fmt, text="TXT (mỗi dòng 1 từ)", variable=self.var_format, value="txt_lines")
        rb3 = ttk.Radiobutton(fmt, text="TXT (phân tách bằng dấu phẩy)", variable=self.var_format, value="txt_csv")
        for rb in (rb1, rb2, rb3):
            rb.pack(side=tk.LEFT, padx=6)

        # Max items
        row = ttk.Frame(opt); row.pack(fill=tk.X, pady=(8, 4))
        ttk.Label(row, text="Số lượng tối đa:").pack(side=tk.LEFT)
        self.var_max = tk.IntVar(value=10000)
        tk.Spinbox(row, from_=20, to=10000, textvariable=self.var_max, width=6).pack(side=tk.LEFT, padx=6)

        # Action buttons
        btns = ttk.Frame(root); btns.pack(fill=tk.X, padx=12, pady=6)
        ttk.Button(btns, text="Tạo danh sách (Ctrl+G)", command=self.on_generate).pack(side=tk.LEFT)
        ttk.Button(btns, text="Copy TẤT CẢ (Ctrl+Shift+C)", command=self.on_copy_all).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Copy mục đã chọn (Ctrl+Shift+S)", command=self.on_copy_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Xuất…", command=self.on_export).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Đánh dấu đã dùng (không xuất)", command=self.on_mark_used).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Xoá xem trước", command=self.on_clear_preview).pack(side=tk.LEFT, padx=6)
        if not WN_AVAILABLE:
            ttk.Button(btns, text="Cài WordNet", command=self.on_wordnet_help).pack(side=tk.RIGHT)

        # Preview list
        mid = ttk.Frame(root); mid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.lst = tk.Listbox(mid, selectmode=tk.EXTENDED)
        self.lst.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.lst.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.lst.configure(yscrollcommand=sb.set)

        # Stats
        self.lbl_status = ttk.Label(root, text="Sẵn sàng.")
        self.lbl_status.pack(anchor=tk.W, padx=12, pady=(0, 10))

    def _build_memory(self):
        root = self.page_memory
        top = ttk.Frame(root); top.pack(fill=tk.X, padx=12, pady=10)
        self.lbl_mem = ttk.Label(top, text="Bộ nhớ: …")
        self.lbl_mem.pack(side=tk.LEFT)
        ttk.Button(top, text="Làm mới", command=self._refresh_stats).pack(side=tk.LEFT, padx=8)

        # Search used keywords
        sr = ttk.Frame(root); sr.pack(fill=tk.X, padx=12, pady=6)
        ttk.Label(sr, text="Tìm trong bộ nhớ đã dùng:").pack(side=tk.LEFT)
        self.var_search = tk.StringVar()
        ttk.Entry(sr, textvariable=self.var_search, width=30).pack(side=tk.LEFT, padx=6)
        ttk.Button(sr, text="Tìm", command=self.on_search_used).pack(side=tk.LEFT)

        # Used list
        mid = ttk.Frame(root); mid.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        self.lst_used = tk.Listbox(mid, selectmode=tk.EXTENDED)
        self.lst_used.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.lst_used.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.lst_used.configure(yscrollcommand=sb.set)

        # Memory controls
        ctl = ttk.Frame(root); ctl.pack(fill=tk.X, padx=12, pady=10)
        ttk.Button(ctl, text="Nhập danh sách đã dùng…", command=self.on_import_used).pack(side=tk.LEFT)
        ttk.Button(ctl, text="Xuất bộ nhớ…", command=self.on_export_used).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctl, text="Xoá mục đã chọn", command=self.on_delete_selected_used).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctl, text="Xoá TOÀN BỘ", command=self.on_reset_all).pack(side=tk.RIGHT)

        # --- Blocklist Section ---
        blf = ttk.LabelFrame(root, text="Blocklist (từ KHÔNG được gợi ý)")
        blf.pack(fill=tk.BOTH, expand=False, padx=12, pady=10)

        top2 = ttk.Frame(blf); top2.pack(fill=tk.X)
        self.lbl_bl = ttk.Label(top2, text="Blocklist: …")
        self.lbl_bl.pack(side=tk.LEFT)
        ttk.Button(top2, text="Làm mới", command=self._refresh_blocklist_ui).pack(side=tk.LEFT, padx=8)

        mid2 = ttk.Frame(blf); mid2.pack(fill=tk.BOTH, expand=True, pady=6)
        self.lst_bl = tk.Listbox(mid2, selectmode=tk.EXTENDED, height=10)
        self.lst_bl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb2 = ttk.Scrollbar(mid2, orient=tk.VERTICAL, command=self.lst_bl.yview)
        sb2.pack(side=tk.LEFT, fill=tk.Y)
        self.lst_bl.configure(yscrollcommand=sb2.set)

        inp = ttk.Frame(blf); inp.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(inp, text="Thêm từ (cách nhau bởi dấu phẩy hoặc xuống dòng):").pack(anchor=tk.W)
        self.txt_bl_add = tk.Text(inp, height=3)
        self.txt_bl_add.pack(fill=tk.X)

        ctl2 = ttk.Frame(blf); ctl2.pack(fill=tk.X, pady=6)
        ttk.Button(ctl2, text="Thêm vào blocklist", command=self.on_bl_add).pack(side=tk.LEFT)
        ttk.Button(ctl2, text="Xoá mục đã chọn", command=self.on_bl_delete).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctl2, text="Nhập blocklist…", command=self.on_bl_import).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctl2, text="Xuất blocklist…", command=self.on_bl_export).pack(side=tk.LEFT, padx=6)

    def _build_about(self):
        root = self.page_about
        txt = tk.Text(root, wrap=tk.WORD, height=20)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        txt.insert(tk.END, (
            f"{APP_NAME} — Keyword generator for stock footage/Adobe Stock\n\n"
            "• Nhập seed (EN). Chọn style packs và POS để mở rộng (WordNet nếu có).\n"
            "• NEW: Copy All / Copy Selected → chọn định dạng trong mục Định dạng.\n"
            "• NEW: Tự động đánh dấu đã dùng khi copy (bật/tắt trong Tuỳ chọn).\n"
            "• NEW: Blocklist có thể chỉnh sửa (thêm/xoá/nhập/xuất).\n\n"
            "Tips:\n"
            "- Nếu thiếu WordNet: cài NLTK + corpora:\n"
            "    pip install nltk\n"
            "    python -c \"import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')\"\n"
            "- CSV xuất một cột tên 'keyword'. TXT có thể mỗi dòng một từ hoặc phân tách bằng dấu phẩy.\n"
            "- Tab Bộ nhớ: quản lý danh sách đã dùng + blocklist.\n"
        ))
        txt.configure(state=tk.DISABLED)

    # ---------- Event handlers ----------
    def on_suggest_seeds(self):
        try:
            n = int(self.var_suggest_count.get())
            cat = self.var_suggest_category.get()
            unique = self.var_suggest_unique.get()
            mode = self.var_suggest_mode.get()

            # Build pool
            pool: List[str] = []
            if cat == "all":
                for lst in SUGGEST_SEED_POOLS.values():
                    pool.extend(lst)
            else:
                pool.extend(SUGGEST_SEED_POOLS.get(cat, []))
            # also allow style-pack terms as seeds
            for values in STYLE_PACKS.values():
                pool.extend(values)

            # Clean + de-dup
            pool_clean: List[str] = []
            seen = set()
            for w in pool:
                c = clean_phrase(w)
                if not c or c in seen:
                    continue
                seen.add(c)
                pool_clean.append(c)

            # Unique filter against used/blocklist/current seeds (optional)
            if unique:
                current_seeds = self._read_text_lines(self.txt_seeds)
                pool_clean = [w for w in pool_clean if w not in self.used_cache and w not in self.blocklist and w not in current_seeds]

            if not pool_clean:
                messagebox.showinfo(APP_NAME, "Pool rỗng sau khi lọc. Hãy tắt 'Không trùng' hoặc chọn nhóm khác.")
                return

            random.shuffle(pool_clean)
            picked = pool_clean[:max(1, min(n, len(pool_clean)))]

            # Write back to seed box
            text = ", ".join(picked)
            if mode == "replace":
                self.txt_seeds.delete("1.0", tk.END)
                self.txt_seeds.insert(tk.END, text)
            else:
                curtxt = self.txt_seeds.get("1.0", tk.END).strip()
                if curtxt:
                    if not curtxt.endswith((",", " ")):
                        curtxt += ", "
                    self.txt_seeds.delete("1.0", tk.END)
                    self.txt_seeds.insert(tk.END, curtxt + text)
                else:
                    self.txt_seeds.insert(tk.END, text)

            log_audit(self.con, "seed_suggest", json.dumps({"cat": cat, "count": len(picked)}))
            self.lbl_status.configure(text=f"Đã đề xuất {len(picked)} seed từ nhóm '{cat}'. (Ctrl+I để đề xuất nhanh)")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi đề xuất seed: {e}")

    def on_generate(self):
        try:
            seeds = self._read_text_lines(self.txt_seeds)
            includes = self._read_text_lines(self.txt_include)
            excludes = self._read_text_lines(self.txt_exclude)

            pos = {name for name, var in self.pos_vars.items() if var.get()}
            packs = {name for name, var in self.pack_vars.items() if var.get()}
            allow_phrases = self.var_allow_phrases.get()
            max_items = int(self.var_max.get())

            if not seeds and not includes and not packs:
                messagebox.showinfo(APP_NAME, "Vui lòng nhập seed/Include hoặc chọn ít nhất 1 gói phong cách.")
                return

            candidates, stats = assemble_candidates(
                seeds=seeds,
                pos_tags=pos,
                include=includes,
                exclude=excludes,
                packs_selected=packs,
                allow_phrases=allow_phrases,
                used=self.used_cache,
                blocklist=self.blocklist,
                max_items=max_items,
            )

            self.lst.delete(0, tk.END)
            for kw in candidates:
                self.lst.insert(tk.END, kw)

            # Status
            vn = (f"Đã tạo {len(candidates)} từ khoá. Đã lọc (đã dùng:{stats['filtered_used_memory']}, trùng:{stats['filtered_dupe_session']}, cụm từ:{stats['filtered_phrases']}, blocklist:{stats['filtered_blocklist']}), exclude:{stats['blocked_exclude_or_blocklist']}.")
            if not WN_AVAILABLE:
                vn += " Chưa cài WordNet → không mở rộng đồng nghĩa/cấp trên/cấp dưới."
            self.lbl_status.configure(text=vn)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi khi tạo danh sách: {e}")

    def on_export(self):
        try:
            items = self._preview_items()
            if not items:
                messagebox.showinfo(APP_NAME, "Không có từ để xuất.")
                return

            fmt = self.var_format.get()
            if fmt == 'csv':
                path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
                if not path:
                    return
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['keyword'])
                    for kw in items:
                        writer.writerow([kw])
            elif fmt == 'txt_lines':
                path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
                if not path:
                    return
                with open(path, 'w', encoding='utf-8') as f:
                    for kw in items:
                        f.write(kw + '\n')
            else:
                # txt_csv
                path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
                if not path:
                    return
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(', '.join(items))

            if self.var_mark_used_on_export.get():
                ctx = json.dumps({
                    "seeds": list(self._read_text_lines(self.txt_seeds)),
                    "packs": [k for k,v in self.pack_vars.items() if v.get()],
                    "action": "export",
                })
                mark_used(self.con, items, context=ctx)
                self.used_cache = load_used_keywords(self.con)
                self._refresh_stats()

            messagebox.showinfo(APP_NAME, f"Exported {len(items)} keywords to:\n{path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi khi xuất: {e}")

    def _do_copy(self, items: List[str]):
        fmt = self.var_format.get()
        try:
            self.clipboard_clear()
            if fmt == 'csv':
                # CSV column header + rows
                text = 'keyword\n' + '\n'.join(items)
            elif fmt == 'txt_lines':
                text = '\n'.join(items)
            else:
                text = ', '.join(items)
            self.clipboard_append(text)
            self.update()  # ensure clipboard owns data

            if self.var_mark_used_on_copy.get():
                ctx = json.dumps({
                    "seeds": list(self._read_text_lines(self.txt_seeds)),
                    "packs": [k for k,v in self.pack_vars.items() if v.get()],
                    "action": "copy",
                })
                mark_used(self.con, items, context=ctx)
                self.used_cache = load_used_keywords(self.con)
                self._refresh_stats()
            messagebox.showinfo(APP_NAME, f"Đã copy {len(items)} từ vào clipboard (định dạng: {fmt}).")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi copy: {e}")

    def on_copy_all(self):
        items = self._preview_items()
        if not items:
            messagebox.showinfo(APP_NAME, "Không có từ để copy.")
            return
        self._do_copy(items)

    def on_copy_selected(self):
        sel = list(self.lst.curselection())
        if not sel:
            messagebox.showinfo(APP_NAME, "Hãy chọn mục để copy.")
            return
        items = [self.lst.get(i) for i in sel]
        self._do_copy(items)

    def on_mark_used(self):
        try:
            items = self._preview_items()
            if not items:
                messagebox.showinfo(APP_NAME, "No keywords to mark.")
                return
            ctx = json.dumps({
                "seeds": list(self._read_text_lines(self.txt_seeds)),
                "packs": [k for k,v in self.pack_vars.items() if v.get()],
                "manual": True,
                "action": "mark_only",
            })
            mark_used(self.con, items, context=ctx)
            self.used_cache = load_used_keywords(self.con)
            self._refresh_stats()
            messagebox.showinfo(APP_NAME, f"Đã đánh dấu {len(items)} từ là ĐÃ DÙNG.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi khi đánh dấu: {e}")

    def on_clear_preview(self):
        self.lst.delete(0, tk.END)
        self.lbl_status.configure(text="Đã xoá danh sách xem trước.")

    def on_search_used(self):
        try:
            q = self._clean_for_ui(self.var_search.get())
            cur = self.con.cursor()
            if q:
                cur.execute("SELECT keyword FROM used_keywords WHERE keyword LIKE ? ORDER BY keyword", (f"%{q}%",))
            else:
                cur.execute("SELECT keyword FROM used_keywords ORDER BY keyword LIMIT 500")
            rows = cur.fetchall()
            self.lst_used.delete(0, tk.END)
            for r in rows:
                self.lst_used.insert(tk.END, r[0])
            self.lbl_mem.configure(text=f"Memory items shown: {len(rows)} (query='{q}')")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi tìm kiếm: {e}")

    def on_import_used(self):
        try:
            path = filedialog.askopenfilename(filetypes=[('CSV/TXT', '*.csv *.txt'), ('All', '*.*')])
            if not path:
                return
            added = import_used_from_file(self.con, path)
            self.used_cache = load_used_keywords(self.con)
            self._refresh_stats()
            messagebox.showinfo(APP_NAME, f"Imported {added} used keywords.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi nhập: {e}")

    def on_export_used(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv'), ('Text', '*.txt')])
            if not path:
                return
            n = export_used_to_file(self.con, path)
            messagebox.showinfo(APP_NAME, f"Exported {n} used keywords to:\n{path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi xuất bộ nhớ: {e}")

    def on_delete_selected_used(self):
        try:
            sel = list(self.lst_used.curselection())
            if not sel:
                messagebox.showinfo(APP_NAME, "Select used keywords to delete.")
                return
            items = [self.lst_used.get(i) for i in sel]
            if not messagebox.askyesno(APP_NAME, f"Delete {len(items)} from memory?"):
                return
            cur = self.con.cursor()
            cur.executemany("DELETE FROM used_keywords WHERE keyword=?", [(i,) for i in items])
            self.con.commit()
            self.used_cache = load_used_keywords(self.con)
            self._refresh_stats()
            self.on_search_used()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi xoá: {e}")

    def on_reset_all(self):
        try:
            if not messagebox.askyesno(APP_NAME, "Reset ALL used keywords? This cannot be undone."):
                return
            cur = self.con.cursor()
            cur.execute("DELETE FROM used_keywords")
            n = cur.rowcount
            self.con.commit()
            self.used_cache = load_used_keywords(self.con)
            self._refresh_stats()
            messagebox.showinfo(APP_NAME, f"Cleared {n} items from memory.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi reset: {e}")

    # --- Blocklist handlers ---
    def on_bl_add(self):
        try:
            raw = self.txt_bl_add.get("1.0", tk.END)
            parts = re.split(r"[\n,]", raw)
            kws = [self._clean_for_ui(p) for p in parts]
            kws = [k for k in kws if k]
            if not kws:
                return
            added = add_blocklist_keywords(self.con, kws)
            self.blocklist = load_blocklist(self.con)
            self._refresh_blocklist_ui()
            self.txt_bl_add.delete("1.0", tk.END)
            messagebox.showinfo(APP_NAME, f"Đã thêm {added} từ vào blocklist.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi thêm blocklist: {e}")

    def on_bl_delete(self):
        try:
            sel = list(self.lst_bl.curselection())
            if not sel:
                messagebox.showinfo(APP_NAME, "Chọn mục để xoá.")
                return
            items = [self.lst_bl.get(i) for i in sel]
            deleted = delete_blocklist_keywords(self.con, items)
            self.blocklist = load_blocklist(self.con)
            self._refresh_blocklist_ui()
            messagebox.showinfo(APP_NAME, f"Đã xoá {deleted} mục khỏi blocklist.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi xoá blocklist: {e}")

    def on_bl_import(self):
        try:
            path = filedialog.askopenfilename(filetypes=[('CSV/TXT', '*.csv *.txt'), ('All', '*.*')])
            if not path:
                return
            added = import_blocklist_from_file(self.con, path)
            self.blocklist = load_blocklist(self.con)
            self._refresh_blocklist_ui()
            messagebox.showinfo(APP_NAME, f"Imported {added} blocklist items.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi nhập blocklist: {e}")

    def on_bl_export(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv'), ('Text', '*.txt')])
            if not path:
                return
            n = export_blocklist_to_file(self.con, path)
            messagebox.showinfo(APP_NAME, f"Exported {n} blocklist items to:\n{path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi xuất blocklist: {e}")

    # ---------- Utilities ----------
    def _read_text_lines(self, widget: tk.Text) -> Set[str]:
        raw = widget.get("1.0", tk.END)
        parts = re.split(r"[\n,]", raw)
        out = set()
        for p in parts:
            c = self._clean_for_ui(p)
            if c and c not in self.blocklist:
                out.add(c)
        return out

    def _preview_items(self) -> List[str]:
        return [self.lst.get(i) for i in range(self.lst.size())]

    def _refresh_stats(self):
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM used_keywords")
        total = cur.fetchone()[0]
        self.lbl_mem.configure(text=f"Memory size: {total} keywords")
        self._refresh_blocklist_ui()

    def _refresh_blocklist_ui(self):
        self.lst_bl.delete(0, tk.END)
        for kw in sorted(self.blocklist):
            self.lst_bl.insert(tk.END, kw)
        self.lbl_bl.configure(text=f"Blocklist size: {len(self.blocklist)} từ")

    def _bind_hotkeys(self):
        self.bind('<Control-g>', lambda e: self.on_generate())
        self.bind('<Control-G>', lambda e: self.on_generate())
        self.bind('<Control-Shift-C>', lambda e: self.on_copy_all())
        self.bind('<Control-Shift-S>', lambda e: self.on_copy_selected())
        self.bind('<Control-i>', lambda e: self.on_suggest_seeds())
        self.bind('<Control-I>', lambda e: self.on_suggest_seeds())
    def _clean_for_ui(self, s: str) -> str:
        return clean_phrase(s)

    def on_wordnet_help(self):
        messagebox.showinfo(APP_NAME, """Cài đặt WordNet (NLTK):

1) pip install nltk
2) python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
""")


    def destroy(self):
        try:
            self.con.close()
        except Exception:
            pass
        return super().destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
