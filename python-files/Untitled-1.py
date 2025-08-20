import os
import json
import csv
import threading
import warnings
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pathlib import Path
import io
import contextlib
import traceback
import datetime

# Coqui TTS
from TTS.api import TTS
import torch

# (Optional) Hugging Face Transformers logging (silence)
try:
    from transformers.utils import logging as hf_logging
except Exception:
    hf_logging = None

# -------- App toggles --------
QUIET = True        # console logs ko chup karna ho to True
USE_GPU = False     # CUDA ho to True
REQUIRE_SPEAKER_WAV = True  # confusion avoid karne ke liye cloning WAV mandatory
# --------------------------------

# (Optional) Helps avoid pickle errors with XTTS configs on some setups
torch.serialization.add_safe_globals([
    __import__("TTS.tts.configs.xtts_config", fromlist=["XttsConfig"]).XttsConfig,
    __import__("TTS.tts.models.xtts", fromlist=["XttsAudioConfig"]).XttsAudioConfig,
    __import__("TTS.config.shared_configs", fromlist=["BaseDatasetConfig"]).BaseDatasetConfig,
    __import__("TTS.tts.models.xtts", fromlist=["XttsArgs"]).XttsArgs
])

if QUIET:
    # Hide torchaudio future-change warning
    warnings.filterwarnings(
        "ignore",
        message=r".*use torchaudio\.load_with_torchcodec.*",
        category=UserWarning,
        module=r"torchaudio\._backend\.utils",
    )
    # Hide transformers v4.50 GenerationMixin deprecation warning
    warnings.filterwarnings(
        "ignore",
        message=r".*PreTrainedModel will NOT inherit from `GenerationMixin`.*",
        category=UserWarning,
    )
    for name in ("TTS", "coqpit", "numba", "torch", "torchaudio"):
        logging.getLogger(name).setLevel(logging.ERROR)
    if hf_logging is not None:
        hf_logging.set_verbosity_error()

APP_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
OUTPUT_DIR = APP_DIR / "voicoo_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ERROR_LOG = OUTPUT_DIR / "error.log"

def log_error(title: str, err: Exception):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.now().isoformat()}] {title}\n")
        f.write("".join(traceback.format_exception(type(err), err, err.__traceback__)))
        # env snapshot
        try:
            import transformers, torch, soundfile
            f.write(
                f"\nVERSIONS -> transformers: {transformers.__version__}, "
                f"torch: {torch.__version__}, soundfile: {getattr(soundfile, '__version__', 'unknown')}\n"
            )
        except Exception:
            pass

def transformers_version_tuple():
    try:
        import transformers
        parts = transformers.__version__.split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch_raw = parts[2] if len(parts) > 2 else "0"
        patch = int(patch_raw.split("+")[0]) if patch_raw.split("+")[0].isdigit() else 0
        return (major, minor, patch, transformers.__version__)
    except Exception:
        return (0, 0, 0, "unknown")

def load_xtts_default():
    # First call will download model if not cached
    return TTS("tts_models/multilingual/xtts_v2", gpu=USE_GPU)

# Global TTS handle (can be swapped if user loads finetuned model)
tts_model = load_xtts_default()

# Try to read built-in speakers (often empty for XTTS v2)
def get_builtin_speakers(ttsm):
    try:
        return list(getattr(ttsm, "speaker_manager").speakers.keys())
    except Exception:
        return []

class VoicooApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voicoo - Voice Generation, Cloning & Finetune Ready")
        self.speaker_wavs = []      # allow multiple reference wavs
        self.custom_model = None     # (model_path, config_path)
        self.builtin_speakers = get_builtin_speakers(tts_model)

        # ----- Notebook tabs -----
        self.nb = ttk.Notebook(root)
        self.tab_synth = ttk.Frame(self.nb)
        self.tab_dataset = ttk.Frame(self.nb)
        self.tab_model = ttk.Frame(self.nb)
        self.nb.add(self.tab_synth, text="Synthesize")
        self.nb.add(self.tab_dataset, text="Dataset & Training")
        self.nb.add(self.tab_model, text="Model")
        self.nb.pack(fill="both", expand=True)

        # ======= Synthesize tab =======
        self._build_synth_tab()

        # ======= Dataset & Training helper tab =======
        self._build_dataset_tab()

        # ======= Model tab =======
        self._build_model_tab()

        # Footer status
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="green", anchor="w")
        self.status_label.pack(fill="x", padx=8, pady=6)

        self._info_startup()

    # --------------- UI Sections ---------------
    def _build_synth_tab(self):
        frame = self.tab_synth

        tk.Label(frame, text="Enter Text:").pack(anchor="w", padx=8, pady=(10,0))
        self.text_entry = tk.Text(frame, width=85, height=5)
        self.text_entry.pack(fill="x", padx=8, pady=6)

        row = ttk.Frame(frame)
        row.pack(fill="x", padx=8, pady=2)
        ttk.Label(row, text="Language:").pack(side="left")
        self.lang_var = tk.StringVar(value="en")
        langs = ["en","hi","es","fr","de","it","ru","pt","tr","pl","nl","cs","ar","zh-cn","ja","hu","ko"]
        ttk.OptionMenu(row, self.lang_var, self.lang_var.get(), *langs).pack(side="left", padx=8)

        btns = ttk.Frame(frame)
        btns.pack(fill="x", padx=8, pady=8)
        ttk.Button(btns, text="Generate Voice", command=self.generate_voice).pack(side="left")

        ttk.Button(btns, text="Add Speaker WAV", command=self.add_speaker_wav).pack(side="left", padx=8)
        ttk.Button(btns, text="Clear Speaker WAVs", command=self.clear_speaker_wavs).pack(side="left")

        self.output_label = tk.Label(frame, text="", fg="blue", anchor="w", justify="left")
        self.output_label.pack(fill="x", padx=8, pady=(6,8))

        self.wav_listbox = tk.Listbox(frame, height=4)
        self.wav_listbox.pack(fill="x", padx=8, pady=(0,8))

    def _build_dataset_tab(self):
        frame = self.tab_dataset

        tk.Label(frame, text="Build dataset for fine-tuning (single speaker):").pack(anchor="w", padx=8, pady=(10,4))

        row1 = ttk.Frame(frame); row1.pack(fill="x", padx=8, pady=4)
        ttk.Button(row1, text="Choose WAV Folder", command=self.choose_wav_folder).pack(side="left")
        self.dataset_dir_var = tk.StringVar(value="")
        ttk.Entry(row1, textvariable=self.dataset_dir_var, width=60).pack(side="left", padx=8)

        tk.Label(frame, text="Transcript CSV (optional, columns: filename,text):").pack(anchor="w", padx=8)
        row2 = ttk.Frame(frame); row2.pack(fill="x", padx=8, pady=4)
        ttk.Button(row2, text="Choose CSV", command=self.choose_transcript_csv).pack(side="left")
        self.csv_path_var = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.csv_path_var, width=60).pack(side="left", padx=8)

        self.speaker_name_var = tk.StringVar(value="custom_speaker")
        row3 = ttk.Frame(frame); row3.pack(fill="x", padx=8, pady=4)
        ttk.Label(row3, text="Speaker name:").pack(side="left")
        ttk.Entry(row3, textvariable=self.speaker_name_var, width=24).pack(side="left", padx=8)

        ttk.Button(frame, text="Create metadata.csv", command=self.create_metadata).pack(anchor="w", padx=8, pady=8)

        self.dataset_info = tk.Label(frame, text="", fg="blue", justify="left", anchor="w")
        self.dataset_info.pack(fill="x", padx=8, pady=(0,6))

        sep = ttk.Separator(frame, orient="horizontal"); sep.pack(fill="x", padx=8, pady=10)

        tk.Label(frame, text="Training (run outside app):", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8)
        tk.Label(
            frame,
            text=(
                "1) Create/verify metadata.csv above.\n"
                "2) Use official XTTS fine-tuning recipe / UI (Colab/WebUI/AllTalk), or CLI per docs.\n"
                "3) After training, you'll have model checkpoint (.pth) + config.json.\n"
                "4) Load them in the Model tab (below) and synthesize without reference WAV."
            ),
            justify="left"
        ).pack(anchor="w", padx=8, pady=(4,4))

    def _build_model_tab(self):
        frame = self.tab_model

        tk.Label(frame, text="Load a Fine-Tuned XTTS Model", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(10,6))
        row1 = ttk.Frame(frame); row1.pack(fill="x", padx=8, pady=4)
        ttk.Button(row1, text="Select model.pth", command=self.pick_model_pth).pack(side="left")
        self.model_pth_var = tk.StringVar(value="")
        ttk.Entry(row1, textvariable=self.model_pth_var, width=60).pack(side="left", padx=8)

        row2 = ttk.Frame(frame); row2.pack(fill="x", padx=8, pady=4)
        ttk.Button(row2, text="Select config.json", command=self.pick_config_json).pack(side="left")
        self.config_json_var = tk.StringVar(value="")
        ttk.Entry(row2, textvariable=self.config_json_var, width=60).pack(side="left", padx=8)

        ttk.Button(frame, text="Load Fine-Tuned Model", command=self.load_finetuned_model).pack(anchor="w", padx=8, pady=8)

        self.model_info = tk.Label(frame, text="", fg="blue", justify="left", anchor="w")
        self.model_info.pack(fill="x", padx=8, pady=(0,6))

        sep = ttk.Separator(frame, orient="horizontal"); sep.pack(fill="x", padx=8, pady=10)

        tk.Label(frame, text="Back to Base XTTS", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8)
        ttk.Button(frame, text="Switch to Base Model", command=self.switch_to_base).pack(anchor="w", padx=8, pady=6)

    # --------------- Helpers ---------------
    def _info_startup(self):
        if self.builtin_speakers:
            self.set_output(f"Built-in speakers found: {self.builtin_speakers}")
        else:
            self.set_output("No built-in speakers. Add Speaker WAV(s) for cloning, or load a fine-tuned model.")

        # Transformers version note (if 4.50+)
        major, minor, patch, ver = transformers_version_tuple()
        if major > 4 or (major == 4 and minor >= 50):
            self.set_output(
                f"{self.output_label.cget('text')}\nNote: transformers {ver} detected. "
                f"For maximum stability, pin to <4.50 (e.g., 4.44.2)."
            )

        self.set_status("Ready ✅", "green")

    def set_status(self, msg, color="green"):
        self.root.after(0, lambda: (self.status_label.config(fg=color), self.status_var.set(msg)))

    def set_output(self, msg):
        self.root.after(0, lambda: self.output_label.config(text=msg))

    def popup_error(self, title, msg):
        self.root.after(0, lambda: messagebox.showerror(title, msg))

    def popup_info(self, title, msg):
        self.root.after(0, lambda: messagebox.showinfo(title, msg))

    def need_wav_guard(self):
        if REQUIRE_SPEAKER_WAV and not self.speaker_wavs:
            self.popup_error(
                "Speaker WAV needed",
                "XTTS v2 is multi-speaker. Please add a clean WAV (6–15s mono speech, no music/noise)."
            )
            return True
        return False

    # --------------- Synth ---------------
    def add_speaker_wav(self):
        files = filedialog.askopenfilenames(filetypes=[("WAV audio", "*.wav")])
        if not files:
            return
        for f in files:
            self.speaker_wavs.append(f)
            self.wav_listbox.insert("end", f)
        self.set_status(f"Loaded {len(files)} reference file(s).", "green")

    def clear_speaker_wavs(self):
        self.speaker_wavs.clear()
        self.wav_listbox.delete(0, "end")
        self.set_status("Reference WAVs cleared.", "orange")

    def generate_voice(self):
        text = self.text_entry.get("1.0", "end").strip()
        if not text:
            messagebox.showerror("Error", "Please enter some text.")
            return

        # Hard guard: make WAV mandatory (avoids "multi-speaker but no speaker" runtime)
        if self.need_wav_guard():
            return

        language = self.lang_var.get()
        out_path = OUTPUT_DIR / "generated_voice.wav"

        def worker():
            try:
                self.set_status("Synthesizing...", "orange")

                # Silence prints like "Using model: xtts" / "Text splitted ..." if QUIET=True
                stdout_sink = io.StringIO() if QUIET else None
                stderr_sink = io.StringIO() if QUIET else None
                ctx_out = contextlib.redirect_stdout(stdout_sink) if QUIET else contextlib.nullcontext()
                ctx_err = contextlib.redirect_stderr(stderr_sink) if QUIET else contextlib.nullcontext()

                with ctx_out, ctx_err:
                    # If only one file, pass string; else list
                    speaker_ref = self.speaker_wavs[0] if len(self.speaker_wavs) == 1 else list(self.speaker_wavs)

                    tts_model.tts_to_file(
                        text=text,
                        file_path=str(out_path),
                        speaker_wav=speaker_ref,
                        language=language
                    )

                self.set_output(f"Voice generated: {out_path}")
                self.set_status("Done ✅", "green")
                self.popup_info("Success", f"Saved: {out_path}")

            except AttributeError as e:
                # GPT2 generate issue (transformers 4.50+ or wrong backend)
                log_error("AttributeError during synthesis", e)
                self.set_status("Failed ❌", "red")
                self.popup_error(
                    "Model backend error",
                    "It looks like the text generator backend isn't exposing `generate()`.\n\n"
                    "Fix:\n1) Open a terminal in your venv\n"
                    "2) Run:\n   pip install --upgrade \"transformers==4.44.2\"\n"
                    "3) Re-run the app.\n\n"
                    f"Details logged to: {ERROR_LOG}"
                )
            except OSError as e:
                # libsndfile or filesystem errors
                log_error("OSError during synthesis", e)
                self.set_status("Failed ❌", "red")
                self.popup_error(
                    "Audio backend error",
                    "Audio write backend error (libsndfile or path).\n\n"
                    "Fix:\n- Ensure: pip install soundfile\n- Save path has write permission.\n\n"
                    f"Details logged to: {ERROR_LOG}"
                )
            except Exception as e:
                log_error("Unhandled error during synthesis", e)
                self.set_status("Failed ❌", "red")
                # Common helpful hints
                major, minor, *_ = transformers_version_tuple()
                hint = ""
                if major > 4 or (major == 4 and minor >= 50):
                    hint = "\nTip: transformers >=4.50 detected. Pin to 4.44.2 for XTTS v2."
                self.popup_error(
                    "Voice generation failed",
                    f"{e.__class__.__name__}: {e}{hint}\n\n"
                    f"Details logged to: {ERROR_LOG}"
                )

        threading.Thread(target=worker, daemon=True).start()

    # --------------- Dataset Builder ---------------
    def choose_wav_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.dataset_dir_var.set(d)

    def choose_transcript_csv(self):
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if p:
            self.csv_path_var.set(p)

    def create_metadata(self):
        wav_dir = Path(self.dataset_dir_var.get())
        csv_path = Path(self.csv_path_var.get()) if self.csv_path_var.get() else None
        spk = self.speaker_name_var.get().strip() or "custom_speaker"

        if not wav_dir.exists():
            self.popup_error("Error", "Please choose a valid WAV folder.")
            return

        wavs = sorted(list(wav_dir.glob("*.wav")))
        if not wavs:
            self.popup_error("Error", "No .wav files found in the selected folder.")
            return

        # Build transcript map if CSV provided
        transcript = {}
        if csv_path and csv_path.exists():
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                # Expect columns: filename, text
                for row in reader:
                    name = row.get("filename") or row.get("file") or row.get("path") or ""
                    text = row.get("text") or ""
                    transcript[name.strip()] = text.strip()

        # Create metadata.csv: "path|text|speaker_name"
        meta_path = wav_dir / "metadata.csv"
        n_with_text = 0
        with open(meta_path, "w", encoding="utf-8") as out:
            for w in wavs:
                key = w.name
                txt = transcript.get(key, "")
                # even if text empty, some UIs auto-transcribe; keep row
                out.write(f"{w.as_posix()}|{txt}|{spk}\n")
                if txt:
                    n_with_text += 1

        msg = (
            f"metadata.csv created at:\n{meta_path}\n"
            f"Total wav: {len(wavs)} | with text: {n_with_text} | speaker: {spk}\n\n"
            "Tip: If text is blank, use your finetune UI/recipe to auto-transcribe or fill later."
        )
        self.dataset_info.config(text=msg)
        self.popup_info("Metadata ready", msg)

    # --------------- Model Load / Switch ---------------
    def pick_model_pth(self):
        p = filedialog.askopenfilename(filetypes=[("Model checkpoint", "*.pth")])
        if p:
            self.model_pth_var.set(p)

    def pick_config_json(self):
        p = filedialog.askopenfilename(filetypes=[("Config JSON", "*.json")])
        if p:
            self.config_json_var.set(p)

    def load_finetuned_model(self):
        model_pth = self.model_pth_var.get().strip()
        config_json = self.config_json_var.get().strip()
        if not (model_pth and config_json):
            self.popup_error("Error", "Please select both model.pth and config.json.")
            return

        def worker():
            global tts_model
            try:
                self.set_status("Loading fine-tuned model...", "orange")
                tts_model = TTS(model_path=model_pth, config_path=config_json, gpu=USE_GPU)
                self.custom_model = (model_pth, config_json)
                self.builtin_speakers = get_builtin_speakers(tts_model)
                info = [
                    f"Loaded fine-tuned model ✅",
                    f"model.pth: {model_pth}",
                    f"config.json: {config_json}",
                    f"Speakers in model: {self.builtin_speakers or '(none listed)'}"
                ]
                self.model_info.config(text="\n".join(info))
                self.set_status("Fine-tuned model ready ✅", "green")
            except Exception as e:
                log_error("Load fine-tuned model failed", e)
                self.set_status("Failed ❌", "red")
                self.popup_error("Load failed", f"{e}\n\nDetails logged to: {ERROR_LOG}")

        threading.Thread(target=worker, daemon=True).start()

    def switch_to_base(self):
        def worker():
            global tts_model
            try:
                self.set_status("Switching to base XTTS...", "orange")
                tts_model = load_xtts_default()
                self.custom_model = None
                self.builtin_speakers = get_builtin_speakers(tts_model)
                self.model_info.config(text="Switched to base XTTS v2.")
                self.set_status("Base model ready ✅", "green")
            except Exception as e:
                log_error("Switch to base model failed", e)
                self.set_status("Failed ❌", "red")
                self.popup_error("Switch failed", f"{e}\n\nDetails logged to: {ERROR_LOG}")

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoicooApp(root)
    root.mainloop()
