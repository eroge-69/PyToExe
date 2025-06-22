import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import os

DEFAULT_TITLES = ["Arabic", "English"]
LANGUAGE_OPTIONS = ["Arabic", "English", "French", "Spanish", "Mandarin", "Kurdish", "Hindi", "German", "Urdu", "Other"]

class AudioTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Tagger Pro")
        self.root.geometry("800x600")
        self.dark_mode = True
        self.file_paths = []
        self.title_entries = []

        self.build_styles()
        self.setup_ui()
        self.add_default_titles()

    def build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#121212")
        style.configure("TLabel", background="#121212", foreground="white", font=('Segoe UI', 11))
        style.configure("TButton", padding=10, relief="flat", background="#03DAC6", foreground="black", font=("Segoe UI Semibold", 11)); style.configure("TFrame", background="#1e1e1e"); style.configure("TLabel", background="#1e1e1e", foreground="#f0f0f0", font=("Segoe UI Semibold", 11)); style.configure("TEntry", padding=8, relief="flat"); style.configure("TCombobox", fieldbackground="#2c2c2c", background="#2c2c2c", foreground="white", font=("Segoe UI", 10)); style.map("TButton", background=[("active", "#00BFA5")])
        style.map("TButton", background=[("active", "#00BFA5")])
        style.configure("TEntry", font=('Segoe UI', 10), padding=6)
        style.configure("TCombobox", fieldbackground="#2c2c2c", background="#2c2c2c", foreground="white", font=('Segoe UI', 10))

    def setup_ui(self):
        self.root.configure(bg="#121212")
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_section_label(self.main_frame, "📁 Select MP4 Files")
        self.file_btn = ttk.Button(self.main_frame, text="Browse", command=self.select_files)
        self.file_btn.pack(pady=5)

        self.files_box = tk.Listbox(self.main_frame, height=5, font=('Segoe UI', 10), bg="#1e1e1e", fg="white", highlightthickness=0, relief="flat", selectbackground="#03DAC6")
        self.files_box.pack(fill=tk.X, padx=5, pady=5)
        self.files_box.drop_target_register(DND_FILES)
        self.files_box.dnd_bind('<<Drop>>', self.on_drop)

        self.track_count_label = ttk.Label(self.main_frame, text="Track count: N/A", font=('Segoe UI', 10, 'italic'))
        self.track_count_label.pack(pady=(0, 15))

        self.create_section_label(self.main_frame, "🎵 Audio Track Languages")
        self.entry_container = ttk.Frame(self.main_frame)
        self.entry_container.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(control_frame, text="➕ Add Language", command=self.add_title_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🌓 Toggle Dark Mode", command=self.toggle_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.main_frame, text="🚀 Start Tagging", command=self.start_tagging).pack(pady=10)

    def create_section_label(self, parent, text):
        label = ttk.Label(parent, text=text, font=('Segoe UI', 12, 'bold'))
        label.pack(anchor="w", pady=(10, 2))

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4")])
        self.show_files()

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        mp4_files = [f for f in files if f.lower().endswith(".mp4")]
        self.file_paths.extend(mp4_files)
        self.show_files()

    def show_files(self):
        self.files_box.delete(0, tk.END)

        if self.file_paths:
            track_total = self.get_audio_track_count(self.file_paths[0])
            self.track_count_label.config(text=f"Track count (first file): {track_total}")
        else:
            self.track_count_label.config(text="Track count: N/A")

        for path in self.file_paths:
            self.files_box.insert(tk.END, os.path.basename(path))

    def get_audio_track_count(self, file_path):
        try:
            result = subprocess.run(["ffmpeg", "-i", file_path],
                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            return result.stderr.count("Audio:")
        except Exception:
            return 0

    def add_default_titles(self):
        for title in DEFAULT_TITLES:
            self.add_title_input(default=title)

    def add_title_input(self, default=""):
        row = ttk.Frame(self.entry_container)
        row.pack(fill=tk.X, pady=6)

        index = len(self.title_entries)
        label = ttk.Label(row, text=f"Track {index + 1}:", width=12)
        label.pack(side=tk.LEFT)

        var = tk.StringVar(value=default)
        dropdown = ttk.Combobox(row, values=LANGUAGE_OPTIONS, textvariable=var, width=35)
        dropdown.pack(side=tk.LEFT, padx=5)
        dropdown.set(default)

        remove_btn = ttk.Button(row, text="🗑 Remove", width=10, command=lambda: self.remove_title_input(row, dropdown))
        remove_btn.pack(side=tk.RIGHT, padx=5)

        self.title_entries.append(dropdown)

    def remove_title_input(self, row, entry):
        row.destroy()
        self.title_entries.remove(entry)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        new_bg = "#121212" if self.dark_mode else "white"
        self.root.configure(bg=new_bg)

    def start_tagging(self):
        titles = [entry.get().strip() for entry in self.title_entries]
        if not all(titles):
            messagebox.showerror("Error", "Please fill in all track titles or remove empty ones.")
            return

        for file_path in self.file_paths:
            track_count = self.get_audio_track_count(file_path)
            if len(titles) > track_count:
                messagebox.showerror("Track Mismatch",
                    f"{os.path.basename(file_path)} only has {track_count} audio track(s), "
                    f"but you entered {len(titles)} titles.")
                return

        success_count = 0
        for file_path in self.file_paths:
            output_file = os.path.splitext(file_path)[0] + "_tagged.mp4"
            cmd = ["ffmpeg", "-i", file_path, "-map", "0:v"]

            for i, title in enumerate(titles):
                cmd += ["-map", f"0:a:{i}", f"-metadata:s:a:{i}", f"title={title}"]

            cmd += ["-c", "copy", output_file]

            try:
                subprocess.run(cmd, check=True)
                success_count += 1
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to tag: {file_path}")

        messagebox.showinfo("Done", f"✅ Tagged {success_count} file(s) successfully.")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AudioTaggerApp(root)
    root.mainloop()
