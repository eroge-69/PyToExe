import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import queue

APP_NAME = "Smart File Organizer"

# Default categories
CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xlsx", ".xls", ".csv", ".ppt", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".cs", ".php", ".rb", ".go", ".kt"]
}

# ------------------- Utility functions -------------------
def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def unique_destination(dst_path):
    """If file already exists, append (1), (2), ..."""
    if not os.path.exists(dst_path):
        return dst_path
    base, ext = os.path.splitext(dst_path)
    i = 1
    while True:
        candidate = f"{base} ({i}){ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1

# ------------------- Worker thread -------------------
class OrganizerWorker(threading.Thread):
    def __init__(self, folder, categories, skip_hidden, progress_q, log_q, done_cb):
        super().__init__(daemon=True)
        self.folder = folder
        self.categories = categories
        self.skip_hidden = skip_hidden
        self.progress_q = progress_q
        self.log_q = log_q
        self.done_cb = done_cb
        self.counts = {cat: 0 for cat in categories}
        self.counts["Others"] = 0

    def run(self):
        try:
            files = [f for f in os.listdir(self.folder)]
            total_files = sum(os.path.isfile(os.path.join(self.folder, f)) for f in files)
            processed = 0

            # Ensure category folders
            for cat in self.categories:
                safe_mkdir(os.path.join(self.folder, cat))
            safe_mkdir(os.path.join(self.folder, "Others"))

            for f in files:
                src = os.path.join(self.folder, f)
                if not os.path.isfile(src):
                    continue

                ext = os.path.splitext(f)[1].lower()
                cat = None
                for c, exts in self.categories.items():
                    if ext in exts:
                        cat = c
                        break
                target_dir = os.path.join(self.folder, cat if cat else "Others")
                dst = os.path.join(target_dir, f)

                try:
                    dst_final = unique_destination(dst)
                    shutil.move(src, dst_final)
                    if cat:
                        self.counts[cat] += 1
                    else:
                        self.counts["Others"] += 1
                    self.log_q.put(f"Moved: {f} → {os.path.basename(dst_final)}")
                except Exception as e:
                    self.log_q.put(f"Error moving {f}: {e}")

                processed += 1
                self.progress_q.put((processed, total_files))

            self.done_cb(self.counts)

        except Exception as e:
            self.log_q.put(f"Fatal error: {e}")
            self.done_cb(None)

# ------------------- Main App -------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.minsize(800, 500)
        self.configure(bg="#1f2630")
        self._apply_style()

        # Queues for thread updates
        self.progress_q = queue.Queue()
        self.log_q = queue.Queue()

        # Top controls
        self._build_topbar()

        # Log panel
        self._build_body()

        # Footer with progress
        self._build_footer()

        # Timers for UI updates
        self.after(100, self._drain_queues)

    def _apply_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass

        bg = "#1f2630"
        fg = "#e6eaf0"
        accent = "#4cc9f0"

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 14))
        style.configure("TButton", padding=8, font=("Segoe UI", 10))
        style.configure("Accent.TButton", padding=10, font=("Segoe UI Semibold", 10))
        style.map("Accent.TButton", background=[("active", accent)], foreground=[("active", "#101318")])
        style.configure("TCheckbutton", background=bg, foreground=fg)

    def _build_topbar(self):
        top = ttk.Frame(self, padding=14)
        top.pack(fill="x")

        title = ttk.Label(top, text="📂 Smart File Organizer", style="Header.TLabel")
        title.pack(side="left")

        self.folder_var = tk.StringVar(value="")

        entry = ttk.Entry(top, textvariable=self.folder_var, width=70)
        entry.pack(side="left", padx=(16, 8))

        browse_btn = ttk.Button(top, text="Browse…", command=self._browse_folder)
        browse_btn.pack(side="left")

    def _build_body(self):
        body = ttk.Frame(self, padding=(14, 0, 14, 0))
        body.pack(fill="both", expand=True)

        log_box = ttk.Labelframe(body, text="Activity Log", padding=8)
        log_box.pack(fill="both", expand=True)

        # Add scrollbar
        self.log_text = tk.Text(log_box, wrap="none", bg="#11161d", fg="#cbd5e1",
                                insertbackground="#cbd5e1", relief="flat")
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_box, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        self._log("Ready.")

    def _build_footer(self):
        foot = ttk.Frame(self, padding=14)
        foot.pack(fill="x")

        self.progress = ttk.Progressbar(foot, orient="horizontal", mode="determinate", length=300)
        self.progress.pack(side="left")

        self.status_var = tk.StringVar(value="Idle")
        status = ttk.Label(foot, textvariable=self.status_var)
        status.pack(side="left", padx=10)

        ttk.Button(foot, text="Organize", style="Accent.TButton", command=self._start).pack(side="right")

    # ------------------- Actions -------------------
    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Organize")
        if folder:
            self.folder_var.set(folder)

    def _start(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Invalid folder", "Please choose a valid folder.")
            return

        self._clear_log()
        self._log(f"Starting organization in: {folder}")
        self.progress.configure(value=0, maximum=1)
        self.status_var.set("Working…")

        worker = OrganizerWorker(
            folder=folder,
            categories=CATEGORIES,
            skip_hidden=True,
            progress_q=self.progress_q,
            log_q=self.log_q,
            done_cb=self._on_done
        )
        worker.start()

    def _on_done(self, counts):
        def finish():
            if counts is None:
                self.status_var.set("Failed")
                messagebox.showerror("Error", "An error occurred. Check the log.")
                return

            total = sum(counts.values())
            self.status_var.set("Done")
            self._log(f"Completed. Total files moved: {total}")

            # Build summary
            summary = "\n".join(f"{cat}: {num}" for cat, num in counts.items() if num > 0)
            if not summary:
                summary = "No files were moved."

            # Show popup
            messagebox.showinfo("Summary", f"Organization complete!\n\nTotal files moved: {total}\n\n{summary}")
        self.after(0, finish)

    # ------------------- Logging -------------------
    def _drain_queues(self):
        try:
            while True:
                processed, total = self.progress_q.get_nowait()
                self.progress.configure(maximum=max(total, 1), value=processed)
                self.status_var.set(f"Processing… {processed}/{total}")
        except queue.Empty:
            pass

        try:
            while True:
                line = self.log_q.get_nowait()
                self._log(line)
        except queue.Empty:
            pass

        self.after(100, self._drain_queues)

    def _log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.delete("1.0", "end")

# ------------------- Main -------------------
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
