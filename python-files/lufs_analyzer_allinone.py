import soundfile as sf
import pyloudnorm as pyln
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os, sys, time, json

SETTINGS_FILE = 'lufs_analyzer_settings.json'

class ProgressWindow:
    def __init__(self, root, title="Ladevorgang"):
        self.top = tk.Toplevel(root)
        self.top.title(title)
        self.top.geometry("460x120")
        self.top.resizable(False, False)
        self.pb = ttk.Progressbar(self.top, orient="horizontal", length=420, mode="determinate")
        self.pb.pack(pady=12)
        self.label = tk.Label(self.top, text="Starte ...")
        self.label.pack()
        self.top.update()

    def update_progress(self, percent, message=""):
        percent = max(0, min(100, percent))
        self.pb["value"] = percent
        self.label.config(text=f"{percent:.0f}% – {message}")
        self.top.update()

    def close(self):
        try:
            self.top.destroy()
        except Exception:
            pass

class LUFSAnalyzerAllInOneProGuided:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LUFS Analyzer – All-in-One PRO (Guided)")
        self.root.geometry("1180x960")

        # State
        self.reference_data = None
        self.reference_filename = None
        self.last_metrics = None
        self.module_status = {}

        # Settings with persistence
        self.genre_viking_var = tk.BooleanVar(value=False)
        self.beginner_mode_var = tk.BooleanVar(value=True)  # zeigt ausführliche Schritt-für-Schritt-Infos
        self.load_settings()

        self.status_var = tk.StringVar(value="Bereit")
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- GUI ----------------
    def setup_gui(self):
        header = tk.Frame(self.root, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(header, text="🎵 LUFS Analyzer – All-in-One PRO (Guided)",
                 font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=(10,2))
        tk.Label(header, text="Chunk-Laden + Progressbar • Maximizer • EQ • Dynamic EQ • Rebalance • LoudMax • Summary • Beginner-Guides",
                 font=("Arial", 10), bg="#2c3e50", fg="#bdc3c7").pack(pady=(0,10))

        toolbar = tk.Frame(self.root)
        toolbar.pack(fill="x", padx=10, pady=8)
        tk.Button(toolbar, text="🎯 Referenz laden", command=self.load_reference,
                  bg="#9b59b6", fg="white", padx=14, pady=8).pack(side="left", padx=5)
        tk.Button(toolbar, text="📁 Song analysieren", command=self.select_and_analyze,
                  bg="#3498db", fg="white", padx=14, pady=8).pack(side="left", padx=5)
        tk.Button(toolbar, text="❌ Beenden", command=self.on_close,
                  bg="#e74c3c", fg="white", padx=14, pady=8).pack(side="right", padx=5)

        # Optionen
        options = tk.Frame(self.root)
        options.pack(fill="x", padx=10)
        tk.Checkbutton(options, text="Viking/Death Metal (Low‑Mid toleranter)",
                       variable=self.genre_viking_var, command=self.on_genre_toggle).pack(side="right")
        tk.Checkbutton(options, text="Beginner‑Modus (Schritt‑für‑Schritt‑Anleitung)",
                       variable=self.beginner_mode_var, command=self.on_beginner_toggle).pack(side="right", padx=12)

        ref_status = tk.Frame(self.root, bg="#ecf0f1")
        ref_status.pack(fill="x", padx=10, pady=(8,0))
        self.ref_status_var = tk.StringVar(value="🎯 Keine Referenz geladen")
        tk.Label(ref_status, textvariable=self.ref_status_var, font=("Arial", 10, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").pack(padx=8, pady=6, anchor="w")

        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(result_frame, text="Analyse-Ergebnisse", font=("Arial", 12, "bold")).pack(anchor="w")
        self.result_text = scrolledtext.ScrolledText(result_frame, font=("Consolas", 10), bg="#f8f9fa")
        self.result_text.pack(fill="both", expand=True)

        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", bg="#ecf0f1").pack(fill="x", side="bottom")

    # ---------------- Settings Persistenz ----------------
    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.genre_viking_var = tk.BooleanVar(value=bool(data.get('genre_viking', False)))
                    self.beginner_mode_var = tk.BooleanVar(value=bool(data.get('beginner_mode', True)))
        except Exception:
            pass

    def save_settings(self):
        try:
            data = {
                'genre_viking': bool(self.genre_viking_var.get()),
                'beginner_mode': bool(self.beginner_mode_var.get())
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_genre_toggle(self):
        if self.genre_viking_var.get():
            self.status_var.set("Genre: Viking/Death Metal – Low‑Mid toleranter (Warn ±4.5 dB / Stark ±6.5 dB)")
        else:
            self.status_var.set("Genre: Standard – EQ-Schwellen ±3.5 dB / ±5.0 dB")
        self.save_settings()

    def on_beginner_toggle(self):
        if self.beginner_mode_var.get():
            self.status_var.set("Beginner‑Modus aktiviert – es werden detaillierte Schritte angezeigt")
        else:
            self.status_var.set("Beginner‑Modus aus – kompakte Hinweise")
        self.save_settings()

    def on_close(self):
        self.save_settings()
        try:
            self.root.destroy()
        except Exception:
            os._exit(0)

    # ---------------- Audio Loading + Progressbar ----------------
    def load_audio_in_chunks(self, filename, title="Lade Datei"):
        info = sf.info(filename)
        total_frames = max(1, info.frames)
        blocksize = 1_000_000  # ~1 Mio Frames pro Block
        progress = ProgressWindow(self.root, title)
        data_blocks = []
        read_frames = 0
        with sf.SoundFile(filename, "r") as f:
            for block in f.blocks(blocksize):
                if np.issubdtype(block.dtype, np.floating):
                    block = np.clip(block, -1.0, 1.0)
                data_blocks.append(block)
                read_frames += len(block)
                percent = (read_frames / total_frames) * 70.0
                progress.update_progress(percent, f"Lese {read_frames}/{total_frames} Frames…")
        y = np.concatenate(data_blocks, axis=0)
        sr = info.samplerate

        # Analyse – simulierte Steps + echte Berechnung
        progress.update_progress(78, "Berechne Lautheit…"); self.root.update()
        meter = pyln.Meter(sr)
        y_mono = y.mean(axis=1) if y.ndim > 1 else y
        lufs = meter.integrated_loudness(y_mono)

        progress.update_progress(88, "Berechne TruePeak…"); self.root.update()
        sample_peak_db, true_peak_db = self.calculate_peaks(y)

        progress.update_progress(94, "Berechne Spektrum…"); self.root.update()
        fft = np.fft.rfft(y_mono)
        freqs = np.fft.rfftfreq(len(y_mono), d=1/sr)
        fft_db = 20 * np.log10(np.abs(fft) + 1e-12)

        progress.update_progress(100, "Fertig")
        time.sleep(0.2)
        progress.close()
        return y, sr, lufs, sample_peak_db, true_peak_db, freqs, fft_db

    # ---------------- Peaks & TruePeak ----------------
    def estimate_true_peak_db(self, signal, oversample=16):
        sig = np.asarray(signal, dtype=np.float64)
        sig = np.clip(sig, -1.0, 1.0)
        if sig.size < 2:
            peak = np.max(np.abs(sig)) if sig.size else 0.0
            return 20*np.log10(peak + 1e-12)
        n = sig.size
        spec = np.fft.rfft(sig)
        up_n = n * oversample
        pad = up_n//2 + 1 - spec.size
        spec_up = np.pad(spec, (0, max(0, pad)))
        up = np.fft.irfft(spec_up, n=up_n)
        up /= oversample
        tp = float(np.max(np.abs(up)))
        return 20*np.log10(tp + 1e-12)

    def calculate_peaks(self, y):
        if np.issubdtype(y.dtype, np.floating):
            y = np.clip(y, -1.0, 1.0)
        def ch_max(x):
            x = np.asarray(x)
            return float(np.max(np.abs(x))) if x.size else 0.0
        if y.ndim > 1:
            l, r = y[:,0], y[:,1]
            sample_peak = max(ch_max(l), ch_max(r))
            sample_peak_db = 20*np.log10(sample_peak + 1e-12)
            tp_l = self.estimate_true_peak_db(l, oversample=16)
            tp_r = self.estimate_true_peak_db(r, oversample=16)
            true_peak_db = max(tp_l, tp_r)
        else:
            sample_peak = ch_max(y)
            sample_peak_db = 20*np.log10(sample_peak + 1e-12)
            true_peak_db = self.estimate_true_peak_db(y, oversample=16)
        if (sample_peak_db <= -1.1) and (true_peak_db > -0.5):
            self.status_var.set("⚠️ Hinweis: SamplePeak < -1.1 dBFS, aber TruePeak nahe 0.0 → Export/Bus prüfen (Normalisierung aus!)")
        return sample_peak_db, true_peak_db

    # ---------------- Bands ----------------
    def get_band(self, freqs, fft_db, fmin, fmax):
        mask = (freqs >= fmin) & (freqs <= fmax)
        return np.mean(fft_db[mask]) if np.any(mask) else -80.0

    # ---------------- Referenz laden ----------------
    def load_reference(self):
        file_path = filedialog.askopenfilename(title="Referenz wählen",
                                               filetypes=[("Audio", "*.wav *.flac *.aiff *.aif *.mp3")])
        if not file_path:
            return
        try:
            y, sr, lufs, sp_db, tp_db, freqs, fft_db = self.load_audio_in_chunks(file_path, "Referenz laden")
            bands = {
                'sub': self.get_band(freqs, fft_db, 20, 60),
                'bass': self.get_band(freqs, fft_db, 60, 250),
                'low_mid': self.get_band(freqs, fft_db, 250, 600),
                'mid': self.get_band(freqs, fft_db, 600, 2500),
                'high_mid': self.get_band(freqs, fft_db, 3000, 4500),
                'high': self.get_band(freqs, fft_db, 8000, 12000),
            }
            self.reference_data = {
                'filename': file_path,
                'lufs': lufs,
                'sample_peak_db': sp_db,
                'true_peak_db': tp_db,
                'bands': bands,
            }
            self.reference_filename = os.path.basename(file_path)
            self.ref_status_var.set(f"Referenz: {self.reference_filename} • LUFS={lufs:.1f}, ISP={tp_db:.1f}")
            self.status_var.set("Referenz geladen – jetzt deinen Song analysieren")
        except Exception as e:
            messagebox.showerror(
                "Fehler", 
                f"Referenz konnte nicht geladen werden:\n{str(e)}"
            )

    # ---------------- Song wählen ----------------
    def select_and_analyze(self):
        if self.reference_data is None:
            messagebox.showwarning("Keine Referenz", "Bitte zuerst eine Referenz laden.")
            return
        file_path = filedialog.askopenfilename(title="Song wählen",
                                               filetypes=[("Audio", "*.wav *.flac *.aiff *.aif")])
        if file_path:
            self.analyze_with_reference(file_path)

    # ---------------- Hilfsfunktionen für Ozone Guides ----------------
    def recommend_eq_node(self, label, delta, center_hz, prefer_shelf=False):
        """Gibt eine textuelle, einsteigerfreundliche EQ-Empfehlung zurück.
        prefer_shelf=True → Low/High Shelf statt Bell.
        """
        action = "senken" if delta > 0 else "anheben"
        amount = abs(delta)
        # Stärke in Stufen
        if amount >= 6.0:
            gain = min(4.5, amount * 0.6)
            strength = "stärker"
        elif amount >= 3.5:
            gain = min(3.0, amount * 0.4)
            strength = "moderat"
        else:
            gain = min(1.5, amount * 0.3)
            strength = "leicht"
        # Q wählen
        if prefer_shelf:
            ftype = "Low Shelf" if center_hz < 400 else "High Shelf"
            q = 0.7
        else:
            ftype = "Bell (Peak)"
            if amount >= 6.0:
                q = 1.0
            elif amount >= 3.5:
                q = 1.2
            else:
                q = 1.4
        return f"{label}: {strength} {action} → {ftype}, Freq ≈ {int(center_hz)} Hz, Q≈{q:.1f}, Gain {('-' if delta>0 else '+')}{gain:.1f} dB"

    def ozone_path_eq(self):
        return (
            "📍 Ozone 12: Equalizer → Module öffnen → Add Band (+) → Type wählen (Bell/Low Shelf/High Shelf) → "
            "Frequenz eingeben → Q einstellen → Gain ziehen. Tipp: ALT für feinere Schritte."
        )

    def ozone_path_dyn_eq(self):
        return (
            "📍 Ozone 12: Dynamic EQ → Add Band → Type Bell → Frequency setzen → Threshold runter bis 1–2 dB Gain‑Red. → "
            "Ratio 2:1, Attack 10–20 ms, Release 80–150 ms, Mode: Peak."
        )

    def ozone_path_maximizer(self):
        return (
            "📍 Ozone 12: Maximizer → Mode: IRC IV (Modern) • True Peak: ON • Margin: −1.2 dB • Character: Balanced (0) • "
            "Stereo Indep: 0 • Transient Emphasis: 10–20% • Soft Clip: OFF. Threshold entsprechend LUFS‑Ziel anpassen."
        )

    def ozone_path_master_rebalance(self):
        return (
            "📍 Ozone 12: Master Rebalance → Target: Vocals/Drums/Bass wählen → Amount ±1–2 dB • Sensitivity 25–50% • "
            "Separation 30–50% • Automatisch durch Song fahren oder Stems anpassen."
        )

    # ---------------- Hauptanalyse ----------------
    def analyze_with_reference(self, filename):
        self.module_status = {
            'maximizer': {'status': 'unknown', 'message': ''},
            'equalizer': {'status': 'unknown', 'message': ''},
            'dynamic_eq': {'status': 'unknown', 'message': ''},
            'rebalance': {'status': 'unknown', 'message': ''},
            'loudmax': {'status': 'unknown', 'message': ''}
        }
        try:
            y, sr, lufs, sp_db, tp_db, freqs, fft_db = self.load_audio_in_chunks(filename, "Song laden")
        except Exception as e:
            messagebox.showerror(
                "Fehler", 
                f"Datei konnte nicht geladen werden:\n{str(e)}"
            )
            return

        song_bands = {
            'sub': self.get_band(freqs, fft_db, 20, 60),
            'bass': self.get_band(freqs, fft_db, 60, 250),
            'low_mid': self.get_band(freqs, fft_db, 250, 600),
            'mid': self.get_band(freqs, fft_db, 600, 2500),
            'high_mid': self.get_band(freqs, fft_db, 3000, 4500),
            'high': self.get_band(freqs, fft_db, 8000, 12000),
        }

        ref = self.reference_data
        self.last_metrics = {
            'lufs': lufs,
            'isp': tp_db,
            'ref_lufs': ref['lufs'],
            'ref_isp': ref['true_peak_db'],
            'delta_lufs': lufs - ref['lufs'],
            'delta_isp': tp_db - ref['true_peak_db'],
            'genre_viking': self.genre_viking_var.get()
        }

        self.result_text.delete(1.0, tk.END)
        self.log(f"🎵 Analyse: {os.path.basename(filename)}")
        self.log(f"🎯 Referenz: {self.reference_filename}")
        self.log("-" * 78)
        self.log(f"Integrated Loudness : {lufs:.2f} LUFS")
        self.log(f"Sample Peak         : {sp_db:.2f} dBFS")
        self.log(f"True Peak (ISP)     : {tp_db:.2f} dBTP")
        self.log(f"Debug: SamplePeak={sp_db:.2f} dBFS, TruePeak={tp_db:.2f} dBTP\n")

        # ---------- Maximizer (Gain vs Referenz) ----------
        self.log("🔹 MAXIMIZER (Gain & Sicherheit)")
        lufs_delta = lufs - ref['lufs']
        if abs(lufs_delta) <= 1.0:
            self.log("✅ Gain ist im Referenzrahmen (±1 LUFS)")
            self.log(self.ozone_path_maximizer())
            self.module_status['maximizer'] = {'status': 'ok', 'message': 'Gain ~ Referenz'}
        elif lufs_delta < 0:
            msg = f"Gain anheben: +{abs(lufs_delta):.1f} dB (Ziel ≈ {ref['lufs']:.1f} LUFS)"
            self.log(f"⚠️ {msg}")
            self.log(self.ozone_path_maximizer())
            self.module_status['maximizer'] = {'status': 'needs_adjustment', 'message': msg}
        else:
            msg = f"Gain absenken: -{abs(lufs_delta):.1f} dB (Ziel ≈ {ref['lufs']:.1f} LUFS)"
            self.log(f"⚠️ {msg}")
            self.log(self.ozone_path_maximizer())
            self.module_status['maximizer'] = {'status': 'needs_adjustment', 'message': msg}

        # ---------- Equalizer (mit konkreten Typen) ----------
        genre_on = self.genre_viking_var.get()
        self.log("\n🔹 EQUALIZER (konkrete Einstellungen, für Anfänger geeignet)")
        self.log(self.ozone_path_eq())
        eq_issues = []
        # (label, center Hz, prefer_shelf)
        bands_cfg = {
            'sub': ("Sub (20–60 Hz)", 40, True),
            'bass': ("Bass (60–250 Hz)", 100, False),
            'low_mid': ("Low‑Mid (250–600 Hz)", 350, False),
            'mid': ("Mid (600–2.5 kHz)", 1200, False),
            'high_mid': ("High‑Mid (3–4.5 kHz)", 3500, False),
            'high': ("High (8–12 kHz)", 10000, True),
        }
        warn_std, strong_std = 3.5, 5.0
        warn_lowmid, strong_lowmid = (4.5, 6.5) if genre_on else (warn_std, strong_std)

        for key, (label, freq, shelf) in bands_cfg.items():
            ref_db = ref['bands'][key]
            song_db = song_bands[key]
            delta = song_db - ref_db
            # Toleranzen
            if key == 'low_mid':
                warn_th, strong_th = warn_lowmid, strong_lowmid
            else:
                warn_th, strong_th = warn_std, strong_std

            if abs(delta) <= warn_th:
                self.log(f"✅ {label}: innerhalb Toleranz (Δ {delta:+.1f} dB)")
                continue

            # Konkrete Empfehlung (Bell/Shelf, Freq, Q, Gain)
            suggestion = self.recommend_eq_node(label, delta, freq, prefer_shelf=shelf)
            if abs(delta) >= strong_th:
                self.log(f"❌ {label}: Δ {delta:+.1f} dB → {suggestion}")
            else:
                self.log(f"⚠️ {label}: Δ {delta:+.1f} dB → {suggestion}")
            eq_issues.append(suggestion)

        if eq_issues:
            self.module_status['equalizer'] = {'status': 'needs_adjustment', 'message': ' | '.join(eq_issues)}
        else:
            self.module_status['equalizer'] = {'status': 'ok', 'message': 'Alle Bänder innerhalb Toleranz'}

        # ---------- Dynamic EQ (sehr konkret) ----------
        self.log("\n🔹 DYNAMIC EQ (problematische Peaks zähmen – Schritt für Schritt)")
        self.log(self.ozone_path_dyn_eq())
        dyn_issues = []
        bass_delta = song_bands['bass'] - ref['bands']['bass']
        if bass_delta > 3.0:
            self.log("⚠️ Bass-Transienten zähmen:")
            self.log("   • Band: 80 Hz • Type: Bell • Q≈1.0 • Dynamic: ON")
            self.log("   • Threshold: so einstellen, dass 1–2 dB Gain Reduction bei Kick/Peaks entsteht")
            self.log("   • Ratio: 2–3:1 • Attack: 10–15 ms • Release: 100–150 ms")
            dyn_issues.append("DynEQ @80 Hz 1–2 dB GR")
        else:
            self.log("✅ Bass-Dynamik: ok")
        hm_delta = song_bands['high_mid'] - ref['bands']['high_mid']
        if hm_delta > 4.0:
            self.log("⚠️ Härten/Sibilanz (Git/Vox) entschärfen:")
            self.log("   • Band: 3.5 kHz • Type: Bell • Q≈2.0 • Dynamic: ON")
            self.log("   • Threshold: 1–2 dB GR bei harschen Stellen • Ratio: 2:1 • Attack: 5–10 ms • Release: 80–120 ms")
            dyn_issues.append("DynEQ @3.5 kHz 1–2 dB GR")
        else:
            self.log("✅ High‑Mid-Dynamik: ok")
        self.module_status['dynamic_eq'] = {'status': ('needs_adjustment' if dyn_issues else 'ok'), 'message': '; '.join(dyn_issues) if dyn_issues else 'Keine dynamischen Hotspots'}

        # ---------- Rebalance (mit Ozone-Weg) ----------
        self.log("\n🔹 REBALANCE (Vocal/Drums/Bass Verhältnis)")
        self.log(self.ozone_path_master_rebalance())
        rb_issues = []
        vocal_ratio_song = song_bands['mid'] - song_bands['high_mid']
        vocal_ratio_ref = ref['bands']['mid'] - ref['bands']['high_mid']
        v_delta = vocal_ratio_song - vocal_ratio_ref
        if v_delta < -2.0:
            self.log("⚠️ Vocals zu leise → Ozone Master Rebalance: Target=Vocals, Amount +1.5 dB, Sens 40%")
            rb_issues.append("Vocals +1–2 dB")
        elif v_delta > 2.0:
            self.log("⚠️ Vocals zu laut → Ozone Master Rebalance: Target=Vocals, Amount −1.5 dB, Sens 40%")
            rb_issues.append("Vocals −1–2 dB")
        else:
            self.log("✅ Vocals im Referenzrahmen")
        drum_ratio_song = song_bands['bass'] - song_bands['mid']
        drum_ratio_ref = ref['bands']['bass'] - ref['bands']['mid']
        d_delta = drum_ratio_song - drum_ratio_ref
        if d_delta < -2.0:
            self.log("⚠️ Drums wirken schwächer → Target=Drums, Amount +1.5 dB, Sens 35%")
            rb_issues.append("Drums +1–2 dB")
        elif d_delta > 2.0:
            self.log("⚠️ Drums zu dominant → Target=Drums, Amount −1.5 dB, Sens 35%")
            rb_issues.append("Drums −1–2 dB")
        else:
            self.log("✅ Drums im Referenzrahmen")
        b_direct = song_bands['bass'] - ref['bands']['bass']
        if b_direct > 5.0:
            self.log("❌ Bass deutlich zu dominant → Target=Bass, Amount −2.5 dB, Sens 40%")
            rb_issues.append("Bass −2–3 dB")
        elif b_direct < -5.0:
            self.log("❌ Bass deutlich zu schwach → Target=Bass, Amount +2.5 dB, Sens 40%")
            rb_issues.append("Bass +2–3 dB")
        elif 3.5 < b_direct <= 5.0:
            self.log("⚠️ Bass etwas zu dominant → Target=Bass, Amount −1.5 dB")
            rb_issues.append("Bass −1–2 dB")
        elif -5.0 <= b_direct < -3.5:
            self.log("⚠️ Bass etwas zu schwach → Target=Bass, Amount +1.5 dB")
            rb_issues.append("Bass +1–2 dB")
        else:
            self.log("✅ Bass-Level i.O.")
        if rb_issues:
            self.module_status['rebalance'] = {'status': 'needs_adjustment', 'message': '; '.join(rb_issues)}
        else:
            self.module_status['rebalance'] = {'status': 'ok', 'message': 'Balancen passen'}

        # ---------- LoudMax (finale ISP Kontrolle) ----------
        self.log("\n🔹 LOUDMAX (finale ISP/Streaming-Kontrolle)")
        if tp_db <= -1.0:
            self.log("✅ Output streaming-sicher (ISP ≤ −1.0 dBTP)")
            self.log("   📍 LoudMax: ISP=ON (leuchtend), Out ≈ −1.0 bis −1.2 dB | Plugin als letztes im Master-Bus | Export: WAV 32‑Bit Float, Normalisierung AUS")
            self.module_status['loudmax'] = {'status': 'ok', 'message': 'ISP ≤ −1.0 dBTP'}
        else:
            msg = f"Output zu hoch: {tp_db:.1f} dBTP → Out = −1.2 dB, ISP=ON"
            self.log(f"⚠️ {msg}")
            self.log("   📍 LoudMax: 'Out' auf −1.2 dB, 'ISP' aktivieren; als letztes Plugin einsetzen; Export ohne Normalisierung.")
            self.module_status['loudmax'] = {'status': 'needs_adjustment', 'message': msg}

        # ---------- Zusammenfassung ----------
        self.generate_summary()

    # ---------------- Summary ----------------
    def generate_summary(self):
        self.log("\n" + "=" * 78)
        self.log("🎯 FINALE ZUSAMMENFASSUNG (Streaming & Referenz)")
        self.log("=" * 78)
        if self.last_metrics is not None:
            lm = self.last_metrics
            genre_str = "Viking/Death Metal" if lm.get('genre_viking') else "Standard"
            self.log(
                f"• Kernwerte: LUFS {lm['lufs']:.2f} (Δ {lm['delta_lufs']:+.2f} vs Ref {lm['ref_lufs']:.2f}) | "
                f"ISP {lm['isp']:.2f} dBTP (Δ {lm['delta_isp']:+.2f} vs Ref {lm['ref_isp']:.2f}) | "
                f"Genre: {genre_str}"
            )
        mapping = {
            'maximizer': 'Maximizer',
            'equalizer': 'Equalizer',
            'dynamic_eq': 'Dynamic EQ',
            'rebalance': 'Rebalance',
            'loudmax': 'LoudMax'
        }
        ok = 0
        total = len(self.module_status)
        for key, info in self.module_status.items():
            name = mapping.get(key, key)
            status = info['status']
            message = info['message']
            if status == 'ok':
                self.log(f"✅ {name}: {message if message else 'OK'}"); ok += 1
            elif status == 'needs_adjustment':
                self.log(f"⚠️ {name}: {message if message else 'Anpassungen empfohlen'}")
            else:
                self.log(f"❓ {name}: Nicht analysiert")
        pct = 100.0 * ok / total if total else 0.0
        self.log("-" * 78)
        if pct == 100.0:
            self.log("🎉 PERFEKT! Alles streaming-sicher und referenzkonform. Bereit für Release! 🚀")
        elif pct >= 80.0:
            self.log(f"🎯 SEHR GUT – {pct:.0f}% OK. Nur kleine Feinschliffe nötig.")
        elif pct >= 60.0:
            self.log(f"⚙️  GUT – {pct:.0f}% OK. Einige Module brauchen Feinanpassung.")
        else:
            self.log(f"🔧 VERBESSERUNG NÖTIG – nur {pct:.0f}% OK. Bitte Empfehlungen umsetzen.")

    # ---------------- Utils ----------------
    def log(self, msg):
        self.result_text.insert(tk.END, msg + "\n")
        self.result_text.see(tk.END)
        self.root.update()

    # ---------------- Run ----------------
    def run(self):
        self.root.mainloop()

# ---------------- Main ----------------
if __name__ == "__main__":
    try:
        app = LUFSAnalyzerAllInOneProGuided()
        app.run()
    except Exception as e:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror(
            "Kritischer Fehler",
            f"Programmstart fehlgeschlagen:\n{str(e)}\n\n"
            f"Bitte installiere benötigte Pakete:\n"
            f"pip install soundfile pyloudnorm numpy"
        )
        sys.exit(1)
