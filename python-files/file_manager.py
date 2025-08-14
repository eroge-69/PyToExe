#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OIBT Archive — полная рабочая версия (single-file)
Python 3.10+, Tk 8.6
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

# -------------------- Константы / пути --------------------

APP_NAME = "OIBT Archive"
DESTINATION_FOLDER = Path.cwd() / "files"
FILE_LIST_PATH = Path.cwd() / "file_list.json"

# В демо храним пароль в коде. В проде: храните хэш и сравнивайте безопасно (bcrypt/scrypt).
PASSWORD_PLAIN = "q123"

# -------------------- Хранилище и утилиты --------------------

@dataclass
class StoredFile:
    name: str
    added_at: str  # ISO-8601

def ensure_dirs() -> None:
    DESTINATION_FOLDER.mkdir(parents=True, exist_ok=True)

def load_file_list() -> list[StoredFile]:
    """Загрузка списка из JSON. Поддерживает миграцию со старого формата (просто массив имён)."""
    if not FILE_LIST_PATH.exists():
        return []
    try:
        data = json.loads(FILE_LIST_PATH.read_text(encoding="utf-8"))
    except Exception:
        # Битый JSON — сохраняем бэкап и начинаем заново
        try:
            FILE_LIST_PATH.replace(FILE_LIST_PATH.with_suffix(".bak"))
        except Exception:
            pass
        return []

    items: list[StoredFile] = []
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and "name" in it:
                items.append(StoredFile(name=str(it["name"]), added_at=str(it.get("added_at", ""))))
            elif isinstance(it, str):
                items.append(StoredFile(name=it, added_at=""))
    return items

def save_file_list(items: list[StoredFile]) -> None:
    FILE_LIST_PATH.write_text(
        json.dumps([asdict(x) for x in items], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def is_valid_filename(name: str) -> bool:
    """Грубая валидация имён (Windows-недопустимые символы + пустые)."""
    if not name or name.strip() == "":
        return False
    # запрещённые символы для кроссплат-совместимости
    return not re.search(r'[\\/:*?"<>|]', name)

def unique_name(dest_dir: Path, base_name: str) -> str:
    """Если файл существует — добавляет _1, _2, ..."""
    p = Path(base_name)
    stem, suffix = p.stem, p.suffix
    candidate = base_name
    i = 1
    while (dest_dir / candidate).exists():
        candidate = f"{stem}_{i}{suffix}"
        i += 1
    return candidate

# -------------------- Приложение --------------------

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1024x640")
        self.root.minsize(900, 560)

        self._apply_style()

        ensure_dirs()
        self.files: list[StoredFile] = load_file_list()
        # Синхронизируем с диском: удалённые с диска — убираем из JSON
        self._prune_missing_files()
        self.all_names_cache: list[str] = [f.name for f in self.files]

        self._build_menu()
        self._build_toolbar()
        self._build_main()
        self._build_statusbar()
        self._bind_shortcuts()

        self.splash: tk.Toplevel | None = None
        self.login: tk.Toplevel | None = None

        self._show_splash_then_login()

    # ---------- Внешний вид ----------

    def _apply_style(self):
        style = ttk.Style()
        try:
            if "clam" in style.theme_names():
                style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", padding=6)
        style.configure("Toolbar.TButton", padding=5)
        style.configure("Search.TEntry", padding=4)
        style.configure("Status.TLabel", padding=3)

    # ---------- Меню/тулбар/основная область ----------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Создать архивное дело…\tCtrl+O", command=self.upload_files)
        filem.add_command(label="Разархивация…\tCtrl+S", command=self.download_file)
        filem.add_separator()
        filem.add_command(label="Обновить список\tCtrl+R", command=self.refresh_from_disk)
        filem.add_separator()
        filem.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=filem)

        editm = tk.Menu(menubar, tearoff=0)
        editm.add_command(label="Переименовать…\tF2", command=self.rename_file)
        editm.add_command(label="Удалить\tDel", command=self.delete_file)
        menubar.add_cascade(label="Правка", menu=editm)

        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="О программе", command=lambda: messagebox.showinfo(APP_NAME, f"{APP_NAME}\nВерсия: v2.1"))
        menubar.add_cascade(label="Справка", menu=helpm)

        self.root.config(menu=menubar)

    def _build_toolbar(self):
        bar = ttk.Frame(self.root, padding=(8, 4))
        bar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(bar, text="Создать дело", command=self.upload_files, style="Toolbar.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Разархивация", command=self.download_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Переименовать", command=self.rename_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="Удалить", command=self.delete_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Обновить", command=self.refresh_from_disk, style="Toolbar.TButton").pack(side=tk.LEFT, padx=6)

    def _build_main(self):
        # Поиск
        find_frame = ttk.Frame(self.root, padding=(10, 6))
        find_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(find_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(find_frame, textvariable=self.search_var, width=40, style="Search.TEntry")
        self.search_entry.pack(side=tk.LEFT, padx=(6, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_filter())
        ttk.Button(find_frame, text="Сброс", command=self._reset_filter).pack(side=tk.LEFT)

        # Список файлов
        pan = ttk.Frame(self.root, padding=(10, 0))
        pan.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(pan, activestyle="none")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(pan, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)

        # Контекстное меню
        self.ctx = tk.Menu(self.root, tearoff=0)
        self.ctx.add_command(label="Переименовать", command=self.rename_file)
        self.ctx.add_command(label="Удалить", command=self.delete_file)
        self.listbox.bind("<Button-3>", self._show_context_menu)

        # Двойной клик — разархивация
        self.listbox.bind("<Double-Button-1>", lambda e: self.download_file())

        # Прогресс
        prog_frame = ttk.Frame(self.root, padding=(10, 8))
        prog_frame.pack(side=tk.TOP, fill=tk.X)
        self.progress = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", length=320)
        self.progress.pack(side=tk.LEFT)
        self.progress_label = ttk.Label(prog_frame, text="Готово")
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Стартовое наполнение
        self._refresh_listbox()

    def _build_statusbar(self):
        self.status = ttk.Label(self.root, style="Status.TLabel", anchor="w", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self._set_status("Добро пожаловать!")

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.upload_files())
        self.root.bind("<Control-s>", lambda e: self.download_file())
        self.root.bind("<Delete>", lambda e: self.delete_file())
        self.root.bind("<F2>", lambda e: self.rename_file())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Control-r>", lambda e: self.refresh_from_disk())

    # ---------- Splash + Login ----------

    def _show_splash_then_login(self):
        self.splash = tk.Toplevel(self.root)
        self.splash.title("Загрузка")
        self.splash.geometry("420x200+200+200")
        self.splash.configure(bg="white")
        self.splash.transient(self.root)
        self.splash.grab_set()

        ttk.Label(self.splash, text=APP_NAME, font=("Helvetica", 18)).pack(pady=24)
        pb = ttk.Progressbar(self.splash, mode="indeterminate", length=180)
        pb.pack(pady=8)
        pb.start(8)

        # через 1.8 сек — логин
        self.root.after(1800, self._show_login)

    def _show_login(self):
        if self.splash and self.splash.winfo_exists():
            self.splash.destroy()

        self.login = tk.Toplevel(self.root)
        self.login.title("Вход")
        self.login.geometry("320x160+240+240")
        self.login.transient(self.root)
        self.login.grab_set()

        ttk.Label(self.login, text="Введите пароль:").pack(pady=(16, 6))
        self.pass_var = tk.StringVar()
        ent = ttk.Entry(self.login, textvariable=self.pass_var, show="*")
        ent.pack(pady=6, padx=16, fill=tk.X)
        ent.focus_set()

        def ok():
            pwd = self.pass_var.get()
            if pwd == PASSWORD_PLAIN:
                self.login.destroy()
                self._set_status("Вход выполнен.")
            else:
                messagebox.showerror("Ошибка", "Неверный пароль")
                self.pass_var.set("")
                ent.focus_set()

        ttk.Button(self.login, text="Войти", command=ok).pack(pady=12)
        self.login.bind("<Return>", lambda e: ok())

    # ---------- Вспомогательные UI-методы ----------

    def _set_status(self, text: str):
        self.status.config(text=text)

    def _focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def _refresh_listbox(self, names: list[str] | None = None):
        if names is None:
            names = [f.name for f in self.files]
        self.listbox.delete(0, tk.END)
        for n in sorted(names, key=str.casefold):
            self.listbox.insert(tk.END, n)
        self._set_status(f"Файлов: {len(names)}")

    def _apply_filter(self):
        term = self.search_var.get().strip().lower()
        if not term:
            self._refresh_listbox()
            return
        filtered = [n for n in self.all_names_cache if term in n.lower()]
        self._refresh_listbox(filtered)

    def _reset_filter(self):
        self.search_var.set("")
        self._refresh_listbox()

    def _selected_name(self) -> str | None:
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])

    def _show_context_menu(self, event):
        try:
            idx = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(idx)
            self.ctx.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx.grab_release()

    # ---------- Синхронизация с диском ----------

    def _prune_missing_files(self):
        """Убираем из JSON записи, которых нет на диске."""
        existing = {p.name for p in DESTINATION_FOLDER.iterdir() if p.is_file()}
        new_list = [f for f in self.files if f.name in existing]
        if len(new_list) != len(self.files):
            self.files = new_list
            save_file_list(self.files)

    def refresh_from_disk(self):
        """Подтягиваем новые файлы из папки и убираем отсутствующие."""
        on_disk = {p.name for p in DESTINATION_FOLDER.iterdir() if p.is_file()}
        names_in_json = {f.name for f in self.files}

        # Добавим новые
        new_added = 0
        for name in sorted(on_disk - names_in_json):
            self.files.append(StoredFile(name=name, added_at=datetime.utcnow().isoformat()))
            new_added += 1

        # Удалим отсутствующие
        removed = 0
        if names_in_json - on_disk:
            self.files = [f for f in self.files if f.name in on_disk]
            removed = len(names_in_json - on_disk)

        if new_added or removed:
            save_file_list(self.files)

        self.all_names_cache = [f.name for f in self.files]
        self._refresh_listbox()
        self._set_status(f"Синхронизировано. Новых: {new_added}, удалённых: {removed}")

    # ---------- Операции с файлами ----------

    def upload_files(self):
        paths = filedialog.askopenfilenames(title="Выберите файлы для загрузки")
        if not paths:
            return
        added = 0
        for p in paths:
            src = Path(p)
            if not src.is_file():
                continue
            if not is_valid_filename(src.name):
                messagebox.showwarning("Имя файла", f"Пропущен файл с некорректным именем: {src.name}")
                continue
            target_name = unique_name(DESTINATION_FOLDER, src.name)
            try:
                shutil.copy2(src, DESTINATION_FOLDER / target_name)
                self.files.append(StoredFile(name=target_name, added_at=datetime.utcnow().isoformat()))
                added += 1
            except Exception as e:
                messagebox.showerror("Ошибка копирования", f"{src.name}: {e}")

        if added:
            save_file_list(self.files)
            self.all_names_cache = [f.name for f in self.files]
            self._refresh_listbox()
            self._set_status(f"Загружено: {added}")
        else:
            self._set_status("Нет загруженных файлов")

    def _simulate_progress(self, on_complete):
        """Индикатор 0..100% за 6–9 секунд, без блокировки UI (через after)."""
        total_ms = int(6000 + (3000 * os.urandom(1)[0] / 255))  # 6000..9000
        steps = 100
        interval = max(30, total_ms // steps)

        self.progress["value"] = 0
        self.progress["maximum"] = steps
        self.progress_label.config(text="Загрузка: 0%")

        def tick(i=0):
            if i > steps:
                self.progress_label.config(text="Готово")
                try:
                    on_complete()
                finally:
                    # небольшая пауза и сброс бара
                    self.root.after(400, self._reset_progress)
                return
            self.progress["value"] = i
            self.progress_label.config(text=f"Загрузка: {i}%")
            self.root.after(interval, lambda: tick(i + 1))

        tick(0)

    def _reset_progress(self):
        self.progress["value"] = 0
        self.progress_label.config(text="Готово")

    def download_file(self):
        name = self._selected_name()
        if not name:
            messagebox.showerror("Ошибка", "Выберите файл для выгрузки")
            return
        src = DESTINATION_FOLDER / name
        if not src.exists():
            messagebox.showerror("Ошибка", f"Файл '{name}' не найден")
            return

        save_dir = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not save_dir:
            return
        save_dir = Path(save_dir)

        def complete():
            try:
                shutil.copy2(src, save_dir / name)
                messagebox.showinfo("Успех", f"Файл '{name}' выгружен в:\n{save_dir}")
                self._set_status("Разархивация завершена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выгрузить: {e}")

        self._simulate_progress(complete)

    def delete_file(self):
        name = self._selected_name()
        if not name:
            messagebox.showerror("Ошибка", "Выберите файл для удаления")
            return
        if not messagebox.askyesno("Удаление файла", f"Удалить '{name}'?"):
            return
        try:
            (DESTINATION_FOLDER / name).unlink(missing_ok=True)
            self.files = [f for f in self.files if f.name != name]
            save_file_list(self.files)
            self.all_names_cache = [f.name for f in self.files]
            self._refresh_listbox()
            self._set_status(f"Удалён: {name}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def rename_file(self):
        name = self._selected_name()
        if not name:
            messagebox.showerror("Ошибка", "Выберите файл для переименования")
            return
        new_name = simpledialog.askstring("Переименовать", "Введите новое имя файла:", initialvalue=name)
        if new_name is None:  # нажали Cancel
            return
        new_name = new_name.strip()
        if new_name == "" or new_name == name:
            return
        if not is_valid_filename(new_name):
            messagebox.showerror("Ошибка", "Недопустимое имя файла")
            return

        old_p = DESTINATION_FOLDER / name
        new_p = DESTINATION_FOLDER / new_name
        if new_p.exists():
            if not messagebox.askyesno("Коллизия", f"Файл '{new_name}' уже существует.\nСоздать уникальное имя?"):
                return
            new_name = unique_name(DESTINATION_FOLDER, new_name)
            new_p = DESTINATION_FOLDER / new_name

        try:
            old_p.rename(new_p)
            for f in self.files:
                if f.name == name:
                    f.name = new_name
                    break
            save_file_list(self.files)
            self.all_names_cache = [f.name for f in self.files]
            self._refresh_listbox()
            # Выделим новый элемент
            idx = 0
            for i in range(self.listbox.size()):
                if self.listbox.get(i) == new_name:
                    idx = i
                    break
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(idx)
            self.listbox.see(idx)
            self._set_status(f"Переименовано в '{new_name}'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать: {e}")

# -------------------- Точка входа --------------------

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
