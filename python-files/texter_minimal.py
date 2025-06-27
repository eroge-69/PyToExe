import tkinter as tk
from tkinter import filedialog
import json, os
from datetime import datetime

CONFIG_FILE = "texter_settings.json"
DEFAULT_PATHS = {
    "time_file": "zeit.txt",
    "date_file": "datum.txt",
    "text_file": "text.txt"
}

class TexterMinimal:
    def __init__(self, root):
        self.root = root
        self.root.title("Texter Minimal by A.R.Pfisterer")
        self.root.geometry("420x330")
        self.root.resizable(False, False)

        self.load_paths()

        # Hauptframe mit Padding
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True)

        font_label = ("Segoe UI", 12)
        font_display = ("Consolas", 16)

        # Zeit
        self.time_label = tk.Label(frame, text="Zeit: --:--:--", font=font_display)
        self.time_label.pack(pady=(0, 5))
        tk.Button(frame, text="Zeit-Datei wählen", font=font_label,
                  command=lambda: self.choose_path("time_file")).pack(pady=(0, 10))

        # Datum
        self.date_label = tk.Label(frame, text="Datum: ----.--.--", font=font_display)
        self.date_label.pack(pady=(0, 5))
        tk.Button(frame, text="Datum-Datei wählen", font=font_label,
                  command=lambda: self.choose_path("date_file")).pack(pady=(0, 10))

        # Freitext
        tk.Label(frame, text="Freitext (z. B. Spiel oder Servername):", font=font_label).pack(pady=(5, 5))
        self.text_entry = tk.Entry(frame, width=30, font=font_display, justify="center")
        self.text_entry.pack(pady=(0, 5))
        self.text_entry.bind("<KeyRelease>", self.save_text)
        tk.Button(frame, text="Text-Datei wählen", font=font_label,
                  command=lambda: self.choose_path("text_file")).pack(pady=(0, 10))

        self.update_time_and_date()

    def load_paths(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.paths = json.load(f)
        else:
            self.paths = DEFAULT_PATHS.copy()
            self.save_paths()

    def save_paths(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.paths, f)

    def choose_path(self, key):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
        if path:
            self.paths[key] = path
            self.save_paths()

    def save_text(self, event=None):
        text = self.text_entry.get()
        path = self.paths.get("text_file", "")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    def update_time_and_date(self):
        now = datetime.now()
        zeit = now.strftime("%H:%M:%S")
        datum = now.strftime("%Y.%m.%d")

        self.time_label.config(text=f"Zeit: {zeit}")
        self.date_label.config(text=f"Datum: {datum}")

        try:
            with open(self.paths["time_file"], "w", encoding="utf-8") as f:
                f.write(zeit)
        except:
            pass

        try:
            with open(self.paths["date_file"], "w", encoding="utf-8") as f:
                f.write(datum)
        except:
            pass

        self.root.after(1000, self.update_time_and_date)

if __name__ == "__main__":
    TexterMinimal(tk.Tk()).root.mainloop()
