#!/usr/bin/env python3
"""
Name-Triggered Media Stopper with Minimal UI
===========================================

This version adds a simple Tkinter GUI for Windows users. It allows entering the
name, selecting the Vosk model path, and starting/stopping the listener without
needing the command line. It can be packaged as a .exe with PyInstaller.

Packaging to .exe (Windows)
---------------------------
1. Install PyInstaller:
   pip install pyinstaller

2. Build the .exe:
   pyinstaller --noconsole --onefile --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" name_listener_gui.py

3. The .exe will appear in the `dist/` folder.

"""
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from dataclasses import dataclass
import platform
import re
import json
import time
import queue
import subprocess

try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    from rapidfuzz import fuzz
except Exception as e:
    messagebox.showerror("Missing Dependency", f"Required package missing: {e}\nInstall dependencies first.")
    sys.exit(1)

try:
    import keyboard  # type: ignore
except Exception:
    keyboard = None

if platform.system() == 'Windows':
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except Exception:
        AudioUtilities = None
        IAudioEndpointVolume = None
else:
    AudioUtilities = None
    IAudioEndpointVolume = None

@dataclass
class Config:
    name: str
    model_path: str
    action: str = "both"
    mute_seconds: int = 5
    threshold: int = 85
    cooldown: int = 7
    device: str | int | None = None
    phrase_boost: list[str] | None = None

class MediaController:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._last_trigger = 0.0

    def _within_cooldown(self) -> bool:
        return (time.time() - self._last_trigger) < self.cfg.cooldown

    def trigger(self):
        if self._within_cooldown():
            return
        self._last_trigger = time.time()
        if self.cfg.action in ("pause", "both"):
            self.pause_media()
        if self.cfg.action in ("mute", "both"):
            self.temp_mute(self.cfg.mute_seconds)

    def pause_media(self):
        if keyboard:
            try:
                keyboard.send("play/pause media")
                return
            except Exception:
                pass
        if platform.system() == 'Linux':
            try:
                subprocess.run(["playerctl", "pause"], check=False)
            except FileNotFoundError:
                pass

    def temp_mute(self, seconds: int):
        if platform.system() == 'Windows' and AudioUtilities and IAudioEndpointVolume:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current_mute = volume.GetMute()
                volume.SetMute(1, None)
                threading.Timer(seconds, lambda: volume.SetMute(current_mute, None)).start()
                return
            except Exception:
                pass
        elif platform.system() == 'Darwin':
            try:
                get_vol = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
                prev = int(get_vol.stdout.strip()) if get_vol.stdout.strip().isdigit() else 50
                subprocess.run(["osascript", "-e", "set volume output volume 0"])
                threading.Timer(seconds, lambda: subprocess.run(["osascript", "-e", f"set volume output volume {prev}"])).start()
            except Exception:
                pass
        elif platform.system() == 'Linux':
            try:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])
                threading.Timer(seconds, lambda: subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])).start()
            except Exception:
                pass

class NameDetector(threading.Thread):
    def __init__(self, cfg: Config, controller: MediaController, log_callback):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.controller = controller
        self.log_callback = log_callback
        self.q: queue.Queue[bytes] = queue.Queue()
        self.running = False
        if not os.path.isdir(cfg.model_path):
            raise FileNotFoundError(f"Vosk model not found at: {cfg.model_path}")
        self.model = Model(cfg.model_path)
        self.samplerate = 16000
        self.rec = KaldiRecognizer(self.model, self.samplerate)
        self.rec.SetWords(True)
        self.target_norm = self._normalize(cfg.name)

    @staticmethod
    def _normalize(s: str) -> str:
        s = s.lower()
        s = re.sub(r"[^a-z0-9\s]", "", s)
        return s.strip()

    def _score(self, text: str) -> int:
        return int(fuzz.partial_ratio(self.target_norm, self._normalize(text)))

    def _on_text(self, text: str):
        if self._score(text) >= self.cfg.threshold:
            self.log_callback(f"Detected: {text}")
            self.controller.trigger()

    def _callback(self, indata, frames, time_info, status):
        self.q.put(bytes(indata))

    def run(self):
        self.running = True
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16', channels=1, callback=self._callback):
            while self.running:
                try:
                    data = self.q.get(timeout=0.5)
                except queue.Empty:
                    continue
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    if res.get('text'):
                        self._on_text(res['text'])
                else:
                    part = json.loads(self.rec.PartialResult())
                    if part.get('partial'):
                        self._on_text(part['partial'])

    def stop(self):
        self.running = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Name Listener")
        self.detector = None

        tk.Label(root, text="Target Name:").pack()
        self.name_var = tk.StringVar()
        tk.Entry(root, textvariable=self.name_var).pack(fill='x')

        tk.Label(root, text="Vosk Model Path:").pack()
        self.model_var = tk.StringVar()
        tk.Entry(root, textvariable=self.model_var).pack(fill='x')
        tk.Button(root, text="Browse", command=self.browse_model).pack()

        self.start_btn = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="Stop", command=self.stop_listening, state='disabled')
        self.stop_btn.pack(pady=5)

        self.log = tk.Text(root, height=10, state='disabled')
        self.log.pack(fill='both', expand=True)

    def browse_model(self):
        path = filedialog.askdirectory()
        if path:
            self.model_var.set(path)

    def log_message(self, msg: str):
        self.log.configure(state='normal')
        self.log.insert('end', msg + "\n")
        self.log.configure(state='disabled')
        self.log.see('end')

    def start_listening(self):
        name = self.name_var.get().strip()
        model = self.model_var.get().strip()
        if not name or not model:
            messagebox.showerror("Error", "Please enter a name and model path.")
            return
        cfg = Config(name=name, model_path=model)
        controller = MediaController(cfg)
        self.detector = NameDetector(cfg, controller, self.log_message)
        self.detector.start()
        self.log_message(f"Listening for: {name}")
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

    def stop_listening(self):
        if self.detector:
            self.detector.stop()
            self.detector = None
            self.log_message("Stopped listening.")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
