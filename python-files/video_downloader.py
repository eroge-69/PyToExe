import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
from pathlib import Path
from datetime import datetime
import logging
import subprocess
import sys
import shutil

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
    import yt_dlp

class AreenaDownloader:
    MAX_TITLE_LEN = 80

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎥 Yle Areena Downloader")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        self.app_dir = Path(sys.argv[0]).resolve().parent
        self.logs_dir = self.app_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.default_download_dir = self.app_dir / "Downloads"
        self.default_download_dir.mkdir(exist_ok=True)

        self.setup_logging()

        self.download_queue: "queue.Queue[tuple[str,str]]" = queue.Queue()
        self.download_counter = 0
        self.download_results = {}
        self.stop_requested = False

        self.build_ui()
        self.apply_light_theme()

        if shutil.which("ffmpeg") is None:
            self.status_var.set("⚠️ FFmpeg not found — merging may fail")

    def setup_logging(self):
        log_file = self.logs_dir / f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        self.log_file = log_file
        logging.info("Application started")

    def log_message(self, message, level="INFO"):
        if level == "ERROR":
            logging.error(message)
        else:
            logging.info(message)
        self.status_var.set(message)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill='both', expand=True)
        main.columnconfigure(1, weight=1)

        ttk.Label(main, text="🎥 Yle Areena Downloader", font=('Arial', 18, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0,16))

        ttk.Label(main, text="Video URL:").grid(row=1, column=0, sticky="w", pady=4)
        self.url_entry = ttk.Entry(main, width=64)
        self.url_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=(8,0))
        self.url_entry.bind('<Return>', lambda _e: self.add_to_queue())
        ttk.Button(main, text="➕ Add to Queue", command=self.add_to_queue).grid(row=1, column=2, padx=(8,0))

        ttk.Label(main, text="Multiple URLs (one per line):").grid(row=2, column=0, sticky="nw", pady=4)
        self.multi_text = scrolledtext.ScrolledText(main, height=6, width=64)
        self.multi_text.grid(row=2, column=1, columnspan=2, sticky="nsew", pady=4, padx=(8,0))
        ttk.Button(main, text="➕ Add Multiple", command=self.add_multiple_urls).grid(row=3, column=1, sticky="e", pady=4)

        ttk.Label(main, text="Save to:").grid(row=4, column=0, sticky="w", pady=(10,0))
        self.folder_var = tk.StringVar(value=str(self.default_download_dir))
        ttk.Entry(main, textvariable=self.folder_var, width=48).grid(row=4, column=1, sticky="ew", pady=(10,0), padx=(8,6))
        ttk.Button(main, text="Browse…", command=self.browse_folder).grid(row=4, column=2, pady=(10,0))

        controls = ttk.Frame(main)
        controls.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")
        ttk.Button(controls, text="📥 Start Downloads", command=self.start_downloads).pack(side=tk.LEFT, padx=(0,10))
        self.stop_button = ttk.Button(controls, text="⏹ Stop All", command=self.stop_all_downloads, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(controls, text="🧹 Clear Queue", command=self.clear_queue).pack(side=tk.LEFT)

        progress_frame = ttk.LabelFrame(main, text="Download Queue & Progress", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)

        self.queue_tree = ttk.Treeview(progress_frame, columns=('Status','Progress'), show='tree headings')
        self.queue_tree.heading('#0', text='Title')
        self.queue_tree.heading('Status', text='Status')
        self.queue_tree.heading('Progress', text='Progress')
        self.queue_tree.column('#0', width=520)
        self.queue_tree.column('Status', width=160)
        self.queue_tree.column('Progress', width=120)
        self.queue_tree.grid(row=0, column=0, sticky="nsew")

        v_scroll = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        h_scroll = ttk.Scrollbar(progress_frame, orient=tk.HORIZONTAL, command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var, relief=tk.SUNKEN).grid(row=7, column=0, columnspan=3, sticky="ew", pady=(10,0))

    def apply_light_theme(self):
        style = ttk.Style()
        try:
            style.theme_use('default')
        except:
            pass

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if url:
            self._add_url_to_queue(url)
        self.url_entry.delete(0, tk.END)

    def add_multiple_urls(self):
        urls = [u.strip() for u in self.multi_text.get("1.0", tk.END).splitlines() if u.strip()]
        for u in urls:
            self._add_url_to_queue(u)
        self.multi_text.delete("1.0", tk.END)

    def _add_url_to_queue(self, url):
        for v in self.download_results.values():
            if v['url'] == url:
                self.status_var.set("Already in queue")
                return

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', url)
        except Exception as e:
            self.log_message(f"Failed to fetch title for {url}: {e}", "ERROR")
            title = url

        if len(title) > self.MAX_TITLE_LEN:
            title = title[:self.MAX_TITLE_LEN] + "…"

        item_id = f"item_{self.download_counter}"
        self.download_counter += 1
        self.queue_tree.insert('', 'end', iid=item_id, text=title, values=('Queued','0%'))
        self.download_queue.put((item_id,url))
        self.download_results[item_id] = {'status':'Queued','progress':'0%','error':None,'url':url}
        self.log_message(f"Added to queue: {title} ({url})")

    def clear_queue(self):
        self.download_queue = queue.Queue()
        self.download_results.clear()
        self.queue_tree.delete(*self.queue_tree.get_children())

    def start_downloads(self):
        if self.download_queue.empty():
            messagebox.showinfo("Info", "Queue is empty.")
            return
        self.stop_requested = False
        self.stop_button.config(state='normal')
        t = threading.Thread(target=self._download_worker, daemon=True)
        t.start()

    def stop_all_downloads(self):
        self.stop_requested = True
        self.stop_button.config(state='disabled')
        self.status_var.set("Stopping downloads…")

    def _download_worker(self):
        while not self.download_queue.empty() and not self.stop_requested:
            item_id, url = self.download_queue.get()
            self._download_video(item_id, url)

        self.stop_button.config(state='disabled')
        self.status_var.set("All downloads completed or stopped")

    def _download_video(self, item_id, url):
        self.queue_tree.set(item_id, 'Status', 'Downloading')
        save_path = Path(self.folder_var.get())
        save_path.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': str(save_path / '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: self._progress_hook(item_id,d)],
            'quiet': True,
            'merge_output_format': 'mp4',
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.queue_tree.set(item_id, 'Status', 'Completed')
            self.queue_tree.set(item_id, 'Progress', '100%')
        except Exception as e:
            self.queue_tree.set(item_id, 'Status', 'Failed')
            self.queue_tree.set(item_id, 'Progress', '0%')
            self.download_results[item_id]['error'] = str(e)
            self.log_message(f"Download failed: {url} - {e}", "ERROR")

    def _progress_hook(self, item_id, d):
        if d['status'] == 'downloading':
            pct = d.get('percent', 0)
            try:
                pct_str = f"{float(pct):.1f}%"
            except:
                pct_str = "0%"
            self.queue_tree.set(item_id, 'Progress', pct_str)

def main():
    root = tk.Tk()
    app = AreenaDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
