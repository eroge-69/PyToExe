import os
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import webbrowser
import multiprocessing
import sys

# Auto-install psutil if missing
def ensure_psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        except Exception as e:
            tk.Tk().withdraw()
            messagebox.showerror("Dependency Error", f"Failed to auto-install psutil: {e}")
            sys.exit(1)
        import psutil
        return psutil
psutil = ensure_psutil()

# Auto-install Pillow (PIL) if missing
try:
    from PIL import Image, ImageTk
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

THEMES = {
    "HACKER": {
        "bg": "#0B1513", "panel": "#161f22", "header": "#08f800", "fg": "#121312",
        "label": "#7fffca", "entry_bg": "#171d1d", "button_bg": "#141d15",
        "button_fg": "#14ff60", "button_active_bg": "#000000", "button_active_fg": "#ffffff",
        "progress": "#0fff4d"
    },
    "BLUE": {
        "bg": "#000000", "panel": "#172852", "header": "#37a7ff", "fg": "#eaf6ff",
        "label": "#ffffff", "entry_bg": "#183163", "button_bg": "#1839a3",
        "button_fg": "#d8e7ff", "button_active_bg": "#39a2ff", "button_active_fg": "#001037",
        "progress": "#00bfff"
    },
    "LIGHT": {
        "bg": "#F8EDED", "panel": "#FFF8F8", "header": "#000000", "fg": "#030303",
        "label": "#000000", "entry_bg": "#000000", "button_bg": "#ffffff",
        "button_fg": "#000000", "button_active_bg": "#000000", "button_active_fg": "#020202",
        "progress": "#000000"
    },
    "BLACK": {
        "bg": "#000000", "panel": "#000000", "header": "#fefeff", "fg": "#F1EDED",
        "label": "#FFFFFF", "entry_bg": "#303030", "button_bg": "#5A5A5A",
        "button_fg": "#ffffff", "button_active_bg": "#dfe0e2", "button_active_fg": "#FFFFFF",
        "progress": "#FFFFFF"
    }
}

def extract_chunk(chunk_lines, domain):
    regex = re.compile(
        rf'(?:https?://)?[^/]*{re.escape(domain)}[^\s]*[=:]\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+:[^\s:]+)',
        re.IGNORECASE
    )
    combos = set()
    for line in chunk_lines:
        m = regex.search(line)
        if m:
            combo = m.group(1).strip()
            if not combo.lower().startswith("n/a") and "@" in combo.split(":")[0]:
                combos.add(combo)
    return combos

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB'}
    while size > power and n < 3:
        size /= power
        n += 1
    return f"{size:.1f} {power_labels[n]}"

class ComboExtractorApp:
    def __init__(self, master):
        self.master = master
        self.theme_name = self.load_theme()  # Load saved theme!
        self.theme = THEMES[self.theme_name]
        self.file_path = None
        self.output_dir = os.path.join(os.getcwd(), "combo_output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.last_output_file = None

        self.master.title("KAZUYA ULTRA FAST COMBO HUNTER")
        self.master.geometry("785x855")
        self.master.minsize(755, 820)

        # Set .ico icon if present (best for Windows/EXE builds)
        ico_path = os.path.join(os.path.dirname(__file__), "frontman.ico")
        if os.path.exists(ico_path):
            try:
                self.master.iconbitmap(ico_path)
            except Exception:
                pass

        # Set top GUI logo (jpg/png)
        self.icon_img = None
        icon_jpg_path = os.path.join(os.path.dirname(__file__), "frontman.jpg")
        icon_png_path = os.path.join(os.path.dirname(__file__), "frontman.png")
        self._logo_path = None
        if os.path.exists(icon_jpg_path):
            self._logo_path = icon_jpg_path
        elif os.path.exists(icon_png_path):
            self._logo_path = icon_png_path

        self.create_widgets()
        self.apply_theme()
        self._sys_monitor_running = False

    def create_widgets(self):
        self.bg = tk.Frame(self.master, bg=self.theme["bg"])
        self.bg.pack(expand=True, fill=tk.BOTH)
        self.panel = tk.Frame(self.bg, bg=self.theme["panel"])
        self.panel.pack(padx=24, pady=18, fill=tk.BOTH, expand=True)

        # TOP-CENTER LOGO ICON
        if self._logo_path:
            try:
                img = Image.open(self._logo_path).resize((52, 52))
                self.img_icon = ImageTk.PhotoImage(img)
                tk.Label(self.panel, image=self.img_icon, bg=self.theme["panel"]).pack(pady=(3, 2))
            except Exception:
                pass

        # TITLE
        self.header = tk.Label(
            self.panel, text="KAZUYA COMBO HUNTER V.1",
            font=("Consolas", 17, "bold"), bg=self.theme["panel"], fg=self.theme["header"]
        )
        self.header.pack(pady=(0, 3))

        # COMPACT system info bar
        self.status_frame = tk.Frame(self.panel, bg="#171d1d")
        self.status_frame.pack(fill=tk.X, padx=0, pady=(0, 4))
        bar_font = ("Consolas", 10, "normal")
        self.sys_status_bar = tk.Label(
            self.status_frame, text=self.get_sys_status_text(),
            font=bar_font, bg="#171d1d", fg="#a0ffb0",
            pady=1, padx=2, anchor="center", justify="center"
        )
        self.sys_status_bar.pack(fill=tk.BOTH, padx=0, pady=0)
        self._sys_monitor_running = False

        # Step 1: Combo File
        file_row = tk.Frame(self.panel, bg=self.theme["panel"])
        file_row.pack(fill=tk.X, pady=(2, 7))
        tk.Label(file_row, text="Combo File:", font=("Segoe UI", 12, "bold"),
                 fg=self.theme["label"], bg=self.theme["panel"]).pack(side=tk.LEFT)
        self.file_label = tk.Label(file_row, text="No file selected", font=("Segoe UI", 10, "italic"),
                                   fg="#7fffca", bg=self.theme["panel"])
        self.file_label.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.browse_button = tk.Button(
            file_row, text="Browse", command=self.browse_file, width=10,
            font=("Segoe UI", 11, "bold"), bg=self.theme["button_bg"], fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_active_fg"],
            cursor="hand2", relief="raised", bd=2
        )
        self.browse_button.pack(side=tk.RIGHT, padx=(12, 2))

        # Step 2: Target
        target_row = tk.Frame(self.panel, bg=self.theme["panel"])
        target_row.pack(fill=tk.X, pady=(2, 7))
        tk.Label(target_row, text="Target Domain:", font=("Segoe UI", 12, "bold"),
                 fg=self.theme["label"], bg=self.theme["panel"]).pack(side=tk.LEFT)
        self.domain_entry = tk.Entry(target_row, font=("Consolas", 11, "bold"), width=21,
                                     bg=self.theme["entry_bg"], fg=self.theme["header"],
                                     insertbackground=self.theme["header"], relief="solid", bd=2)
        self.domain_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Step 3: Theme
        theme_frame = tk.Frame(self.panel, bg=self.theme["panel"])
        theme_frame.pack(pady=(0, 7))
        tk.Label(theme_frame, text="Theme:", font=("Segoe UI", 11, "bold"),
                 fg=self.theme["label"], bg=self.theme["panel"]).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.theme_name)
        self.theme_option = tk.OptionMenu(
            theme_frame, self.theme_var, *THEMES.keys(), command=self.change_theme
        )
        self.theme_option.config(
            width=12, font=("Segoe UI", 10),
            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_active_fg"],
            relief="raised", cursor="hand2"
        )
        self.theme_option.pack(side=tk.LEFT, padx=8)

        # STATUS Title (bold, green, above progress bar)
        self.status_title = tk.Label(
            self.panel,
            text="STATUS",
            font=("Consolas", 15, "bold"),
            bg=self.theme["panel"],
            fg=self.theme["header"]
        )
        self.status_title.pack(pady=(7, 0))  # Add a bit of space above

        # Progress Bar + %
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("custom.Horizontal.TProgressbar",
                        background=self.theme["progress"], troughcolor=self.theme["panel"], thickness=14)
        self.progress = ttk.Progressbar(self.panel, length=520, mode='determinate', style="custom.Horizontal.TProgressbar")
        self.progress.pack(pady=(7, 0))
        self.progress_label = tk.Label(self.panel, text="Loading... 0%", font=("Consolas", 11, "bold"),
                                       fg=self.theme["header"], bg=self.theme["panel"])
        self.progress_label.pack(pady=(0, 5))
        self.progress_status_label = tk.Label(
            self.panel, text="Progress: 0%", font=("Segoe UI", 11, "bold"),
            bg=self.theme["panel"], fg=self.theme["label"]
        )
        self.progress_status_label.pack(pady=(0, 6))

        # Extraction info
        self.status_label = tk.Label(
            self.panel, text="Status: Idle", font=("Segoe UI", 11, "bold"),
            bg=self.theme["panel"], fg=self.theme["header"]
        )
        self.status_label.pack(pady=(2, 5))

        self.extracted_label = tk.Label(
            self.panel, text="", font=("Consolas", 11, "bold"),
            bg=self.theme["panel"], fg=self.theme["header"]
        )
        self.extracted_label.pack(pady=(1, 7))

        self.output_label = tk.Label(
            self.panel, text="", font=("Segoe UI", 10, "bold"),
            fg="#00EB1F", bg=self.theme["panel"], cursor="hand2"
        )
        self.output_label.pack(pady=(1, 8))
        self.output_label.bind("<Button-1>", self.open_output_folder)

        self.start_button = tk.Button(
            self.panel, text="START EXTRACTION", command=self.run_extraction, width=21,
            font=("Segoe UI", 13, "bold"),
            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_active_fg"],
            cursor="hand2", relief="raised", bd=4
        )
        self.start_button.pack(pady=(7, 10))

        self.instructions = tk.Label(
            self.panel,
            text=(
                "Steps:\n"
                "1️⃣  Browse and select your combo file (.txt)\n"
                "2️⃣  Enter a target domain (ex: capcut)\n"
                "3️⃣  Pick a color theme\n"
                "4️⃣  Click 'START EXTRACTION'\n\n"
                "✔  Only real combos like email:password are extracted\n"
                "✔  Output: 'combo_output' folder (click label to open)\n"
                "✔  Ultra fast parallel mode = no lag (millions of lines OK)\n"
                "✔  Live RAM/CPU/cores above!"
            ),
            font=("Segoe UI", 10), bg=self.theme["panel"], fg=self.theme["label"], justify="left"
        )
        self.instructions.pack(pady=(0, 1))

    # ========== THEME SAVE/LOAD ==========
    def save_theme(self):
        try:
            with open("kazuya_theme.txt", "w") as f:
                f.write(self.theme_var.get())
        except Exception:
            pass

    def load_theme(self):
        try:
            with open("kazuya_theme.txt", "r") as f:
                value = f.read().strip()
                if value in THEMES:
                    return value
        except Exception:
            pass
        return "HACKER"

    def change_theme(self, val):
        self.apply_theme()
        self.save_theme()
    # =====================================

    def apply_theme(self):
        self.theme = THEMES[self.theme_var.get()]
        self.bg.config(bg=self.theme["bg"])
        self.panel.config(bg=self.theme["panel"])
        self.header.config(bg=self.theme["panel"], fg=self.theme["header"])
        self.status_frame.config(bg="#171d1d")
        self.sys_status_bar.config(bg="#171d1d", fg="#a0ffb0")
        for row in [self.file_label, self.status_label, self.extracted_label,
                    self.instructions, self.progress_label, self.output_label,
                    self.progress_status_label, self.status_title]:
            row.config(bg=self.theme["panel"])
        self.status_label.config(fg=self.theme["header"])
        self.progress_label.config(fg=self.theme["header"])
        self.progress_status_label.config(fg=self.theme["label"])
        self.status_title.config(bg=self.theme["panel"], fg=self.theme["header"])
        self.output_label.config(fg="#41f700")
        for btn in [self.browse_button, self.start_button]:
            btn.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                       activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_active_fg"])
        self.domain_entry.config(bg=self.theme["entry_bg"], fg=self.theme["header"], insertbackground=self.theme["header"])
        self.theme_option.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                activebackground=self.theme["button_active_bg"], activeforeground=self.theme["button_active_fg"])
        # Always use compact font for sys_status_bar
        self.sys_status_bar.config(font=("Consolas", 10, "normal"))

    def browse_file(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select Combo File", filetypes=filetypes)
        if path:
            self.file_path = path
            self.file_label.config(text=os.path.basename(path), fg=self.theme["header"])

    def get_sys_status_text(self):
        if not psutil:
            return "System RAM: N/A | CPUs: N/A | CPU Usage: N/A | App RAM: N/A"
        vm = psutil.virtual_memory()
        total = format_bytes(vm.total)
        avail = format_bytes(vm.available)
        cpus = psutil.cpu_count(logical=True)
        cpu_pct = psutil.cpu_percent(interval=0.1)
        process = psutil.Process(os.getpid())
        used = format_bytes(process.memory_info().rss)
        return (
            f"🖥️ System RAM: {total} / {avail}    "
            f"🧠 App RAM: {used}    "
            f"🟩 Logical CPUs: {cpus}    "
            f"⚡ CPU Usage: {cpu_pct:.0f}%"
        )

    def sys_monitor(self):
        if not psutil:
            self.sys_status_bar.config(
                text="System RAM: N/A | CPUs: N/A | CPU Usage: N/A | App RAM: N/A",
                font=("Consolas", 9, "normal")
            )
            return
        self._sys_monitor_running = True
        while self._sys_monitor_running:
            text = self.get_sys_status_text()
            self.sys_status_bar.config(text=text, font=("Consolas", 10, "normal"))
            time.sleep(1)

    def stop_sys_monitor(self):
        self._sys_monitor_running = False

    def run_extraction(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a combo file first.")
            return
        target = self.domain_entry.get().strip().lower()
        if not target:
            messagebox.showerror("Error", "Please enter the TARGET domain.")
            return

        # RAM SAFETY CHECK
        try:
            file_size = os.path.getsize(self.file_path)
            est_ram_needed = int(file_size * 2.2)
            ram_ok = True
            warning_msg = ""
            if psutil:
                avail = psutil.virtual_memory().available
                if est_ram_needed > avail:
                    ram_ok = False
                    warning_msg = (
                        f"WARNING: Combo file is large ({format_bytes(file_size)}). "
                        f"Estimated RAM needed: {format_bytes(est_ram_needed)}\n"
                        f"Available RAM: {format_bytes(avail)}\n"
                        "You may run out of memory and the app could freeze or crash.\n"
                        "It's recommended to process on a PC with more RAM or use a smaller file."
                    )
            if not ram_ok:
                if not messagebox.askyesno("RAM WARNING", warning_msg + "\n\nContinue anyway?"):
                    return
        except Exception:
            pass

        self.start_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.domain_entry.config(state="disabled")
        self.theme_option.config(state="disabled")
        self.extracted_label.config(text="")
        self.output_label.config(text="")
        self.status_label.config(text="Status: Extracting...", fg=self.theme["header"])
        self.progress["value"] = 0
        self.progress_label.config(text="Loading... 1%", fg=self.theme["header"])
        self.progress_status_label.config(text="Progress: 1%")
        Thread(target=self.sys_monitor, daemon=True).start()
        Thread(target=self.parallel_extraction, args=(target,)).start()

    def update_progress(self, percent):
        self.progress["value"] = percent
        self.progress_label.config(text=f"Loading... {percent}%", fg=self.theme["header"])
        self.progress_status_label.config(text=f"Progress: {percent}%")
        self.progress.update()

    def parallel_extraction(self, target):
        start_time = time.time()
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
        except Exception:
            total_lines = 1
        chunk_size = 300_000
        chunks = []
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            chunk = []
            for line in f:
                chunk.append(line)
                if len(chunk) >= chunk_size:
                    chunks.append(list(chunk))
                    chunk.clear()
            if chunk:
                chunks.append(list(chunk))
        n_chunks = len(chunks)

        manager = multiprocessing.Manager()
        results = manager.list()
        progress = manager.Value('i', 0)
        def callback(res):
            results.append(res)
            progress.value += 1
            percent = int((progress.value / n_chunks) * 100)
            if percent < 100:
                self.master.after(0, lambda: self.update_progress(percent))
        pool = multiprocessing.Pool(processes=max(2, multiprocessing.cpu_count() - 1))
        for i in range(n_chunks):
            pool.apply_async(extract_chunk, args=(chunks[i], target), callback=callback)
        pool.close()
        pool.join()
        combos = set()
        for s in results:
            combos.update(s)
        match_count = len(combos)
        count_label = f"{match_count // 1000}k" if match_count >= 1000 else str(match_count)
        output_file = os.path.join(self.output_dir, f"{count_label}_{target}_combos.txt")
        self.last_output_file = output_file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(combos)))
            elapsed = time.time() - start_time
            msg = f"✅ DONE! Saved: {os.path.basename(output_file)} ({elapsed:.2f}s)"
            result = f"Extracted combos: {match_count}"
        except Exception as e:
            msg = f"❌ Error: {e}"
            result = ""
        self.progress["value"] = 100
        self.progress_label.config(text="Loading... 100%", fg=self.theme["header"])
        self.progress_status_label.config(text="Progress: 100%")
        self.status_label.config(text=msg, fg=self.theme["header"])
        self.extracted_label.config(text=result)
        self.output_label.config(
            text="🗂 Open 'combo_output' folder (Click here)",
            fg="#41f700"
        )
        self.finish_processing()
        self.stop_sys_monitor()

    def open_output_folder(self, event=None):
        if os.name == "nt":  # Windows
            os.startfile(self.output_dir)
        else:  # Mac or Linux
            webbrowser.open(f"file://{self.output_dir}")

    def finish_processing(self):
        self.start_button.config(state="normal")
        self.browse_button.config(state="normal")
        self.domain_entry.config(state="normal")
        self.theme_option.config(state="normal")

def launch_gui():
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = ComboExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()