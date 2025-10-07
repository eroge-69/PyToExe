import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import yt_dlp

# -------------- Download Logic --------------
def download_video(url, path, log_box):
    if not url.strip():
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return

    if not path or not os.path.isdir(path):
        messagebox.showerror("Error", "Please choose a valid download folder.")
        return

    log_box.config(state="normal")
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, "Starting download...\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            log_text = f"Downloading... {percent} | {speed} | ETA: {eta}\n"
            update_log(log_box, log_text)
        elif d['status'] == 'finished':
            update_log(log_box, f"\nDownload finished! Processing video...\n")

    ydl_opts = {
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'format': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best',
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'quiet': True,
    }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            update_log(log_box, "\n✅ Download Complete!\n")
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            update_log(log_box, f"\n❌ Error: {e}\n")
            messagebox.showerror("Download Error", str(e))

    threading.Thread(target=run_download).start()

def update_log(log_box, text):
    log_box.config(state="normal")
    log_box.insert(tk.END, text)
    log_box.see(tk.END)
    log_box.config(state="disabled")

# -------------- GUI Setup --------------
def create_gui():
    root = tk.Tk()
    root.title("YouTube 4K Video Downloader")
    root.geometry("600x400")
    root.resizable(False, False)
    root.configure(bg="#0f172a")  # dark blue background

    title_label = tk.Label(root, text="YouTube 4K Downloader", fg="white", bg="#0f172a",
                           font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=10)

    # URL input
    url_frame = tk.Frame(root, bg="#0f172a")
    url_frame.pack(pady=10)
    tk.Label(url_frame, text="Video URL:", bg="#0f172a", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT)
    url_entry = ttk.Entry(url_frame, width=60)
    url_entry.pack(side=tk.LEFT, padx=5)

    # Folder chooser
    path_frame = tk.Frame(root, bg="#0f172a")
    path_frame.pack(pady=10)
    tk.Label(path_frame, text="Save to:", bg="#0f172a", fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT)
    path_var = tk.StringVar()
    path_entry = ttk.Entry(path_frame, textvariable=path_var, width=45)
    path_entry.pack(side=tk.LEFT, padx=5)
    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
    ttk.Button(path_frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

    # Download button
    download_btn = ttk.Button(root, text="⬇️ Download 4K", width=20,
                              command=lambda: download_video(url_entry.get(), path_var.get(), log_box))
    download_btn.pack(pady=10)

    # Log output box
    log_box = tk.Text(root, height=10, width=70, state="disabled", bg="#1e293b", fg="#f1f5f9",
                      font=("Consolas", 10), wrap="word")
    log_box.pack(pady=10, padx=10)

    # Footer
    footer = tk.Label(root, text="Made with ❤️ using yt-dlp + ffmpeg",
                      bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9))
    footer.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
