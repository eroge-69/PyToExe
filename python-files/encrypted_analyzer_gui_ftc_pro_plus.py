
import argparse
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from PIL import Image, ImageTk

# --- Signatures & hints ---
MAGIC_SIGNATURES = [
    ("OpenSSL 'Salted__'", b"Salted__", 0),
    ("ZIP (PK\x03\x04)", b"PK\x03\x04", 0),
    ("ZIP (empty dir PK\x05\x06)", b"PK\x05\x06", 0),
    ("ZIP (spanned PK\x07\x08)", b"PK\x07\x08", 0),
    ("7-Zip", b"7z\xBC\xAF'\x1C", 0),
    ("RAR 4.x", b"Rar!\x1A\x07\x00", 0),
    ("RAR 5.x", b"Rar!\x1A\x07\x01\x00", 0),
    ("GZIP", b"\x1F\x8B\x08", 0),
    ("BZIP2", b"BZh", 0),
    ("XZ/LZMA", b"\xFD7zXZ\x00", 0),
    ("LUKS", b"LUKS\xBA\xBE", 0),
    ("BitLocker (MSFTE)", b"\xEB\x52\x90MSDOS5.0", 0),
    ("BitLocker FVE-FS", b"-FVE-FS-", 3),
    ("PGP ASCII Armor", b"-----BEGIN PGP", 0),
    ("PNG (not encrypted)", b"\x89PNG\r\n\x1a\n", 0),
    ("PDF (not encrypted)", b"%PDF", 0),
    ("ELF Binary (not encrypted)", b"\x7FELF", 0),
    ("Windows EXE MZ (not encrypted)", b"MZ", 0),
]

LIKELY_METHOD_HINTS = {
    "OpenSSL 'Salted__'": "Likely AES-CBC (OpenSSL default) with salted key derivation.",
    "LUKS": "Linux Unified Key Setup container; cipher (often aes-xts) stored in header.",
    "BitLocker (MSFTE)": "BitLocker/Windows volume; AES-based.",
    "BitLocker FVE-FS": "BitLocker metadata region; AES-based.",
    "PGP ASCII Armor": "OpenPGP (e.g., RSA+AES hybrid); textual armor.",
    "7-Zip": "7z container; may use AES-256 with LZMA compression.",
    "RAR 5.x": "RAR5 container; optional AES encryption.",
    "ZIP (PK\x03\x04)": "ZIP container; may use ZipCrypto or AES (check extra fields)."
}

# --- Profiles ---
PROFILES = {
    "Default":      {"window_kib": 64,  "low": 5.5, "high": 7.5, "scales": [2,4,8]},
    "Disk-Image":   {"window_kib": 256, "low": 5.7, "high": 7.7, "scales": [2,4,8,16]},
    "Container/Archive": {"window_kib": 128, "low": 5.6, "high": 7.8, "scales": [2,4,8]},
    "Text/Source":  {"window_kib": 32,  "low": 5.0, "high": 7.0, "scales": [2,3,5]},
    "Media/Binary": {"window_kib": 64,  "low": 5.4, "high": 7.6, "scales": [2,4,8]},
}

def auto_profile_for_signatures(sig_hits):
    s = set(sig_hits)
    if any(x in s for x in ["ZIP (PK\x03\x04)", "7-Zip", "RAR 4.x", "RAR 5.x", "GZIP", "BZIP2", "XZ/LZMA"]):
        return "Container/Archive"
    if any(x in s for x in ["LUKS", "BitLocker (MSFTE)", "BitLocker FVE-FS", "OpenSSL 'Salted__'", "PGP ASCII Armor"]):
        return "Disk-Image"
    if any(x in s for x in ["PNG (not encrypted)", "ELF Binary (not encrypted)", "Windows EXE MZ (not encrypted)"]):
        return "Media/Binary"
    if "PDF (not encrypted)" in s:
        return "Text/Source"
    return "Default"

# --- Helpers ---
def read_head(path, n=64*1024):
    with open(path, "rb") as f:
        return f.read(n)

def file_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return None

def detect_signatures(head_bytes):
    hits = []
    for name, sig, offset in MAGIC_SIGNATURES:
        if len(head_bytes) >= offset + len(sig) and head_bytes[offset:offset+len(sig)] == sig:
            hits.append(name)
    return hits

def shannon_entropy(data_bytes):
    if not data_bytes:
        return 0.0
    import numpy as np
    counts = np.bincount(np.frombuffer(data_bytes, dtype=np.uint8), minlength=256)
    probs = counts / counts.sum()
    nz = probs[probs > 0]
    H = -np.sum(nz * np.log2(nz))
    return float(H)

def chi_square_uniformity(data_bytes):
    if not data_bytes:
        return 0.0
    import numpy as np
    counts = np.bincount(np.frombuffer(data_bytes, dtype=np.uint8), minlength=256)
    expected = counts.sum() / 256.0
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = np.nansum(((counts - expected) ** 2) / (expected if expected > 0 else 1))
    return float(chi2)

def repeating_block_ratio(data_bytes, block_size=16):
    if len(data_bytes) < block_size * 2:
        return 0.0
    blocks = [bytes(data_bytes[i:i+block_size]) for i in range(0, len(data_bytes) - block_size + 1, block_size)]
    total = len(blocks)
    unique = len(set(blocks))
    return 1.0 - (unique / total) if total > 0 else 0.0

def rolling_entropy(path, window=64*1024, max_samples=240):
    size = file_size(path) or 0
    if size == 0:
        return [], []
    entropies, offsets = [], []
    samples = min((size + window - 1) // window, max_samples)
    pos = 0
    with open(path, "rb") as f:
        for _ in range(int(samples)):
            f.seek(pos)
            chunk = f.read(window)
            if not chunk:
                break
            entropies.append(shannon_entropy(chunk))
            offsets.append(pos)
            pos += window
            if pos >= size:
                break
    return offsets, entropies

# --- FTC ---
def ftc_label_for_entropy(H, low, high):
    if H < low:
        return 1
    elif H > high:
        return -1
    else:
        return 0

def ftc_window_labels(path, window=64*1024, max_windows=1024, low=5.5, high=7.5):
    size = file_size(path) or 0
    if size == 0:
        return [], [], []
    labels, entropies, offsets = [], [], []
    samples = min((size + window - 1) // window, max_windows)
    pos = 0
    with open(path, "rb") as f:
        for _ in range(int(samples)):
            f.seek(pos)
            chunk = f.read(window)
            if not chunk:
                break
            H = shannon_entropy(chunk)
            entropies.append(H)
            offsets.append(pos)
            labels.append(ftc_label_for_entropy(H, low, high))
            pos += window
            if pos >= size:
                break
    return offsets, entropies, labels

def tri_entropy_from_labels(labels):
    if not labels:
        return 0.0, 0.0, { -1:0, 0:0, 1:0 }
    import numpy as np
    arr = np.array(labels, dtype=int)
    counts = {v:int(np.sum(arr==v)) for v in (-1,0,1)}
    total = len(labels)
    probs = np.array([counts[-1]/total, counts[0]/total, counts[1]/total], dtype=float)
    nz = probs[probs>0]
    H3 = -np.sum(nz * np.log2(nz))
    mu = (counts[1] - counts[-1]) / total
    return H3, mu, counts

def longest_monosign_run(labels):
    if not labels:
        return 0
    best, cur = 1, 1
    for i in range(1, len(labels)):
        if labels[i] == labels[i-1] and labels[i] != 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best

def simple_multiscale_labels(labels, scales=(2,4,8)):
    out = []
    L = len(labels)
    for s in scales:
        if L < s:
            out.append([])
            continue
        grouped = []
        for i in range(0, L, s):
            chunk = labels[i:i+s]
            if not chunk:
                continue
            import numpy as np
            vals, counts = np.unique(chunk, return_counts=True)
            maj = vals[np.argmax(counts)]
            grouped.append(int(maj))
        out.append(grouped)
    return out

# --- Rendering ---
def fig_to_pil(fig):
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    buf = canvas.buffer_rgba()
    im = Image.frombuffer('RGBA', canvas.get_width_height(), bytes(buf), 'raw', 'RGBA', 0, 1)
    return im

def render_hist_pil(data_bytes, width=1200, height=400):
    import numpy as np
    counts = np.bincount(np.frombuffer(data_bytes, dtype=np.uint8), minlength=256) if data_bytes else np.zeros(256, dtype=int)
    fig = Figure(figsize=(width/100, height/100), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(range(256), counts)
    ax.set_title("Byte-Histogramm")
    ax.set_xlabel("Bytewert")
    ax.set_ylabel("Anzahl")
    fig.tight_layout()
    return fig_to_pil(fig)

def render_entropy_pil(offsets, entropies, width=1200, height=400):
    fig = Figure(figsize=(width/100, height/100), dpi=100)
    ax = fig.add_subplot(111)
    if offsets and entropies:
        ax.plot(offsets, entropies)
    ax.set_title("Rolling Entropy (bits/Byte)")
    ax.set_xlabel("Offset (Bytes)")
    ax.set_ylabel("Entropie")
    ax.set_ylim(0, 8)
    fig.tight_layout()
    return fig_to_pil(fig)

def render_strip_pil(scales_labels, width=1200, height=260):
    import numpy as np
    rows = len(scales_labels)
    cols = max((len(r) for r in scales_labels), default=0)
    if rows == 0 or cols == 0:
        fig = Figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("FTC-Strip (keine Daten)")
        return fig_to_pil(fig)
    M = np.zeros((rows, cols), dtype=float)
    for r, row in enumerate(scales_labels):
        for c, v in enumerate(row):
            M[r, c] = 0.0 if v == -1 else (0.5 if v == 0 else 1.0)
    fig = Figure(figsize=(width/100, height/100), dpi=100)
    ax = fig.add_subplot(111)
    ax.imshow(M, aspect='auto', interpolation='nearest')
    ax.set_title("FTC-Strip (multiskalig)")
    ax.set_xlabel("Fenster (Position →)")
    ax.set_ylabel("Skalen")
    fig.tight_layout()
    return fig_to_pil(fig)

def pil_to_tk(im): return ImageTk.PhotoImage(im)

# --- Guess & 72/28 ---
def guess_encryption_method(signature_hits, head_bytes, fullbytes_sample):
    hints = [LIKELY_METHOD_HINTS[s] for s in signature_hits if s in LIKELY_METHOD_HINTS]
    ecb_ratio = repeating_block_ratio(fullbytes_sample, 16)
    if ecb_ratio > 0.02:
        hints.append(f"Repeating 16-byte blocks ({ecb_ratio:.1%}) → possible ECB or structured data.")
    H = shannon_entropy(fullbytes_sample)
    if H > 7.5:
        hints.append("High entropy suggests compressed or encrypted data.")
    elif H < 5.0:
        hints.append("Lower entropy suggests plaintext or structured/uncompressed data.")
    return hints

def ternary_72_28_score(entropy_bits):
    chaos = entropy_bits / 8.0
    order = 1.0 - chaos
    dist_72_28 = abs(order - 0.72) + abs(chaos - 0.28)
    dist_28_72 = abs(order - 0.28) + abs(chaos - 0.72)
    if chaos >= 0.9:
        label = "Dominant chaos (likely encrypted/compressed)"
    elif order >= 0.9:
        label = "Dominant order (likely plaintext/structured)"
    else:
        label = "Mixed structure"
    return chaos, order, dist_72_28, dist_28_72, label

# --- JSON ---
def make_report(data):
    return json.dumps(data, indent=2, ensure_ascii=False)

# --- GUI ---
class AnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Encrypted File Analyzer — 72/28 + FTC (PRO++)")
        self.geometry("1260x900")
        self.minsize(1100, 780)
        self._build_widgets()
        self._hist_imgtk = None
        self._entropy_imgtk = None
        self._ftc_imgtk = None
        self.last_results = None

    def _build_widgets(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=8, pady=8)
        self.path_var = tk.StringVar()
        ttk.Label(top, text="Datei:").grid(row=0, column=0, sticky="w")
        self.path_entry = ttk.Entry(top, textvariable=self.path_var, width=90)
        self.path_entry.grid(row=0, column=1, padx=6, sticky="we")
        ttk.Button(top, text="Öffnen…", command=self.choose_file).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Analysieren", command=self.run_analysis).grid(row=0, column=3, padx=4)

        prof = ttk.Frame(self); prof.pack(fill="x", padx=8, pady=(0,6))
        self.profile_var = tk.StringVar(value="Default")
        ttk.Label(prof, text="Profil:").pack(side="left")
        self.profile_combo = ttk.Combobox(prof, textvariable=self.profile_var, values=list(PROFILES.keys()), state="readonly", width=22)
        self.profile_combo.pack(side="left", padx=(4,12))
        ttk.Button(prof, text="Profil anwenden", command=self.apply_profile).pack(side="left", padx=4)
        ttk.Button(prof, text="Auto anwenden", command=self.auto_apply_profile).pack(side="left", padx=4)

        tun = ttk.Frame(self); tun.pack(fill="x", padx=8, pady=(0,8))
        self.window_kib = tk.IntVar(value=PROFILES["Default"]["window_kib"])
        self.low_thr = tk.DoubleVar(value=PROFILES["Default"]["low"])
        self.high_thr = tk.DoubleVar(value=PROFILES["Default"]["high"])
        self.scales_str = tk.StringVar(value=",".join(map(str, PROFILES["Default"]["scales"])))
        ttk.Label(tun, text="Fenstergröße (KiB):").pack(side="left")
        ttk.Entry(tun, textvariable=self.window_kib, width=6).pack(side="left", padx=(4,12))
        ttk.Label(tun, text="Low H:").pack(side="left")
        ttk.Entry(tun, textvariable=self.low_thr, width=6).pack(side="left", padx=(4,12))
        ttk.Label(tun, text="High H:").pack(side="left")
        ttk.Entry(tun, textvariable=self.high_thr, width=6).pack(side="left", padx=(4,12))
        ttk.Label(tun, text="Skalen:").pack(side="left")
        ttk.Entry(tun, textvariable=self.scales_str, width=12).pack(side="left", padx=(4,12))
        ttk.Button(tun, text="Kalibrieren", command=self.calibrate_thresholds).pack(side="left", padx=4)
        ttk.Button(tun, text="Histogramm PNG", command=self.export_hist_png).pack(side="left", padx=4)
        ttk.Button(tun, text="Entropie PNG", command=self.export_entropy_png).pack(side="left", padx=4)
        ttk.Button(tun, text="Heatmap PNG", command=self.export_heatmap_png).pack(side="left", padx=4)
        ttk.Button(tun, text="JSON-Report", command=self.export_json).pack(side="left", padx=4)

        mid = ttk.Panedwindow(self, orient="horizontal"); mid.pack(fill="both", expand=True, padx=8, pady=8)
        left = ttk.Frame(mid); mid.add(left, weight=1)
        self.results = ScrolledText(left, height=20, wrap="word"); self.results.pack(fill="both", expand=True)
        right = ttk.Frame(mid); mid.add(right, weight=1)
        self.hist_label = ttk.Label(right, text="Byte-Histogramm", anchor="center"); self.hist_label.pack(fill="x")
        self.hist_canvas = tk.Label(right); self.hist_canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.ent_label = ttk.Label(right, text="Rolling Entropy", anchor="center"); self.ent_label.pack(fill="x")
        self.ent_canvas = tk.Label(right); self.ent_canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.ftc_label = ttk.Label(right, text="FTC-Strip (multiskalig)", anchor="center"); self.ftc_label.pack(fill="x")
        self.ftc_canvas = tk.Label(right); self.ftc_canvas.pack(fill="both", expand=True, padx=4, pady=4)

        self.status = tk.StringVar(value="Bereit.")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=8, pady=(0,8))
        top.columnconfigure(1, weight=1)

    def choose_file(self):
        path = filedialog.askopenfilename(title="Datei auswählen")
        if path:
            self.path_var.set(path); self.run_analysis()

    def apply_profile(self):
        name = self.profile_var.get()
        p = PROFILES.get(name, PROFILES["Default"])
        self.window_kib.set(p["window_kib"]); self.low_thr.set(p["low"]); self.high_thr.set(p["high"])
        self.scales_str.set(",".join(map(str, p["scales"])))

    def auto_apply_profile(self):
        path = self.path_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", "Bitte zuerst eine Datei wählen."); return
        head = read_head(path, 256*1024); sig_hits = detect_signatures(head)
        name = auto_profile_for_signatures(sig_hits)
        self.profile_var.set(name); self.apply_profile()
        self.status.set(f"Auto-Profil angewendet: {name}")

    def parse_scales(self):
        try:
            vals = [int(x.strip()) for x in self.scales_str.get().split(",") if x.strip()]
            vals = [v for v in vals if v >= 2]
            return vals if vals else [2,4,8]
        except Exception:
            return [2,4,8]

    def calibrate_thresholds(self):
        path = self.path_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", "Bitte zuerst eine Datei wählen."); return
        window = max(1, int(self.window_kib.get())) * 1024
        _, ents = rolling_entropy(path, window=window, max_samples=480)
        if not ents:
            messagebox.showerror("Fehler", "Keine Daten für Kalibrierung."); return
        import numpy as np
        lo = float(np.percentile(ents, 30)); hi = float(np.percentile(ents, 70))
        self.low_thr.set(round(lo, 3)); self.high_thr.set(round(hi, 3))
        self.status.set(f"Kalibriert: Low={lo:.3f}, High={hi:.3f}")

    def export_hist_png(self):
        if not self.last_results: messagebox.showerror("Fehler", "Bitte zuerst analysieren."); return
        suggested = os.path.splitext(self.last_results["file"]["path"])[0] + "_hist.png"
        out = filedialog.asksaveasfilename(title="Histogramm speichern", defaultextension=".png",
                                           initialfile=os.path.basename(suggested), filetypes=[("PNG","*.png")])
        if not out: return
        im = render_hist_pil(self.last_results["sample"]["bytes"])
        im.save(out, "PNG"); self.status.set(f"Histogramm gespeichert: {out}")

    def export_entropy_png(self):
        if not self.last_results: messagebox.showerror("Fehler", "Bitte zuerst analysieren."); return
        suggested = os.path.splitext(self.last_results["file"]["path"])[0] + "_entropy.png"
        out = filedialog.asksaveasfilename(title="Entropie speichern", defaultextension=".png",
                                           initialfile=os.path.basename(suggested), filetypes=[("PNG","*.png")])
        if not out: return
        im = render_entropy_pil(self.last_results["rolling"]["offsets"], self.last_results["rolling"]["entropies"])
        im.save(out, "PNG"); self.status.set(f"Entropie gespeichert: {out}")

    def export_heatmap_png(self):
        if not self.last_results: messagebox.showerror("Fehler", "Bitte zuerst analysieren."); return
        suggested = os.path.splitext(self.last_results["file"]["path"])[0] + "_ftc_heatmap.png"
        out = filedialog.asksaveasfilename(title="FTC-Heatmap speichern", defaultextension=".png",
                                           initialfile=os.path.basename(suggested), filetypes=[("PNG","*.png")])
        if not out: return
        im = render_strip_pil(self.last_results["ftc"]["scales_labels"], width=1600, height=260)
        im.save(out, "PNG"); self.status.set(f"Heatmap gespeichert: {out}")

    def export_json(self):
        if not self.last_results: messagebox.showerror("Fehler", "Bitte zuerst analysieren."); return
        suggested = os.path.splitext(self.last_results["file"]["path"])[0] + "_analysis.json"
        out = filedialog.asksaveasfilename(title="JSON-Report speichern", defaultextension=".json",
                                           initialfile=os.path.basename(suggested), filetypes=[("JSON","*.json")])
        if not out: return
        with open(out, "w", encoding="utf-8") as f: f.write(make_report(self.last_results))
        self.status.set(f"JSON gespeichert: {out}")

    def run_analysis(self):
        path = self.path_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Fehler", "Bitte eine gültige Datei auswählen."); return
        try:
            self.status.set("Analysiere…"); self.update_idletasks()
            window = max(1, int(self.window_kib.get())) * 1024
            low = float(self.low_thr.get()); high = float(self.high_thr.get()); scales = self.parse_scales()

            head = read_head(path, 256*1024); size = file_size(path) or 0; sig_hits = detect_signatures(head)
            sample_size = min(size, 8 * 1024 * 1024)
            with open(path, "rb") as f: sample = f.read(sample_size)

            H_total = shannon_entropy(sample); chi2 = chi_square_uniformity(sample)
            ecb_ratio = repeating_block_ratio(sample, 16)
            hints = guess_encryption_method(sig_hits, head, sample)
            offsets, ents = rolling_entropy(path, window=window, max_samples=240)

            chaos, order, d_72_28, d_28_72, label = ternary_72_28_score(H_total)

            _, _, f_labels = ftc_window_labels(path, window=window, low=low, high=high)
            H3, mu, counts = tri_entropy_from_labels(f_labels)
            r0 = counts.get(0,0) / max(len(f_labels),1)
            longest_run = longest_monosign_run(f_labels)
            scales_all = [f_labels] + simple_multiscale_labels(f_labels, scales=tuple(scales))
            auth_ok = (0.55 <= r0 <= 0.80) and (abs(mu) < 0.10) and (H3 > 0.9)

            # Render images for GUI
            self._hist_imgtk = pil_to_tk(render_hist_pil(sample, width=800, height=260)); self.hist_canvas.configure(image=self._hist_imgtk)
            self._entropy_imgtk = pil_to_tk(render_entropy_pil(offsets, ents, width=800, height=260)); self.ent_canvas.configure(image=self._entropy_imgtk)
            self._ftc_imgtk = pil_to_tk(render_strip_pil(scales_all, width=800, height=200)); self.ftc_canvas.configure(image=self._ftc_imgtk)

            # Results text
            self.results.delete("1.0", "end")
            self.results.insert("end", f"Datei: {path}\nGröße: {size:,} Bytes\n\n")
            if sig_hits:
                self.results.insert("end", "Erkannte Header/Signaturen:\n")
                for s in sig_hits:
                    self.results.insert("end", f"  • {s}")
                    if s in LIKELY_METHOD_HINTS: self.results.insert("end", f"  → {LIKELY_METHOD_HINTS[s]}")
                    self.results.insert("end", "\n")
                self.results.insert("end", "\n")
            else:
                self.results.insert("end", "Keine bekannten Header/Signaturen erkannt.\n\n")
            self.results.insert("end", f"Shannon-Entropie (Stichprobe): {H_total:.3f} bits/Byte\n")
            self.results.insert("end", f"Chi-Quadrat (Uniformität): {chi2:.2f}\n")
            self.results.insert("end", f"Wiederholungsrate 16-Byte-Blöcke: {ecb_ratio:.2%}\n\n")
            self.results.insert("end", "72/28-Balance:\n")
            self.results.insert("end", f"  • Chaos ≈ {chaos*100:.1f}% | Ordnung ≈ {order*100:.1f}% — {label}\n")
            self.results.insert("end", f"  • Distanz zu 72/28: {d_72_28:.3f} | zu 28/72: {d_28_72:.3f}\n\n")
            self.results.insert("end", "FTC-Analyse:\n")
            self.results.insert("end", f"  • Fenster: {len(f_labels)} × {window//1024} KiB | Skalen: {scales}\n")
            self.results.insert("end", f"  • Zählung: chaos(-1)={counts.get(-1,0)}, natural(0)={counts.get(0,0)}, order(+1)={counts.get(1,0)}\n")
            self.results.insert("end", f"  • r0: {r0:.2f} | H3: {H3:.3f} bits | μ: {mu:.3f} | längste Mono-Run: {longest_run}\n")
            self.results.insert("end", f"  • Authenticity-Heuristik (FTC): {'OK' if auth_ok else 'auffällig'}\n\n")
            if hints:
                self.results.insert("end", "Heuristische Hinweise:\n")
                for h in hints: self.results.insert("end", f"  • {h}\n")
                self.results.insert("end", "\n")
            self.results.insert("end", "Hinweise:\n  • Profile: 'Auto anwenden' wählt auf Basis der Header ein passendes Profil.\n  • Kalibriere Low/High mit Prozentilen, falls Datentyp stark variiert.\n")

            # Store report
            self.last_results = {
                "file": {"path": path, "size": int(size)},
                "profile": {
                    "applied": self.profile_var.get(),
                    "window_kib": int(window//1024),
                    "low": float(low), "high": float(high), "scales": scales,
                },
                "signatures": sig_hits,
                "stats": {"entropy_bits_per_byte": float(H_total), "chi_square": float(chi2), "ecb_repeating_block_ratio": float(ecb_ratio)},
                "balance_72_28": {"chaos": float(chaos), "order": float(order), "dist_to_72_28": float(d_72_28), "dist_to_28_72": float(d_28_72), "label": label},
                "rolling": {"offsets": [int(x) for x in offsets], "entropies": [float(x) for x in ents]},
                "ftc": {
                    "labels": [int(x) for x in f_labels],
                    "counts": {str(k): int(v) for k,v in counts.items()},
                    "r0": float(r0), "H3": float(H3), "mu": float(mu),
                    "longest_run": int(longest_run),
                    "scales_labels": [[int(x) for x in row] for row in scales_all],
                    "authenticity_ok": bool(auth_ok),
                },
                "sample": {
                    "bytes_included": len(sample) <= 1_000_000,
                    "length": len(sample),
                    "bytes": sample if len(sample) <= 1_000_000 else b"",
                },
                "hints": hints,
            }
            self.status.set("Fertig.")
        except Exception as e:
            self.status.set("Fehler."); messagebox.showerror("Fehler bei Analyse", str(e))

# --- CLI ---
def run_cli(args):
    path = args.input
    if not os.path.exists(path):
        print("Input-Datei nicht gefunden:", path); sys.exit(2)

    prof = PROFILES.get(args.profile, PROFILES["Default"])
    window = (args.window_kib if args.window_kib else prof["window_kib"]) * 1024
    low = args.low if args.low is not None else prof["low"]
    high = args.high if args.high is not None else prof["high"]
    scales = [int(x) for x in args.scales.split(",")] if args.scales else prof["scales"]

    head = read_head(path, 256*1024); sig_hits = detect_signatures(head)
    size = file_size(path) or 0
    sample_size = min(size, 8 * 1024 * 1024)
    with open(path, "rb") as f: sample = f.read(sample_size)

    H_total = shannon_entropy(sample); chi2 = chi_square_uniformity(sample)
    ecb_ratio = repeating_block_ratio(sample, 16)
    hints = guess_encryption_method(sig_hits, head, sample)
    offsets, ents = rolling_entropy(path, window=window, max_samples=240)

    chaos, order, d_72_28, d_28_72, label = ternary_72_28_score(H_total)

    _, _, f_labels = ftc_window_labels(path, window=window, low=low, high=high)
    H3, mu, counts = tri_entropy_from_labels(f_labels)
    r0 = counts.get(0,0) / max(len(f_labels),1)
    longest_run = longest_monosign_run(f_labels)
    scales_all = [f_labels] + simple_multiscale_labels(f_labels, scales=tuple(scales))
    auth_ok = (0.55 <= r0 <= 0.80) and (abs(mu) < 0.10) and (H3 > 0.9)

    if args.export_hist:
        im = render_hist_pil(sample, width=1200, height=400); im.save(args.export_hist, "PNG"); print("Histogramm exportiert:", args.export_hist)
    if args.export_entropy:
        im = render_entropy_pil(offsets, ents, width=1200, height=400); im.save(args.export_entropy, "PNG"); print("Entropie exportiert:", args.export_entropy)
    if args.export_heatmap:
        im = render_strip_pil(scales_all, width=1600, height=260); im.save(args.export_heatmap, "PNG"); print("Heatmap exportiert:", args.export_heatmap)
    if args.export_json:
        report = {
            "file": {"path": path, "size": int(size)},
            "profile": {"applied": args.profile if args.profile else "Default", "window_kib": int(window//1024), "low": float(low), "high": float(high), "scales": scales},
            "signatures": sig_hits,
            "stats": {"entropy_bits_per_byte": float(H_total), "chi_square": float(chi2), "ecb_repeating_block_ratio": float(ecb_ratio)},
            "balance_72_28": {"chaos": float(chaos), "order": float(order), "dist_to_72_28": float(d_72_28), "dist_to_28_72": float(d_28_72), "label": label},
            "rolling": {"offsets": [int(x) for x in offsets], "entropies": [float(x) for x in ents]},
            "ftc": {"labels": [int(x) for x in f_labels], "counts": {str(k): int(v) for k,v in counts.items()}, "r0": float(r0), "H3": float(H3), "mu": float(mu), "longest_run": int(longest_run), "scales_labels": [[int(x) for x in row] for row in scales_all], "authenticity_ok": bool(auth_ok)},
            "hints": hints,
        }
        with open(args.export_json, "w", encoding="utf-8") as f: json.dump(report, f, indent=2, ensure_ascii=False)
        print("JSON exportiert:", args.export_json)

def main():
    parser = argparse.ArgumentParser(description="Encrypted File Analyzer — 72/28 + FTC (PRO++)")
    parser.add_argument("--input", help="Pfad zur Datei (für CLI)")
    parser.add_argument("--profile", choices=list(PROFILES.keys()), help="Profilname")
    parser.add_argument("--window-kib", type=int, help="Fenstergröße in KiB (override Profil)")
    parser.add_argument("--low", type=float, help="Low-Entropie-Schwelle (override Profil)")
    parser.add_argument("--high", type=float, help="High-Entropie-Schwelle (override Profil)")
    parser.add_argument("--scales", type=str, help="Skalenliste, z.B. 2,4,8 (override Profil)")
    parser.add_argument("--export-hist", help="PNG für Histogramm (CLI)")
    parser.add_argument("--export-entropy", help="PNG für Rolling Entropy (CLI)")
    parser.add_argument("--export-heatmap", help="PNG für FTC-Heatmap (CLI)")
    parser.add_argument("--export-json", help="JSON-Report-Datei (CLI)")
    args, _ = parser.parse_known_args()

    if args.input and (args.export_hist or args.export_entropy or args.export_heatmap or args.export_json):
        run_cli(args); return

    try:
        app = AnalyzerGUI(); app.mainloop()
    except Exception as e:
        print("Startfehler:", e)

if __name__ == "__main__":
    main()
