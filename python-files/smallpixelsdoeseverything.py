#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Side-by-Side Video Comparison Tool + Post-Export Zoom Annotator (NO AUDIO)
===========================================================================

What’s new in this build
------------------------
• **No audio always**: the exporter never maps or encodes audio.
• **Post-export zoom step** (your extra tool integrated): after exporting the side-by-side video,
  the app can immediately run an interactive, pause-on-zoom annotator that lets you select
  mirrored ROIs and renders a new "_zoomedversion" file. This integrates the logic you pasted
  (rewritten to run inside this app, without Tkinter).

Install prerequisites (ensure `ffmpeg` is on PATH):
    pip install PyQt5 ffmpeg-python opencv-python pillow imagehash scikit-image numpy

IMPORTANT notes kept from earlier
---------------------------------
Live video playback & interactive linked scrubbing
The preview is a static composite frame (fast, robust). A fully synced dual playback preview with timelines, cut markers, and “difference heatmap” overlays is doable (PyQtGraph/Qt Multimedia), but it’s non-trivial across OS/codec combinations. We can add it next if you want.

Full scene-locked export (piecewise time map in FFmpeg graph)
The code enforces global offset and builds a time map, but the final export currently applies global alignment (trim/setpts) rather than segment-wise time warps / dup/drops around matched cuts. That’s because encoding piecewise alignment reliably in a single FFmpeg graph is complex (requires segment splitting and concat). If you want, I can implement:

Per-segment trim/setpts/tpad and concat to force cuts to coincide;

Or gentle setpts time-warps with guardrails (≤0.2%) per segment.

Font configuration for drawtext
I try a set of common font files. On systems without those fonts, FFmpeg might use fontconfig to find a fallback. If drawtext fails, set fontfile explicitly (e.g., DejaVuSans path). We can also expose a “Pick font” option in the UI.

Edge cases with exotic codecs
OpenCV/ffmpeg frame probing for previews should be fine for most formats. For rare codecs/containers (e.g., 10-bit ProRes RAW), adding a dedicated FFmpeg pipe decoder for previews could help.

Variable frame rate (VFR) & super-long clips
The analysis step uses normalized low-res MP4s for speed, which also makes VFR quirks negligible. For multi-hour content, we could add a setting to limit the analysis duration or use sparser sampling.

Advanced compression options
The current mapping targets H.264 in .mp4 and FFV1/RAW for lossless cases. If you want HEVC (x265), ProRes, or AV1, I can add presets tied to the slider levels.

Centerline style in UI
In preview/export, centerline is 2px white. If you want to expose thickness/color in the UI, we can add simple controls.
"""

import os
import sys
import json
import tempfile
import subprocess
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

import numpy as np
import cv2
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QSlider, QProgressBar, QGroupBox, QFormLayout,
    QMessageBox, QCheckBox, QComboBox
)

import ffmpeg

# -----------------------------
# Data models
# -----------------------------

@dataclass
class VideoMeta:
    path: str
    width: int
    height: int
    fps: float
    duration: float
    rotation: int  # 0, 90, 180, 270
    has_video: bool = True


@dataclass
class AlignmentResult:
    coarse_offset_sec: float
    refined_offset_sec: float
    confidence: float  # 0..1
    ssim_peak: float   # peak SSIM


@dataclass
class SceneCutData:
    cut_times: List[float]


@dataclass
class TimeMapSegment:
    start: float
    end: float
    slope: float
    shift: float


@dataclass
class TimeMap:
    segments: List[TimeMapSegment]


# -----------------------------
# FFprobe helpers
# -----------------------------

def run_ffprobe(path: str) -> Dict:
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-print_format", "json", path],
            capture_output=True, text=True, check=True
        )
        return json.loads(res.stdout)
    except Exception as e:
        raise RuntimeError(f"ffprobe failed on {path}: {e}")


def extract_meta(path: str) -> VideoMeta:
    info = run_ffprobe(path)
    vstreams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not vstreams:
        raise ValueError(f"No video stream in: {path}")
    v = vstreams[0]
    width = int(v.get("width"))
    height = int(v.get("height"))

    def parse_rate(s: str) -> float:
        try:
            a, b = s.split('/')
            a = float(a); b = float(b)
            return a / b if b != 0 else 0.0
        except Exception:
            return 0.0

    fps = parse_rate(v.get("r_frame_rate", "0/0")) or parse_rate(v.get("avg_frame_rate", "0/0"))
    if fps <= 0:
        fps = 30.0

    duration = float(info.get("format", {}).get("duration", 0.0))

    rot = 0
    tags = v.get("tags", {}) or {}
    if "rotate" in tags:
        try:
            rot = int(tags["rotate"]) % 360
        except Exception:
            rot = 0

    return VideoMeta(path=path, width=width, height=height, fps=fps, duration=duration, rotation=rot)


# -----------------------------
# Helpers
# -----------------------------

def ensure_tempdir() -> str:
    d = os.path.join(tempfile.gettempdir(), "sbs_compare_tool")
    os.makedirs(d, exist_ok=True)
    return d


def downscale_video_to_tmp(path: str, fps: float, width: int = 320, gray: bool = True) -> str:
    tmpdir = ensure_tempdir()
    out = os.path.join(tmpdir, f"analysis_{os.path.basename(path)}_{width}px_{'gray' if gray else 'color'}_{fps:.2f}fps.mp4")
    if os.path.exists(out):
        return out
    vf = [f"scale=w={width}:h=-2:flags=bicubic", "pad=ceil(iw/2)*2:ceil(ih/2)*2"]
    if gray:
        vf.append("format=gray")
    vf_str = ",".join(vf)
    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-vf", vf_str + f",fps={fps}",
        "-an", "-movflags", "+faststart",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        out,
    ]
    subprocess.run(cmd, check=True)
    return out


def sample_frames_with_ts(path: str, as_gray=True) -> Tuple[List[np.ndarray], List[float], float, Tuple[int, int]]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    if fps <= 0:
        fps = 30.0
    frames, ts = [], []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        pts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if as_gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(frame)
        ts.append(pts)
    w = frames[0].shape[1] if frames else 0
    h = frames[0].shape[0] if frames else 0
    cap.release()
    return frames, ts, fps, (w, h)


def image_to_phash(img: np.ndarray) -> int:
    pil = Image.fromarray(img)
    h = imagehash.phash(pil)
    bits = 0
    arr = np.array(h.hash, dtype=np.uint8).flatten()
    for b in arr:
        bits = (bits << 1) | int(b)
    return bits


def hamming_distance_int(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def coarse_align_by_phash(seqA: List[int], seqB: List[int], tsA: List[float], tsB: List[float], max_search_sec: float = 60.0) -> float:
    if not seqA or not seqB:
        return 0.0
    dtA = (tsA[1] - tsA[0]) if len(tsA) > 1 else 0.5
    dtB = (tsB[1] - tsB[0]) if len(tsB) > 1 else 0.5
    max_shift_frames = int(max_search_sec / max(dtA, dtB))
    best_shift, best_score = 0, float('inf')
    for shift in range(-max_shift_frames, max_shift_frames + 1):
        total = 0; count = 0
        for i in range(len(seqA)):
            j = i + shift
            if 0 <= j < len(seqB):
                total += hamming_distance_int(seqA[i], seqB[j])
                count += 1
        if count > 5:
            avg = total / count
            if avg < best_score:
                best_score, best_shift = avg, shift
    return best_shift * dtB


def refine_align_ssim(framesA: List[np.ndarray], tsA: List[float],
                      framesB: List[np.ndarray], tsB: List[float],
                      coarse_offset: float, window_sec: float = 2.0, step: float = 0.05) -> Tuple[float, float]:
    if not framesA or not framesB:
        return coarse_offset, 0.0
    tmin, tmax = coarse_offset - window_sec, coarse_offset + window_sec
    best_s, best_off = -1.0, coarse_offset

    def find_idx(ts_list, t):
        return int(np.argmin(np.abs(np.array(ts_list) - t)))

    A_times = np.array(tsA)
    if len(A_times) == 0:
        return coarse_offset, 0.0
    probe_mask = (A_times >= 0.5) & (A_times <= (A_times[-1] - 0.5))
    probe_idx = np.where(probe_mask)[0]
    if len(probe_idx) > 200:
        probe_idx = probe_idx[::max(1, len(probe_idx)//200)]

    for off in np.arange(tmin, tmax + 1e-9, step):
        s_vals = []
        for i in probe_idx:
            tA = A_times[i]
            tB = tA + off
            j = find_idx(tsB, tB)
            if 0 <= j < len(framesB):
                Aimg = cv2.resize(framesA[i], (192, 108), interpolation=cv2.INTER_AREA)
                Bimg = cv2.resize(framesB[j], (192, 108), interpolation=cv2.INTER_AREA)
                s_val = ssim(Aimg, Bimg)
                s_vals.append(s_val)
        if s_vals:
            avg = float(np.mean(s_vals))
            if avg > best_s:
                best_s, best_off = avg, float(off)
    return best_off, max(0.0, best_s)


def detect_scene_cuts(frames: List[np.ndarray], ts: List[float]) -> SceneCutData:
    if len(frames) < 3:
        return SceneCutData(cut_times=[])
    prev_hist = None
    diffs = []
    for f in frames:
        if len(f.shape) == 2:
            f3 = cv2.cvtColor(f, cv2.COLOR_GRAY2BGR)
        else:
            f3 = f
        hsv = cv2.cvtColor(f3, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        hist = cv2.normalize(hist, None).flatten()
        if prev_hist is None:
            diffs.append(0.0)
        else:
            inter = np.sum(np.minimum(prev_hist, hist))
            diffs.append(1.0 - float(inter))
        prev_hist = hist
    diffs = np.array(diffs)
    mu, sigma = float(np.mean(diffs)), float(np.std(diffs))
    thr = mu + 2.5 * sigma
    cuts, last_t = [], -999.0
    for i, sc in enumerate(diffs):
        if sc > thr:
            t = ts[i]
            if t - last_t >= 0.5:
                cuts.append(t)
                last_t = t
    return SceneCutData(cut_times=cuts)


def match_cuts_greedy(cutsA: List[float], cutsB: List[float], max_gap: float = 1.0) -> List[Tuple[float, float]]:
    i = j = 0
    pairs = []
    while i < len(cutsA) and j < len(cutsB):
        a, b = cutsA[i], cutsB[j]
        if abs(a - b) <= max_gap:
            pairs.append((a, b)); i += 1; j += 1
        elif a < b:
            i += 1
        else:
            j += 1
    return pairs


def build_time_map(pairs: List[Tuple[float, float]]) -> TimeMap:
    if len(pairs) < 2:
        return TimeMap([TimeMapSegment(0.0, 1e9, 1.0, 0.0)])
    pairs_sorted = sorted(pairs)
    bt = np.array([b for (_, b) in pairs_sorted], dtype=np.float64)
    at = np.array([a for (a, _) in pairs_sorted], dtype=np.float64)
    segments: List[TimeMapSegment] = []
    for k in range(len(bt) - 1):
        b0, b1 = bt[k], bt[k+1]
        a0, a1 = at[k], at[k+1]
        slope = (a1 - a0) / (b1 - b0) if (b1 - b0) > 1e-6 else 1.0
        slope = max(0.998, min(1.002, slope))
        shift = a0 - slope * b0
        segments.append(TimeMapSegment(start=b0, end=b1, slope=float(slope), shift=float(shift)))
    segments.append(TimeMapSegment(start=bt[-1], end=1e9, slope=segments[-1].slope, shift=segments[-1].shift))
    segments.insert(0, TimeMapSegment(start=-1e9, end=bt[0], slope=segments[0].slope, shift=segments[0].shift))
    return TimeMap(segments)


def estimate_bitrate_kbps(width: int, height: int, fps: float, level: int, complexity: float = 1.0) -> float:
    pps = width * height * fps
    level_curve = {1: 12.0, 2: 8.0, 3: 6.0, 4: 4.5, 5: 3.5, 6: 2.7, 7: 2.0, 8: 1.5, 9: 1.1, 10: 0.8}
    k = level_curve.get(int(level), 2.0) * complexity
    kbps = (pps / 1000.0) * (k / (1920 * 1080 * 30)) * 25000
    return max(300.0, kbps)


def human_size(bytes_val: float) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    s = float(bytes_val)
    for u in units:
        if s < 1024.0:
            return f"{s:.2f} {u}"
        s /= 1024.0
    return f"{s:.2f} PB"


def pick_fontfile_candidates() -> List[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    return [p for p in candidates if os.path.isfile(p)]


# -----------------------------
# Alignment worker (threaded)
# -----------------------------

class AlignmentWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object, object)
    error = pyqtSignal(str)

    def __init__(self, pathA: str, pathB: str):
        super().__init__()
        self.pathA = pathA
        self.pathB = pathB

    def run(self):
        try:
            self.progress.emit("Preprocessing videos…")
            a_coarse = downscale_video_to_tmp(self.pathA, fps=2.0, width=320, gray=True)
            b_coarse = downscale_video_to_tmp(self.pathB, fps=2.0, width=320, gray=True)
            a_ref = downscale_video_to_tmp(self.pathA, fps=10.0, width=320, gray=True)
            b_ref = downscale_video_to_tmp(self.pathB, fps=10.0, width=320, gray=True)

            self.progress.emit("Extracting frames (coarse)…")
            A_coarse_frames, A_coarse_ts, _, _ = sample_frames_with_ts(a_coarse, as_gray=True)
            B_coarse_frames, B_coarse_ts, _, _ = sample_frames_with_ts(b_coarse, as_gray=True)

            self.progress.emit("Computing perceptual hashes…")
            A_hash = [image_to_phash(f) for f in A_coarse_frames]
            B_hash = [image_to_phash(f) for f in B_coarse_frames]

            self.progress.emit("Finding coarse offset by pHash correlation…")
            coarse_off = coarse_align_by_phash(A_hash, B_hash, A_coarse_ts, B_coarse_ts, max_search_sec=60.0)

            self.progress.emit("Extracting frames (refine)…")
            A_r_frames, A_r_ts, _, _ = sample_frames_with_ts(a_ref, as_gray=True)
            B_r_frames, B_r_ts, _, _ = sample_frames_with_ts(b_ref, as_gray=True)

            self.progress.emit("Refining offset with SSIM…")
            refined_off, peak_ssim = refine_align_ssim(A_r_frames, A_r_ts, B_r_frames, B_r_ts, coarse_off, window_sec=2.0, step=0.05)

            conf = float(max(0.0, min(1.0, (peak_ssim - 0.3) / (0.95 - 0.3)))) if peak_ssim > 0 else 0.0

            self.progress.emit("Detecting scene cuts…")
            scenesA = detect_scene_cuts(A_coarse_frames, A_coarse_ts)
            scenesB = detect_scene_cuts(B_coarse_frames, B_coarse_ts)

            align = AlignmentResult(coarse_offset_sec=float(coarse_off), refined_offset_sec=float(refined_off), confidence=conf, ssim_peak=float(peak_ssim))
            self.finished.emit(align, scenesA, scenesB)
        except Exception as e:
            self.error.emit(str(e))


# -----------------------------
# Integrated Zoom Annotator (no Tkinter; runs on exported SxS video)
# -----------------------------

class ZoomAnnotator:
    """Interactive pause-on-zoom annotator adapted from your script. No audio.
    Usage: ZoomAnnotator().run_on_video(path_to_exported_sbs_video)
    """

    PADDING = 24
    ANIM_DUR = 1.0
    HOLD_DUR = 5.0
    ZOOM_OUT_MULT = 2.0
    DRAW_BOX_THICK = 2
    MIN_SEL_W = 8
    MIN_SEL_H = 8

    def __init__(self):
        self.paused = False
        self.first_pt = None
        self.selections: List[Dict] = []
        self.current_frame = None
        self.frame_idx = 0
        self.input_path = None
        self.fps = 30.0
        self.w = 0
        self.h = 0

    @staticmethod
    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    def toggle_pause(self):
        self.paused = not self.paused

    @staticmethod
    def ease_in_out(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return t * t * (3 - 2 * t)

    def compute_scale(self, reg_w, reg_h):
        target_w_each = (self.w - 3 * self.PADDING) // 2
        target_h_each = self.h - 2 * self.PADDING
        return min(target_w_each / reg_w, target_h_each / reg_h)

    def render_zoomed_canvas(self, base_frame, sel, t, phase):
        h, w = base_frame.shape[:2]
        half = w // 2
        x1, y1, x2, y2 = sel['x1'], sel['y1'], sel['x2'], sel['y2']
        reg_w, reg_h = (x2 - x1), (y2 - y1)
        scale_final = self.compute_scale(reg_w, reg_h)
        if phase == 'in':
            scale = 1.0 + (scale_final - 1.0) * self.ease_in_out(t)
        elif phase == 'hold':
            scale = scale_final
        else:
            scale = scale_final + (1.0 - scale_final) * self.ease_in_out(t)
        cropL = base_frame[y1:y2, x1:x2]
        cropR = base_frame[y1:y2, half + x1: half + x2]
        new_w = max(1, int(round(reg_w * scale)))
        new_h = max(1, int(round(reg_h * scale)))
        zoomL = cv2.resize(cropL, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        zoomR = cv2.resize(cropR, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        canvas = np.zeros_like(base_frame)
        y_off = (self.h - new_h) // 2
        xL = self.PADDING
        xR = self.PADDING * 2 + new_w
        canvas[y_off:y_off + new_h, xL:xL + new_w] = zoomL
        canvas[y_off:y_off + new_h, xR:xR + new_w] = zoomR
        cv2.rectangle(canvas, (xL, y_off), (xL + new_w, y_off + new_h), (0, 255, 0), self.DRAW_BOX_THICK)
        cv2.rectangle(canvas, (xR, y_off), (xR + new_w, y_off + new_h), (0, 255, 0), self.DRAW_BOX_THICK)
        return canvas

    def on_mouse(self, event, x, y, flags, userdata):
        if not self.paused or event != cv2.EVENT_LBUTTONDOWN:
            return
        if self.current_frame is None:
            return
        h, w = self.current_frame.shape[:2]
        half = w // 2
        if self.first_pt is None:
            self.first_pt = (x, y)
            print(f"[INFO] First corner: {self.first_pt}")
            return
        x1, y1 = self.first_pt
        x2, y2 = x, y
        lx, rx = sorted((x1, x2))
        ty, by = sorted((y1, y2))
        if x1 < half:
            lx = self.clamp(lx, 0, half)
            rx = self.clamp(rx, 0, half)
        else:
            lx = self.clamp(lx - half, 0, half)
            rx = self.clamp(rx - half, 0, half)
        if (rx - lx) < self.MIN_SEL_W or (by - ty) < self.MIN_SEL_H:
            print("[WARN] Selection too small; ignored.")
            self.first_pt = None
            return
        self.selections.append({'frame': self.frame_idx, 'x1': int(lx), 'y1': int(ty), 'x2': int(rx), 'y2': int(by)})
        print(f"[INFO] Added selection at frame {self.frame_idx}: ({lx},{ty})->({rx},{by}) [LEFT coords]")
        self.first_pt = None
        self.toggle_pause()

    @staticmethod
    def ensure_ffmpeg():
        from shutil import which
        return which('ffmpeg') is not None

    def encode_with_ffmpeg(self, seq_dir, out_path):
        pattern = os.path.join(seq_dir, 'frame_%06d.png')
        cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(self.fps), '-i', pattern]
        ext_lower = os.path.splitext(out_path)[1].lower()
        if ext_lower == '.mkv':
            cmd += ['-c:v', 'ffv1', '-level', '3', '-g', '1', '-pix_fmt', 'rgb24', out_path]
        elif ext_lower == '.avi':
            cmd += ['-c:v', 'rawvideo', '-pix_fmt', 'bgr24', out_path]
        elif ext_lower == '.mp4':
            cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '0', '-pix_fmt', 'yuv444p', '-an', out_path]
        elif ext_lower == '.mov':
            cmd += ['-c:v', 'rawvideo', '-pix_fmt', 'bgr24', out_path]
        else:
            fallback = os.path.splitext(out_path)[0] + '.mkv'
            print(f"[WARN] Extension {ext_lower} not fully supported losslessly; writing {fallback} instead.")
            cmd += ['-c:v', 'ffv1', '-level', '3', '-g', '1', '-pix_fmt', 'rgb24', fallback]
            out_path = fallback
        print('[INFO] Finalizing zoomed video with ffmpeg...')
        print('       ' + ' '.join(cmd))
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            raise RuntimeError('ffmpeg failed to encode zoomed output.')
        return out_path

    def preview_with_live_zooms(self):
        sels = sorted(self.selections, key=lambda s: s['frame'])
        next_sel_idx = 0
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            raise RuntimeError('Failed to open exported video for preview.')
        cv2.namedWindow('VIDEO', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('VIDEO', self.on_mouse)
        self.frame_idx = 0
        last = None
        while True:
            need_zoom = False
            sel = None
            if next_sel_idx < len(sels) and self.frame_idx == sels[next_sel_idx]['frame'] and not self.paused:
                need_zoom = True
                sel = sels[next_sel_idx]
                next_sel_idx += 1
            if not self.paused and not need_zoom:
                ok, frame = cap.read()
                if not ok:
                    print('[INFO] End of video during preview.')
                    break
                self.current_frame = frame
                last = frame
                self.frame_idx += 1
                disp = frame.copy()
            elif need_zoom:
                base = last if last is not None else self.current_frame
                if base is None:
                    ok, base = cap.read()
                    if not ok:
                        break
                    self.current_frame = base
                    last = base
                in_f = max(1, int(round(self.fps * self.ANIM_DUR)))
                hold_f = max(1, int(round(self.fps * self.HOLD_DUR)))
                out_f = max(1, int(round(in_f / self.ZOOM_OUT_MULT)))
                for i in range(in_f):
                    disp = self.render_zoomed_canvas(base, sel, i / max(1, in_f - 1), 'in')
                    cv2.imshow('VIDEO', disp)
                    if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
                        cap.release(); cv2.destroyAllWindows(); return
                for i in range(hold_f):
                    disp = self.render_zoomed_canvas(base, sel, 1.0, 'hold')
                    cv2.imshow('VIDEO', disp)
                    if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
                        cap.release(); cv2.destroyAllWindows(); return
                for i in range(out_f):
                    disp = self.render_zoomed_canvas(base, sel, i / max(1, out_f - 1), 'out')
                    cv2.imshow('VIDEO', disp)
                    if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
                        cap.release(); cv2.destroyAllWindows(); return
                continue
            else:
                disp = last if last is not None else np.zeros((self.h, self.w, 3), np.uint8)
            if self.paused and self.first_pt is not None:
                cv2.circle(disp, self.first_pt, 6, (0, 255, 0), -1)
            cv2.imshow('VIDEO', disp)
            key = cv2.waitKey(int(1000 / (self.fps if not self.paused else 30))) & 0xFF
            if key == ord(' '):
                self.toggle_pause()
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def render_zoomed_video(self, out_path):
        sels = sorted(self.selections, key=lambda s: s['frame'])
        in_frames  = max(1, int(round(self.fps * self.ANIM_DUR)))
        hold_frames = max(1, int(round(self.fps * self.HOLD_DUR)))
        out_frames = max(1, int(round(in_frames / self.ZOOM_OUT_MULT)))
        seq_dir = tempfile.mkdtemp(prefix='zoomseq_')
        print(f"[INFO] Rendering zoom frames to: {seq_dir}")
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            os.rmdir(seq_dir)
            raise RuntimeError('Failed to open exported video for zoom render.')
        total_written = 0
        idx = 0
        next_sel_idx = 0
        while True:
            if next_sel_idx < len(sels) and idx == sels[next_sel_idx]['frame']:
                ok, base = cap.read()
                if not ok:
                    break
                sel = sels[next_sel_idx]
                next_sel_idx += 1
                for i in range(in_frames):
                    out_img = self.render_zoomed_canvas(base, sel, i / max(1, in_frames - 1), 'in')
                    cv2.imwrite(os.path.join(seq_dir, f'frame_{total_written:06d}.png'), out_img)
                    total_written += 1
                for i in range(hold_frames):
                    out_img = self.render_zoomed_canvas(base, sel, 1.0, 'hold')
                    cv2.imwrite(os.path.join(seq_dir, f'frame_{total_written:06d}.png'), out_img)
                    total_written += 1
                for i in range(out_frames):
                    out_img = self.render_zoomed_canvas(base, sel, i / max(1, out_frames - 1), 'out')
                    cv2.imwrite(os.path.join(seq_dir, f'frame_{total_written:06d}.png'), out_img)
                    total_written += 1
                idx += 1
                continue
            ok, frame = cap.read()
            if not ok:
                break
            cv2.imwrite(os.path.join(seq_dir, f'frame_{total_written:06d}.png'), frame)
            total_written += 1
            idx += 1
            if total_written % 200 == 0:
                print(f"[INFO] Rendered {total_written} frames…")
        cap.release()
        if total_written == 0:
            os.rmdir(seq_dir)
            raise RuntimeError('No frames rendered during zoom pass.')
        final_path = self.encode_with_ffmpeg(seq_dir, out_path) if self.ensure_ffmpeg() else None
        if final_path is None:
            # Minimal fallback to raw AVI if ffmpeg missing
            final_path = os.path.splitext(out_path)[0] + '.avi'
            fourcc = cv2.VideoWriter_fourcc(*'DIB ')
            vw = cv2.VideoWriter(final_path, fourcc, self.fps, (self.w, self.h))
            if not vw.isOpened():
                raise RuntimeError('OpenCV VideoWriter failed; install ffmpeg for robust output.')
            for i in range(total_written):
                png_path = os.path.join(seq_dir, f'frame_{i:06d}.png')
                img = cv2.imread(png_path, cv2.IMREAD_COLOR)
                vw.write(img)
            vw.release()
        # cleanup
        for name in os.listdir(seq_dir):
            try: os.remove(os.path.join(seq_dir, name))
            except: pass
        try: os.rmdir(seq_dir)
        except: pass
        return final_path

    def run_on_video(self, exported_path: str) -> Optional[str]:
        self.input_path = exported_path
        base, ext = os.path.splitext(exported_path)
        out_path = f"{base}_zoomedversion{ext}"
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            QMessageBox.critical(None, 'Zoom Annotator', 'Failed to open exported video.')
            return None
        self.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        print('[INFO] Zoom Annotator — space to pause, click two corners while paused, q to finish.')
        self.preview_with_live_zooms()
        if not self.selections:
            print('[INFO] No selections added. Skipping zoom render.')
            return None
        final_path = self.render_zoomed_video(out_path)
        print(f"\n[DONE] Wrote zoomed file: {final_path}")
        return final_path


# -----------------------------
# GUI
# -----------------------------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Side-by-Side Video Comparison Tool — with Zoom Annotator (NO AUDIO)")
        self.setMinimumSize(QSize(980, 760))

        self.metaA: Optional[VideoMeta] = None
        self.metaB: Optional[VideoMeta] = None
        self.align_result: Optional[AlignmentResult] = None
        self.scenesA: Optional[SceneCutData] = None
        self.scenesB: Optional[SceneCutData] = None
        self.time_map: TimeMap = TimeMap([TimeMapSegment(0.0, 1e9, 1.0, 0.0)])
        self.global_offset: float = 0.0
        self.snap_to_cut: bool = False

        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)

        # File selectors
        file_box = QGroupBox("1) Select Videos")
        fform = QFormLayout()
        self.pathA_edit = QLineEdit(); self.pathA_btn = QPushButton("Browse…")
        self.pathB_edit = QLineEdit(); self.pathB_btn = QPushButton("Browse…")
        self.pathA_btn.clicked.connect(lambda: self.pick_file(self.pathA_edit))
        self.pathB_btn.clicked.connect(lambda: self.pick_file(self.pathB_edit))
        rowA = QHBoxLayout(); rowA.addWidget(self.pathA_edit); rowA.addWidget(self.pathA_btn)
        rowB = QHBoxLayout(); rowB.addWidget(self.pathB_edit); rowB.addWidget(self.pathB_btn)
        fform.addRow("Left Video (A):", QWidget()); fform.addRow(rowA)
        fform.addRow("Right Video (B):", QWidget()); fform.addRow(rowB)
        file_box.setLayout(fform)
        root.addWidget(file_box)

        # Labels & Logo
        lab_box = QGroupBox("2) Labels & Logo")
        ll = QFormLayout()
        self.labelA_edit = QLineEdit(); self.labelA_edit.setPlaceholderText("Label for LEFT video (bottom-left)")
        self.labelB_edit = QLineEdit(); self.labelB_edit.setPlaceholderText("Label for RIGHT video (bottom-left)")
        self.logo_edit = QLineEdit(); self.logo_btn = QPushButton("Pick Logo…")
        self.logo_btn.clicked.connect(lambda: self.pick_file(self.logo_edit, image=True))
        lrow = QHBoxLayout(); lrow.addWidget(self.logo_edit); lrow.addWidget(self.logo_btn)
        ll.addRow("Left label:", self.labelA_edit)
        ll.addRow("Right label:", self.labelB_edit)
        ll.addRow("Logo (applies to right video, top-right):", QWidget()); ll.addRow(lrow)
        lab_box.setLayout(ll)
        root.addWidget(lab_box)

        # Alignment
        align_box = QGroupBox("3) Alignment")
        av = QVBoxLayout()
        self.auto_btn = QPushButton("Auto Align (pHash + SSIM)")
        self.auto_btn.clicked.connect(self.handle_auto_align)
        self.align_info = QLabel("Offset: n/a | Confidence: n/a | SSIM peak: n/a")
        self.snap_check = QCheckBox("Snap slider to nearest matched cut")
        self.snap_check.stateChanged.connect(lambda s: setattr(self, 'snap_to_cut', s == Qt.Checked))
        self.offset_slider = QSlider(Qt.Horizontal)
        self.offset_slider.setMinimum(-500); self.offset_slider.setMaximum(500); self.offset_slider.setSingleStep(1)
        self.offset_slider.valueChanged.connect(self.slider_changed)
        self.offset_label = QLabel("Manual offset: 0.00 s (B relative to A)")
        btnrow = QHBoxLayout()
        self.nudge1b = QPushButton("−1 frame"); self.nudge1f = QPushButton("+1 frame")
        self.nudge5b = QPushButton("−5 frames"); self.nudge5f = QPushButton("+5 frames")
        for b in [self.nudge1b, self.nudge1f, self.nudge5b, self.nudge5f]:
            b.setEnabled(False); btnrow.addWidget(b)
        self.nudge1b.clicked.connect(lambda: self.nudge_frames(-1))
        self.nudge1f.clicked.connect(lambda: self.nudge_frames(+1))
        self.nudge5b.clicked.connect(lambda: self.nudge_frames(-5))
        self.nudge5f.clicked.connect(lambda: self.nudge_frames(+5))
        self.progress = QProgressBar(); self.progress.setRange(0, 0); self.progress.hide()
        av.addWidget(self.auto_btn); av.addWidget(self.align_info); av.addWidget(self.snap_check)
        av.addWidget(self.offset_slider); av.addWidget(self.offset_label); av.addLayout(btnrow); av.addWidget(self.progress)
        align_box.setLayout(av)
        root.addWidget(align_box)

        # Compression & Estimate
        comp_box = QGroupBox("4) Compression & Size Estimate")
        cf = QFormLayout()
        self.comp_slider = QSlider(Qt.Horizontal); self.comp_slider.setMinimum(1); self.comp_slider.setMaximum(10); self.comp_slider.setValue(4)
        self.comp_slider.valueChanged.connect(self.update_size_estimate)
        self.est_label = QLabel("Estimated size: n/a")
        cf.addRow("Compression (1 = lossless, 10 = small):", self.comp_slider)
        cf.addRow(self.est_label)
        comp_box.setLayout(cf)
        root.addWidget(comp_box)

        # Export
        exp_box = QGroupBox("5) Export")
        ex = QFormLayout()
        self.out_path = QLineEdit(); self.out_btn = QPushButton("Choose output…")
        self.out_btn.clicked.connect(self.pick_output)
        orow = QHBoxLayout(); orow.addWidget(self.out_path); orow.addWidget(self.out_btn)
        self.container_combo = QComboBox(); self.container_combo.addItems([".mp4 (H.264)", ".mkv (FFV1/lossless only)", ".mov (uncompressed)"])
        self.chk_zoom_after = QCheckBox("Run zoom annotator after export")
        self.start_btn = QPushButton("Start Export")
        self.start_btn.clicked.connect(self.start_export)
        self.start_btn.setEnabled(False)
        ex.addRow("Output file:", QWidget()); ex.addRow(orow)
        ex.addRow("Container:", self.container_combo)
        ex.addRow(self.chk_zoom_after)
        ex.addRow(self.start_btn)
        exp_box.setLayout(ex)
        root.addWidget(exp_box)

        # Preview (static)
        pvbox = QGroupBox("Preview (static composite frame for layout check)")
        pv = QVBoxLayout()
        self.preview_label = QLabel("Preview will appear here after Auto Align or when both files are loaded.")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(QSize(640, 360))
        pv.addWidget(self.preview_label)
        pvbox.setLayout(pv)
        root.addWidget(pvbox)

        root.addStretch()

    # ---- UI callbacks ----
    def pick_file(self, target: QLineEdit, image: bool = False):
        filt = "Images (*.png *.jpg *.jpeg *.bmp *.webp)" if image else "Videos (*.mp4 *.mkv *.avi *.mov *.m4v)"
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", filt)
        if path:
            target.setText(path)
            if not image:
                self.update_meta(); self.update_start_enabled(); self.update_preview_static()

    def pick_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save output as", "output.mp4", "Video (*.mp4 *.mkv *.mov)")
        if path:
            self.out_path.setText(path)

    def update_meta(self):
        try:
            if self.pathA_edit.text():
                self.metaA = extract_meta(self.pathA_edit.text())
            if self.pathB_edit.text():
                self.metaB = extract_meta(self.pathB_edit.text())
        except Exception as e:
            QMessageBox.critical(self, "Metadata error", str(e))

    def update_start_enabled(self):
        ok = bool(self.pathA_edit.text() and self.pathB_edit.text())
        self.start_btn.setEnabled(ok)

    def slider_changed(self, val: int):
        self.global_offset = float(val) / 100.0
        if self.snap_to_cut and self.scenesA and self.scenesB and self.align_result:
            pairs = match_cuts_greedy(self.scenesA.cut_times, [t + self.global_offset for t in self.scenesB.cut_times], max_gap=1.0)
            candidates = []
            for a, bshifted in pairs:
                b = bshifted - self.global_offset
                candidates.append(a - b)
            if candidates:
                cur = self.global_offset
                best = min(candidates, key=lambda x: abs(x - cur))
                if abs(best - cur) > 0.001:
                    self.global_offset = best
                    self.offset_slider.blockSignals(True)
                    self.offset_slider.setValue(int(round(best * 100.0)))
                    self.offset_slider.blockSignals(False)
        self.offset_label.setText(f"Manual offset: {self.global_offset:.2f} s (B relative to A)")
        self.update_preview_static()

    def nudge_frames(self, frames: int):
        fps = 30.0
        if self.metaA and self.metaA.fps > fps: fps = self.metaA.fps
        if self.metaB and self.metaB.fps > fps: fps = self.metaB.fps
        delta = frames / max(1.0, fps)
        new_val = self.offset_slider.value() + int(round(delta * 100.0))
        new_val = max(self.offset_slider.minimum(), min(self.offset_slider.maximum(), new_val))
        self.offset_slider.setValue(new_val)

    def handle_auto_align(self):
        if not (self.pathA_edit.text() and self.pathB_edit.text()):
            QMessageBox.warning(self, "Missing files", "Please select both videos first.")
            return
        self.progress.show(); self.auto_btn.setEnabled(False)
        self.worker = AlignmentWorker(self.pathA_edit.text(), self.pathB_edit.text())
        self.worker.progress.connect(lambda s: self.progress.setFormat(s))
        self.worker.finished.connect(self.on_align_finished)
        self.worker.error.connect(self.on_align_error)
        self.worker.start()

    def on_align_error(self, msg: str):
        self.progress.hide(); self.auto_btn.setEnabled(True)
        QMessageBox.critical(self, "Alignment error", msg)

    def on_align_finished(self, align: AlignmentResult, scenesA: SceneCutData, scenesB: SceneCutData):
        self.progress.hide(); self.auto_btn.setEnabled(True)
        self.align_result = align
        self.scenesA = scenesA
        self.scenesB = scenesB
        self.global_offset = align.refined_offset_sec
        self.offset_slider.blockSignals(True)
        self.offset_slider.setValue(int(round(self.global_offset * 100.0)))
        self.offset_slider.blockSignals(False)
        self.align_info.setText(
            f"Offset: {align.refined_offset_sec:+.2f}s (coarse {align.coarse_offset_sec:+.2f}s) | "
            f"Confidence: {align.confidence:.2f} | SSIM peak: {align.ssim_peak:.3f}"
        )
        for b in [self.nudge1b, self.nudge1f, self.nudge5b, self.nudge5f]:
            b.setEnabled(True)
        b_shifted = [t + self.global_offset for t in (self.scenesB.cut_times or [])]
        pairs = match_cuts_greedy(self.scenesA.cut_times or [], b_shifted, max_gap=1.0)
        pairs_orig = [(a, b - self.global_offset) for (a, b) in pairs]
        self.time_map = build_time_map(pairs_orig)
        self.update_size_estimate(); self.update_preview_static()

    def pick_base_resolution(self) -> Tuple[int, int]:
        if not (self.metaA and self.metaB):
            return (1920, 1080)
        pixA = self.metaA.width * self.metaA.height
        pixB = self.metaB.width * self.metaB.height
        return (self.metaA.width, self.metaA.height) if pixA >= pixB else (self.metaB.width, self.metaB.height)

    def update_size_estimate(self):
        if not (self.metaA and self.metaB):
            self.est_label.setText("Estimated size: n/a"); return
        base_w, base_h = self.pick_base_resolution()
        out_w = base_w * 2 + 2
        fps = max(self.metaA.fps, self.metaB.fps, 24.0)
        level = int(self.comp_slider.value())
        kbps = estimate_bitrate_kbps(out_w, base_h, fps, level, complexity=1.0)
        dur = max(self.metaA.duration, self.metaB.duration)
        size_bytes = (kbps * 1000 / 8.0) * dur
        self.est_label.setText(f"Estimated size (@ {kbps:.0f} kbps): {human_size(size_bytes)}")

    # --- Frame extraction & preview ---
    def load_frame_at_time(self, path: str, t: float, w: int, h: int, rotation: int) -> Optional[np.ndarray]:
        tmp = os.path.join(ensure_tempdir(), f"frame_{os.path.basename(path)}_{t:.2f}.png")
        vf_parts = []
        if rotation == 90:
            vf_parts.append("transpose=clock")
        elif rotation == 270:
            vf_parts.append("transpose=cclock")
        elif rotation == 180:
            vf_parts.append("hflip,vflip")
        vf_parts.append(f"scale=w={w}:h={h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2")
        vf = ",".join(vf_parts)
        cmd = ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", vf, "-q:v", "2", tmp]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            img = cv2.imread(tmp, cv2.IMREAD_COLOR)
            return img
        except Exception:
            return None
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    def update_preview_static(self):
        if not (self.metaA and self.metaB):
            return
        base_w, base_h = self.pick_base_resolution()
        out_w = base_w * 2 + 2
        tA = min(self.metaA.duration, self.metaB.duration) / 2.0
        tB = max(0.0, min(self.metaB.duration, tA + self.global_offset))
        left = self.load_frame_at_time(self.metaA.path, tA, base_w, base_h, self.metaA.rotation)
        right = self.load_frame_at_time(self.metaB.path, tB, base_w, base_h, self.metaB.rotation)
        if left is None or right is None:
            self.preview_label.setText("Preview unavailable for these files.")
            return
        canvas = np.zeros((base_h, out_w, 3), dtype=np.uint8)
        canvas[:, :] = (16, 16, 16)
        canvas[:, :base_w, :] = left
        canvas[:, base_w:base_w+2, :] = (255, 255, 255)
        canvas[:, base_w+2:base_w+2+base_w, :] = right
        labelA = self.labelA_edit.text().strip()
        labelB = self.labelB_edit.text().strip()
        if labelA:
            cv2.putText(canvas, labelA, (10, base_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (240, 240, 240), 2, cv2.LINE_AA)
        if labelB:
            cv2.putText(canvas, labelB, (base_w + 12, base_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (240, 240, 240), 2, cv2.LINE_AA)
        logo_path = self.logo_edit.text().strip()
        if logo_path and os.path.isfile(logo_path):
            try:
                logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                if logo is not None:
                    max_w = int(base_w * 0.12)
                    scale = min(1.0, max_w / max(1, logo.shape[1]))
                    new_w = int(logo.shape[1] * scale)
                    new_h = int(logo.shape[0] * scale)
                    logo_r = cv2.resize(logo, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    x = base_w + 2 + (base_w - new_w - 12)
                    y = 12
                    if logo_r.shape[2] == 4:
                        alpha = logo_r[:, :, 3:4] / 255.0
                        roi = canvas[y:y+new_h, x:x+new_w, :3]
                        canvas[y:y+new_h, x:x+new_w, :3] = (alpha * logo_r[:, :, :3] + (1 - alpha) * roi).astype(np.uint8)
                    else:
                        canvas[y:y+new_h, x:x+new_w, :] = logo_r
            except Exception:
                pass
        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        scaled = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    # ---- Export (NO AUDIO) ----
    def start_export(self):
        try:
            if not (self.metaA and self.metaB):
                QMessageBox.warning(self, "Missing files", "Please select both videos.")
                return
            if not self.out_path.text().strip():
                QMessageBox.warning(self, "Missing output", "Please choose an output file.")
                return
            out = self.out_path.text().strip()
            base_w, base_h = self.pick_base_resolution()
            line_w = 2
            out_w = base_w * 2 + line_w

            fontfiles = pick_fontfile_candidates()
            fontfile = fontfiles[0] if fontfiles else None
            if fontfile is None:
                QMessageBox.information(self, "Font note",
                                        "No common fontfile found. FFmpeg will try system fontconfig. If drawtext fails, install DejaVuSans and set font in code.")
            labelA = self.labelA_edit.text().strip()
            labelB = self.labelB_edit.text().strip()
            logo_path = self.logo_edit.text().strip() if os.path.isfile(self.logo_edit.text().strip()) else None

            off = self.global_offset
            a_trim = max(0.0, +off)
            b_trim = max(0.0, -off)

            inA = ffmpeg.input(self.metaA.path)
            inB = ffmpeg.input(self.metaB.path)

            def apply_rotation(vstream, rotation):
                if rotation == 90:
                    return vstream.filter('transpose', 'clock')
                elif rotation == 270:
                    return vstream.filter('transpose', 'cclock')
                elif rotation == 180:
                    return vstream.filter('hflip').filter('vflip')
                return vstream

            vA = apply_rotation(inA.video, self.metaA.rotation).filter('trim', start=a_trim).filter('setpts', 'PTS-STARTPTS')
            vB = apply_rotation(inB.video, self.metaB.rotation).filter('trim', start=b_trim).filter('setpts', 'PTS-STARTPTS')

            vA = vA.filter('scale', w=base_w, h=-1, force_original_aspect_ratio='decrease').filter('pad', base_w, base_h, '(ow-iw)/2', '(oh-ih)/2')
            vB = vB.filter('scale', w=base_w, h=-1, force_original_aspect_ratio='decrease').filter('pad', base_w, base_h, '(ow-iw)/2', '(oh-ih)/2')

            if labelA:
                argsA = {'text': labelA, 'fontsize': 24, 'fontcolor': 'white', 'x': '20', 'y': 'h-th-20', 'borderw': 2, 'bordercolor': 'black@0.7'}
                if fontfile: argsA['fontfile'] = fontfile
                vA = vA.filter('drawtext', **argsA)
            if labelB:
                argsB = {'text': labelB, 'fontsize': 24, 'fontcolor': 'white', 'x': '20', 'y': 'h-th-20', 'borderw': 2, 'bordercolor': 'black@0.7'}
                if fontfile: argsB['fontfile'] = fontfile
                vB = vB.filter('drawtext', **argsB)

            fps_out = max(self.metaA.fps, self.metaB.fps, 24.0)
            base_canvas = ffmpeg.input(f'color=s={out_w}x{base_h}:c=black', f='lavfi', r=fps_out)
            comp = ffmpeg.overlay(base_canvas, vA, x=0, y=0)
            centerline = ffmpeg.input(f'color=s={line_w}x{base_h}:c=white', f='lavfi', r=fps_out)
            comp = ffmpeg.overlay(comp, centerline, x=base_w, y=0)
            comp = ffmpeg.overlay(comp, vB, x=base_w + line_w, y=0)

            if logo_path:
                logo_in = ffmpeg.input(logo_path)
                logo_scaled = logo_in.filter('scale', w=f'min(iw,{int(base_w*0.12)})', h='-1', force_original_aspect_ratio='decrease')
                x_expr = f"{base_w + line_w} + {base_w} - w - 20"
                y_expr = "20"
                comp = ffmpeg.overlay(comp, logo_scaled, x=x_expr, y=y_expr)

            cont = self.container_combo.currentText()
            level = int(self.comp_slider.value())
            common_kwargs = {'r': fps_out, 'pix_fmt': 'yuv444p'}

            if cont.startswith('.mp4'):
                vcodec = 'libx264'
                crf_map = {1: 0, 2: 10, 3: 12, 4: 14, 5: 17, 6: 19, 7: 22, 8: 24, 9: 26, 10: 28}
                crf = crf_map.get(level, 18)
                preset = 'veryslow' if level == 1 else ('slow' if level <= 6 else 'medium')
                stream = ffmpeg.output(comp, out, vcodec=vcodec, crf=crf, preset=preset, movflags='+faststart', **common_kwargs)
            elif cont.startswith('.mkv'):
                if level == 1:
                    stream = ffmpeg.output(comp, out, vcodec='ffv1', level='3', g=1, **common_kwargs)
                else:
                    stream = ffmpeg.output(comp, out, vcodec='libx264', crf={2:10,3:12,4:14,5:17,6:19,7:22,8:24,9:26,10:28}.get(level,18), preset='slow', **common_kwargs)
            else:  # .mov
                stream = ffmpeg.output(comp, out, vcodec='rawvideo', **common_kwargs)

            stream = stream.overwrite_output()

            self.start_btn.setEnabled(False)
            self.progress.setFormat("Exporting with FFmpeg…"); self.progress.setRange(0, 0); self.progress.show()
            try:
                ffmpeg.run(stream, quiet=False)
                self.progress.hide()
                QMessageBox.information(self, "Done", f"Export finished:\n{out}")
                # Optional post-export zoom pass
                if self.chk_zoom_after.isChecked():
                    zoomer = ZoomAnnotator()
                    try:
                        final_zoom = zoomer.run_on_video(out)
                        if final_zoom:
                            QMessageBox.information(self, "Zoom Annotator", f"Zoomed file saved as:\n{final_zoom}")
                        else:
                            QMessageBox.information(self, "Zoom Annotator", "Zoom step skipped or no selections made.")
                    except Exception as ze:
                        QMessageBox.critical(self, "Zoom Annotator", f"Zoom step failed:\n{ze}")
            except ffmpeg.Error as e:
                self.progress.hide()
                emsg = e.stderr.decode('utf-8', errors='ignore') if hasattr(e, 'stderr') else str(e)
                QMessageBox.critical(self, "FFmpeg error", emsg)
            finally:
                self.start_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Export error", str(e))
            self.start_btn.setEnabled(True)
            self.progress.hide()


# -----------------------------
# App entry
# -----------------------------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
