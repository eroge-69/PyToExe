import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import time

class CopyGUI:
    def __init__(self, root):
        self.root = root
        root.title("Datei kopieren")
        root.geometry("750x320")

        # Flags für Steuerung
        self.stop_copy = False
        self.pause_copy = False
        self.current_dest = None

        # Quelle
        tk.Label(root, text="Quelle:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.source_entry = tk.Entry(root, width=50)
        self.source_entry.grid(row=0, column=1, padx=5)
        tk.Button(root, text="...", command=self.choose_source).grid(row=0, column=2, padx=5)

        # Ziel
        tk.Label(root, text="Ziel:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.dest_entry = tk.Entry(root, width=50)
        self.dest_entry.grid(row=1, column=1, padx=5)
        tk.Button(root, text="...", command=self.choose_dest).grid(row=1, column=2, padx=5)

        # Fortschritt
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=2, column=1, pady=10)
        self.progress_label = tk.Label(root, text="Noch nichts kopiert")
        self.progress_label.grid(row=3, column=1)

        # Buttons für Steuerung
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=4, column=1, pady=20)

        tk.Button(btn_frame, text="Start Kopieren", command=self.start_copy, width=15, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        self.pause_button = tk.Button(btn_frame, text="Pause", command=self.toggle_pause, width=15, bg="#FFC107")
        self.pause_button.grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Stop", command=self.stop, width=15, bg="#F44336", fg="white").grid(row=0, column=2, padx=5)

        # Drag & Drop aktivieren
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', self.drop)

    def choose_source(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, filename)

    def choose_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            src = self.source_entry.get()
            if src:
                filename = os.path.basename(src)
                full_dest = os.path.join(folder, filename)
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, full_dest)
            else:
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, folder)

    def start_copy(self):
        self.stop_copy = False
        self.pause_copy = False
        threading.Thread(target=self.copy_file, daemon=True).start()

    def stop(self):
        self.stop_copy = True

    def toggle_pause(self):
        self.pause_copy = not self.pause_copy
        if self.pause_copy:
            self.pause_button.config(text="Fortsetzen", bg="#2196F3", fg="white")
        else:
            self.pause_button.config(text="Pause", bg="#FFC107", fg="black")

    def copy_file(self):
        src = self.source_entry.get()
        dst = self.dest_entry.get()
        self.current_dest = dst

        if not os.path.isfile(src):
            messagebox.showerror("Fehler", "Ungültige Quelldatei")
            return
        if not dst:
            messagebox.showerror("Fehler", "Ungültiges Ziel")
            return

        try:
            total_size = os.path.getsize(src)
            copied_size = 0
            chunk_size = 1024 * 1024  # 1 MB Blöcke
            start_time = time.time()

            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                while True:
                    if self.stop_copy:
                        fdst.close()
                        if os.path.exists(dst):
                            os.remove(dst)
                        messagebox.showinfo("Abgebrochen", "Kopiervorgang wurde gestoppt und unvollständige Datei gelöscht")
                        return

                    if self.pause_copy:
                        time.sleep(0.1)
                        continue

                    buf = fsrc.read(chunk_size)
                    if not buf:
                        break
                    fdst.write(buf)
                    copied_size += len(buf)

                    elapsed = time.time() - start_time
                    speed = copied_size / elapsed if elapsed > 0 else 0
                    remaining = (total_size - copied_size) / speed if speed > 0 else 0

                    percent = int((copied_size / total_size) * 100)
                    self.update_progress(copied_size, total_size, percent, remaining, speed)

            messagebox.showinfo("Erfolg", f"Datei wurde kopiert nach:\n{dst}")
            self.update_progress(total_size, total_size, 100, 0, 0)

        except Exception as e:
            if self.current_dest and os.path.exists(self.current_dest):
                os.remove(self.current_dest)
            messagebox.showerror("Fehler", str(e))

    def format_size(self, size_bytes):
        if size_bytes >= 1024**3:
            return f"{size_bytes/1024**3:.2f} GB"
        elif size_bytes >= 1024**2:
            return f"{size_bytes/1024**2:.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes/1024:.2f} KB"
        else:
            return f"{size_bytes} B"

    def format_time(self, seconds):
        if seconds <= 0:
            return "0s"
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            m, s = divmod(int(seconds), 60)
            return f"{m}m {s}s"
        else:
            h, rem = divmod(int(seconds), 3600)
            m, s = divmod(rem, 60)
            return f"{h}h {m}m {s}s"

    def update_progress(self, copied, total, percent, remaining, speed):
        self.progress["value"] = percent
        speed_text = f"{self.format_size(speed)}/s" if speed > 0 else "-"
        self.progress_label.config(
            text=f"{self.format_size(copied)} von {self.format_size(total)} ({percent}%) - Restzeit: {self.format_time(remaining)} - Geschwindigkeit: {speed_text}"
        )
        self.root.update_idletasks()

    def drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file_path)
        elif os.path.isdir(file_path):
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyGUI(root)
    root.mainloop()
