import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import json
import threading
import time

FFMPEG_PATH = "ffmpeg"

# التحقق من ffmpeg/ffprobe
try:
    subprocess.run([FFMPEG_PATH, "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run([FFMPEG_PATH.replace("ffmpeg", "ffprobe"), "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except Exception:
    messagebox.showerror("خطأ", "FFmpeg أو FFprobe غير مثبت أو غير موجود في PATH.\nيرجى تثبيته من: https://ffmpeg.org/download.html")
    exit()

selected_file = ""
video_duration = 0

def get_duration_ffprobe(file_path):
    try:
        result = subprocess.run(
            [FFMPEG_PATH.replace("ffmpeg", "ffprobe"),
             "-v", "error", "-show_entries", "format=duration",
             "-of", "json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError("ffprobe لم يعمل بشكل صحيح.")
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل في قراءة مدة الفيديو:\n{e}")
        return None

def choose_file():
    global selected_file, video_duration
    selected_file = filedialog.askopenfilename(filetypes=[("MOV Files", "*.mov")])
    if selected_file:
        file_label.config(text=os.path.basename(selected_file))
        video_duration = get_duration_ffprobe(selected_file)
        if video_duration:
            status_label.config(text=f"✅ تم اختيار الملف. المدة: {round(video_duration, 2)} ثانية")
        else:
            file_label.config(text="")
            status_label.config(text="❌ فشل في قراءة المدة")
            selected_file = ""

def compress_to_webm(input_path, output_path, bitrate, progress_bar, status_label):
    try:
        start_time = time.time()
        cmd = [
            FFMPEG_PATH,
            "-i", input_path,
            "-c:v", "libvpx-vp9",
            "-b:v", f"{bitrate}M",
            "-minrate", f"{bitrate}M",
            "-maxrate", f"{bitrate}M",
            "-bufsize", "10M",
            "-pix_fmt", "yuva420p",
            "-auto-alt-ref", "0",
            "-deadline", "realtime",
            "-cpu-used", "4",
            output_path
        ]

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        while True:
            line = process.stderr.readline()
            if not line:
                break
            if "time=" in line:
                time_str = line.split("time=")[-1].split(" ")[0]
                h, m, s = map(float, time_str.strip().split(":"))
                current_sec = h * 3600 + m * 60 + s
                if video_duration:
                    percent = min(100, (current_sec / video_duration) * 100)
                    progress_bar["value"] = percent
                    elapsed = time.time() - start_time
                    estimated_total = elapsed / (percent / 100) if percent > 0 else 0
                    remaining = estimated_total - elapsed
                    status_label.config(text=f"يتم التحويل... {int(percent)}% - متوقع {int(remaining)} ثوانٍ")
                    root.update_idletasks()
        process.wait()
        progress_bar["value"] = 100
        status_label.config(text="✅ تم الضغط بنجاح")
        messagebox.showinfo("نجاح", f"تم إنشاء الملف:\n{output_path}")
    except Exception as e:
        messagebox.showerror("خطأ أثناء التحويل", str(e))

def start_compression():
    global selected_file, video_duration
    if not selected_file:
        messagebox.showwarning("تنبيه", "يرجى اختيار ملف أولًا.")
        return
    try:
        target_size = float(size_entry.get())
    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال حجم صحيح بالميغابايت.")
        return
    if not video_duration:
        messagebox.showerror("خطأ", "تعذر الحصول على مدة الفيديو.")
        return

    target_bits = target_size * 8 * 1024 * 1024
    bitrate_mbps = round(target_bits / video_duration / 1_000_000, 2)
    output_path = os.path.splitext(selected_file)[0] + "_compressed.webm"

    progress_bar["value"] = 0
    status_label.config(text="🔄 جاري بدء الضغط...")
    threading.Thread(target=compress_to_webm, args=(
        selected_file, output_path, bitrate_mbps, progress_bar, status_label), daemon=True).start()

# ================= واجهة المستخدم =================

root = tk.Tk()
root.title("ضغط فيديو MOV إلى WebM شفاف")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="📦 الحجم المستهدف بالميغابايت (مثال: 40):").pack()
size_entry = tk.Entry(frame, width=10)
size_entry.insert(0, "40")
size_entry.pack(pady=5)

tk.Button(frame, text="📂 اختر ملف MOV", command=choose_file, width=30).pack(pady=5)

file_label = tk.Label(frame, text="", fg="blue")
file_label.pack(pady=2)

tk.Button(frame, text="🚀 ابدأ الضغط", command=start_compression, width=30).pack(pady=10)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(frame, text="", fg="green")
status_label.pack()

root.mainloop()
