import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Optional, Callable

BACKGROUND = '#f7f7f7'
TEXT_COLOR = '#333333'
BUTTON_ORANGE = '#ff8c00'
BUTTON_RED = '#ff4444'
PROGRESS_BAR = '#ff8c00'

KNOWN_HACKS = [
    "impact", "wurst", "meteor", "aristois",
    "kami", "inertia", "liquidbounce",
    "seedcracker", "baritone",
]


class SafeMCChecker:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Minecraft Чекер")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND)

        self.check_in_progress = False
        self.scan_thread = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        self.welcome_frame = tk.Frame(self.root, bg=BACKGROUND)
        self.check_frame = tk.Frame(self.root, bg=BACKGROUND)
        self.result_frame = tk.Frame(self.root, bg=BACKGROUND)

        tk.Label(
            self.welcome_frame,
            text="Minecraft Чекер",
            font=("Arial", 18, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        ).pack(pady=20)

        tk.Label(
            self.welcome_frame,
            text="Выберите тип проверки:",
            font=("Arial", 12),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        ).pack(pady=10)

        btn_frame = tk.Frame(self.welcome_frame, bg=BACKGROUND)
        btn_frame.pack(pady=20)

        self.quick_btn = tk.Button(
            btn_frame,
            text="Быстрая проверка",
            command=self._start_quick_scan,
            font=("Arial", 12),
            bg=BUTTON_ORANGE,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT
        )
        self.quick_btn.pack(side=tk.LEFT, padx=10)

        self.full_btn = tk.Button(
            btn_frame,
            text="Полная проверка",
            command=self._start_full_scan,
            font=("Arial", 12),
            bg=BUTTON_ORANGE,
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT
        )
        self.full_btn.pack(side=tk.LEFT, padx=10)

        tk.Label(
            self.check_frame,
            text="Проверка системы",
            font=("Arial", 18, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        ).pack(pady=20)

        self.progress_label = tk.Label(
            self.check_frame,
            font=("Arial", 12),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        )
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(
            self.check_frame,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.progress_bar.pack(pady=20)

        self.details_label = tk.Label(
            self.check_frame,
            font=("Arial", 10),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        )
        self.details_label.pack(pady=5)

        tk.Label(
            self.result_frame,
            text="Результаты проверки",
            font=("Arial", 18, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOR
        ).pack(pady=20)

        self.result_icon = tk.Label(
            self.result_frame,
            font=("Arial", 50),
            bg=BACKGROUND
        )
        self.result_icon.pack(pady=10)

        self.result_text = tk.Text(
            self.result_frame,
            height=12,
            width=70,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg='white',
            fg=TEXT_COLOR,
            padx=10,
            pady=10
        )

        scroll = ttk.Scrollbar(
            self.result_frame,
            command=self.result_text.yview
        )
        self.result_text.config(yscrollcommand=scroll.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(
            self.result_frame,
            text="Закрыть",
            command=self.root.destroy,
            font=("Arial", 12, "bold"),
            bg=BUTTON_RED,
            fg='white',
            padx=30,
            pady=8,
            relief=tk.FLAT
        ).pack(pady=20)

        self._show_frame(self.welcome_frame)

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Horizontal.TProgressbar",
            background=PROGRESS_BAR,
            troughcolor=BACKGROUND
        )

    def _show_frame(self, frame: tk.Frame):
        for f in [self.welcome_frame, self.check_frame, self.result_frame]:
            f.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def _update_progress(self, current: int, total: int, message: str):
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar["value"] = percent
            self.progress_label.config(text=f"{percent}%")
        self.details_label.config(text=message)
        self.root.update()

    def _start_quick_scan(self):
        self.check_in_progress = True
        self._show_frame(self.check_frame)
        self.progress_bar["value"] = 0

        def scan():
            try:
                found_files = quick_scan(self._update_progress)
                self.check_in_progress = False
                self._show_results(found_files, "Быстрая проверка завершена!")
            except Exception as e:
                self.check_in_progress = False
                messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        threading.Thread(target=scan, daemon=True).start()

    def _start_full_scan(self):
        if not messagebox.askyesno(
                "Подтверждение",
                "Полная проверка может занять много времени. Продолжить?",
                parent=self.root
        ):
            return

        self.check_in_progress = True
        self._show_frame(self.check_frame)
        self.progress_bar["value"] = 0

        def scan():
            try:
                found_files = full_scan(self._update_progress)
                self.check_in_progress = False
                self._show_results(found_files, "Полная проверка завершена!")
            except Exception as e:
                self.check_in_progress = False
                messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        threading.Thread(target=scan, daemon=True).start()

    def _show_results(self, found_hacks: List[str], message: str):
        if found_hacks:
            self.result_icon.config(text="❌", fg=BUTTON_RED)
            result_text = (
                f"{message}\n\nНайдено {len(found_hacks)} подозрительных файлов:\n\n"
                f"{'\n'.join(found_hacks[:30])}"
            )
            if len(found_hacks) > 30:
                result_text += f"\n\n...и ещё {len(found_hacks) - 30} файлов"
        else:
            self.result_icon.config(text="✔", fg="#4CAF50")
            result_text = f"{message}\n\nЧиты не обнаружены. Ваш компьютер чист!"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
        self.result_text.config(state=tk.DISABLED)
        self._show_frame(self.result_frame)

    def on_close(self):
        if self.check_in_progress:
            messagebox.showwarning(
                "Проверка в процессе",
                "Пожалуйста, дождитесь завершения проверки."
            )
        else:
            self.root.destroy()


def get_all_drives() -> List[str]:
    if os.name == 'nt':
        import string
        from ctypes import windll
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1
        return drives
    return ["/"]


def scan_path(path: str, progress_callback: Optional[Callable] = None) -> List[str]:
    found = []
    if not os.path.exists(path):
        return found

    try:
        files = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                files.append(filepath)

                if progress_callback and len(files) % 100 == 0:
                    progress_callback(len(files), 0, f"Сканирование {path}...")

        for file in files:
            filename = os.path.basename(file).lower()
            for hack in KNOWN_HACKS:
                if re.search(r'\b' + re.escape(hack.lower()) + r'\b', filename):
                    found.append(file)
    except Exception:
        pass

    return found


def quick_scan(progress_callback: Optional[Callable] = None) -> List[str]:
    paths = [
        os.path.expanduser("~/.minecraft"),
        os.path.join(os.getenv("APPDATA", ""), ".minecraft"),
        os.path.join(os.getenv("LOCALAPPDATA", ""), ""),
        os.path.join(os.getenv("APPDATA", ""), ""),
        os.path.join(os.getenv("PROGRAMFILES", ""), ""),
        os.path.join(os.getenv("PROGRAMFILES(X86)", ""), ""),
        os.path.join(os.getenv("PROGRAMDATA", ""), "")
    ]

    found = []
    total = len(paths)

    for i, path in enumerate(paths):
        if progress_callback:
            progress_callback(i, total, f"Проверка {os.path.basename(path)}...")
        found.extend(scan_path(path))

    return found


def full_scan(progress_callback: Optional[Callable] = None) -> List[str]:
    found = []
    drives = get_all_drives()
    total_files = 0

    # Подсчет общего количества файлов для прогресса
    for drive in drives:
        for root, _, files in os.walk(drive):
            total_files += len(files)
            if progress_callback:
                progress_callback(0, total_files, "Подсчет файлов...")

    # Проверка файлов
    checked_files = 0
    for drive in drives:
        for root, _, files in os.walk(drive):
            for file in files:
                filename = file.lower()
                for hack in KNOWN_HACKS:
                    if re.search(r'\b' + re.escape(hack.lower()) + r'\b', filename):
                        found.append(os.path.join(root, file))

                checked_files += 1
                if progress_callback and checked_files % 100 == 0:
                    progress_callback(checked_files, total_files, f"Проверка {drive}...")

    return found


if __name__ == "__main__":
    root = tk.Tk()
    app = SafeMCChecker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()