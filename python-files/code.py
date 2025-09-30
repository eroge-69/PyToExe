# play_50hz_for_py2exe.py
"""
50 Hz Tone Player — compatible with py2exe.com/convert

این برنامه فقط از کتابخانه‌های استاندارد پایتون استفاده می‌کند و در ویندوز با winsound
یک فایل WAV تولید‌شده را به‌صورت حلقه‌ای پخش می‌کند.

قبل از استفاده: مطمئن شوید که صاحب دستگاه رضایت داده است.
"""

import math
import wave
import struct
import tempfile
import os
import sys
import tkinter as tk
from tkinter import messagebox

# winsound فقط در ویندوز وجود دارد
try:
    import winsound
except ImportError:
    winsound = None

# تنظیمات صوتی
SAMPLE_RATE = 44100        # نمونه‌برداری (Hz)
FREQ = 50.0                # فرکانس تون (Hz)
DURATION_SECONDS = 5       # طول فایل WAV (ثانیه) — فایل را حلقه می‌کنیم
AMPLITUDE = 0.1            # دامنه 0..1 (کم نگه دارید برای محافظت از گوش/بلندگو)

class ToneWav:
    def __init__(self, freq=FREQ, sr=SAMPLE_RATE, duration=DURATION_SECONDS, amplitude=AMPLITUDE):
        self.freq = float(freq)
        self.sr = int(sr)
        self.duration = float(duration)
        self.amplitude = float(amplitude)
        self.filename = None

    def generate(self):
        """فایل WAV را در یک فایل موقت تولید و مسیر آن را بازمی‌گرداند."""
        n_samples = int(self.sr * self.duration)
        max_amp = 32767  # 16-bit PCM

        # فایل موقت ایجاد می‌کنیم (delete=False چون winsound ممکن است آن را باز کند)
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        fname = tf.name
        tf.close()  # فقط نام می‌خواهیم؛ خودمان می‌نویسیم

        with wave.open(fname, 'w') as wf:
            wf.setnchannels(1)            # تک کاناله (mono)
            wf.setsampwidth(2)           # 16-bit
            wf.setframerate(self.sr)

            for i in range(n_samples):
                t = i / self.sr
                # تولید سینوس 50Hz
                sample = self.amplitude * math.sin(2.0 * math.pi * self.freq * t)
                int_sample = int(sample * max_amp)
                data = struct.pack('<h', int_sample)
                wf.writeframesraw(data)

            wf.writeframes(b'')  # پایان نوشتن

        self.filename = fname
        return fname

    def cleanup(self):
        if self.filename and os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except Exception:
                pass
            self.filename = None

class App:
    def __init__(self, root):
        self.root = root
        root.title("50 Hz Tone Player (Visible)")
        root.geometry("360x170")
        root.resizable(False, False)

        tk.Label(root, text="این برنامه یک تون ۵۰ هرتز پخش می‌کند.\nقبل از پخش، از صاحب دستگاه اجازه بگیرید.", justify="center").pack(padx=10, pady=10)

        self.status_var = tk.StringVar(value="متوقف")
        self.tone = ToneWav()
        self.is_playing = False

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=(4,6))

        self.start_btn = tk.Button(btn_frame, text="شروع پخش", width=14, command=self.start)
        self.start_btn.grid(row=0, column=0, padx=6)

        self.stop_btn = tk.Button(btn_frame, text="توقف پخش", width=14, command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=6)

        tk.Label(root, textvariable=self.status_var).pack(pady=(6,0))

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        if winsound is None:
            messagebox.showerror("خطا", "این برنامه فقط در ویندوز قابل اجرا است (نیاز به winsound).")
            root.after(10, root.destroy)

    def start(self):
        if winsound is None:
            return
        if self.is_playing:
            return
        try:
            fname = self.tone.generate()
            # پخش حلقه‌ای (SND_LOOP) به صورت غیر هم‌زمان (SND_ASYNC)
            winsound.PlaySound(fname, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            self.is_playing = True
            self.status_var.set("در حال پخش (حلقه‌ای)")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("خطا در پخش", f"پخش صدا امکان‌پذیر نیست:\n{e}")

    def stop(self):
        if not self.is_playing:
            return
        try:
            # توقف پخش
            winsound.PlaySound(None, winsound.SND_PURGE)
        finally:
            # سپس فایل موقت را حذف کن
            self.tone.cleanup()
            self.is_playing = False
            self.status_var.set("متوقف")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def on_close(self):
        # قبل از خروج، اگر در حال پخش است آن را قطع و فایل را حذف کن
        try:
            if self.is_playing:
                winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
        self.tone.cleanup()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
