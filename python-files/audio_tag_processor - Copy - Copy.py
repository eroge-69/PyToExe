# -*- coding: utf-8 -*-
# Audio Tagger v2.3

# --- وابستگی‌ها ---
# pip install pydub librosa numpy soundfile pygame

import os
import logging
import queue
import threading
import multiprocessing
import time
import random
import sys
import io
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Entry, Checkbutton, StringVar,
    BooleanVar, IntVar, DoubleVar, filedialog, messagebox, simpledialog,
    scrolledtext, Toplevel
)
from tkinter import ttk

# --- بررسی و ایمپورت کتابخانه‌های ضروری ---
try:
    from pydub import AudioSegment
    from pydub.silence import detect_silence
    import librosa
    import numpy as np
    import pygame
except ImportError as e:
    root_check = Tk()
    root_check.withdraw()
    messagebox.showerror(
        "وابستگی یافت نشد",
        f"یکی از کتابخانه‌های مورد نیاز نصب نیست: {e}\n"
        "لطفاً با دستور زیر آنها را نصب کنید:\n"
        "pip install pydub librosa numpy soundfile pygame"
    )
    root_check.destroy()
    exit()

# --- راه‌اندازی سیستم لاگ‌نویسی ---
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

# --- توابع کمکی ---
def ms_to_hhmmss(ms):
    if ms is None or ms < 0: return "00:00:00.000"
    millis = int(ms % 1000)
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    hours = int((ms / (1000 * 60 * 60)) % 24)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"

def hhmmss_to_ms(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            return None
        h = int(parts[0])
        m = int(parts[1])
        s_parts = parts[2].split('.')
        s = int(s_parts[0])
        ms = int(s_parts[1]) if len(s_parts) > 1 else 0
        return (h * 3600 + m * 60 + s) * 1000 + ms
    except (ValueError, IndexError):
        return None

def ms_to_seconds_float(ms):
    """تبدیل میلی‌ثانیه به ثانیه به صورت اعشاری."""
    return ms / 1000.0

def extract_rich_features(segment_before_point, segment_at_point, absolute_position_ms, total_duration_ms):
    features = {}
    try:
        features['relative_position'] = absolute_position_ms / total_duration_ms if total_duration_ms > 0 else 0
        features['total_duration_ms'] = total_duration_ms
        silence_thresh = segment_before_point.dBFS - 16
        silences = detect_silence(segment_before_point, min_silence_len=250, silence_thresh=silence_thresh)
        features['silence_count'] = len(silences)
        features['total_silence_duration'] = sum([s[1] - s[0] for s in silences]) if silences else 0
        if silences:
             features['last_silence_proximity'] = (10000 - (10000 - silences[-1][1])) / 10000.0
        else:
             features['last_silence_proximity'] = 0.0
        features['energy_before'] = segment_before_point.rms
        features['energy_at'] = segment_at_point.rms
        features['energy_ratio'] = segment_at_point.rms / segment_at_point.rms if segment_at_point.rms > 0 else 1.0
        y = np.array(segment_at_point.get_array_of_samples()).astype(np.float32)
        sr = segment_at_point.frame_rate
        if np.max(np.abs(y)) > 0:
            y /= np.max(np.abs(y))
        
        features['mfccs_mean'] = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T, axis=0)
        features['contrast_mean'] = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr).T, axis=0)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo.item() if hasattr(tempo, 'item') else tempo) if tempo else 0.0
    except Exception as e:
        print(f"خطا در استخراج ویژگی‌های غنی: {e}")
        return None
    return features

class ManualTagTrainer(Toplevel):
    def __init__(self, parent, audio_segment, file_name):
        super().__init__(parent)
        self.title(f"آموزش تگ پایانی: {file_name}")
        
        self.parent = parent
        self.duration_ms = len(audio_segment)
        self.selected_time_ms = DoubleVar(value=self.duration_ms * 0.95)
        self.safe_zone_end_ms = DoubleVar(value=self.duration_ms * 0.98)
        
        # Initialize attributes to prevent AttributeError
        self.final_selected_time = None
        self.final_safe_zone_end = None

        self.is_playing = False
        self.is_user_dragging = False
        self.start_pos_ms = 0
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            # Convert pydub segment to a standard in-memory WAV for pygame
            with io.BytesIO() as wav_io:
                audio_segment.set_frame_rate(44100).set_channels(2).export(wav_io, format="wav")
                wav_io.seek(0)
                pygame.mixer.music.load(wav_io)
        except Exception as e:
            error_message = f"امکان مقداردهی اولیه یا بارگذاری فایل با Pygame وجود ندارد:\n\n{type(e).__name__}: {e}"
            logging.error(f"Pygame init/load error: {type(e).__name__}: {e}", exc_info=True)
            messagebox.showerror("خطای Pygame", error_message, parent=self)
            self.destroy()
            return

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.wait_window(self)

    def _create_widgets(self):
        slider_width = self.parent.winfo_screenwidth() - 200

        time_frame = Frame(self)
        time_frame.pack(fill="x", padx=20, pady=(10, 2))
        Label(time_frame, text="۱. نقطه دقیق شروع تیتراژ (آبی):").pack(anchor='w')
        self.time_slider = ttk.Scale(time_frame, from_=0, to=self.duration_ms, orient="horizontal", variable=self.selected_time_ms, command=self._on_time_slider_drag, length=slider_width)
        self.time_slider.bind("<ButtonPress-1>", lambda e: self._set_dragging(True))
        self.time_slider.bind("<ButtonRelease-1>", lambda e: self._set_dragging(False, "time"))
        self.time_slider.pack(fill="x")
        self.time_label = Label(time_frame, text="", font=("Arial", 10))
        self.time_label.pack(anchor='e')

        safe_zone_frame = Frame(self)
        safe_zone_frame.pack(fill="x", padx=20, pady=5)
        Label(safe_zone_frame, text="۲. حداکثر موقعیت مجاز (قرمز):").pack(anchor='w')
        self.safe_zone_slider = ttk.Scale(safe_zone_frame, from_=0, to=self.duration_ms, orient="horizontal", variable=self.safe_zone_end_ms, command=self._on_safe_zone_slider_drag, length=slider_width)
        self.safe_zone_slider.bind("<ButtonPress-1>", lambda e: self._set_dragging(True))
        self.safe_zone_slider.bind("<ButtonRelease-1>", lambda e: self._set_dragging(False))
        self.safe_zone_slider.pack(fill="x")
        self.safe_zone_label = Label(safe_zone_frame, text="", font=("Arial", 10), fg="red")
        self.safe_zone_label.pack(anchor='e')
        
        self._update_labels()

        controls_frame = Frame(self)
        controls_frame.pack(pady=10)
        Button(controls_frame, text="⏪ ۱۰ ثانیه", command=lambda: self._seek(-10000)).pack(side="left", padx=5)
        self.play_pause_button = Button(controls_frame, text="▶️ پخش", width=10, command=self._toggle_play)
        self.play_pause_button.pack(side="left", padx=5)
        Button(controls_frame, text="۱۰ ثانیه ⏩", command=lambda: self._seek(10000)).pack(side="left", padx=5)
        
        manual_input_frame = Frame(self)
        manual_input_frame.pack(pady=5)
        Label(manual_input_frame, text="یا زمان را دستی وارد کنید (HH:MM:SS):").pack(side="left")
        self.manual_time_entry = Entry(manual_input_frame, width=10)
        self.manual_time_entry.pack(side="left", padx=5)
        Button(manual_input_frame, text="تنظیم", command=self._set_time_from_entry).pack(side="left")

        action_frame = Frame(self)
        action_frame.pack(pady=(10, 10))
        Button(action_frame, text="✅ ثبت و ادامه", command=self._confirm_selection, bg="#4CAF50", fg="white").pack(side="left", padx=10)
        Button(action_frame, text="❌ لغو آموزش", command=self._on_close, bg="#f44336", fg="white").pack(side="left", padx=10)

    def _set_time_from_entry(self):
        time_str = self.manual_time_entry.get()
        time_ms = hhmmss_to_ms(time_str)
        if time_ms is not None and 0 <= time_ms <= self.duration_ms:
            self.selected_time_ms.set(time_ms)
            if self.safe_zone_end_ms.get() < time_ms:
                self.safe_zone_end_ms.set(time_ms)
            self._update_labels()
        else:
            messagebox.showerror("خطا", "فرمت زمان نامعتبر است یا خارج از محدوده فایل است.\nلطفاً از فرمت HH:MM:SS استفاده کنید.", parent=self)

    def _set_dragging(self, status, slider_type=None):
        self.is_user_dragging = status
        if not status and slider_type == "time" and self.is_playing:
            self._start_playback()

    def _on_time_slider_drag(self, value_str):
        if self.selected_time_ms.get() > self.safe_zone_end_ms.get():
            self.selected_time_ms.set(self.safe_zone_end_ms.get())
        self._update_labels()

    def _on_safe_zone_slider_drag(self, value_str):
        if self.safe_zone_end_ms.get() < self.selected_time_ms.get():
            self.safe_zone_end_ms.set(self.selected_time_ms.get())
        self._update_labels()

    def _update_labels(self):
        time_val = self.selected_time_ms.get()
        safe_val = self.safe_zone_end_ms.get()
        self.time_label.config(text=f"زمان تگ: {ms_to_hhmmss(time_val)}")
        safe_percent = (safe_val / self.duration_ms) * 100 if self.duration_ms > 0 else 0
        self.safe_zone_label.config(text=f"حداکثر موقعیت: {ms_to_hhmmss(safe_val)} ({safe_percent:.1f}%)")

    def _toggle_play(self):
        if self.is_playing:
            self._stop_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        try:
            self._stop_playback() 
            self.is_playing = True
            self.start_pos_ms = self.selected_time_ms.get()
            pygame.mixer.music.play(start=ms_to_seconds_float(self.start_pos_ms))
            self.play_pause_button.config(text="⏸️ توقف")
            self.after(100, self._live_update_playback_position)
        except pygame.error as e:
            messagebox.showerror("خطای پخش", f"خطا در هنگام پخش صدا: {e}", parent=self)
            self.is_playing = False
            self.play_pause_button.config(text="▶️ پخش")

    def _live_update_playback_position(self):
        if not self.is_playing:
            return

        if pygame.mixer.music.get_busy():
            if not self.is_user_dragging:
                current_playback_time_ms = pygame.mixer.music.get_pos()
                new_slider_pos = self.start_pos_ms + current_playback_time_ms
                if new_slider_pos <= self.duration_ms:
                    self.selected_time_ms.set(new_slider_pos)
            self.after(100, self._live_update_playback_position)
        else:
            self.is_playing = False
            self.play_pause_button.config(text="▶️ پخش")

    def _stop_playback(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        self.play_pause_button.config(text="▶️ پخش")

    def _seek(self, offset_ms):
        was_playing = self.is_playing
        self._stop_playback()
        current_pos = self.selected_time_ms.get()
        new_pos = max(0, min(current_pos + offset_ms, self.duration_ms))
        self.selected_time_ms.set(new_pos)
        if was_playing: self._start_playback()

    def _confirm_selection(self):
        self.final_selected_time = int(self.selected_time_ms.get())
        self.final_safe_zone_end = int(self.safe_zone_end_ms.get())
        self._on_close()

    def _on_close(self):
        self._stop_playback()
        pygame.mixer.quit()
        self.destroy()

class AudioTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامه تگ‌گذاری صوتی - نسخه 2.3")
        self.root.geometry("850x800")
        self.root.minsize(800, 700)
        self.root.configure(bg="#f0f0f0")

        self.file_list = []
        self.output_bitrate = StringVar(value="192k")
        self.process_count = IntVar(value=8)
        self.tag_groups = {}
        self.end_tag_times_log = {}
        self.unified_time_enabled = BooleanVar(value=False)
        self.unified_time_str = StringVar(value="00:00:00")

        self._create_widgets()
        self.root.after(100, self._poll_log_queue)
        messagebox.showinfo(
            "نیازمندی مهم",
            "برای پردازش فرمت‌های صوتی، باید FFmpeg و Pygame روی سیستم شما نصب باشند."
        )

    def _create_widgets(self):
        main_frame = Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="۱. لیست فایل‌های ورودی")
        input_frame.pack(fill="x", pady=5, padx=5)
        
        input_buttons_frame = Frame(input_frame)
        input_buttons_frame.pack(fill="x", pady=5)
        Button(input_buttons_frame, text="افزودن فایل‌ها", command=self._select_files).pack(side="left", padx=5)
        Button(input_buttons_frame, text="افزودن پوشه", command=self._select_folder).pack(side="left", padx=5)
        Button(input_buttons_frame, text="حذف انتخاب‌شده", command=self._remove_selected_files).pack(side="right", padx=5)
        Button(input_buttons_frame, text="پاک کردن لیست", command=self._clear_file_list).pack(side="right", padx=5)

        tree_frame = Frame(input_frame)
        tree_frame.pack(fill="x", expand=True)
        self.file_tree = ttk.Treeview(tree_frame, columns=("path",), show="headings", height=5)
        self.file_tree.heading("path", text="مسیر فایل")
        self.file_tree.pack(side="left", fill="x", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tag_frame = ttk.LabelFrame(main_frame, text="۲. مدیریت گروه‌های تگ")
        self.tag_frame.pack(fill="both", expand=True, pady=5, padx=5)
        self.notebook = ttk.Notebook(self.tag_frame)
        self.notebook.pack(fill="both", expand=True, pady=5)
        tag_controls_frame = Frame(self.tag_frame)
        tag_controls_frame.pack(fill="x", pady=5)
        Button(tag_controls_frame, text="افزودن گروه", command=self._add_group).pack(side="left")
        Button(tag_controls_frame, text="حذف گروه", command=self._remove_group).pack(side="left", padx=10)

        output_frame = ttk.LabelFrame(main_frame, text="۳. تنظیمات خروجی و پردازش")
        output_frame.pack(fill="x", pady=5, padx=5)
        
        row1 = Frame(output_frame)
        row1.pack(fill="x", pady=2)
        Label(row1, text="بیت‌ریت خروجی (AAC):").pack(side="left", padx=5)
        Entry(row1, textvariable=self.output_bitrate, width=10).pack(side="left", padx=5)
        Label(row1, text="تعداد پردازش همزمان:").pack(side="left", padx=20)
        ttk.Combobox(row1, textvariable=self.process_count, values=[1, 2, 4, 8, 16], width=5).pack(side="left")

        unified_frame = Frame(output_frame)
        unified_frame.pack(fill="x", pady=5)
        self.unified_check = Checkbutton(unified_frame, text="اعمال زمان تگ پایانی یکسان برای همه:", variable=self.unified_time_enabled, command=self._toggle_unified_entry)
        self.unified_check.pack(side="left", padx=5)
        self.unified_entry = Entry(unified_frame, textvariable=self.unified_time_str, width=12, state="disabled")
        self.unified_entry.pack(side="left", padx=5)
        Label(unified_frame, text="(HH:MM:SS)").pack(side="left")

        process_frame = ttk.LabelFrame(main_frame, text="۴. شروع عملیات")
        process_frame.pack(fill="x", pady=5, padx=5)
        self.start_button = Button(process_frame, text="شروع پردازش", command=self._start_processing_thread)
        self.start_button.pack(side="left", padx=10, pady=10)
        self.progress_bar = ttk.Progressbar(process_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", expand=True, side="left", padx=10)
        self.progress_label = Label(process_frame, text="0/0")
        self.progress_label.pack(side="left", padx=5)

        log_frame = ttk.LabelFrame(main_frame, text="گزارش عملیات")
        log_frame.pack(fill="both", expand=True, pady=5, padx=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, state="disabled", height=10)
        self.log_text.pack(fill="both", expand=True, padx=5)
    
    def _toggle_unified_entry(self):
        state = "normal" if self.unified_time_enabled.get() else "disabled"
        self.unified_entry.config(state=state)

    def _update_file_list_ui(self):
        self.file_tree.delete(*self.file_tree.get_children())
        for f in self.file_list:
            self.file_tree.insert("", "end", values=(str(f),))

    def _select_files(self):
        files = filedialog.askopenfilenames(filetypes=(("فایل‌های صوتی", "*.mp3 *.wav *.aac *.m4a"),("همه", "*.*")))
        if files:
            for f in files:
                p = Path(f)
                if p not in self.file_list: self.file_list.append(p)
            self._update_file_list_ui()

    def _select_folder(self):
        d = filedialog.askdirectory()
        if d:
            folder_path = Path(d)
            files_in_folder = sorted([p for p in folder_path.glob("*") if p.suffix.lower() in ['.mp3', '.wav', '.aac', '.m4a']])
            for f in files_in_folder:
                if f not in self.file_list: self.file_list.append(f)
            self._update_file_list_ui()

    def _remove_selected_files(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("هشدار", "هیچ فایلی برای حذف انتخاب نشده است.")
            return
        files_to_remove = [self.file_tree.item(item)['values'][0] for item in selected_items]
        for f_str in files_to_remove:
            try: self.file_list.remove(Path(f_str))
            except ValueError: pass
        self._update_file_list_ui()

    def _clear_file_list(self):
        self.file_list.clear()
        self._update_file_list_ui()

    def _add_group(self):
        group_name = simpledialog.askstring("نام گروه جدید", "یک نام برای گروه تگ جدید وارد کنید:")
        if not group_name or group_name in self.tag_groups:
            messagebox.showwarning("خطا", "نام گروه نمی‌تواند خالی یا تکراری باشد.")
            return

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=group_name)
        group_data = {
            "start_enabled": BooleanVar(), "start_path": StringVar(),
            "start_time_min": StringVar(value="0"), "start_time_sec": StringVar(value="5"),
            "middle_enabled": BooleanVar(), "middle_path": StringVar(),
            "end_enabled": BooleanVar(), "end_path": StringVar(),
        }
        self.tag_groups[group_name] = group_data
        self._create_tag_widgets(tab, group_data)
        self.notebook.select(tab)
        logging.info(f"گروه تگ '{group_name}' ایجاد شد.")

    def _create_tag_widgets(self, parent, data):
        f1 = Frame(parent); f1.pack(fill="x", padx=10, pady=5)
        Checkbutton(f1, text="تگ ابتدایی:", variable=data["start_enabled"]).pack(side="left")
        Entry(f1, textvariable=data["start_path"], state="readonly", width=40).pack(side="left", expand=True, fill="x", padx=5)
        Button(f1, text="انتخاب...", command=lambda: self._select_tag_file(data["start_path"])).pack(side="left")
        Label(f1, text="در زمان:").pack(side="left", padx=(10, 2))
        Entry(f1, textvariable=data["start_time_min"], width=3).pack(side="left")
        Label(f1, text=":").pack(side="left")
        Entry(f1, textvariable=data["start_time_sec"], width=3).pack(side="left")
        Label(f1, text="(دقیقه:ثانیه)").pack(side="left")
        
        f2 = Frame(parent); f2.pack(fill="x", padx=10, pady=5)
        Checkbutton(f2, text="تگ میانی: ", variable=data["middle_enabled"]).pack(side="left")
        Entry(f2, textvariable=data["middle_path"], state="readonly", width=40).pack(side="left", expand=True, fill="x", padx=5)
        Button(f2, text="انتخاب...", command=lambda: self._select_tag_file(data["middle_path"])).pack(side="left")

        f3 = Frame(parent); f3.pack(fill="x", padx=10, pady=5)
        Checkbutton(f3, text="تگ پایانی:", variable=data["end_enabled"]).pack(side="left")
        Entry(f3, textvariable=data["end_path"], state="readonly", width=40).pack(side="left", expand=True, fill="x", padx=5)
        Button(f3, text="انتخاب...", command=lambda: self._select_tag_file(data["end_path"])).pack(side="left")

    def _remove_group(self):
        if not self.notebook.tabs(): return
        selected_tab_index = self.notebook.index(self.notebook.select())
        group_name = self.notebook.tab(selected_tab_index, "text")
        if messagebox.askyesno("تایید حذف", f"آیا از حذف گروه '{group_name}' مطمئن هستید؟"):
            self.notebook.forget(selected_tab_index)
            del self.tag_groups[group_name]
            logging.info(f"گروه '{group_name}' حذف شد.")
            
    def _select_tag_file(self, var):
        f = filedialog.askopenfilename(filetypes=(("فایل‌های صوتی", "*.mp3 *.wav"), ("همه", "*.*")))
        if f: var.set(f)

    def _poll_log_queue(self):
        while True:
            try:
                record = log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.log_text.configure(state="normal")
                self.log_text.insert("end", record + "\n")
                self.log_text.configure(state="disabled")
                self.log_text.see("end")
        self.root.after(100, self._poll_log_queue)

    def _update_progress(self, current, total):
        if total > 0:
            self.progress_bar["value"] = (current / total) * 100
            self.progress_label.config(text=f"{current}/{total}")
        else:
            self.progress_bar["value"] = 0
            self.progress_label.config(text="0/0")
        self.root.update_idletasks()

    def _start_processing_thread(self):
        if not self.file_list:
            messagebox.showerror("خطا", "لطفاً حداقل یک فایل ورودی به لیست اضافه کنید.")
            return
        if not self.tag_groups:
            messagebox.showerror("خطا", "لطفاً حداقل یک گروه تگ ایجاد کنید.")
            return

        self.start_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.end_tag_times_log.clear()

        self.processing_thread = threading.Thread(
            target=self._run_processing, daemon=True
        )
        self.processing_thread.start()

    def _run_processing(self):
        try:
            files_to_process = sorted(self.file_list)
            learned_profiles = []
            training_data = {} 
            
            # --- حالت زمان یکسان ---
            if self.unified_time_enabled.get():
                unified_time_ms = hhmmss_to_ms(self.unified_time_str.get())
                if unified_time_ms is None:
                    messagebox.showerror("خطا", "فرمت زمان وارد شده برای حالت یکسان اشتباه است. لطفاً از HH:MM:SS استفاده کنید.")
                    self.start_button.config(state="normal")
                    return
                
                logging.info(f"شروع پردازش با زمان یکسان {self.unified_time_str.get()} برای همه فایل‌ها.")
                for f in files_to_process:
                    training_data[f] = {'user_time': unified_time_ms}

            # --- حالت آموزش هوشمند ---
            else:
                training_files = []
                prediction_files = list(files_to_process)
                num_training_samples = min(len(files_to_process), 3)

                if num_training_samples > 0 and any(g["end_enabled"].get() for g in self.tag_groups.values()):
                    training_files = random.sample(files_to_process, num_training_samples)
                    prediction_files = [f for f in files_to_process if f not in training_files]
                    
                    for f in training_files:
                        logging.info(f"در حال بارگذاری اطلاعات فایل آموزشی: {f.name}")
                        try:
                            audio = AudioSegment.from_file(f)
                        except Exception as e:
                            logging.error(f"امکان بارگذاری فایل آموزشی {f.name} وجود ندارد: {e}")
                            continue
                        
                        logging.info(f"باز کردن پنجره آموزش برای فایل: {f.name}")
                        self.root.attributes('-disabled', True)
                        trainer = ManualTagTrainer(self.root, audio, f.name)
                        self.root.attributes('-disabled', False)
                        
                        if trainer.final_selected_time is not None:
                            training_data[f] = {'user_time': trainer.final_selected_time}
                            
                            segment_before = audio[trainer.final_selected_time - 10000 : trainer.final_selected_time]
                            segment_at = audio[trainer.final_selected_time : trainer.final_selected_time + 5000]
                            profile = extract_rich_features(segment_before, segment_at, trainer.final_selected_time, len(audio))
                            if profile:
                                profile['safe_zone_end_ms'] = trainer.final_safe_zone_end
                                learned_profiles.append(profile)
                                logging.info(f"پروفایل ویژگی از نقطه {ms_to_hhmmss(trainer.final_selected_time)} در فایل {f.name} یاد گرفته شد.")
                        else:
                            logging.warning(f"آموزش برای فایل {f.name} لغو شد.")

            # --- آماده‌سازی و اجرای وظایف ---
            tasks = []
            for group_name, group_data in self.tag_groups.items():
                for f in files_to_process:
                    task_data_dict = {key: val.get() for key, val in group_data.items()}
                    user_time = training_data.get(f, {}).get('user_time')
                    tasks.append((f, group_name, task_data_dict, learned_profiles, self.output_bitrate.get(), user_time))

            pool_size = self.process_count.get()
            manager = multiprocessing.Manager()
            p_log_queue = manager.Queue()
            
            log_thread = threading.Thread(target=self._log_listener, args=(p_log_queue,), daemon=True)
            log_thread.start()

            with multiprocessing.Pool(processes=pool_size, initializer=init_worker_logging, initargs=(p_log_queue,)) as pool:
                results = pool.starmap(process_file_worker, tasks)
            
            p_log_queue.put(None)
            log_thread.join()

            files_processed = 0
            total_tasks = len(tasks)
            for result in results:
                files_processed += 1
                if result and result['status'] == 'success':
                    group, fname, time_str = result['group_name'], result['filename'], result['end_tag_time']
                    if time_str:
                        if group not in self.end_tag_times_log: self.end_tag_times_log[group] = {}
                        self.end_tag_times_log[group][fname] = time_str
                self._update_progress(files_processed, total_tasks)

            self._write_end_tag_logs()
            logging.info("--- تمام عملیات با موفقیت به پایان رسید. ---")
            messagebox.showinfo("عملیات موفق", "پردازش تمام فایل‌ها به پایان رسید.")

        except Exception as e:
            logging.error(f"یک خطای کلی رخ داد: {e}", exc_info=True)
            messagebox.showerror("خطای کلی", f"یک خطای پیش‌بینی نشده رخ داد: {e}")
        finally:
            self.start_button.config(state="normal")
    
    def _log_listener(self, q):
        while True:
            try:
                record = q.get()
                if record is None: break
                log_queue.put(record)
            except Exception:
                import sys
                print(f"Log listener error: {sys.exc_info()[0]}")

    def _write_end_tag_logs(self):
        if not self.end_tag_times_log or not self.file_list: return
        
        output_dir_base = self.file_list[0].parent
        log_file_path = output_dir_base / "LAST_TAG_TIMES.txt"

        log_lines = []
        sorted_groups = sorted(self.end_tag_times_log.keys())
        for group_name in sorted_groups:
            time_logs = self.end_tag_times_log[group_name]
            sorted_filenames = sorted(time_logs.keys())
            for filename in sorted_filenames:
                log_lines.append(f"{filename} (گروه: {group_name}): {time_logs[filename]}")
                
        if not log_lines:
            return
            
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_lines))
        logging.info(f"فایل گزارش زمان تگ پایانی در مسیر {log_file_path} ذخیره شد.")

def init_worker_logging(q):
    worker_logger = logging.getLogger()
    if not worker_logger.handlers:
         worker_logger.addHandler(QueueHandler(q))
         worker_logger.setLevel(logging.INFO)

def process_file_worker(audio_file_path, group_name, group_data, learned_profiles, bitrate, user_selected_time):
    worker_logger = logging.getLogger()
    try:
        worker_logger.info(f"شروع پردازش '{audio_file_path.name}' برای گروه '{group_name}'")
        main_audio = AudioSegment.from_file(audio_file_path)
        
        if group_data["start_enabled"]:
            try:
                start_tag = AudioSegment.from_file(group_data["start_path"])
                start_pos_min = int(group_data.get("start_time_min", 0))
                start_pos_sec = int(group_data.get("start_time_sec", 0))
                start_pos_ms = (start_pos_min * 60 + start_pos_sec) * 1000
                main_audio = main_audio.overlay(start_tag, position=start_pos_ms)
            except Exception as e:
                worker_logger.error(f"خطا در اعمال تگ ابتدایی به {audio_file_path.name}: {e}")

        if group_data["middle_enabled"]:
            try:
                middle_tag = AudioSegment.from_file(group_data["middle_path"])
                middle_pos = (len(main_audio) / 2) - (len(middle_tag) / 2)
                main_audio = main_audio.overlay(middle_tag, position=middle_pos)
            except Exception as e:
                worker_logger.error(f"خطا در اعمال تگ میانی به {audio_file_path.name}: {e}")
        
        end_tag_time_str = None
        if group_data["end_enabled"]:
            try:
                end_tag = AudioSegment.from_file(group_data["end_path"])
                
                if user_selected_time is not None:
                    worker_logger.info(f"استفاده از زمان انتخابی کاربر: {ms_to_hhmmss(user_selected_time)}")
                    end_pos_ms = user_selected_time
                else:
                    end_pos_ms = find_end_tag_position(main_audio, learned_profiles, worker_logger)
                
                main_audio = main_audio.overlay(end_tag, position=end_pos_ms)
                end_tag_time_str = ms_to_hhmmss(end_pos_ms)
                worker_logger.info(f"تگ پایانی در زمان {end_tag_time_str} برای فایل {audio_file_path.name} قرار گرفت.")
            except Exception as e:
                worker_logger.error(f"خطا در اعمال تگ پایانی به {audio_file_path.name}: {e}")
                
        base_dir = audio_file_path.parent
        output_dir = base_dir / f"output_{group_name}"
        output_dir.mkdir(exist_ok=True)
        # تغییر نام و فرمت خروجی
        output_file_path = output_dir / f"{audio_file_path.stem}.aac"
        main_audio.export(output_file_path, format="adts", bitrate=bitrate)
        
        return {
            "status": "success", "filename": audio_file_path.name,
            "group_name": group_name, "end_tag_time": end_tag_time_str
        }
    except Exception as e:
        worker_logger.error(f"خطای غیرمنتظره در پردازشگر برای فایل {audio_file_path.name}: {e}")
        return {"status": "error", "filename": audio_file_path.name, "group_name": group_name, "end_tag_time": None}

def find_end_tag_position(audio, learned_profiles, logger):
    duration_ms = len(audio)

    if learned_profiles:
        logger.info("استفاده از سیستم امتیازدهی پیشرفته برای پیدا کردن نقطه تگ پایانی...")
        
        avg_learned_profile = {}
        for key in learned_profiles[0]:
            if isinstance(learned_profiles[0][key], np.ndarray):
                avg_learned_profile[key] = np.mean([p[key] for p in learned_profiles], axis=0)
            else:
                avg_learned_profile[key] = np.mean([p[key] for p in learned_profiles])
        
        avg_safe_zone_percent = np.mean([(p['safe_zone_end_ms'] / p['total_duration_ms']) for p in learned_profiles if 'total_duration_ms' in p and p['total_duration_ms'] > 0])

        search_end_ms = int(duration_ms * avg_safe_zone_percent)
        search_start_ms = int(search_end_ms - (duration_ms * 0.25))
        search_start_ms = max(0, search_start_ms)

        best_pos = None
        best_score = -1
        
        weights = {'position': 0.4, 'silence': 0.2, 'energy': 0.25, 'music': 0.15}

        for i in range(search_start_ms, search_end_ms, 2000):
            segment_before = audio[i - 10000 : i]
            segment_at = audio[i : i + 5000]
            candidate_profile = extract_rich_features(segment_before, segment_at, i, duration_ms)
            if not candidate_profile: continue

            pos_score = 1 - (abs(candidate_profile['relative_position'] - avg_learned_profile['relative_position']) / 0.1)
            pos_score = max(0, pos_score)
            
            silence_score_1 = 1 - abs(candidate_profile['silence_count'] - avg_learned_profile['silence_count']) / (avg_learned_profile['silence_count'] + 1e-6)
            silence_score_2 = 1 - abs(candidate_profile['total_silence_duration'] - avg_learned_profile['total_silence_duration']) / (avg_learned_profile['total_silence_duration'] + 1e-6)
            silence_score = max(0, (silence_score_1 + silence_score_2) / 2)

            energy_score = 1 - abs(candidate_profile['energy_ratio'] - avg_learned_profile['energy_ratio']) / (avg_learned_profile['energy_ratio'] + 1e-6)
            energy_score = max(0, energy_score)

            music_dist = np.linalg.norm(candidate_profile['mfccs_mean'] - avg_learned_profile['mfccs_mean'])
            music_score = 1 / (1 + music_dist)

            total_score = (weights['position'] * pos_score +
                           weights['silence'] * silence_score +
                           weights['energy'] * energy_score +
                           weights['music'] * music_score)
            
            if total_score > best_score:
                best_score = total_score
                best_pos = i
        
        if best_pos is None:
            logger.warning("هیچ نقطه مناسبی بر اساس یادگیری یافت نشد. استفاده از حالت خودکار.")
            return find_end_tag_position(audio, [], logger) 
            
        logger.info(f"بهترین نقطه بر اساس امتیازدهی: {ms_to_hhmmss(best_pos)} با امتیاز {best_score:.2f}")
        return best_pos

    logger.info("استفاده از حالت خودکار (VAD) برای پیدا کردن نقطه تگ پایانی...")
    try:
        y = np.array(audio.get_array_of_samples()).astype(np.float32)
        non_silent_intervals = librosa.effects.split(y, top_db=40, frame_length=2048, hop_length=512)
        
        if len(non_silent_intervals) > 0:
            last_speech_end_sample = non_silent_intervals[-1][1]
            last_speech_end_ms = librosa.samples_to_time(last_speech_end_sample, sr=audio.frame_rate) * 1000
            
            buffer_ms = 2000 
            final_pos = last_speech_end_ms + buffer_ms
            logger.info(f"آخرین صحبت در {ms_to_hhmmss(last_speech_end_ms)}, موقعیت تگ در {ms_to_hhmmss(final_pos)}")
            return int(final_pos)

    except Exception as e:
        logger.error(f"خطا در حالت خودکار تشخیص تگ پایانی: {e}")

    fallback_pos = duration_ms - 30000
    logger.warning(f"امکان تشخیص خودکار وجود نداشت. از موقعیت پیش‌فرض {ms_to_hhmmss(fallback_pos)} استفاده می‌شود.")
    return fallback_pos

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    log_filename = "audio_tagger.log"
    if os.path.exists(log_filename):
        try:
            os.remove(log_filename)
        except PermissionError:
            pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(processName)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_filename, mode='w', encoding='utf-8')],
    )
    logger = logging.getLogger()
    logger.addHandler(QueueHandler(log_queue))

    root = Tk()
    app = AudioTaggerApp(root)
    root.mainloop()
