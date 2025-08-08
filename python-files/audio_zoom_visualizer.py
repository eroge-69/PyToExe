import os
import sys
import threading
import queue as thread_queue
import time
import math
import subprocess
from dataclasses import dataclass
from typing import Tuple, Optional, List

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf
import imageio_ffmpeg

# Tkinter GUI (no paid licenses required)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


@dataclass
class RenderConfig:
    audio_path: str
    image_path: str
    output_path: str
    width: int
    height: int
    fps: int
    zoom_strength: float  # e.g., 0.03 subtle
    smoothing_ms: int     # e.g., 250
    crf: int              # lower is higher quality
    preset: str           # ffmpeg preset, e.g., veryfast
    threads: Optional[int]
    resample_quality: str # 'fast' | 'quality'
    band_name: str
    song_name: str
    show_overlay: bool


class GracefulKiller:
    def __init__(self):
        self._stop = False

    def stop(self):
        self._stop = True

    def should_stop(self) -> bool:
        return self._stop


def get_ffmpeg_path() -> str:
    # Use imageio-ffmpeg to ensure a working ffmpeg binary is available
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode_audio_ffmpeg_mono_f32(audio_path: str, target_sr: int = 44100) -> Tuple[np.ndarray, int]:
    """Decode any audio via FFmpeg to mono float32 PCM. Returns samples and sample rate."""
    ffmpeg_path = get_ffmpeg_path()
    cmd = [
        ffmpeg_path,
        "-v", "error",
        "-i", audio_path,
        "-f", "f32le",
        "-ac", "1",
        "-ar", str(target_sr),
        "-vn",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg decode failed: {proc.stderr.decode(errors='ignore')[:300]}"
        )
    raw = proc.stdout
    data = np.frombuffer(raw, dtype=np.float32)
    return data, target_sr


def load_audio_mono(audio_path: str) -> Tuple[np.ndarray, int]:
    # First try soundfile (good for WAV/FLAC/OGG)
    try:
        data, sr = sf.read(audio_path, always_2d=True)
        mono = data.mean(axis=1).astype(np.float32)
        return mono, sr
    except Exception:
        # Fall back to FFmpeg for formats like MP3/M4A/AAC
        mono, sr = decode_audio_ffmpeg_mono_f32(audio_path, target_sr=44100)
        return mono.astype(np.float32, copy=False), sr


def compute_rms_envelope(
    mono: np.ndarray,
    sr: int,
    fps: int,
    smoothing_ms: int,
    percentile_clip: float = 99.0,
) -> np.ndarray:
    """Compute per-frame loudness envelope (RMS), smoothed and normalized to [0,1]."""
    samples_per_frame = max(1, int(round(sr / fps)))
    total_frames = math.ceil(len(mono) / samples_per_frame)

    # Compute frame RMS (block-wise)
    rms = np.empty(total_frames, dtype=np.float32)
    for i in range(total_frames):
        start = i * samples_per_frame
        end = min(len(mono), start + samples_per_frame)
        block = mono[start:end]
        if block.size == 0:
            rms[i] = 0.0
        else:
            # Add a tiny epsilon to avoid sqrt(0) instability
            rms[i] = float(np.sqrt(np.mean(block * block) + 1e-12))

    # Exponential moving average smoothing
    dt = 1.0 / fps
    tau = max(1e-3, smoothing_ms / 1000.0)
    alpha = dt / (tau + dt)
    smooth = np.empty_like(rms)
    acc = 0.0
    for i, v in enumerate(rms):
        acc = (1.0 - alpha) * acc + alpha * v
        smooth[i] = acc

    # Normalize using high percentile to avoid spikes dominating
    scale = np.percentile(smooth, percentile_clip)
    if scale <= 1e-8:
        norm = np.zeros_like(smooth)
    else:
        norm = np.clip(smooth / float(scale), 0.0, 1.0)

    return norm


def fit_cover_to_canvas(img: Image.Image, canvas_size: Tuple[int, int]) -> Image.Image:
    """Scale and center-crop the cover to exactly fill the canvas without bars."""
    cw, ch = canvas_size
    iw, ih = img.size
    if iw == 0 or ih == 0:
        raise ValueError("Invalid image dimensions")

    # Scale to cover
    scale = max(cw / iw, ch / ih)
    new_w = max(1, int(math.ceil(iw * scale)))
    new_h = max(1, int(math.ceil(ih * scale)))
    base = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - cw) // 2
    top = (new_h - ch) // 2
    return base.crop((left, top, left + cw, top + ch))


def find_modern_font() -> Optional[str]:
    """Try to find a modern system font path on Windows. Return None if not found."""
    candidates = [
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeui.ttf"),  # Segoe UI
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeuib.ttf"),  # Segoe UI Bold
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "arial.ttf"),     # Arial as fallback
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def build_text_overlay(text: str, canvas_size: Tuple[int, int]) -> Optional[Image.Image]:
    if not text:
        return None
    cw, ch = canvas_size
    if cw <= 0 or ch <= 0:
        return None

    overlay = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Font sizing ~4.5% of height
    font_size = max(14, int(round(ch * 0.045)))
    font_path = find_modern_font()
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    margin = max(12, int(round(ch * 0.022)))
    # Measure and position at bottom-right
    try:
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = draw.textlength(text, font=font), font_size

    x = cw - margin - tw
    y = ch - margin - th
    x = max(0, x)
    y = max(0, y)

    # Slightly translucent white with soft black stroke
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 230),
              stroke_width=2, stroke_fill=(0, 0, 0, 150))
    return overlay


def render_video(config: RenderConfig, progress_cb, log_cb, killer: GracefulKiller) -> Optional[str]:
    start_time = time.time()
    try:
        ffmpeg_path = get_ffmpeg_path()
    except Exception as e:
        log_cb(f"Failed to locate FFmpeg: {e}")
        return "Failed to locate FFmpeg"

    # Load inputs
    try:
        mono, sr = load_audio_mono(config.audio_path)
    except Exception as e:
        return f"Failed to read audio: {e}"

    try:
        img = Image.open(config.image_path).convert("RGB")
    except Exception as e:
        return f"Failed to open image: {e}"

    # Prepare base canvas and pre-fit to output aspect
    canvas_size = (config.width, config.height)
    base = fit_cover_to_canvas(img, canvas_size)

    # Prepare text overlay if requested
    overlay_text = None
    if config.show_overlay:
        text_parts = []
        if config.song_name:
            text_parts.append(config.song_name)
        if config.band_name:
            if text_parts:
                text_parts.append("—")
            text_parts.append(config.band_name)
        overlay_text = " ".join(text_parts).strip()
    overlay_img = build_text_overlay(overlay_text, canvas_size) if overlay_text else None

    # Compute envelope
    env = compute_rms_envelope(mono, sr, config.fps, config.smoothing_ms)
    num_frames = len(env)

    # Limit frames to audio duration exactly
    duration_s = len(mono) / float(sr)
    target_frames = int(math.ceil(duration_s * config.fps))
    num_frames = min(num_frames, target_frames)
    env = env[:num_frames]

    # FFmpeg writer (rawvideo pipe)
    ff_cmd = [
        ffmpeg_path,
        "-hide_banner",
        "-nostats",
        "-loglevel", "error",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{config.width}x{config.height}",
        "-r", str(config.fps),
        "-i", "-",
        "-i", config.audio_path,
        "-shortest",
        "-c:v", "libx264",
        "-preset", config.preset,
        "-crf", str(config.crf),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ]
    if config.threads and config.threads > 0:
        ff_cmd += ["-threads", str(config.threads)]
    ff_cmd += [config.output_path]

    try:
        proc = subprocess.Popen(
            ff_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,  # capture for error only
            bufsize=10**7,
        )
    except Exception as e:
        return f"Failed to start FFmpeg: {e}"

    # Choose resample filter
    resample_filter = Image.BICUBIC if config.resample_quality == "quality" else Image.BILINEAR

    last_update = 0
    try:
        for idx in range(num_frames):
            if killer.should_stop():
                try:
                    if proc.stdin:
                        proc.stdin.close()
                except Exception:
                    pass
                try:
                    proc.kill()
                except Exception:
                    pass
                return "Canceled by user"

            # Subtle zoom factor
            zoom = 1.0 + config.zoom_strength * float(env[idx])
            # Resize base accordingly
            scaled_w = max(config.width, int(round(config.width * zoom)))
            scaled_h = max(config.height, int(round(config.height * zoom)))

            if scaled_w == base.width and scaled_h == base.height:
                frame = base
            else:
                frame = base.resize((scaled_w, scaled_h), resample=resample_filter)

            # Center crop to canvas
            left = (frame.width - config.width) // 2
            top = (frame.height - config.height) // 2
            frame = frame.crop((left, top, left + config.width, top + config.height))

            # Apply text overlay
            if overlay_img is not None:
                frame = frame.convert("RGBA")
                frame.alpha_composite(overlay_img)
                frame = frame.convert("RGB")

            # Write raw RGB to ffmpeg
            assert proc.stdin is not None
            proc.stdin.write(frame.tobytes())

            # Progress callback (limit UI thrash)
            now = time.time()
            if now - last_update > 0.05 or idx == num_frames - 1:
                elapsed = now - start_time
                done_ratio = (idx + 1) / num_frames
                if done_ratio > 0:
                    total_est = elapsed / done_ratio
                    eta = max(0.0, total_est - elapsed)
                else:
                    eta = 0.0
                progress_cb(idx + 1, num_frames, elapsed, eta)
                last_update = now

        # Close stdin to signal end of stream
        assert proc.stdin is not None
        proc.stdin.close()

        # Drain output (avoid deadlock)
        try:
            _, stderr = proc.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, stderr = proc.communicate()
            return f"FFmpeg timed out. stderr: {stderr.decode(errors='ignore')[:500]}"

        if proc.returncode != 0:
            return f"FFmpeg failed with code {proc.returncode}. stderr: {stderr.decode(errors='ignore')[:500]}"

    except Exception as e:
        try:
            proc.kill()
        except Exception:
            pass
        return f"Render error: {e}"

    return None


def human_time(seconds: float) -> str:
    seconds = int(max(0, round(seconds)))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Subtle Cover Zoom Visualizer")
        self.q: thread_queue.Queue = thread_queue.Queue()
        self.render_thread: Optional[threading.Thread] = None
        self.killer = GracefulKiller()

        # Batch state
        self.batch_audio_files: List[str] = []

        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}
        frm = ttk.Frame(self.root)
        frm.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Row 0: Audio (single) + Batch add
        ttk.Label(frm, text="Audio file (acapella):").grid(row=0, column=0, sticky="w", **pad)
        self.audio_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.audio_var, width=60).grid(row=0, column=1, sticky="ew", **pad)
        small_btns = ttk.Frame(frm)
        small_btns.grid(row=0, column=2, sticky="w", **pad)
        ttk.Button(small_btns, text="Browse", command=self._browse_audio).grid(row=0, column=0, padx=2)
        ttk.Button(small_btns, text="Add multiple…", command=self._browse_audio_multiple).grid(row=0, column=1, padx=2)

        # Row 1: Image
        ttk.Label(frm, text="Cover image:").grid(row=1, column=0, sticky="w", **pad)
        self.image_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.image_var, width=60).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self._browse_image).grid(row=1, column=2, **pad)

        # Row 2: Output (single) + Output folder (batch)
        ttk.Label(frm, text="Output file:").grid(row=2, column=0, sticky="w", **pad)
        self.output_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.output_var, width=60).grid(row=2, column=1, sticky="ew", **pad)
        out_btns = ttk.Frame(frm)
        out_btns.grid(row=2, column=2, sticky="w", **pad)
        ttk.Button(out_btns, text="Save As…", command=self._save_output).grid(row=0, column=0, padx=2)

        ttk.Label(frm, text="Output folder (batch):").grid(row=3, column=0, sticky="w", **pad)
        self.out_dir_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.out_dir_var, width=60).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Choose Folder", command=self._choose_out_dir).grid(row=3, column=2, **pad)

        # Row 4: Band/Song overlay
        ttk.Label(frm, text="Band name:").grid(row=4, column=0, sticky="w", **pad)
        self.band_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.band_var, width=30).grid(row=4, column=1, sticky="w", **pad)
        ttk.Label(frm, text="Song name:").grid(row=4, column=1, sticky="e", padx=(250, 2))
        self.song_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.song_var, width=30).grid(row=4, column=1, sticky="e", padx=(0, 2))
        self.show_overlay_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Show overlay", variable=self.show_overlay_var).grid(row=4, column=2, sticky="w", **pad)

        # Row 5: Resolution + FPS
        ttk.Label(frm, text="Resolution:").grid(row=5, column=0, sticky="w", **pad)
        self.res_combo = ttk.Combobox(frm, state="readonly",
                                      values=["1080p (1920x1080)", "720p (1280x720)", "Square (1080x1080)", "Square (720x720)", "Custom"],
                                      width=24)
        self.res_combo.set("720p (1280x720)")
        self.res_combo.grid(row=5, column=1, sticky="w", **pad)
        self.res_combo.bind("<<ComboboxSelected>>", self._on_res_change)

        ttk.Label(frm, text="W:").grid(row=5, column=1, sticky="e", padx=(220, 2))
        self.w_var = tk.StringVar(value="1280")
        ttk.Entry(frm, textvariable=self.w_var, width=7).grid(row=5, column=1, sticky="e", padx=(250, 2))
        ttk.Label(frm, text="H:").grid(row=5, column=1, sticky="e", padx=(305, 2))
        self.h_var = tk.StringVar(value="720")
        ttk.Entry(frm, textvariable=self.h_var, width=7).grid(row=5, column=1, sticky="e", padx=(330, 2))
        ttk.Label(frm, text="FPS:").grid(row=5, column=1, sticky="e", padx=(385, 2))
        self.fps_var = tk.StringVar(value="25")
        self.fps_box = ttk.Spinbox(frm, from_=1, to=60, textvariable=self.fps_var, width=4)
        self.fps_box.grid(row=5, column=1, sticky="e", padx=(420, 2))

        # Row 6: Zoom + Smoothing
        ttk.Label(frm, text="Zoom strength:").grid(row=6, column=0, sticky="w", **pad)
        self.zoom_var = tk.DoubleVar(value=30.0)  # 0..100 -> 0..0.1
        self.zoom_scale = ttk.Scale(frm, from_=0, to=100, orient="horizontal", variable=self.zoom_var)
        self.zoom_scale.grid(row=6, column=1, sticky="ew", **pad)
        self.zoom_label = ttk.Label(frm, text="0.030")
        self.zoom_label.grid(row=6, column=2, sticky="w", **pad)
        self.zoom_scale.bind("<Motion>", lambda e: self._update_zoom_label())
        self.zoom_scale.bind("<ButtonRelease-1>", lambda e: self._update_zoom_label())

        ttk.Label(frm, text="Smoothing (ms):").grid(row=7, column=0, sticky="w", **pad)
        self.smooth_var = tk.IntVar(value=250)
        self.smooth_scale = ttk.Scale(frm, from_=50, to=1000, orient="horizontal")
        self.smooth_scale.configure(value=self.smooth_var.get())
        self.smooth_scale.configure(command=lambda v: self.smooth_var.set(int(float(v))))
        self.smooth_scale.grid(row=7, column=1, sticky="ew", **pad)
        self.smooth_label = ttk.Label(frm, text="250")
        self.smooth_label.grid(row=7, column=2, sticky="w", **pad)
        self.smooth_scale.bind("<Motion>", lambda e: self._update_smooth_label())
        self.smooth_scale.bind("<ButtonRelease-1>", lambda e: self._update_smooth_label())

        # Row 8: Quality/preset/crf/threads
        ttk.Label(frm, text="Speed/Quality:").grid(row=8, column=0, sticky="w", **pad)
        self.resample_var = tk.StringVar(value="fast")
        self.resample_combo = ttk.Combobox(frm, textvariable=self.resample_var, state="readonly", values=["fast", "quality"], width=10)
        self.resample_combo.grid(row=8, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Preset:").grid(row=8, column=1, sticky="e", padx=(220, 2))
        self.preset_var = tk.StringVar(value="veryfast")
        self.preset_combo = ttk.Combobox(frm, textvariable=self.preset_var, state="readonly",
                                         values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"], width=10)
        self.preset_combo.grid(row=8, column=1, sticky="e", padx=(260, 2))

        ttk.Label(frm, text="CRF:").grid(row=8, column=1, sticky="e", padx=(355, 2))
        self.crf_var = tk.IntVar(value=20)
        self.crf_box = ttk.Spinbox(frm, from_=16, to=28, textvariable=self.crf_var, width=4)
        self.crf_box.grid(row=8, column=1, sticky="e", padx=(390, 2))

        ttk.Label(frm, text="Threads:").grid(row=8, column=1, sticky="e", padx=(435, 2))
        self.threads_var = tk.IntVar(value=0)
        self.threads_box = ttk.Spinbox(frm, from_=0, to=32, textvariable=self.threads_var, width=4)
        self.threads_box.grid(row=8, column=1, sticky="e", padx=(480, 2))

        # Row 9: Batch list
        ttk.Label(frm, text="Batch files:").grid(row=9, column=0, sticky="nw", **pad)
        self.batch_list = tk.Listbox(frm, height=4)
        self.batch_list.grid(row=9, column=1, sticky="nsew", **pad)
        list_btns = ttk.Frame(frm)
        list_btns.grid(row=9, column=2, sticky="nw", **pad)
        ttk.Button(list_btns, text="Remove", command=self._remove_selected_batch).grid(row=0, column=0, pady=2)
        ttk.Button(list_btns, text="Clear", command=self._clear_batch).grid(row=1, column=0, pady=2)
        frm.rowconfigure(9, weight=1)
        frm.columnconfigure(1, weight=1)

        # Row 10: Progress
        self.progress = ttk.Progressbar(frm, orient="horizontal", maximum=1000, length=500)
        self.progress.grid(row=10, column=0, columnspan=2, sticky="ew", **pad)
        self.pct_label = ttk.Label(frm, text="0%")
        self.pct_label.grid(row=10, column=2, sticky="w", **pad)
        self.eta_label = ttk.Label(frm, text="ETA: -- | Elapsed: --")
        self.eta_label.grid(row=11, column=0, columnspan=3, sticky="w", **pad)

        # Row 12: Log
        self.log = tk.Text(frm, height=10, width=100, state="disabled")
        self.log.grid(row=12, column=0, columnspan=3, sticky="nsew", **pad)
        frm.rowconfigure(12, weight=1)

        # Row 13: Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=13, column=0, columnspan=3, sticky="e", **pad)
        self.render_btn = ttk.Button(btn_frame, text="Render", command=self._on_render)
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel, state="disabled")
        self.exit_btn = ttk.Button(btn_frame, text="Exit", command=self.root.destroy)
        self.render_btn.grid(row=0, column=0, padx=4)
        self.cancel_btn.grid(row=0, column=1, padx=4)
        self.exit_btn.grid(row=0, column=2, padx=4)

        self._update_zoom_label()
        self._update_smooth_label()

    def _choose_out_dir(self):
        path = filedialog.askdirectory(title="Choose output folder")
        if path:
            self.out_dir_var.set(path)

    def _update_zoom_label(self):
        self.zoom_label.config(text=f"{self.zoom_var.get()/1000:.3f}")

    def _update_smooth_label(self):
        self.smooth_label.config(text=str(self.smooth_var.get()))

    def _on_res_change(self, _evt=None):
        label = self.res_combo.get()
        res_map = {
            "1080p (1920x1080)": (1920, 1080),
            "720p (1280x720)": (1280, 720),
            "Square (1080x1080)": (1080, 1080),
            "Square (720x720)": (720, 720),
            "Custom": (0, 0),
        }
        w, h = res_map.get(label, (1280, 720))
        if w > 0 and h > 0:
            self.w_var.set(str(w))
            self.h_var.set(str(h))

    def _browse_audio(self):
        path = filedialog.askopenfilename(title="Select audio", filetypes=[("Audio", "*.wav;*.mp3;*.flac;*.m4a;*.aac;*.ogg")])
        if path:
            self.audio_var.set(path)
            if not self.output_var.get():
                self.output_var.set(self._infer_output_path(path))

    def _browse_audio_multiple(self):
        files = filedialog.askopenfilenames(title="Select multiple audio files", filetypes=[("Audio", "*.wav;*.mp3;*.flac;*.m4a;*.aac;*.ogg")])
        if files:
            added = 0
            for f in files:
                f = str(f)
                if f not in self.batch_audio_files:
                    self.batch_audio_files.append(f)
                    self.batch_list.insert("end", f)
                    added += 1
            if added:
                self._log(f"Added {added} file(s) to batch queue.")

    def _remove_selected_batch(self):
        sel = list(self.batch_list.curselection())
        sel.reverse()
        for idx in sel:
            path = self.batch_list.get(idx)
            self.batch_list.delete(idx)
            try:
                self.batch_audio_files.remove(path)
            except ValueError:
                pass
        if sel:
            self._log("Removed selected file(s) from batch queue.")

    def _clear_batch(self):
        self.batch_list.delete(0, "end")
        self.batch_audio_files.clear()
        self._log("Cleared batch queue.")

    def _browse_image(self):
        path = filedialog.askopenfilename(title="Select cover image", filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp")])
        if path:
            self.image_var.set(path)

    def _save_output(self):
        path = filedialog.asksaveasfilename(title="Save output", defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if path:
            self.output_var.set(path)

    def _log(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_inputs_state(self, disabled: bool):
        state = "disabled" if disabled else "normal"
        widgets = [
            self.res_combo, self.fps_box, self.preset_combo, self.crf_box, self.threads_box,
            self.resample_combo, self.zoom_scale, self.smooth_scale, self.render_btn,
            self.batch_list,
        ]
        for w in widgets:
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def _infer_output_path(self, audio_path: str) -> str:
        base, _ = os.path.splitext(audio_path)
        return base + "_visualized.mp4"

    def _infer_output_file_in_dir(self, audio_path: str, out_dir: str) -> str:
        name = Path(audio_path).stem + "_visualized.mp4"
        return str(Path(out_dir) / name)

    def _parse_resolution(self) -> Tuple[int, int]:
        try:
            w = int(self.w_var.get())
            h = int(self.h_var.get())
            return max(8, w), max(8, h)
        except Exception:
            return 1280, 720

    def _on_render(self):
        audio = self.audio_var.get().strip()
        image = self.image_var.get().strip()
        output = self.output_var.get().strip()
        out_dir = self.out_dir_var.get().strip()

        if not os.path.isfile(image):
            messagebox.showerror("Error", "Please choose a valid image file.")
            return

        w, h = self._parse_resolution()
        try:
            fps = int(self.fps_var.get())
        except Exception:
            fps = 25
        zoom = float(self.zoom_var.get()) / 1000.0
        smoothing = int(self.smooth_var.get())
        preset = self.preset_var.get()
        crf = int(self.crf_var.get())
        threads = int(self.threads_var.get())
        threads = None if threads == 0 else threads
        resample_quality = self.resample_var.get()

        # Build jobs: either single or batch
        jobs: List[Tuple[str, str]] = []  # (audio_path, output_path)
        if self.batch_audio_files:
            if not out_dir:
                messagebox.showerror("Error", "For batch rendering, choose an output folder.")
                return
            if not os.path.isdir(out_dir):
                try:
                    os.makedirs(out_dir, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot create output folder: {e}")
                    return
            for a in self.batch_audio_files:
                if os.path.isfile(a):
                    jobs.append((a, self._infer_output_file_in_dir(a, out_dir)))
            if not jobs:
                messagebox.showerror("Error", "Batch list is empty or files missing.")
                return
        else:
            if not os.path.isfile(audio):
                messagebox.showerror("Error", "Please choose a valid audio file (or add multiple).")
                return
            if not output:
                output = self._infer_output_path(audio)
                self.output_var.set(output)
            jobs.append((audio, output))

        base_cfg = dict(
            image_path=image,
            width=w,
            height=h,
            fps=fps,
            zoom_strength=zoom,
            smoothing_ms=smoothing,
            crf=crf,
            preset=preset,
            threads=threads,
            resample_quality=resample_quality,
            band_name=self.band_var.get().strip(),
            song_name=self.song_var.get().strip(),
            show_overlay=self.show_overlay_var.get(),
        )

        self._set_inputs_state(True)
        self.cancel_btn.configure(state="normal")
        self.killer = GracefulKiller()

        def progress_cb(done: int, total: int, elapsed: float, eta: float):
            self.q.put(("progress", (done, total, elapsed, eta)))

        def log_cb(msg: str):
            self.q.put(("log", msg))

        def work():
            for index, (a_path, o_path) in enumerate(jobs, start=1):
                if self.killer.should_stop():
                    break
                # Auto-fill song name from filename if empty per job
                per_song = self.band_var.get().strip()
                per_title = self.song_var.get().strip() or Path(a_path).stem
                cfg = RenderConfig(audio_path=a_path, output_path=o_path, **base_cfg,
                                   band_name=per_song, song_name=per_title)
                self.q.put(("log", f"[Job {index}/{len(jobs)}] Rendering: {Path(a_path).name}"))
                err = render_video(cfg, progress_cb, log_cb, self.killer)
                if err:
                    self.q.put(("log", f"ERROR: {err}"))
                    if self.killer.should_stop():
                        break
                else:
                    self.q.put(("log", f"Finished: {o_path}"))
            self.q.put(("done", None))

        self.render_thread = threading.Thread(target=work, daemon=True)
        self.render_thread.start()
        if len(jobs) > 1:
            self._log(f"Started batch render with {len(jobs)} file(s)...")
        else:
            self._log("Starting render...")

    def _on_cancel(self):
        if self.render_thread and self.render_thread.is_alive():
            self.killer.stop()
            self._log("Canceling... This may take a few seconds.")

    def _poll_queue(self):
        try:
            while True:
                item = self.q.get_nowait()
                kind = item[0]
                if kind == "progress":
                    done, total, elapsed, eta = item[1]
                    pct = int(done * 1000 / max(1, total))
                    self.progress['value'] = pct
                    self.pct_label.config(text=f"{pct//10}%")
                    self.eta_label.config(text=f"ETA: {human_time(eta)} | Elapsed: {human_time(elapsed)}")
                elif kind == "log":
                    self._log(item[1])
                elif kind == "done":
                    err = item[1]
                    self.cancel_btn.configure(state="disabled")
                    self._set_inputs_state(False)
                    if err:
                        self._log(f"ERROR: {err}")
                    else:
                        self._log(f"Render completed successfully. Saved to: {self.output_var.get()}")
        except thread_queue.Empty:
            pass
        self.root.after(50, self._poll_queue)


def gui_main():
    root = tk.Tk()
    # Improve default padding/spacing
    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass
    App(root)
    root.geometry("1020x560")
    root.minsize(820, 480)
    root.mainloop()


if __name__ == "__main__":
    try:
        gui_main()
    except Exception as e:
        print(f"Fatal error: {e}") 