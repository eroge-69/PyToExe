import os
import shutil
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import json
import threading
import datetime

# ========================
# CONFIG & HISTORY
# ========================
CONFIG_FILE = "organizer_config.json"
HISTORY_FILE = "organize_history.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"theme": "light", "custom_rules": {}}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(action):
    history = load_history()
    history.append(action)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-10:], f)

# ========================
# CORE ORGANIZE FUNCTION
# ========================
def organize_files(main_folder, log_callback, progress_callback, custom_rules=None, safe_mode=False):
    base_rules = {
        '.gif': 'Images', '.jpeg': 'Images', '.jpg': 'Images', '.png': 'Images',
        '.webp': 'Images', '.bmp': 'Images', '.tiff': 'Images', '.svg': 'Images',
        '.mp4': 'Videos', '.mkv': 'Videos', '.avi': 'Videos', '.mov': 'Videos',
        '.mp3': 'Music', '.wav': 'Music', '.flac': 'Music', '.aac': 'Music',
        '.pdf': 'Documents', '.docx': 'Documents', '.xlsx': 'Documents', '.txt': 'Documents',
        '.zip': 'Compressed', '.rar': 'Compressed', '.7z': 'Compressed',
        '.py': 'Code', '.js': 'Code', '.html': 'Code', '.css': 'Code',
        '.exe': 'Programs', '.msi': 'Programs',
        '.ini': 'System Files', '.log': 'System Files'
    }

    if custom_rules:
        base_rules.update(custom_rules)

    items = [f for f in os.listdir(main_folder) if os.path.isfile(os.path.join(main_folder, f))]
    total = len(items)
    moved_count = 0
    move_log = []
    stats = {}

    for i, item in enumerate(items):
        item_path = os.path.join(main_folder, item)
        _, ext = os.path.splitext(item)
        ext = ext.lower()

        folder_name = base_rules.get(ext, "Others")
        stats[folder_name] = stats.get(folder_name, 0) + 1

        if not safe_mode:
            target_folder = os.path.join(main_folder, folder_name)
            os.makedirs(target_folder, exist_ok=True)
            dest_path = os.path.join(target_folder, item)

            counter = 1
            original_dest = dest_path
            while os.path.exists(dest_path):
                name, ext_part = os.path.splitext(original_dest)
                dest_path = f"{name}_{counter}{ext_part}"
                counter += 1

            shutil.move(item_path, dest_path)
            move_log.append((item, item_path, dest_path))
            moved_count += 1

        log_callback(f"{'[SIM] ' if safe_mode else ''}✅ {item} → {folder_name}")
        if total > 0:
            progress_callback((i + 1) / total * 100)

    mode_msg = " (Safe Mode)" if safe_mode else ""
    log_callback(f"\n🎉 Done! {moved_count if not safe_mode else total} files processed{mode_msg}.")
    return move_log, stats

# ========================
# UNDO
# ========================
def undo_last_operation(log_callback):
    history = load_history()
    if not history:
        log_callback("❌ No operation to undo.")
        return
    last_op = history.pop()
    restored = 0
    for _, orig, new in reversed(last_op):
        if os.path.exists(new):
            shutil.move(new, orig)
            restored += 1
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)
    log_callback(f"↩️ Undid last action ({restored} files restored).")

# ========================
# MAIN APP CLASS
# ========================
class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.current_image = None
        self.setup_theme()
        self.root.title("✨ File Organizer Pro v2 — Pola Security")
        self.root.geometry("950x680")
        self.root.resizable(False, False)

        self.setup_background()
        self.setup_ui()

    def setup_theme(self):
        self.bg_color = "#1e1e2e" if self.config["theme"] == "dark" else "#f0f2f5"
        self.fg_color = "white" if self.config["theme"] == "dark" else "#2d3748"
        self.card_bg = "#2d2d44" if self.config["theme"] == "dark" else "white"
        self.btn_bg = "#4a4a8a" if self.config["theme"] == "dark" else "#4a6cf7"
        self.log_bg = "#252536" if self.config["theme"] == "dark" else "#f9f9f9"
        self.log_fg = "white" if self.config["theme"] == "dark" else "black"

    def setup_background(self):
        self.canvas = tk.Canvas(self.root, width=950, height=680, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Gradient background
        colors = [
            (60, 60, 120),   # top
            (40, 40, 90),    # mid
            (20, 20, 60)     # bottom (dark mode base)
        ] if self.config["theme"] == "dark" else [
            (106, 138, 240),
            (150, 180, 255),
            (200, 220, 255)
        ]

        for i in range(680):
            ratio = i / 680
            r = int(colors[0][0] + (colors[2][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[2][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[2][2] - colors[0][2]) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, 950, i, fill=color)

    def setup_ui(self):
        # Main card
        self.main_frame = tk.Frame(self.canvas, bg=self.card_bg, relief="flat")
        self.canvas.create_window(475, 320, window=self.main_frame, width=880, height=580)

        # Header
        title = tk.Label(
            self.main_frame,
            text="📂 Smart File Organizer Pro v2",
            font=("Segoe UI", 18, "bold"),
            bg=self.card_bg,
            fg=self.fg_color
        )
        title.pack(pady=(15, 5))

        # Theme toggle
        theme_btn = ttk.Button(
            self.main_frame,
            text="🌙 Toggle Theme" if self.config["theme"] == "light" else "☀️ Toggle Theme",
            command=self.toggle_theme
        )
        theme_btn.pack(pady=2)

        # Folder selection
        self.folder_path = tk.StringVar()
        ttk.Button(self.main_frame, text="📁 Choose Folder", command=self.choose_folder).pack(pady=8)
        tk.Entry(self.main_frame, textvariable=self.folder_path, width=80, state='readonly').pack(pady=3)

        # Action buttons
        btn_frame = tk.Frame(self.main_frame, bg=self.card_bg)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="🚀 Organize", command=self.start_organize).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🛡️ Safe Mode", command=lambda: self.start_organize(safe=True)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="↩️ Undo", command=self.undo_last).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="⚙️ Custom Rules", command=self.open_custom_rules).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="📤 Export Log", command=self.export_log).pack(side="left", padx=4)

        # Preview + Stats
        lower_frame = tk.Frame(self.main_frame, bg=self.card_bg)
        lower_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # File preview
        self.preview_label = tk.Label(lower_frame, text="🖼️ Select a folder to preview images", bg=self.card_bg, fg=self.fg_color)
        self.preview_label.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Stats panel
        self.stats_text = tk.Text(lower_frame, width=25, height=15, bg=self.card_bg, fg=self.fg_color, font=("Consolas", 9))
        self.stats_text.pack(side="right", fill="y")
        self.stats_text.insert(tk.END, "📊 Stats will appear here\nafter organizing.")

        # Progress & log
        self.progress_bar = ttk.Progressbar(self.main_frame, length=700, mode="determinate")
        self.progress_bar.pack(pady=8)

        self.log_box = tk.Text(self.main_frame, height=8, bg=self.log_bg, fg=self.log_fg, font=("Consolas", 9))
        self.log_box.pack(padx=15, pady=(0, 10), fill="x")
        self.log_box_scroll = ttk.Scrollbar(self.log_box, orient="vertical", command=self.log_box.yview)
        self.log_box_scroll.pack(side="right", fill="y")
        self.log_box.config(yscrollcommand=self.log_box_scroll.set)

        # Telegram link
        link = tk.Label(
            self.root,
            text="🔗 Join Pola Security Channel",
            fg="#4a90e2" if self.config["theme"] == "light" else "#6ab7ff",
            cursor="hand2",
            bg=self.bg_color,
            font=("Segoe UI", 10, "underline")
        )
        link.place(relx=0.5, rely=0.965, anchor="center")
        link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/pola_security/1312"))

    def toggle_theme(self):
        self.config["theme"] = "dark" if self.config["theme"] == "light" else "light"
        save_config(self.config)
        self.restart_gui()

    def restart_gui(self):
        self.root.destroy()
        root = tk.Tk()
        app = FileOrganizerApp(root)
        root.mainloop()

    def log(self, msg):
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def update_progress(self, val):
        self.progress_bar['value'] = val

    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)
            self.preview_image(path)

    def preview_image(self, folder):
        try:
            images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            if images:
                img_path = os.path.join(folder, images[0])
                img = Image.open(img_path)
                img.thumbnail((200, 200))
                img = ImageOps.expand(img, border=2, fill='white')
                self.current_image = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.current_image, text="")
            else:
                self.preview_label.config(image="", text="🖼️ No images found")
        except Exception as e:
            self.preview_label.config(image="", text=f"⚠️ Preview error: {str(e)[:30]}")

    def open_custom_rules(self):
        rules = self.config.get("custom_rules", {})
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Rules")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Extension (e.g. .log):").pack(pady=(10,0))
        ext_entry = ttk.Entry(dialog, width=30)
        ext_entry.pack()

        tk.Label(dialog, text="Folder Name (e.g. Logs):").pack()
        folder_entry = ttk.Entry(dialog, width=30)
        folder_entry.pack()

        def add_rule():
            ext = ext_entry.get().strip().lower()
            folder = folder_entry.get().strip()
            if ext and folder:
                if not ext.startswith('.'):
                    ext = '.' + ext
                rules[ext] = folder
                self.config["custom_rules"] = rules
                save_config(self.config)
                ext_entry.delete(0, tk.END)
                folder_entry.delete(0, tk.END)
                update_listbox()
                messagebox.showinfo("✅ Success", f"Rule added: {ext} → {folder}")

        ttk.Button(dialog, text="➕ Add Rule", command=add_rule).pack(pady=10)

        listbox = tk.Listbox(dialog, width=60, height=15)
        listbox.pack(padx=10, pady=5)

        def update_listbox():
            listbox.delete(0, tk.END)
            for ext, folder in rules.items():
                listbox.insert(tk.END, f"{ext} → {folder}")

        def remove_rule():
            sel = listbox.curselection()
            if sel:
                item = listbox.get(sel[0])
                ext = item.split(" → ")[0]
                if ext in rules:
                    del rules[ext]
                    self.config["custom_rules"] = rules
                    save_config(self.config)
                    update_listbox()

        ttk.Button(dialog, text="🗑️ Remove Selected", command=remove_rule).pack(pady=5)
        update_listbox()

    def start_organize(self, safe=False):
        path = self.folder_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("⚠️", "Select a valid folder!")
            return

        self.progress_bar['value'] = 0
        self.log_box.delete(1.0, tk.END)
        self.log("🔍 Starting...")

        thread = threading.Thread(target=self._organize_thread, args=(path, safe))
        thread.daemon = True
        thread.start()

    def _organize_thread(self, path, safe):
        try:
            move_log, stats = organize_files(
                path,
                self.log,
                self.update_progress,
                custom_rules=self.config.get("custom_rules"),
                safe_mode=safe
            )
            if not safe:
                save_history(move_log)

            # Update stats panel
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "📊 File Distribution:\n\n")
            for cat, count in sorted(stats.items()):
                self.stats_text.insert(tk.END, f"{cat}: {count}\n")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}")

    def undo_last(self):
        self.log("↩️ Undoing last operation...")
        undo_last_operation(self.log)

    def export_log(self):
        log_content = self.log_box.get(1.0, tk.END).strip()
        if not log_content:
            messagebox.showinfo("ℹ️", "Log is empty!")
            return
        filename = f"organize_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(log_content)
            messagebox.showinfo("✅", f"Log saved to:\n{filepath}")

# ========================
# RUN
# ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()