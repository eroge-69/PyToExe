#!/usr/bin/env python3
"""
MiniPyOS — игрушечная «операционная система» в окне.

Особенности демо:
- Окно «рабочего стола» с панелью задач и лаунчером приложений
- Виртуальная файловая система (VFS) в папке ./pyos_disk
- Терминал с базовыми командами: help, ls, cd, pwd, cat, echo, mkdir, rm, clear, time, about, exit
- Блокнот (редактор текста) с открытием/сохранением файлов только внутри VFS
- Файловый менеджер (просмотр и навигация в VFS)
- Настройки (тема светлая/тёмная, автосохранение конфигурации)
- Диспетчер «процессов» (показывает открытые окна приложений)
- Примитивная система плагинов: любые .py из ./apps, содержащие функцию register(app_context)

Запуск: python mini_py_os.py
Зависимости: только стандартная библиотека Python (tkinter/ttk).
"""
from __future__ import annotations
import os
import sys
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "MiniPyOS"
APP_VERSION = "0.1.0"

# Директории
BASE_DIR = Path(os.getcwd())
VFS_ROOT = BASE_DIR / "pyos_disk"
CONFIG_DIR = BASE_DIR / ".pyos"
APPS_DIR = BASE_DIR / "apps"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "light",  # light | dark
    "last_cwd": "/",
}

# ============================ Утилиты ============================

def ensure_dirs():
    VFS_ROOT.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    # создадим стартовые файлы
    (VFS_ROOT / "readme.txt").write_text(
        "Добро пожаловать в MiniPyOS!\nЭто виртуальный диск. Файлы за его пределами недоступны.",
        encoding="utf-8",
    ) if not (VFS_ROOT / "readme.txt").exists() else None


def load_config() -> dict:
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


# Путь внутри VFS: нормализация и безопасность

def vfs_norm(path: str) -> Path:
    p = (VFS_ROOT / path.lstrip("/\\")).resolve()
    # Запрет выхода за пределы VFS
    if not str(p).startswith(str(VFS_ROOT.resolve())):
        raise PermissionError("Выход за пределы VFS запрещён")
    return p


# ============================ Контекст приложения ============================
class AppContext:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_config()
        self.cwd = self.cfg.get("last_cwd", "/")
        self.processes: dict[str, tk.Toplevel] = {}
        self.plugins: dict[str, callable] = {}

    def set_cwd(self, new_cwd: str):
        # проверим существование
        p = vfs_norm(new_cwd)
        p.mkdir(parents=True, exist_ok=True)
        # сохранить как путь вида "/sub/dir"
        rel = "/" + str(p.relative_to(VFS_ROOT)).replace("\\", "/") if p != VFS_ROOT else "/"
        self.cwd = rel
        self.cfg["last_cwd"] = rel
        save_config(self.cfg)

    def abs_path(self, rel: str) -> Path:
        if rel in ("/", ""):
            return VFS_ROOT
        if rel.startswith("/"):
            return vfs_norm(rel)
        # относительный от cwd
        base = vfs_norm(self.cwd)
        return vfs_norm(str((base / rel).as_posix()))

    # процесс-менеджер
    def register_window(self, title: str, win: tk.Toplevel):
        self.processes[title] = win
        def on_close():
            try:
                del self.processes[title]
            except KeyError:
                pass
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)
        update_taskbar()

    def broadcast(self, event: str, payload: dict | None = None):
        # для плагинов/окон
        pass


# ============================ Темы ============================
LIGHT = {
    "bg": "#f4f4f5",
    "fg": "#111827",
    "panel": "#e5e7eb",
}
DARK = {
    "bg": "#0b1220",
    "fg": "#e5e7eb",
    "panel": "#111827",
}


def apply_theme(style: ttk.Style, theme: str):
    palette = LIGHT if theme == "light" else DARK
    root.configure(bg=palette["bg"])  # type: ignore
    style.configure("TFrame", background=palette["bg"])
    style.configure("TLabel", background=palette["bg"], foreground=palette["fg"])
    style.configure("TButton", padding=6)
    style.configure("Panel.TFrame", background=palette["panel"]) 


# ============================ Приложения ============================

def open_about(ctx: AppContext):
    win = tk.Toplevel(root)
    win.title(f"О системе — {APP_NAME}")
    win.geometry("380x220")
    frame = ttk.Frame(win, padding=12)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=f"{APP_NAME} {APP_VERSION}", font=("Segoe UI", 14, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Игрушечная ОС в окне. Всё хранится в ./pyos_disk").pack(anchor="w", pady=(8,0))
    ttk.Label(frame, text="Автор: вы :)  Лицензия: do-what-you-want").pack(anchor="w")
    ttk.Button(frame, text="OK", command=win.destroy).pack(anchor="e", pady=16)
    ctx.register_window("About", win)


def open_notepad(ctx: AppContext, open_path: str | None = None):
    win = tk.Toplevel(root)
    win.title("Блокнот")
    win.geometry("700x480")
    ctx.register_window("Notepad", win)

    current_file: list[Path | None] = [None]

    def do_open():
        base = ctx.abs_path(".")
        file = filedialog.askopenfilename(initialdir=base, title="Открыть файл из VFS")
        if not file:
            return
        p = vfs_norm(Path(file).relative_to(VFS_ROOT).as_posix())
        text.delete("1.0", "end")
        try:
            text.insert("1.0", p.read_text(encoding="utf-8"))
            current_file[0] = p
            win.title(f"Блокнот — {p.name}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def do_save_as():
        base = ctx.abs_path(".")
        file = filedialog.asksaveasfilename(initialdir=base, title="Сохранить в VFS")
        if not file:
            return
        p = vfs_norm(Path(file).relative_to(VFS_ROOT).as_posix())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.get("1.0", "end-1c"), encoding="utf-8")
        current_file[0] = p
        win.title(f"Блокнот — {p.name}")

    def do_save():
        if current_file[0] is None:
            return do_save_as()
        p = current_file[0]
        assert isinstance(p, Path)
        p.write_text(text.get("1.0", "end-1c"), encoding="utf-8")

    toolbar = ttk.Frame(win, padding=(8,6))
    toolbar.pack(fill="x")
    ttk.Button(toolbar, text="Открыть", command=do_open).pack(side="left")
    ttk.Button(toolbar, text="Сохранить", command=do_save).pack(side="left")
    ttk.Button(toolbar, text="Сохранить как", command=do_save_as).pack(side="left")

    text = tk.Text(win, wrap="word", undo=True)
    text.pack(fill="both", expand=True)

    if open_path:
        p = ctx.abs_path(open_path)
        if p.exists():
            text.insert("1.0", p.read_text(encoding="utf-8"))
            current_file[0] = p
            win.title(f"Блокнот — {p.name}")


def open_file_manager(ctx: AppContext):
    win = tk.Toplevel(root)
    win.title("Файловый менеджер")
    win.geometry("720x500")
    ctx.register_window("Files", win)

    path_var = tk.StringVar(value=ctx.cwd)

    def refresh():
        tree.delete(*tree.get_children(""))
        p = ctx.abs_path(path_var.get())
        try:
            for entry in sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name.lower())):
                tree.insert("", "end", values=("DIR" if entry.is_dir() else "FILE", entry.name, entry.stat().st_size))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def enter_dir():
        sel = tree.focus()
        if not sel:
            return
        vals = tree.item(sel, "values")
        if vals and vals[0] == "DIR":
            new = Path(path_var.get().rstrip("/")) / vals[1]
            ctx.set_cwd(new.as_posix())
            path_var.set(ctx.cwd)
            refresh()

    def up_dir():
        if ctx.cwd == "/":
            return
        new = Path(ctx.cwd).parent.as_posix()
        ctx.set_cwd(new if new != "." else "/")
        path_var.set(ctx.cwd)
        refresh()

    def open_file():
        sel = tree.focus()
        if not sel:
            return
        vals = tree.item(sel, "values")
        if vals and vals[0] == "FILE":
            open_notepad(ctx, (Path(ctx.cwd) / vals[1]).as_posix())

    top = ttk.Frame(win, padding=8)
    top.pack(fill="x")
    ttk.Button(top, text="⬅", width=3, command=up_dir).pack(side="left")
    ttk.Entry(top, textvariable=path_var).pack(side="left", fill="x", expand=True, padx=6)
    ttk.Button(top, text="Перейти", command=lambda: (ctx.set_cwd(path_var.get()), refresh())).pack(side="left")

    cols = ("Тип", "Имя", "Размер")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
    tree.pack(fill="both", expand=True)
    tree.bind("<Double-1>", lambda e: (enter_dir() if tree.item(tree.focus(), "values")[0]=="DIR" else open_file()))

    refresh()


def open_settings(ctx: AppContext):
    win = tk.Toplevel(root)
    win.title("Настройки")
    win.geometry("380x240")
    ctx.register_window("Settings", win)

    frame = ttk.Frame(win, padding=12)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Тема интерфейса").grid(row=0, column=0, sticky="w")
    theme_var = tk.StringVar(value=ctx.cfg.get("theme", "light"))
    ttk.Radiobutton(frame, text="Светлая", variable=theme_var, value="light").grid(row=1, column=0, sticky="w")
    ttk.Radiobutton(frame, text="Тёмная", variable=theme_var, value="dark").grid(row=2, column=0, sticky="w")

    def apply_and_save():
        ctx.cfg["theme"] = theme_var.get()
        save_config(ctx.cfg)
        apply_theme(style, ctx.cfg["theme"])

    ttk.Button(frame, text="Применить", command=apply_and_save).grid(row=3, column=0, pady=12, sticky="w")

    ttk.Label(frame, text=f"Версия: {APP_VERSION}").grid(row=4, column=0, sticky="w", pady=(8,0))


def open_task_manager(ctx: AppContext):
    win = tk.Toplevel(root)
    win.title("Диспетчер окон")
    win.geometry("420x300")
    ctx.register_window("TaskMgr", win)

    tree = ttk.Treeview(win, columns=("title",), show="headings")
    tree.heading("title", text="Окно")
    tree.pack(fill="both", expand=True)

    def refresh():
        tree.delete(*tree.get_children(""))
        for title in sorted(ctx.processes.keys()):
            tree.insert("", "end", values=(title,))

    def close_selected():
        sel = tree.focus()
        if not sel:
            return
        title = tree.item(sel, "values")[0]
        w = ctx.processes.get(title)
        if w:
            w.destroy()
            refresh()

    btns = ttk.Frame(win, padding=8)
    btns.pack(fill="x")
    ttk.Button(btns, text="Обновить", command=refresh).pack(side="left")
    ttk.Button(btns, text="Закрыть окно", command=close_selected).pack(side="left", padx=6)

    refresh()


# ============================ Терминал ============================
class Terminal(ttk.Frame):
    PROMPT = "> "

    def __init__(self, master, ctx: AppContext):
        super().__init__(master)
        self.ctx = ctx
        self.text = tk.Text(self, height=20)
        self.text.pack(fill="both", expand=True)
        self.text.bind("<Return>", self.on_enter)
        self.text.insert("end", self.PROMPT)
        self.text.mark_set("insert", "end")

    def on_enter(self, event=None):
        # получить текущую строку
        line_start = self.text.index("insert linestart")
        line_end = self.text.index("insert lineend")
        cmd = self.text.get(line_start, line_end).strip().lstrip(self.PROMPT)
        self.text.insert("end", "\n")
        self.execute(cmd)
        self.text.insert("end", self.PROMPT)
        self.text.see("end")
        return "break"

    def write(self, s: str):
        self.text.insert("end", s + "\n")

    def execute(self, cmdline: str):
        if not cmdline:
            return
        parts = cmdline.split()
        cmd, *args = parts
        try:
            if cmd == "help":
                self.write("Команды: help, ls, cd, pwd, cat, echo, mkdir, rm, clear, time, about, exit")
            elif cmd == "ls":
                p = self.ctx.abs_path(args[0]) if args else self.ctx.abs_path(".")
                if p.is_dir():
                    for e in sorted(p.iterdir(), key=lambda e: e.name.lower()):
                        self.write(("[D] " if e.is_dir() else "    ") + e.name)
                else:
                    self.write(p.name)
            elif cmd == "cd":
                target = args[0] if args else "/"
                self.ctx.set_cwd((Path(self.ctx.cwd) / target).as_posix() if not target.startswith("/") else target)
            elif cmd == "pwd":
                self.write(self.ctx.cwd)
            elif cmd == "cat":
                p = self.ctx.abs_path(args[0])
                if p.is_file():
                    self.write(p.read_text(encoding="utf-8"))
                else:
                    self.write("Не файл")
            elif cmd == "echo":
                self.write(" ".join(args))
            elif cmd == "mkdir":
                p = self.ctx.abs_path(args[0])
                p.mkdir(parents=True, exist_ok=True)
            elif cmd == "rm":
                p = self.ctx.abs_path(args[0])
                if p.is_dir():
                    shutil.rmtree(p)
                elif p.exists():
                    p.unlink()
            elif cmd == "clear":
                self.text.delete("1.0", "end")
            elif cmd == "time":
                self.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif cmd == "about":
                self.write(f"{APP_NAME} {APP_VERSION}")
            elif cmd == "exit":
                self.master.destroy()
            else:
                self.write(f"Неизвестная команда: {cmd}")
        except Exception as e:
            self.write(f"Ошибка: {e}")


def open_terminal(ctx: AppContext):
    win = tk.Toplevel(root)
    win.title("Терминал")
    win.geometry("720x360")
    term = Terminal(win, ctx)
    term.pack(fill="both", expand=True)
    ctx.register_window("Terminal", win)


# ============================ Плагины ============================

def load_plugins(ctx: AppContext):
    sys.path.insert(0, str(APPS_DIR))
    for mod in APPS_DIR.glob("*.py"):
        try:
            m = __import__(mod.stem)
            if hasattr(m, "register"):
                m.register(ctx)
                ctx.plugins[mod.stem] = m
        except Exception as e:
            print("Ошибка плагина", mod.stem, e)


# ============================ Рабочий стол ============================

def update_clock():
    now = datetime.now().strftime("%H:%M:%S")
    clock_var.set(now)
    root.after(1000, update_clock)  # tick


def update_taskbar():
    # обновить список кнопок окон
    for w in taskbar_apps.winfo_children():
        w.destroy()
    for title, win in app_ctx.processes.items():
        ttk.Button(taskbar_apps, text=title, command=lambda w=win: (w.deiconify(), w.lift())).pack(side="left", padx=2)


def make_launcher_button(parent, text: str, command):
    btn = ttk.Button(parent, text=text, command=command)
    btn.pack(side="left", padx=6)


# ============================ main ============================
root = tk.Tk()
root.title(f"{APP_NAME} — рабочий стол")
root.geometry("1024x640")
style = ttk.Style()

app_ctx = AppContext(root)
apply_theme(style, app_ctx.cfg.get("theme", "light"))
ensure_dirs()

# Верхняя панель (лаунчер)
launcher = ttk.Frame(root, style="Panel.TFrame", padding=8)
launcher.pack(fill="x")

make_launcher_button(launcher, "Терминал", lambda: open_terminal(app_ctx))
make_launcher_button(launcher, "Файлы", lambda: open_file_manager(app_ctx))
make_launcher_button(launcher, "Блокнот", lambda: open_notepad(app_ctx))
make_launcher_button(launcher, "Настройки", lambda: open_settings(app_ctx))
make_launcher_button(launcher, "О системе", lambda: open_about(app_ctx))
make_launcher_button(launcher, "Диспетчер", lambda: open_task_manager(app_ctx))

# Основная область «рабочего стола»
desktop = ttk.Frame(root, padding=16)
desktop.pack(fill="both", expand=True)
welcome = ttk.Label(desktop, text="Добро пожаловать в MiniPyOS! Открывайте приложения сверху.", font=("Segoe UI", 12))
welcome.pack(anchor="center", expand=True)

# Панель задач снизу
status = ttk.Frame(root, style="Panel.TFrame", padding=6)
status.pack(fill="x", side="bottom")

clock_var = tk.StringVar(value="--:--:--")
clock_lbl = ttk.Label(status, textvariable=clock_var)
clock_lbl.pack(side="right")

# список открытых окон
taskbar_apps = ttk.Frame(status)
taskbar_apps.pack(side="left")

update_clock()
update_taskbar()

# Загрузка плагинов
load_plugins(app_ctx)

# Запуск цикла
root.mainloop()
