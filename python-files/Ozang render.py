import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import re
import queue
import sys
import shutil
import random
import math

class FFmpegGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OzangMusic v.3")
        self.root.geometry("720x540")
        self.root.resizable(True, True)

        self.cva_log_queue = queue.Queue()
        self.cva_temp_files = []
        self.cva_video_file_path = ""
        self.cva_audio_file_paths = {}
        if sys.platform == "win32":
            self.subprocess_flags = subprocess.CREATE_NO_WINDOW
        else:
            self.subprocess_flags = 0

        self.tab_control = ttk.Notebook(root)

        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Gabung Video')

        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text='Loop Video')

        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab3, text='Konversi Video')

        self.tab4 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab4, text='Gabung Audio')

        self.tab5 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab5, text='Gabung Video & Audio')

        self.tab6 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab6, text='Konversi Audio')

        self.tab_control.pack(expand=1, fill="both")

        self.setup_combine_videos_tab()
        self.setup_loop_video_tab()             # <- sudah pakai durasi jam
        self.setup_convert_video_tab()
        self.setup_combine_audio_tab()
        self.setup_combine_video_audio_tab()
        self.setup_audio_converter_tab()

        self.status_var = tk.StringVar(value="Siap")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.check_ffmpeg()
        self.total_duration_seconds = 0
        self.check_log_queue_cva()

    # ---------- Util dasar ----------

    def check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=self.subprocess_flags)
            self.status_var.set("FFmpeg terdeteksi. Aplikasi siap digunakan.")
        except FileNotFoundError:
            messagebox.showerror("Error", "FFmpeg tidak ditemukan. Pastikan FFmpeg sudah terinstal dan tersedia di PATH sistem Anda.")
            self.status_var.set("Error: FFmpeg tidak ditemukan")

    def get_duration(self, file_path):
        try:
            command = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=self.subprocess_flags)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
            return 0

    def run_ffmpeg_command(self, command, success_message, cleanup_file=None):
        self.set_ui_state(False)
        def run_command_thread():
            self.root.after(0, self.status_var.set, "Mempersiapkan...")
            try:
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, creationflags=self.subprocess_flags,
                    encoding='utf-8', errors='ignore'
                )
                stderr_output = []
                for line in iter(process.stderr.readline, ""):
                    line = line.strip()
                    if not line:
                        continue
                    stderr_output.append(line)
                    if "time=" in line and "speed=" in line:
                        time_match = re.search(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})", line)
                        if time_match and self.total_duration_seconds > 0:
                            h, m, s_ms = time_match.group(1).split(':')
                            s, ms = s_ms.split('.')
                            elapsed = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 100
                            progress = min(100, (elapsed / self.total_duration_seconds) * 100)
                            self.root.after(0, self.status_var.set, f"Proses: {progress:.2f}%")
                        else:
                            self.root.after(0, self.status_var.set, "Memproses...")

                process.wait()
                if process.returncode == 0:
                    self.root.after(0, lambda: messagebox.showinfo("Sukses", success_message))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error FFmpeg", "\n".join(stderr_output[-15:])))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error Aplikasi", str(e)))
            finally:
                if cleanup_file and os.path.exists(cleanup_file):
                    os.remove(cleanup_file)
                self.total_duration_seconds = 0
                self.set_ui_state(True)

        threading.Thread(target=run_command_thread, daemon=True).start()

    def browse_input_file(self, var, file_type):
        types = {
            "video": [("Video", "*.mp4 *.mkv *.avi *.mov")],
            "audio": [("Audio", "*.mp3 *.wav *.aac *.flac *.m4a")],
            "all":   [("All", "*.*")]
        }
        path = filedialog.askopenfilename(filetypes=types.get(file_type, []))
        if path:
            var.set(path)

    def browse_output_file(self, var, ext):
        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{ext.upper()} File", f"*.{ext}")])
        if path:
            var.set(path)

    def set_ui_state(self, is_enabled):
        state = 'normal' if is_enabled else 'disabled'
        self.status_var.set("Siap" if is_enabled else "Sedang memproses...")
        for i in range(self.tab_control.index("end")):
            try:
                self.tab_control.tab(i, state=state)
            except tk.TclError:
                pass

    # ---------- Tab 1: Gabung Video (concat copy) ----------

    def setup_combine_videos_tab(self):
        main_frame = ttk.LabelFrame(self.tab1, text="Gabung Video Menjadi Satu (Mode Cepat)")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.video_listbox = tk.Listbox(list_frame, height=5, yscrollcommand=scrollbar.set)
        self.video_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.video_listbox.yview)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill="x", padx=5)

        ttk.Button(button_frame, text="Tambah Video", command=self.add_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Video", command=self.remove_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Naik", command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Turun", command=self.move_down).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(pady=10, fill="x", padx=10)

        ttk.Label(output_frame, text="File Output:").pack(side=tk.LEFT, padx=5)
        self.output_var_combine = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var_combine).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=lambda: self.browse_output_file(self.output_var_combine, "mp4")).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Mulai Proses Penggabungan Cepat", command=self.process_combine_videos).pack(pady=10)
        self.video_paths = []

    def add_video(self):
        paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")])
        for path in paths:
            if path not in self.video_paths:
                self.video_paths.append(path)
                self.video_listbox.insert(tk.END, os.path.basename(path))

    def remove_video(self):
        for index in reversed(self.video_listbox.curselection()):
            self.video_listbox.delete(index)
            del self.video_paths[index]

    def _move_item(self, listbox, path_list, direction):
        selection = listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        new_idx = idx + direction
        if 0 <= new_idx < listbox.size():
            text = listbox.get(idx)
            listbox.delete(idx)
            listbox.insert(new_idx, text)
            listbox.selection_set(new_idx)
            listbox.activate(new_idx)
            if path_list is not None:
                path = path_list.pop(idx)
                path_list.insert(new_idx, path)

    def move_up(self):
        self._move_item(self.video_listbox, self.video_paths, -1)

    def move_down(self):
        self._move_item(self.video_listbox, self.video_paths, 1)

    def process_combine_videos(self):
        if len(self.video_paths) < 2:
            messagebox.showwarning("Peringatan", "Pilih setidaknya dua video untuk digabungkan.")
            return

        output_file = self.output_var_combine.get()
        if not output_file:
            messagebox.showwarning("Peringatan", "File output belum ditentukan.")
            return

        messagebox.showinfo(
            "Info Mode Cepat",
            "Anda menggunakan Mode Cepat (tanpa render ulang).\n"
            "Proses akan sangat cepat, tetapi bisa gagal jika format video (resolusi, codec) tidak seragam."
        )

        list_file = "ffmpeg_video_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for path in self.video_paths:
                f.write("file '" + path.replace('\\', '/') + "'\n")

        command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_file]
        self.run_ffmpeg_command(command, "Proses penggabungan cepat selesai.", cleanup_file=list_file)

    # ---------- Tab 2: Loop Video (berdasarkan durasi jam) ----------

    def setup_loop_video_tab(self):
        main_frame = ttk.LabelFrame(self.tab2, text="Panjangkan Video (Loop)")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10, fill="x")

        ttk.Label(input_frame, text="File Input:").pack(side=tk.LEFT, padx=5)
        self.input_var_loop = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var_loop).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_input_file(self.input_var_loop, "video")).pack(side=tk.LEFT, padx=5)

        loop_frame = ttk.Frame(main_frame)
        loop_frame.pack(pady=10, fill="x")

        ttk.Label(loop_frame, text="Durasi Target (Jam):").pack(side=tk.LEFT, padx=5)
        self.loop_hours_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(loop_frame, from_=0.25, to=48.0, increment=0.25, textvariable=self.loop_hours_var, width=6).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(pady=10, fill="x")

        ttk.Label(output_frame, text="File Output:").pack(side=tk.LEFT, padx=5)
        self.output_var_loop = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var_loop).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=lambda: self.browse_output_file(self.output_var_loop, "mp4")).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Proses Loop Video", command=self.process_loop_video).pack(pady=10)

    def process_loop_video(self):
        input_file = self.input_var_loop.get()
        if not input_file:
            messagebox.showwarning("Peringatan", "File input belum dipilih.")
            return

        output_file = self.output_var_loop.get()
        if not output_file:
            messagebox.showwarning("Peringatan", "File output belum ditentukan.")
            return

        try:
            target_hours = float(self.loop_hours_var.get() or 0)
        except Exception:
            target_hours = 0.0
        if target_hours <= 0:
            messagebox.showwarning("Peringatan", "Durasi target harus lebih dari 0.")
            return

        video_duration = self.get_duration(input_file)
        if video_duration <= 0:
            messagebox.showerror("Error", "Gagal membaca durasi video. Pastikan file valid.")
            return

        target_seconds = target_hours * 3600.0
        loop_count = max(1, math.ceil(target_seconds / video_duration))

        # supaya indikator progress jalan (baca 'time=' dari log ffmpeg)
        self.total_duration_seconds = target_seconds

        # -stream_loop (loop_count-1) + -t agar dipotong pas pada target
        if loop_count <= 1:
            command = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", "-t", str(target_seconds), output_file]
        else:
            command = [
                "ffmpeg", "-y",
                "-stream_loop", str(loop_count - 1), "-i", input_file,
                "-c", "copy", "-t", str(target_seconds), output_file
            ]

        self.run_ffmpeg_command(command, f"Proses loop video selesai. (~{loop_count}x pengulangan)")

    # ---------- Tab 3: Konversi Video ----------

    def setup_convert_video_tab(self):
        main_frame = ttk.LabelFrame(self.tab3, text="Konversi Video")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10, fill="x")

        ttk.Label(input_frame, text="File Input:").pack(side=tk.LEFT, padx=5)
        self.input_var_convert = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var_convert).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_input_file(self.input_var_convert, "video")).pack(side=tk.LEFT, padx=5)

        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(pady=10, fill="x")

        ttk.Label(settings_frame, text="CRF (0-51, default 23):").pack(side=tk.LEFT, padx=5)
        self.crf_var = tk.IntVar(value=23)
        ttk.Spinbox(settings_frame, from_=0, to=51, textvariable=self.crf_var, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="Preset:").pack(side=tk.LEFT, padx=5)
        presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
        self.preset_var = tk.StringVar(value="fast")
        ttk.Combobox(settings_frame, textvariable=self.preset_var, values=presets, width=10, state="readonly").pack(side=tk.LEFT, padx=5)

        audio_frame = ttk.Frame(main_frame)
        audio_frame.pack(pady=10, fill="x")

        ttk.Label(audio_frame, text="Audio Bitrate (kbps):").pack(side=tk.LEFT, padx=5)
        self.audio_bitrate_var = tk.IntVar(value=192)
        ttk.Spinbox(audio_frame, from_=32, to=320, increment=32, textvariable=self.audio_bitrate_var, width=5).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(pady=10, fill="x")

        ttk.Label(output_frame, text="File Output:").pack(side=tk.LEFT, padx=5)
        self.output_var_convert = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var_convert).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=lambda: self.browse_output_file(self.output_var_convert, "mp4")).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Proses Konversi", command=self.process_convert_video).pack(pady=10)

    def process_convert_video(self):
        input_file = self.input_var_convert.get()
        if not input_file:
            return messagebox.showwarning("Peringatan", "File input belum dipilih.")
        output_file = self.output_var_convert.get()
        if not output_file:
            return messagebox.showwarning("Peringatan", "File output belum ditentukan.")

        self.total_duration_seconds = self.get_duration(input_file)
        command = [
            "ffmpeg", "-y", "-i", input_file,
            "-c:v", "libx264", "-crf", str(self.crf_var.get()), "-preset", self.preset_var.get(),
            "-c:a", "aac", "-b:a", f"{self.audio_bitrate_var.get()}k",
            output_file
        ]
        self.run_ffmpeg_command(command, "Proses konversi video selesai.")

    # ---------- Tab 4: Gabung Audio ----------

    def setup_combine_audio_tab(self):
        main_frame = ttk.LabelFrame(self.tab4, text="Gabung Audio Menjadi Satu")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.audio_listbox = tk.Listbox(list_frame, height=5, yscrollcommand=scrollbar.set)
        self.audio_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.audio_listbox.yview)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill="x")

        ttk.Button(button_frame, text="Tambah Audio", command=self.add_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Audio", command=self.remove_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Naik", command=self.move_up_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Turun", command=self.move_down_audio).pack(side=tk.LEFT, padx=5)

        bitrate_frame = ttk.Frame(main_frame)
        bitrate_frame.pack(pady=5, fill="x")
        ttk.Label(bitrate_frame, text="Audio Bitrate Output (kbps):").pack(side=tk.LEFT, padx=5)
        self.output_audio_bitrate_var = tk.IntVar(value=192)
        ttk.Spinbox(bitrate_frame, from_=32, to=320, increment=32, textvariable=self.output_audio_bitrate_var, width=5).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(pady=10, fill="x")

        ttk.Label(output_frame, text="File Output:").pack(side=tk.LEFT, padx=5)
        self.output_var_audio = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var_audio).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=lambda: self.browse_output_file(self.output_var_audio, "mp3")).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Proses Penggabungan Audio", command=self.process_combine_audio).pack(pady=10)
        self.audio_paths = []

    def add_audio(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.flac *.m4a")])
        for path in paths:
            if path not in self.audio_paths:
                self.audio_paths.append(path)
                self.audio_listbox.insert(tk.END, os.path.basename(path))

    def remove_audio(self):
        for index in reversed(self.audio_listbox.curselection()):
            self.audio_listbox.delete(index)
            del self.audio_paths[index]

    def move_up_audio(self):
        self._move_item(self.audio_listbox, self.audio_paths, -1)

    def move_down_audio(self):
        self._move_item(self.audio_listbox, self.audio_paths, 1)

    def process_combine_audio(self):
        if len(self.audio_paths) < 2:
            return messagebox.showwarning("Peringatan", "Pilih setidaknya dua file audio.")
        output_file = self.output_var_audio.get()
        if not output_file:
            return messagebox.showwarning("Peringatan", "File output belum ditentukan.")

        self.total_duration_seconds = sum(self.get_duration(path) for path in self.audio_paths)

        command = ["ffmpeg", "-y"]
        for path in self.audio_paths:
            command.extend(["-i", path])

        filter_complex = "".join([f"[{i}:a]" for i in range(len(self.audio_paths))]) + f"concat=n={len(self.audio_paths)}:v=0:a=1[aout]"
        command.extend(["-filter_complex", filter_complex, "-map", "[aout]"])
        command.extend(["-acodec", "libmp3lame", "-b:a", f"{self.output_audio_bitrate_var.get()}k", output_file])

        self.run_ffmpeg_command(command, "Proses penggabungan audio selesai.")

    # ---------- Tab 5: Gabung Video & Audio (durasi target jam) ----------

    def setup_combine_video_audio_tab(self):
        main_frame = ttk.Frame(self.tab5, padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)

        # Langkah 1
        lf1 = ttk.Labelframe(main_frame, text=" Langkah 1: Pilih File Video & Audio ")
        lf1.grid(row=0, column=0, sticky="ew", pady=(0,10))
        for c in range(3):
            lf1.columnconfigure(c, weight=1 if c==1 else 0)

        self.cva_video_path_var = tk.StringVar(value="Belum ada video dipilih")
        ttk.Button(lf1, text="Pilih File Video...", command=self.cva_select_video_file).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(lf1, textvariable=self.cva_video_path_var, state="readonly").grid(row=0, column=1, sticky="ew", padx=(0,10), pady=5)

        self.cva_include_original_audio = tk.BooleanVar(value=True)
        ttk.Checkbutton(lf1, text="Sertakan & gabungkan audio asli dari video (jika ada)", variable=self.cva_include_original_audio).grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

        ttk.Button(lf1, text="Tambah File Audio...", command=self.cva_add_audio_files).grid(row=2, column=0, columnspan=2, padx=10, pady=(5,10), sticky="ew")

        # Langkah 2
        lf2 = ttk.Labelframe(main_frame, text=" Langkah 2: Atur & Urutkan File Audio ")
        lf2.grid(row=1, column=0, sticky="nsew", pady=(0,10))
        lf2.columnconfigure(0, weight=1); lf2.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(lf2)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        list_frame.rowconfigure(0, weight=1); list_frame.columnconfigure(0, weight=1)

        self.cva_audio_listbox = tk.Listbox(list_frame, font=("Segoe UI", 9), height=6)
        self.cva_audio_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.cva_audio_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.cva_audio_listbox.config(yscrollcommand=scrollbar.set)

        btns = ttk.Frame(lf2)
        btns.grid(row=0, column=1, padx=(5,10), pady=10, sticky="ns")
        ttk.Button(btns, text="Naik", command=lambda: self._move_item(self.cva_audio_listbox, None, -1)).pack(fill="x", pady=(0,5))
        ttk.Button(btns, text="Turun", command=lambda: self._move_item(self.cva_audio_listbox, None, 1)).pack(fill="x", pady=(0,5))
        ttk.Button(btns, text="Acak", command=self.cva_shuffle_audio).pack(fill="x", pady=(0,5))
        ttk.Button(btns, text="Hapus", command=self.cva_remove_audio).pack(fill="x", pady=(0,5))
        ttk.Button(btns, text="Bersihkan", command=self.cva_clear_audio).pack(fill="x")

        # Langkah 3
        lf3 = ttk.Labelframe(main_frame, text=" Langkah 3: Ekstrak Durasi (Opsional) ")
        lf3.grid(row=2, column=0, sticky="nsew", pady=(0,10))
        lf3.columnconfigure(0, weight=1)
        self.cva_total_audio_label = ttk.Label(lf3, text="Total Durasi Audio: 00:00:00")
        self.cva_total_audio_label.grid(row=0, column=1, sticky="e", padx=10, pady=(8,0))
        ttk.Button(lf3, text="Buat & Salin Tracklist", command=self.cva_build_and_copy_tracklist).grid(row=0, column=0, sticky="w", padx=10, pady=(8,0))

        self.cva_tracklist_text = scrolledtext.ScrolledText(lf3, height=4, wrap=tk.WORD)
        self.cva_tracklist_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,10))
        self.cva_tracklist_text.insert("1.0", "Klik tombol 'Buat & Salin Tracklist' setelah semua audio diatur...")

        # Langkah 4
        lf4 = ttk.Labelframe(main_frame, text=" Langkah 4: Tentukan Durasi Output (Jam) ")
        lf4.grid(row=3, column=0, sticky="ew", pady=(0,10))
        ttk.Label(lf4, text="Durasi Target (Jam):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.cva_target_hours_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(lf4, from_=0.25, to=48.0, increment=0.25, textvariable=self.cva_target_hours_var, width=6).grid(row=0, column=1, sticky="w")
        self.cva_video_loop_info = ttk.Label(lf4, text="Pengulangan Video: N/A")
        self.cva_video_loop_info.grid(row=0, column=2, padx=10, sticky="w")

        # Langkah 5
        lf5 = ttk.Labelframe(main_frame, text=" Langkah 5: Tentukan File Output ")
        lf5.grid(row=4, column=0, sticky="ew", pady=(0,5))
        ttk.Label(lf5, text="Simpan Sebagai:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.cva_output_path_var = tk.StringVar()
        ttk.Entry(lf5, textvariable=self.cva_output_path_var).grid(row=0, column=1, sticky="ew", padx=(0,10), pady=8)
        lf5.columnconfigure(1, weight=1)
        ttk.Button(lf5, text="Browse...", command=lambda: self.browse_output_file(self.cva_output_path_var, "mp4")).grid(row=0, column=2, padx=10)

        # Tombol Proses
        self.cva_process_button = ttk.Button(main_frame, text="MULAI PROSES GABUNG & LOOP", command=self.cva_start_processing_thread)
        self.cva_process_button.grid(row=5, column=0, sticky="ew", pady=5)

        # Log
        log_frame = ttk.Labelframe(main_frame, text=" Log Proses ")
        log_frame.grid(row=6, column=0, sticky="nsew", pady=(5, 0))
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        self.cva_log_text = scrolledtext.ScrolledText(log_frame, state="disabled", wrap=tk.WORD, font=("Courier New", 9), height=4)
        self.cva_log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Internal
        self.cva_audio_file_paths = {}
        self.cva_video_file_path = ""

    def cva_log(self, message):
        self.cva_log_queue.put(message)

    def check_log_queue_cva(self):
        while not self.cva_log_queue.empty():
            message = self.cva_log_queue.get_nowait()
            if self.cva_log_text.winfo_exists():
                self.cva_log_text.config(state='normal')
                self.cva_log_text.insert(tk.END, message + '\n')
                self.cva_log_text.config(state='disabled')
                self.cva_log_text.see(tk.END)
        self.root.after(100, self.check_log_queue_cva)

    def cva_select_video_file(self):
        self.browse_input_file(self.cva_video_path_var, "video")
        self.cva_video_file_path = self.cva_video_path_var.get()
        try:
            vdur = self.get_duration(self.cva_video_file_path)
            th = float(self.cva_target_hours_var.get())
            if vdur and th:
                loops = math.ceil((th*3600)/vdur)
                self.cva_video_loop_info.config(text=f"Pengulangan Video: ~{loops}x")
        except Exception:
            self.cva_video_loop_info.config(text="Pengulangan Video: N/A")

    def cva_add_audio_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav *.aac *.flac *.m4a")])
        for path in paths:
            filename = os.path.basename(path)
            if filename not in self.cva_audio_file_paths:
                self.cva_audio_file_paths[filename] = path
                self.cva_audio_listbox.insert(tk.END, filename)
        self.cva_update_total_audio_label()

    def cva_remove_audio(self):
        for index in reversed(self.cva_audio_listbox.curselection()):
            name = self.cva_audio_listbox.get(index)
            if name in self.cva_audio_file_paths:
                del self.cva_audio_file_paths[name]
            self.cva_audio_listbox.delete(index)
        self.cva_update_total_audio_label()

    def cva_clear_audio(self):
        self.cva_audio_listbox.delete(0, tk.END)
        self.cva_audio_file_paths.clear()
        self.cva_update_total_audio_label()

    def cva_shuffle_audio(self):
        items = list(self.cva_audio_listbox.get(0, tk.END))
        random.shuffle(items)
        self.cva_audio_listbox.delete(0, tk.END)
        for it in items:
            self.cva_audio_listbox.insert(tk.END, it)
        self.cva_update_total_audio_label()

    def cva_seconds_to_hhmmss(self, secs):
        secs = int(round(secs))
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def cva_build_and_copy_tracklist(self):
        names = list(self.cva_audio_listbox.get(0, tk.END))
        if not names:
            messagebox.showwarning("Peringatan", "Tidak ada audio di daftar.")
            return
        lines = []
        total = 0.0
        for i, nm in enumerate(names, 1):
            path = self.cva_audio_file_paths.get(nm, "")
            d = self.get_duration(path) if path else 0.0
            total += d
            lines.append(f"{i:02d}. {nm} — {self.cva_seconds_to_hhmmss(d)}")
        lines.append("")
        lines.append(f"Total: {self.cva_seconds_to_hhmmss(total)}")
        text = "\n".join(lines)
        self.cva_tracklist_text.delete("1.0", tk.END)
        self.cva_tracklist_text.insert("1.0", text)
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except Exception:
            pass
        self.cva_update_total_audio_label()

    def cva_update_total_audio_label(self):
        total = 0.0
        for nm in self.cva_audio_listbox.get(0, tk.END):
            p = self.cva_audio_file_paths.get(nm, "")
            total += self.get_duration(p) if p else 0.0
        self.cva_total_audio_label.config(text=f"Total Durasi Audio: {self.cva_seconds_to_hhmmss(total)}")

    def cva_has_audio_stream(self, file_path):
        try:
            cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", file_path]
            r = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=self.subprocess_flags)
            return bool(r.stdout.strip())
        except Exception:
            return False

    def cva_start_processing_thread(self):
        if not self.cva_video_file_path or not os.path.exists(self.cva_video_file_path):
            return messagebox.showerror("Error", "File video tidak valid.")
        ordered_audio_names = self.cva_audio_listbox.get(0, tk.END)
        if not ordered_audio_names:
            return messagebox.showerror("Error", "Tidak ada file audio dalam daftar.")
        try:
            target_hours = float(self.cva_target_hours_var.get())
            if target_hours <= 0:
                raise ValueError
        except Exception:
            return messagebox.showerror("Error", "Durasi target harus berupa angka > 0.")

        self.set_ui_state(False)
        self.cva_log("\n" + "="*50 + "\n=== MEMULAI PROSES ===\n" + "="*50)
        self.status_var.set("Sedang Memproses... Silakan Tunggu dan lihat Log.")

        work_dir = os.path.dirname(self.cva_video_file_path)
        ordered_audio_paths = [self.cva_audio_file_paths[name] for name in ordered_audio_names]
        include_orig = self.cva_include_original_audio.get()
        out_path = self.cva_output_path_var.get().strip() or os.path.join(work_dir, "Video_Siap_UPLOAD.mp4")

        thread = threading.Thread(
            target=self.cva_run_processing_logic,
            args=(work_dir, self.cva_video_file_path, ordered_audio_paths, target_hours, include_orig, out_path),
            daemon=True
        )
        thread.start()

    def cva_run_processing_logic(self, work_dir, video_input_original_path, ordered_audio_paths, target_hours, include_orig, final_output):
        self.cva_temp_files = []
        original_dir = os.getcwd()
        os.chdir(work_dir)
        try:
            # 1) Gabungkan audio menjadi satu file
            self.cva_log("Menggabungkan semua file audio...")
            temp_music_path = os.path.join(work_dir, "temp_Gabung_Musik.mp3")
            self.cva_temp_files.append(temp_music_path)
            inputs = []
            for path in ordered_audio_paths:
                inputs.extend(["-i", path])
            filter_complex = "".join(f"[{i}:a]" for i in range(len(ordered_audio_paths))) + f"concat=n={len(ordered_audio_paths)}:v=0:a=1[a]"
            self.cva_run_command(["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex, "-map", "[a]", temp_music_path])

            # 2) Durasi target dalam detik
            duration = max(1.0, float(target_hours) * 3600.0)
            self.cva_log(f"Durasi target: {self.cva_seconds_to_hhmmss(duration)}")

            # 3) Buat video hingga durasi target
            self.cva_log("Membuat video dasar hingga durasi target...")
            temp_merged_video = os.path.join(work_dir, "temp_merged_video.mp4")
            self.cva_temp_files.append(temp_merged_video)

            has_audio = self.cva_has_audio_stream(video_input_original_path)

            if include_orig and has_audio:
                cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "-1", "-i", video_input_original_path,
                    "-stream_loop", "-1", "-i", temp_music_path,
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(duration), temp_merged_video
                ]
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "-1", "-i", video_input_original_path,
                    "-stream_loop", "-1", "-i", temp_music_path,
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(duration), temp_merged_video
                ]
            self.cva_run_command(cmd)

            # 4) Simpan output final
            final_output_name = final_output
            if not os.path.isabs(final_output_name):
                final_output_name = os.path.join(work_dir, final_output_name)

            self.cva_log("Menyimpan output final...")
            self.cva_run_command(["ffmpeg", "-y", "-i", temp_merged_video, "-c", "copy", final_output_name])

            self.cva_log("\n" + "="*50 + "\n✅ === PROSES SELESAI ===\n" + "="*50)
            self.cva_log(f"File yang dihasilkan:\n✅ {final_output_name}")
            self.status_var.set(f"Selesai! {os.path.basename(final_output_name)} telah dibuat.")
        except (subprocess.CalledProcessError, ValueError) as e:
            error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
            self.cva_log(f"❌ Error: {error_msg}")
            self.status_var.set("Error! Cek log untuk detail.")
        except Exception as e:
            self.cva_log(f"❌ Error Tak Terduga: {e}")
            self.status_var.set("Error! Cek log untuk detail.")
        finally:
            self.cva_log("\nMembersihkan file temporer...")
            for f in self.cva_temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                        self.cva_log(f"  - Dihapus: {os.path.basename(f)}")
                    except OSError as err:
                        self.cva_log(f"  - Gagal hapus {os.path.basename(f)}: {err}")
            os.chdir(original_dir)
            self.set_ui_state(True)

    def cva_run_command(self, cmd):
        return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', creationflags=self.subprocess_flags)

    # ---------- Tab 6: Konversi Audio ----------

    def setup_audio_converter_tab(self):
        main_frame = ttk.LabelFrame(self.tab6, text="Konversi Berbagai Format Audio")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10, fill="x")
        ttk.Label(input_frame, text="File Input:").pack(side=tk.LEFT, padx=5)
        self.input_var_audio_conv = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var_audio_conv).pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_input_file(self.input_var_audio_conv, "all")).pack(side=tk.LEFT, padx=5)

        options_frame = ttk.Frame(main_frame)
        options_frame.pack(pady=10, fill="x")
        ttk.Label(options_frame, text="Format Output:").pack(side=tk.LEFT, padx=5)
        self.output_format_var = tk.StringVar(value="MP3")
        formats = ["MP3", "AAC (untuk M4A)", "WAV"]
        ttk.Combobox(options_frame, textvariable=self.output_format_var, values=formats, width=15, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="Bitrate (kbps):").pack(side=tk.LEFT, padx=5)
        self.audio_bitrate_var_conv = tk.IntVar(value=192)
        ttk.Spinbox(options_frame, from_=32, to=320, increment=32, textvariable=self.audio_bitrate_var_conv, width=7).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(pady=10, fill="x")
        ttk.Label(output_frame, text="File Output:").pack(side=tk.LEFT, padx=5)
        self.output_var_audio_conv = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var_audio_conv).pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        def browse_audio_output():
            ext = {"MP3": "mp3", "AAC (untuk M4A)": "m4a", "WAV": "wav"}.get(self.output_format_var.get(), "mp3")
            self.browse_output_file(self.output_var_audio_conv, ext)
        ttk.Button(output_frame, text="Browse", command=browse_audio_output).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Mulai Proses Konversi", command=self.process_audio_conversion).pack(pady=20)

    def process_audio_conversion(self):
        input_file = self.input_var_audio_conv.get()
        if not input_file:
            return messagebox.showwarning("Peringatan", "File input belum dipilih.")
        output_file = self.output_var_audio_conv.get()
        if not output_file:
            return messagebox.showwarning("Peringatan", "File output belum ditentukan.")

        self.total_duration_seconds = self.get_duration(input_file)

        output_format = self.output_format_var.get()
        codec_map = {"MP3": "libmp3lame", "AAC (untuk M4A)": "aac", "WAV": "pcm_s16le"}
        audio_codec = codec_map[output_format]

        if output_format == "WAV":
            command = ["ffmpeg", "-y", "-i", input_file, "-vn", "-acodec", audio_codec, output_file]
        else:
            bitrate = f"{self.audio_bitrate_var_conv.get()}k"
            command = ["ffmpeg", "-y", "-i", input_file, "-vn", "-acodec", audio_codec, "-b:a", bitrate, output_file]

        self.run_ffmpeg_command(command, f"Proses konversi ke {output_format} selesai.")

if __name__ == "__main__":
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('vista')
    except tk.TclError:
        pass
    app = FFmpegGUI(root)
    root.mainloop()
