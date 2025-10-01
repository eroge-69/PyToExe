#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Music Generator GUI (MusicGen, 8D, MP3/FLAC) with:
- Auto-setup (installs dependencies + ffmpeg)
- Prompt Assistant: Text → structured, MusicGen-safe prompts
- Preset buttons + BPM slider/entry
- 8s Preview player
- RAM-safe streaming generation
"""

# ----------------------------
# Bootstrap: auto-install deps
# ----------------------------
import importlib.util, subprocess, sys, os, platform, shutil
def _have(pkg: str) -> bool:
    try: return importlib.util.find_spec(pkg) is not None
    except Exception: return False
def _pip_install(args): subprocess.check_call([sys.executable, "-m", "pip", "install"] + args)
def ensure_package(pkg: str, attempts: list[list[str]] | None = None):
    if _have(pkg): return
    attempts = attempts or [[pkg]]
    last = None
    for args in attempts:
        try:
            print(f"[setup] Installing {args!r} ..."); _pip_install(args)
            if _have(pkg): print(f"[setup] {pkg} ready."); return
        except Exception as e: last = e; print(f"[setup] Failed {args!r}: {e}")
    if not _have(pkg): raise RuntimeError(f"Could not install {pkg}. Last error: {last}")
def ensure_ffmpeg():
    if shutil.which("ffmpeg"): return
    sysname = platform.system().lower()
    if "windows" in sysname:
        print("[setup] ffmpeg not found. Attempting portable download...")
        try:
            import urllib.request, zipfile, tempfile
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            tmp = tempfile.mkdtemp(); zip_path = os.path.join(tmp, "ffmpeg.zip")
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf: zf.extractall(tmp)
            ffmpeg_exe = None
            for r,_,f in os.walk(tmp):
                if "ffmpeg.exe" in f: ffmpeg_exe = os.path.join(r,"ffmpeg.exe"); break
            if not ffmpeg_exe: print("[setup] Could not find ffmpeg.exe in archive."); return
            bindir = os.path.abspath(os.path.join(os.path.dirname(__file__), "ffmpeg-bin"))
            os.makedirs(bindir, exist_ok=True); shutil.copy(ffmpeg_exe, os.path.join(bindir,"ffmpeg.exe"))
            os.environ["PATH"] = bindir + os.pathsep + os.environ.get("PATH","")
            print(f"[setup] ffmpeg ready at: {bindir}")
        except Exception as e:
            print(f"[setup] Could not auto-install ffmpeg: {e}\n       Please install manually.")
    elif "darwin" in sysname:
        print("[setup] ffmpeg not found. Install with Homebrew:\n  brew install ffmpeg")
    else:
        print("[setup] ffmpeg not found. Install with apt/yum/pacman, e.g.:\n  sudo apt-get install ffmpeg")
# Core deps
ensure_package("numpy")
if not _have("soundfile"): ensure_package("soundfile", [["pysoundfile"]])
ensure_package("pydub"); ensure_package("tqdm"); ensure_package("simpleaudio")
# Torch (CUDA → CPU fallback)
try:
    ensure_package("torch", [
        ["torch","torchvision","torchaudio","--index-url","https://download.pytorch.org/whl/cu121"],
        ["torch","torchvision","torchaudio","--index-url","https://download.pytorch.org/whl/cu118"],
        ["torch","torchvision","torchaudio"]
    ])
    ensure_package("torchaudio", [["torchaudio"]])
except Exception as e:
    print(f"[setup] Torch warning: {e} (CPU fallback ok)")
# MusicGen
ensure_package("audiocraft")
# ffmpeg for export
ensure_ffmpeg()

# ----------------------------
# App imports
# ----------------------------
import re, math, queue, threading, datetime as dt, random
from dataclasses import dataclass
import numpy as np, soundfile as sf
from pydub import AudioSegment
from pydub.utils import mediainfo
import simpleaudio as sa
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

_musicgen = None; _torch = None

SAFE_ARTIST_KEYWORDS = [
    r"\bin the style of\b", r"\bsounds like\b", r"\bjust like\b", r"\bcopy\b", r"\brecreate\b",
    r"\bremake\b", r"\brip[- ]?off\b", r"\bparody of\b",
]
KNOWN_ARTISTS = [
    "taylor swift","drake","billie eilish","arijit singh","ar rahman","dua lipa","the weeknd",
    "coldplay","adele","ed sheeran","bts","eminem","rihanna","selena gomez","blackpink",
    "metallica","nirvana","queen","pink floyd","beethoven","bach","mozart","kishore kumar",
    "kishore","rahman","arijit","beethoven","bach","mozart"
]

def lazy_import_models():
    global _musicgen, _torch
    if _musicgen is None or _torch is None:
        from audiocraft.models import MusicGen
        import torch
        _musicgen = MusicGen; _torch = torch

def sanitize_filename(name: str) -> str:
    keep = " ._-()[]{}"
    return "".join(c for c in name if c.isalnum() or c in keep).strip()[:120]

def secs_to_hms(seconds: int) -> str:
    h = seconds // 3600; m = (seconds % 3600) // 60; s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def stereo_from_mono(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1: return np.stack([x,x], axis=0)
    if x.shape[0] == 1: return np.concatenate([x,x], axis=0)
    return x

def apply_8d_pan_chunk(x: np.ndarray, sr: int, start_sample: int, period_sec: float = 8.0, depth: float = 1.0) -> np.ndarray:
    x = stereo_from_mono(x); _, n = x.shape
    idx = start_sample + np.arange(n); t = idx / max(sr, 1); period = max(period_sec, 0.1)
    pan = np.sin(2*np.pi*(t/period)) * np.clip(depth, 0.0, 1.0)
    mono = x.mean(axis=0)
    left = mono * (0.5*(1 - pan)); right = mono * (0.5*(1 + pan))
    y = np.stack([left,right], axis=0)
    k = int(sr*0.015)
    if k>2:
        win = np.hanning(k); smear = np.convolve(y.mean(axis=0), win, mode='same')
        if np.max(np.abs(smear))>1e-9: smear = smear/np.max(np.abs(smear))*0.15; y += np.stack([smear*0.5,smear*0.5])
    peak = np.max(np.abs(y)); 
    if peak>1.0: y = y/(peak+1e-9)
    return y

def safety_check_prompt(prompt: str, extra_artists=None):
    p = prompt.lower(); issues = []
    for rx in SAFE_ARTIST_KEYWORDS:
        if re.search(rx, p): issues.append(f"Contains risky phrase matching: {rx}")
    if '"' in prompt or "'" in prompt: issues.append("Contains quoted phrase that may be a song or lyric.")
    for a in (extra_artists or []) + KNOWN_ARTISTS:
        if re.search(rf"\b{re.escape(a.lower())}\b", p): issues.append(f"Mentions artist: {a}")
    return issues

@dataclass
class GenConfig:
    model_name: str = "facebook/musicgen-small"
    chunk_sec: int = 30
    sample_rate: int = 32000
    top_k: int = 250
    top_p: float = 0.0
    temperature: float = 1.0
    cfg_coef: float = 3.0
    seed: int | None = None

def load_model(model_name: str):
    lazy_import_models()
    model = _musicgen.get_pretrained(model_name)
    return model

def generate_chunk(model, prompt: str, seconds: int, cfg: GenConfig):
    model.set_generation_params(use_sampling=True, top_k=cfg.top_k, top_p=cfg.top_p,
                                temperature=cfg.temperature, cfg_coef=cfg.cfg_coef, duration=seconds)
    if cfg.seed is not None: _torch.manual_seed(cfg.seed)
    out = model.generate([prompt], progress=True)
    wav = out[0].cpu().numpy()
    return wav, model.sample_rate

def export_mp3_from_wav(wav_path: str, out_mp3: str, bitrate="320k"):
    seg = AudioSegment.from_file(wav_path, format="wav")
    seg.export(out_mp3, format="mp3", bitrate=bitrate, parameters=["-write_xing", "0"])

def export_flac_from_wav(wav_path: str, out_flac: str):
    seg = AudioSegment.from_file(wav_path, format="wav")
    seg.export(out_flac, format="flac")

# ----------------------------
# Prompt Assistant (Text → Prompt)
# ----------------------------
GENRES = {
    "lofi": ["lo-fi","lofi","study","cafe","chillhop"],
    "ambient": ["ambient","pad","meditation","drone","atmosphere"],
    "cinematic": ["cinematic","score","soundtrack","film","orchestral"],
    "house": ["house","deep house","dance","club"],
    "trap": ["trap","808","hi-hat rolls","drill"],
    "hiphop": ["hip hop","boom bap","rap"],
    "pop": ["pop","radio","chart","dance-pop"],
    "rock": ["rock","indie","alt","grunge"],
    "indian": ["bollywood","hindustani","carnatic","raag","bansuri","tabla"],
    "metal": ["metal","heavy","distorted guitars"],
    "edm": ["edm","festival","drop","synth lead"],
}
MOODS = ["chill","uplifting","melancholic","dark","epic","romantic","groovy","calm","energetic","mysterious","hopeful","nostalgic","dreamy","cinematic"]
INSTRUMENTS = {
    "lofi": ["warm Rhodes","dusty piano","soft synth pads","electric bass","lo-fi drums","vinyl crackle"],
    "ambient": ["evolving pads","soft piano motifs","granular textures","subtle strings","field recordings"],
    "cinematic": ["strings","piano","braams","sub booms","light percussion","choir","woodwinds"],
    "house": ["four-on-the-floor kick","saw bass","claps","plucky synths","noisy risers"],
    "trap": ["808 bass","snappy snares","hi-hat rolls","plucks","pad layers"],
    "hiphop": ["boom bap drums","upright bass","piano chops","rhodes","sub bass"],
    "pop": ["bright synths","acoustic guitar","electric bass","modern drums","wordless vocal chops"],
    "rock": ["clean electric guitars","acoustic drums","bass guitar","organ/pads"],
    "indian": ["tabla","bansuri (flute)","tanpura drone","strings section","light percussion"],
    "metal": ["distorted rhythm guitars","double-kick drums","bass guitar","lead guitar"],
    "edm": ["supersaw leads","sidechained pads","sub bass","build-ups","impacts"],
}
TEXTURES = ["warm","analog","tape-saturated","wide stereo","punchy","airy","lush","intimate","lo-fi","crisp","cinematic space","club-ready"]
ARRANGEMENTS = [
    "intro → build → main groove → breakdown → finale",
    "slow intro → theme development → climactic swell → gentle outro",
    "groove-based loop with subtle 16-bar variations",
    "A → B → A → B with evolving textures",
]

def scrub_unsafe(text: str) -> str:
    p = text.lower()
    p = re.sub(r"[\"“”‘’'][^\"“”‘’']+[\"“”‘’']", " ", p)  # quoted titles
    for a in KNOWN_ARTISTS: p = re.sub(rf"\b{re.escape(a.lower())}\b", " ", p)
    for rx in SAFE_ARTIST_KEYWORDS: p = re.sub(rx, " ", p)
    p = re.sub(r"\s+", " ", p).strip()
    return p

def guess_bpm(tokens: list[str]) -> int | None:
    for t in tokens:
        m = re.match(r"(\d{2,3})\s*bpm$", t)
        if m:
            bpm = int(m.group(1))
            if 50 <= bpm <= 220: return bpm
    for t in tokens:
        if t.isdigit():
            bpm = int(t)
            if 50 <= bpm <= 220: return bpm
    return None

def pick(items, n=1, rnd=None):
    rnd = rnd or random
    n = min(len(items), n)
    return rnd.sample(items, n) if n>1 else [rnd.choice(items)]

def detect_genre(tokens: list[str]) -> str:
    joined = " ".join(tokens)
    best, best_score = "lofi", 0
    for g, kws in GENRES.items():
        score = sum(1 for kw in kws if kw in joined)
        if score > best_score: best, best_score = g, score
    return best

def idea_to_prompt(idea: str, prefer_len="short", rnd_seed: int | None = None, forced_bpm: int | None = None) -> str:
    rnd = random.Random(rnd_seed) if rnd_seed is not None else random
    clean = scrub_unsafe(idea)
    tokens = [t.strip() for t in re.split(r"[,\s]+", clean) if t.strip()]
    genre = detect_genre(tokens)
    mood = pick(MOODS, 1, rnd=rnd)[0]
    bpm = forced_bpm or guess_bpm([t.lower() for t in tokens])
    if bpm is None:
        bpm_ranges = {
            "lofi": (70,95), "ambient": (60,80), "cinematic": (60,110), "hiphop": (80,100),
            "trap": (130,160), "house": (118,126), "pop": (95,120), "rock": (85,140),
            "indian": (70,110), "metal": (120,180), "edm": (120,128)
        }
        lo, hi = bpm_ranges.get(genre, (90,120)); bpm = rnd.randint(lo, hi)
    instruments = pick(INSTRUMENTS.get(genre, ["piano","pads","bass","drums"]), n=4 if prefer_len!="short" else 3, rnd=rnd)
    texture = pick(TEXTURES, 1, rnd=rnd)[0]
    arrangement = pick(ARRANGEMENTS, 1, rnd=rnd)[0]
    notes = [
        "no vocals, or wordless vocal chops only",
        "avoid references to specific artists or songs",
        "natural dynamics, gentle sidechain if electronic",
        "clean mix, pleasant headroom (~-1 dBFS peak)",
    ]
    env = None
    lc = clean
    if any(k in lc for k in ["rain","storm","monsoon"]): env = "light rain foley in background"
    elif any(k in lc for k in ["ocean","sea","waves","beach"]): env = "distant ocean waves"
    elif any(k in lc for k in ["cafe","coffee","latte"]): env = "subtle cafe ambience (very low)"
    lines = [
        f"Genre: {genre}; Mood: {mood}; Tempo: {bpm} BPM.",
        f"Instruments: {', '.join(instruments)}.",
        f"Texture/Production: {texture}.",
        f"Arrangement: {arrangement}.",
    ]
    if env: lines.append(f"Background ambience: {env}.")
    lines.append("Guidelines: " + "; ".join(notes) + ".")
    return " ".join(lines)

# ----------------------------
# Worker & GUI
# ----------------------------
class Worker(threading.Thread):
    def __init__(self, task_q, log_fn):
        super().__init__(daemon=True); self.task_q = task_q; self.log = log_fn
    def run(self):
        while True:
            fn, args = self.task_q.get()
            try: fn(*args)
            except Exception as e:
                self.log(f"ERROR: {e}"); messagebox.showerror("Error", str(e))
            finally: self.task_q.task_done()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Music Generator (MusicGen, 8D, MP3/FLAC + Prompt Assistant)")
        self.geometry("1020x860"); self.minsize(980, 820)
        self.task_q = queue.Queue(); self.worker = Worker(self.task_q, self.log); self.worker.start()

        self.model_var = tk.StringVar(value="facebook/musicgen-small")
        self.hours_var = tk.StringVar(value="0"); self.minutes_var = tk.StringVar(value="0"); self.seconds_var = tk.StringVar(value="30")
        self.seed_var = tk.StringVar(value=""); self.chunk_var = tk.StringVar(value="30")
        self.outdir_var = tk.StringVar(value=os.path.abspath("./outputs"))
        self.basename_var = tk.StringVar(value="ai_music_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.safe_mode_var = tk.BooleanVar(value=True)
        self.enable_8d_var = tk.BooleanVar(value=False)
        self.pan_period_var = tk.StringVar(value="8.0"); self.pan_depth_var = tk.StringVar(value="1.0")
        self.export_flac_var = tk.BooleanVar(value=True); self.mp3_bitrate_var = tk.StringVar(value="320k")
        # Prompt Assistant state
        self.idea_seed_var = tk.StringVar(value="")    # deterministic prompt gen seed (optional)
        self.bpm_var = tk.StringVar(value="0")         # 0/empty = auto BPM
        self._preview_play_obj = None
        self._build_gui()

    def _build_gui(self):
        pad = {"padx": 10, "pady": 8}

        # Prompt Assistant (Text → Prompt)
        frm_pa = ttk.LabelFrame(self, text="Prompt Assistant (Text → Safe, Structured Prompt)")
        frm_pa.pack(fill="x", **pad)

        # Row 1: idea + seed
        row1 = ttk.Frame(frm_pa); row1.pack(fill="x", padx=8, pady=(8,4))
        ttk.Label(row1, text="Your idea:").pack(side="left")
        self.idea_entry = tk.Entry(row1); self.idea_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(row1, text="Seed (opt):").pack(side="left")
        tk.Entry(row1, textvariable=self.idea_seed_var, width=8).pack(side="left", padx=(4,8))

        # Row 2: presets + BPM slider + entry
        row2 = ttk.Frame(frm_pa); row2.pack(fill="x", padx=8, pady=(4,4))

        # Presets
        presets = [
            ("Lo-fi Study",      "lofi study cafe vibes, warm, rain"),
            ("Epic Score",       "epic cinematic orchestral battle"),
            ("Deep House",       "deep house club banger 124 bpm"),
            ("Indian Ambient",   "indian ambient bansuri meditation"),
            ("Trap 150",         "dark trap 150 bpm 808"),
            ("Rock Jam",         "energetic indie rock jam"),
        ]
        pframe = ttk.Frame(row2); pframe.pack(side="left")
        ttk.Label(pframe, text="Presets:").grid(row=0, column=0, sticky="w")
        for i,(label,idea) in enumerate(presets, start=1):
            def make_cmd(text=idea):
                return lambda: self._apply_preset(text)
            ttk.Button(pframe, text=label, command=make_cmd()).grid(row=i//3+1, column=(i-1)%3, sticky="w", padx=2, pady=2)

        # BPM control
        bframe = ttk.Frame(row2); bframe.pack(side="right")
        ttk.Label(bframe, text="BPM (0=auto):").grid(row=0, column=0, sticky="e", padx=(0,6))
        # Scale 50–220
        self.bpm_scale = tk.Scale(bframe, from_=50, to=220, orient="horizontal", showvalue=True, length=240,
                                  command=self._on_bpm_scale)
        self.bpm_scale.set(120)
        self.bpm_scale.grid(row=0, column=1, sticky="w")
        tk.Entry(bframe, textvariable=self.bpm_var, width=6).grid(row=0, column=2, sticky="w", padx=(8,0))
        ttk.Button(bframe, text="Auto", command=lambda: self._set_bpm_auto()).grid(row=0, column=3, padx=(6,0))

        # Row 3: actions + tip
        row3 = ttk.Frame(frm_pa); row3.pack(fill="x", padx=8, pady=(6,8))
        ttk.Button(row3, text="Generate Prompt", command=self.generate_prompt_from_idea).pack(side="left")
        ttk.Button(row3, text="Clear", command=lambda: self.idea_entry.delete(0,"end")).pack(side="left", padx=(6,0))
        self.pa_tip = tk.Label(frm_pa, anchor="w", justify="left", fg="#444",
            text="Tip: try 'chill cafe vibes with rain', 'epic cinematic battle', 'deep house 124 bpm', 'indian ambient bansuri'.")
        self.pa_tip.pack(fill="x", padx=8, pady=(0,6))

        # Main Prompt box
        frm_prompt = ttk.LabelFrame(self, text="MusicGen Prompt")
        frm_prompt.pack(fill="x", **pad)
        self.prompt_text = tk.Text(frm_prompt, height=6, wrap="word")
        self.prompt_text.pack(fill="x", padx=8, pady=8)

        # Settings
        frm_set = ttk.LabelFrame(self, text="Settings"); frm_set.pack(fill="x", **pad)
        ttk.Label(frm_set, text="Model:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(frm_set, textvariable=self.model_var, values=[
            "facebook/musicgen-small","facebook/musicgen-medium","facebook/musicgen-melody"
        ], width=30).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(frm_set, text="Duration (hh:mm:ss):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm_set, textvariable=self.hours_var, width=4).grid(row=1, column=1, sticky="w")
        ttk.Label(frm_set, text=":").grid(row=1, column=1, sticky="w", padx=(38,0))
        ttk.Entry(frm_set, textvariable=self.minutes_var, width=4).grid(row=1, column=1, sticky="w", padx=(52,0))
        ttk.Label(frm_set, text=":").grid(row=1, column=1, sticky="w", padx=(86,0))
        ttk.Entry(frm_set, textvariable=self.seconds_var, width=4).grid(row=1, column=1, sticky="w", padx=(100,0))
        ttk.Label(frm_set, text="  (30 sec to 12 hours)").grid(row=1, column=2, sticky="w")
        ttk.Label(frm_set, text="Gen chunk (sec):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm_set, textvariable=self.chunk_var, width=6).grid(row=2, column=1, sticky="w")
        ttk.Label(frm_set, text="(recommended 20–30)").grid(row=2, column=2, sticky="w")
        ttk.Label(frm_set, text="Seed (optional):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm_set, textvariable=self.seed_var, width=10).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(frm_set, text="Enable 8D pan", variable=self.enable_8d_var).grid(row=4, column=0, sticky="w")
        ttk.Label(frm_set, text="Period (sec):").grid(row=4, column=1, sticky="w", padx=(0,4))
        ttk.Entry(frm_set, textvariable=self.pan_period_var, width=6).grid(row=4, column=1, sticky="w", padx=(88,0))
        ttk.Label(frm_set, text="Depth (0–1):").grid(row=4, column=2, sticky="w", padx=(0,4))
        ttk.Entry(frm_set, textvariable=self.pan_depth_var, width=6).grid(row=4, column=2, sticky="w", padx=(84,0))
        ttk.Checkbutton(frm_set, text="Safe Mode (copyright pre-check)", variable=self.safe_mode_var).grid(row=5, column=0, sticky="w")

        # Output
        frm_out = ttk.LabelFrame(self, text="Output"); frm_out.pack(fill="x", **pad)
        ttk.Label(frm_out, text="Folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm_out, textvariable=self.outdir_var, width=60).grid(row=0, column=1, sticky="w")
        ttk.Button(frm_out, text="Browse…", command=self.browse_outdir).grid(row=0, column=2, padx=6)
        ttk.Label(frm_out, text="File base name:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm_out, textvariable=self.basename_var, width=40).grid(row=1, column=1, sticky="w")

        # Export options
        frm_exp = ttk.LabelFrame(self, text="Export Options"); frm_exp.pack(fill="x", **pad)
        ttk.Checkbutton(frm_exp, text="Also export FLAC (lossless)", variable=self.export_flac_var).grid(row=0, column=0, sticky="w")
        ttk.Label(frm_exp, text="MP3 bitrate:").grid(row=0, column=1, sticky="e")
        ttk.Entry(frm_exp, textvariable=self.mp3_bitrate_var, width=8).grid(row=0, column=2, sticky="w", padx=(6,0))
        ttk.Label(frm_exp, text="(e.g., 320k, 256k)").grid(row=0, column=3, sticky="w")

        # Actions
        frm_act = ttk.Frame(self); frm_act.pack(fill="x", **pad)
        ttk.Button(frm_act, text="Generate", command=self.start_generate).pack(side="left")
        ttk.Button(frm_act, text="Preview 8s", command=self.start_preview).pack(side="left", padx=8)
        ttk.Button(frm_act, text="Stop Preview", command=self.stop_preview).pack(side="left")
        ttk.Button(frm_act, text="Close", command=self.quit).pack(side="right")

        # Progress + log
        frm_prog = ttk.LabelFrame(self, text="Progress"); frm_prog.pack(fill="both", expand=True, **pad)
        self.pb = ttk.Progressbar(frm_prog, orient="horizontal", length=400, mode="determinate")
        self.pb.pack(fill="x", padx=8, pady=8)
        self.log_box = tk.Text(frm_prog, height=16, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

    # ---- Prompt Assistant helpers
    def _apply_preset(self, text: str):
        self.idea_entry.delete(0,"end"); self.idea_entry.insert(0, text)
        # try to set sensible BPM from preset text if it ends with '### bpm'
        m = re.search(r"(\d{2,3})\s*bpm", text.lower())
        if m:
            bpm = int(m.group(1))
            self._set_bpm(bpm)
        else:
            # put genre-typical defaults
            if "house" in text.lower(): self._set_bpm(124)
            elif "trap" in text.lower(): self._set_bpm(150)
            elif "lofi" in text.lower(): self._set_bpm(88)
            elif "rock" in text.lower(): self._set_bpm(120)
            elif "cinematic" in text.lower(): self._set_bpm_auto()
            else: self._set_bpm_auto()

    def _on_bpm_scale(self, _val):
        # When user drags the scale, reflect in entry (does not force, unless Generate Prompt pressed)
        self.bpm_var.set(str(int(float(self.bpm_scale.get()))))

    def _set_bpm(self, bpm: int):
        bpm = max(50, min(220, int(bpm)))
        self.bpm_scale.set(bpm)
        self.bpm_var.set(str(bpm))

    def _set_bpm_auto(self):
        self.bpm_var.set("0")  # 0 = auto
        # Keep slider where it is (visual hint), but entry drives forcing logic

    # ---- Prompt Assistant main action
    def generate_prompt_from_idea(self):
        idea = self.idea_entry.get().strip()
        if not idea:
            messagebox.showerror("No idea", "Type a short idea first (e.g., 'chill cafe vibes with rain').")
            return
        seed_text = self.idea_seed_var.get().strip()
        seed = None
        if seed_text:
            try: seed = int(seed_text)
            except ValueError: seed = None
        forced_bpm = None
        try:
            val = int(self.bpm_var.get().strip() or "0")
            if 50 <= val <= 220: forced_bpm = val
        except ValueError:
            forced_bpm = None
        prompt = idea_to_prompt(idea, rnd_seed=seed, forced_bpm=forced_bpm)
        if safety_check_prompt(prompt):  # extra safe
            prompt = scrub_unsafe(prompt)
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", prompt)
        self.log("Prompt Assistant generated a structured prompt.")

    # ---- Utility / common
    def log(self, msg: str):
        self.log_box.insert("end", msg + "\n"); self.log_box.see("end"); self.update_idletasks()
    def browse_outdir(self):
        d = filedialog.askdirectory(initialdir=self.outdir_var.get() or ".")
        if d: self.outdir_var.set(d)

    # -----------------
    # Generate (full)
    # -----------------
    def start_generate(self):
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showerror("Missing prompt", "Please enter a prompt or use the Prompt Assistant."); return
        try:
            h = int(self.hours_var.get() or "0"); m = int(self.minutes_var.get() or "0"); s = int(self.seconds_var.get() or "0")
            duration = h*3600 + m*60 + s
        except ValueError:
            messagebox.showerror("Invalid duration", "Please enter numeric values for hh:mm:ss."); return
        if duration < 30 or duration > 12*3600:
            messagebox.showerror("Invalid duration", "Duration must be between 30 seconds and 12 hours."); return
        try: chunk = int(self.chunk_var.get() or "30")
        except ValueError: messagebox.showerror("Chunk size", "Chunk seconds should be 5–60."); return
        if chunk < 5 or chunk > 60:
            messagebox.showerror("Chunk size", "Chunk seconds should be between 5 and 60."); return
        seed = self.seed_var.get().strip(); seed_val = int(seed) if seed else None
        outdir = self.outdir_var.get().strip() or "."; os.makedirs(outdir, exist_ok=True)
        base = sanitize_filename(self.basename_var.get().strip() or "ai_music")
        out_mp3 = os.path.join(outdir, f"{base}.mp3"); out_flac = os.path.join(outdir, f"{base}.flac")
        bitrate = (self.mp3_bitrate_var.get() or "320k").strip()
        if self.safe_mode_var.get():
            issues = safety_check_prompt(prompt)
            if issues:
                msg = "⚠️ Safety pre-check:\n\n" + "\n".join(f"• {i}" for i in issues) + \
                      "\n\nPlease rephrase using high-level musical traits (tempo, mood, instruments, genre)."
                messagebox.showwarning("Safety check", msg); self.log("Safety check blocked generation."); return
        self.pb["value"] = 0; self.pb["maximum"] = duration
        self.task_q.put((self._do_generate, (prompt, duration, chunk, seed_val, out_mp3, out_flac, bitrate, self.export_flac_var.get())))

    def _do_generate(self, prompt, duration, chunk_sec, seed, out_mp3, out_flac, bitrate, export_flac):
        tmp_wav = out_mp3.replace(".mp3", "_tmp.wav")
        try:
            self.log("Loading model… (first time can be slow)")
            model = load_model(self.model_var.get()); sr = 32000
            cfg = GenConfig(model_name=self.model_var.get(), chunk_sec=chunk_sec, sample_rate=sr, seed=seed)
            frames_written = 0; enable_8d = self.enable_8d_var.get()
            period = float(self.pan_period_var.get() or "8.0"); depth = float(self.pan_depth_var.get() or "1.0")
            with sf.SoundFile(tmp_wav, mode="w", samplerate=sr, channels=2, subtype="FLOAT") as wav_out:
                remaining = duration; part = 0
                while remaining > 0:
                    part += 1; sec = int(min(chunk_sec, remaining)); self.log(f"Generating chunk {part} ({sec}s)…")
                    wav, sr_got = generate_chunk(model, prompt, sec, cfg)
                    if sr_got != sr: raise RuntimeError(f"Unexpected sample rate {sr_got} from model.")
                    y = apply_8d_pan_chunk(wav, sr, frames_written, period, depth) if enable_8d else stereo_from_mono(wav)
                    peak = np.max(np.abs(y)); 
                    if peak>0.99: y = y/(peak+1e-9)*0.98
                    wav_out.write(y.T.astype(np.float32))
                    frames_written += y.shape[1]; remaining -= sec
                    self.pb["value"] = min(self.pb["maximum"], self.pb["value"] + sec); self.update_idletasks()
            self.log(f"Exporting MP3 → {out_mp3}")
            try: export_mp3_from_wav(tmp_wav, out_mp3, bitrate=bitrate)
            except FileNotFoundError: self.log("ERROR: ffmpeg not found."); raise
            if export_flac:
                self.log(f"Exporting FLAC → {out_flac}")
                try: export_flac_from_wav(tmp_wav, out_flac)
                except FileNotFoundError: self.log("ERROR: ffmpeg not found for FLAC."); raise
            try:
                info = mediainfo(out_mp3); br = info.get("bit_rate") or bitrate
                self.log(f"Done. MP3 bitrate: {br}. Duration: ~{secs_to_hms(duration)}")
            except Exception: self.log(f"Done. Duration: ~{secs_to_hms(duration)}")
            saved = out_mp3 + (f"\n{out_flac}" if export_flac else ""); messagebox.showinfo("Success", f"Saved:\n{saved}")
        except Exception as e:
            self.log(f"ERROR: {e}"); raise
        finally:
            try:
                if os.path.exists(tmp_wav): os.remove(tmp_wav)
            except Exception: pass

    # -------------
    # Preview (8s)
    # -------------
    def start_preview(self):
        prompt = self.prompt_text.get("1.0","end").strip()
        if not prompt: messagebox.showerror("Missing prompt","Please enter a prompt or use the Prompt Assistant."); return
        if self.safe_mode_var.get() and safety_check_prompt(prompt):
            messagebox.showwarning("Safety check","Preview blocked: please remove artist/song references."); return
        seed = self.seed_var.get().strip(); seed_val = int(seed) if seed else None
        self.task_q.put((self._do_preview, (prompt, 8, 8, seed_val)))
    def _do_preview(self, prompt, seconds, chunk_sec, seed):
        try:
            self.log("Preparing 8s preview…"); model = load_model(self.model_var.get()); sr = 32000
            cfg = GenConfig(chunk_sec=chunk_sec, sample_rate=sr, seed=seed)
            wav, sr_got = generate_chunk(model, prompt, seconds, cfg)
            if sr_got != sr: raise RuntimeError(f"Unexpected sample rate {sr_got}")
            if self.enable_8d_var.get():
                period = float(self.pan_period_var.get() or "8.0"); depth = float(self.pan_depth_var.get() or "1.0")
                y = apply_8d_pan_chunk(wav, sr, 0, period, depth)
            else: y = stereo_from_mono(wav)
            peak = np.max(np.abs(y)); 
            if peak>0.99: y = y/(peak+1e-9)*0.98
            audio_i16 = (np.clip(y, -1.0, 1.0).T * 32767.0).astype(np.int16)
            self.stop_preview()
            self._preview_play_obj = sa.play_buffer(audio_i16.tobytes(), num_channels=2, bytes_per_sample=2, sample_rate=sr)
            self.log("Playing preview…")
        except Exception as e:
            self.log(f"Preview error: {e}"); messagebox.showerror("Preview Error", str(e))
    def stop_preview(self):
        try:
            if self._preview_play_obj and self._preview_play_obj.is_playing():
                self._preview_play_obj.stop(); self._preview_play_obj = None; self.log("Preview stopped.")
        except Exception: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()