#!/usr/bin/env python3
import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Configuration
MAX_FPS = 60
AUDIO_BITRATE = 192  # kbps
CRF = 23  # lower = higher quality, higher = smaller size
MOTION_DROP_THRESHOLD = 0.12  # motion score to decide frame dropping

def _creationflags():
    if os.name == 'nt':
        return subprocess.CREATE_NO_WINDOW
    return 0

def run_ffprobe(path):
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate', '-show_entries', 'format=duration',
        '-of', 'json', path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=_creationflags())
    info = json.loads(proc.stdout)
    stream = info.get('streams', [])[0]
    width = int(stream.get('width', 0))
    height = int(stream.get('height', 0))
    num, den = map(int, stream.get('r_frame_rate', '0/1').split('/'))
    fps = num / den if den != 0 else 0
    duration = float(info.get('format', {}).get('duration', 0))
    return width, height, fps, duration

def count_scene_changes(path, threshold=0.05, max_probe_seconds=60):
    import re
    from subprocess import PIPE
    duration = run_ffprobe(path)[3]
    probe_dur = min(duration, max_probe_seconds)
    cmd = [
        'ffmpeg', '-hide_banner', '-v', 'error', '-ss', '0', '-t', str(probe_dur), '-i', path,
        '-vf', f"select='gt(scene,{threshold})',showinfo", '-f', 'null', '-'
    ]
    proc = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, text=True, creationflags=_creationflags())
    return proc.stderr.count('pts_time:')

def decide_frame_drop(duration, motion_score, fps):
    drop = 1
    if duration > 120 and motion_score < 0.08:
        drop = 3
    elif duration > 90 and motion_score < 0.12:
        drop = 2
    if fps and (fps // drop) < 15:
        drop = max(1, fps // 15)
    return int(drop)

def build_filters(fps, drop_factor):
    filters = []
    if drop_factor and drop_factor > 1 and fps:
        new_fps = max(15, int(fps // drop_factor))
        filters.append(f"fps={new_fps}")
    if fps and fps > MAX_FPS:
        filters.append(f"fps={MAX_FPS}")
    return ",".join(filters) if filters else None

def main():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Info", "Method By cark12345 On Dc")

    input_path = filedialog.askopenfilename(title="Select your video file (basename must be 'input')",
                                            filetypes=[("Video files", "*.mp4;*.mov;*.mkv;*.avi;*.webm")])
    if not input_path:
        return
    base = os.path.splitext(os.path.basename(input_path))[0].lower()
    if base != "input":
        messagebox.showerror("Error", "Selected file must be named exactly 'input'.")
        return

    out_dir = os.path.dirname(input_path)
    output_path = os.path.join(out_dir, "output.mp4")

    width, height, fps, duration = run_ffprobe(input_path)
    scene_count = count_scene_changes(input_path, threshold=0.06, max_probe_seconds=40)
    motion_score = scene_count / max(duration, 1.0)
    drop_factor = decide_frame_drop(duration, motion_score, fps)
    vf = build_filters(fps, drop_factor)

    cmd = ['ffmpeg', '-y', '-i', input_path]
    if vf:
        cmd += ['-vf', vf]
    cmd += [
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', str(CRF),
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', f'{AUDIO_BITRATE}k',
        '-movflags', '+faststart',
        output_path
    ]

    subprocess.run(cmd, check=True, creationflags=_creationflags())
    messagebox.showinfo("Done", "Video Completed :)")
    try:
        if os.name == 'nt':
            subprocess.run(['explorer', '/select,', output_path])
        elif os.name == 'posix':
            subprocess.run(['xdg-open', out_dir])
    except Exception:
        pass

if __name__ == '__main__':
    main()
