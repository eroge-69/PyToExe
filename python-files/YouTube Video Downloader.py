import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from yt_dlp import YoutubeDL

download_folder = os.getcwd()
download_archive = os.path.join(download_folder, "download_archive.txt")
log_history = []

# Globals to control pause/resume
download_thread = None
pause_flag = threading.Event()
pause_flag.set()  # Initially not paused

# --- Logger for yt-dlp with ETA and Speed info ---
class MyLogger:
    def __init__(self, textbox):
        self.textbox = textbox

    def debug(self, msg): pass
    def warning(self, msg):
        self._log(f"[WARNING] {msg}")
    def error(self, msg):
        self._log(f"[ERROR] {msg}")
    def info(self, msg):
        self._log(msg)

    def _log(self, msg):
        self.textbox.insert(tk.END, msg + "\n")
        self.textbox.see(tk.END)
        log_history.append(msg)

def format_eta(seconds):
    if seconds is None or seconds < 0:
        return "ETA: N/A"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"ETA: {h}h {m}m {s}s"
    elif m > 0:
        return f"ETA: {m}m {s}s"
    else:
        return f"ETA: {s}s"

def log_progress(d):
    pause_flag.wait()
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '').strip().replace('%', '')
        speed = d.get('_speed_str', 'N/A')
        eta = format_eta(d.get('eta'))
        try:
            progress = float(percent_str)
            progress_bar["value"] = progress
            progress_bar.update()
            log_text = f"⬇️ {percent_str}% | Speed: {speed} | {eta} | {d.get('filename', '')}"
            # Clear last progress line and insert new
            logbox.delete('end-2l', 'end-1l')
            logbox.insert(tk.END, log_text + "\n")
            logbox.see(tk.END)
            if dark_mode.get():
                logbox.tag_config('progress', foreground='cyan')
                logbox.tag_add('progress', 'end-2l', 'end-1l')
        except Exception:
            pass
    elif d['status'] == 'finished':
        progress_bar["value"] = 100
        progress_bar.update()
        finished_msg = f"✅ Finished: {d.get('filename', '')}"
        logbox.insert(tk.END, finished_msg + "\n")
        logbox.see(tk.END)
        log_history.append(finished_msg)

def download(urls, audio_only, quality, logbox):
    global pause_flag
    if isinstance(urls, str):
        urls = [urls]

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'format': quality,
        'quiet': True,
        'noplaylist': False,
        'logger': MyLogger(logbox),
        'progress_hooks': [log_progress],
        'download_archive': download_archive,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if audio_only else []
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                log_msg = f"\n🔗 Downloading: {url}"
                logbox.insert(tk.END, log_msg + "\n")
                logbox.see(tk.END)
                log_history.append(log_msg)
                progress_bar["value"] = 0
                progress_bar.update()
                ydl.download([url])
        done_msg = "\n✅ All downloads completed!\n"
        logbox.insert(tk.END, done_msg)
        logbox.see(tk.END)
        log_history.append(done_msg)
    except Exception as e:
        err_msg = f"\n❌ Error: {str(e)}\n"
        logbox.insert(tk.END, err_msg)
        logbox.see(tk.END)
        log_history.append(err_msg)

def start_download_thread():
    global download_thread, pause_flag
    if download_thread and download_thread.is_alive():
        messagebox.showinfo("Info", "Download already in progress.")
        return

    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Missing Input", "Please enter a YouTube URL.")
        return

    pause_flag.set()  # Reset pause

    logbox.delete(1.0, tk.END)
    log_history.clear()
    quality = quality_var.get()
    audio_only = audio_var.get()

    download_thread = threading.Thread(target=download, args=(url, audio_only, quality, logbox))
    download_thread.start()

def load_batch_file_thread():
    global download_thread, pause_flag
    if download_thread and download_thread.is_alive():
        messagebox.showinfo("Info", "Download already in progress.")
        return

    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return
    with open(path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    if not urls:
        messagebox.showwarning("Empty File", "The selected file contains no valid URLs.")
        return

    pause_flag.set()  # Reset pause

    logbox.delete(1.0, tk.END)
    log_history.clear()
    quality = quality_var.get()
    audio_only = audio_var.get()

    download_thread = threading.Thread(target=download, args=(urls, audio_only, quality, logbox))
    download_thread.start()

def choose_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder
        folder_label.config(text=f"📁 Folder: {download_folder}")

def toggle_pause():
    global pause_flag
    if pause_flag.is_set():
        pause_flag.clear()
        pause_button.config(text="▶️ Resume")
        logbox.insert(tk.END, "\n⏸ Download paused by user.\n")
        logbox.see(tk.END)
    else:
        pause_flag.set()
        pause_button.config(text="⏸ Pause")
        logbox.insert(tk.END, "\n▶️ Download resumed.\n")
        logbox.see(tk.END)

def toggle_dark_mode():
    if dark_mode.get():
        # Dark colors
        root.config(bg="#222222")
        for widget in root.winfo_children():
            try:
                widget.config(bg="#222222", fg="white")
            except:
                pass
        logbox.config(bg="#333333", fg="white", insertbackground='white')
        progress_bar.config(style="black.Horizontal.TProgressbar")
    else:
        # Light colors
        root.config(bg="SystemButtonFace")
        for widget in root.winfo_children():
            try:
                widget.config(bg="SystemButtonFace", fg="black")
            except:
                pass
        logbox.config(bg="white", fg="black", insertbackground='black')
        progress_bar.config(style="default.Horizontal.TProgressbar")

def export_log():
    if not log_history:
        messagebox.showinfo("Info", "No log data to save.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text files", "*.txt")],
                                        title="Save Download Log")
    if path:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_history))
            messagebox.showinfo("Success", f"Log saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log:\n{e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("🎬 YouTube Downloader with Speed, Dark Mode & Log Export")
root.geometry("700x600")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('default')
style.configure("black.Horizontal.TProgressbar", troughcolor='#555555', background='#00ffff')

tk.Label(root, text="YouTube Video / Playlist URL:", font=("Arial", 11)).pack(pady=(10, 0))
url_entry = tk.Entry(root, width=90, font=("Arial", 10))
url_entry.pack(pady=5)

audio_var = tk.BooleanVar()
tk.Checkbutton(root, text="Audio only (MP3)", variable=audio_var).pack()

quality_var = tk.StringVar(value="best")
tk.Label(root, text="Select Quality:", font=("Arial", 10)).pack(pady=(10, 0))
quality_options = ["best", "bestaudio/best", "bestvideo[height<=720]+bestaudio/best", "bestvideo[height<=480]+bestaudio/best"]
quality_menu = ttk.Combobox(root, values=quality_options, textvariable=quality_var, state="readonly", width=50)
quality_menu.pack()

folder_label = tk.Label(root, text=f"📁 Folder: {download_folder}", fg="blue", font=("Arial", 9))
folder_label.pack(pady=3)
tk.Button(root, text="Choose Download Folder", command=choose_folder).pack(pady=(0, 10))

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

download_button = tk.Button(btn_frame, text="⬇️ Download", width=20, command=start_download_thread)
download_button.grid(row=0, column=0, padx=5)

batch_button = tk.Button(btn_frame, text="📄 Download from .txt file", width=25, command=load_batch_file_thread)
batch_button.grid(row=0, column=1, padx=5)

pause_button = tk.Button(root, text="⏸ Pause", width=20, command=toggle_pause)
pause_button.pack(pady=(5, 10))

dark_mode = tk.BooleanVar()
dark_mode_check = tk.Checkbutton(root, text="🌙 Dark Mode", variable=dark_mode, command=toggle_dark_mode)
dark_mode_check.pack(pady=(0, 10))

tk.Label(root, text="📊 Progress", font=("Arial", 10)).pack(pady=(10, 0))
progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate", style="default.Horizontal.TProgressbar")
progress_bar.pack(pady=5)

tk.Label(root, text="📋 Download Log", font=("Arial", 10)).pack()
logbox = scrolledtext.ScrolledText(root, width=85, height=15, font=("Courier", 9))
logbox.pack(padx=10, pady=(0, 10))

export_button = tk.Button(root, text="📥 Export Log to File", width=20, command=export_log)
export_button.pack(pady=(0, 15))

tk.Label(root, text="Powered by yt-dlp | Made with ❤️", font=("Arial", 9), fg="gray").pack(side=tk.BOTTOM, pady=5)

root.mainloop()