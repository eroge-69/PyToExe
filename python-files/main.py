"""
School Music Scheduler — обновлённый вариант с удобным редактором расписания
- GUI: tkinter + ttk
- Аудио: pygame.mixer (pip install pygame)

Нововведения:
- Удобный редактор расписания: табличный вид (Treeview) с колонками Время, Действие, Вкл/Выкл.
- Кнопки: Добавить, Редактировать, Удалить, Вверх, Вниз, Включить/Выключить, Сохранить, Загрузить, Сбросить в шифр.
- Диалог для добавления/редактирования (спинбоксы для часа/минут, выбор действия, переключатель включено).
- Автосохранение расписания в файл в домашней папке при закрытии (файл: ~/.music_scheduler_schedule.json).
- Двойной клик на строке — редактирование.

Инструкции по использованию UI:
- Выберите папку с музыкой.
- При необходимости измените порядок/время расписания через таблицу и кнопки рядом.
- Можно сохранять и загружать расписания в файл.

Запуск: как и раньше — python music_scheduler.py (перед этим: pip install pygame)
"""

import os
import json
import random
import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import pygame

SUPPORTED_EXTS = (".mp3", ".wav")
AUTOSAVE_FILENAME = os.path.join(os.path.expanduser("~"), ".music_scheduler_schedule.json")


class EditScheduleDialog(simpledialog.Dialog):
    """Простой диалог для добавления/редактирования элемента расписания"""

    def __init__(self, parent, title=None, time_val="09:15", action_val="resume", enabled=True):
        self.time_val = time_val
        self.action_val = action_val
        self.enabled = enabled
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Час:").grid(row=0, column=0, padx=6, pady=6)
        tk.Label(master, text="Хвилина:").grid(row=0, column=2, padx=6, pady=6)

        hh, mm = ("09", "15")
        if self.time_val and ":" in self.time_val:
            try:
                p = self.time_val.split(":")
                hh = f"{int(p[0]):02d}"
                mm = f"{int(p[1]):02d}"
            except Exception:
                hh, mm = ("09", "15")

        self.hour_sb = tk.Spinbox(master, from_=0, to=23, width=3, format="%02.0f")
        self.hour_sb.delete(0, tk.END)
        self.hour_sb.insert(0, hh)
        self.hour_sb.grid(row=0, column=1)

        self.min_sb = tk.Spinbox(master, from_=0, to=59, width=3, format="%02.0f")
        self.min_sb.delete(0, tk.END)
        self.min_sb.insert(0, mm)
        self.min_sb.grid(row=0, column=3)

        tk.Label(master, text="Действие:").grid(row=1, column=0, padx=6, pady=6)
        self.action_cb = ttk.Combobox(master, values=("resume", "pause"), state="readonly", width=10)
        self.action_cb.set(self.action_val)
        self.action_cb.grid(row=1, column=1, columnspan=3, sticky="w", padx=6)

        self.enabled_var = tk.BooleanVar(value=self.enabled)
        self.enabled_cb = tk.Checkbutton(master, text="Включено", variable=self.enabled_var)
        self.enabled_cb.grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))

        return self.hour_sb

    def apply(self):
        try:
            h = int(self.hour_sb.get())
            m = int(self.min_sb.get())
            h = max(0, min(23, h))
            m = max(0, min(59, m))
            self.time_val = f"{h:02d}:{m:02d}"
        except Exception:
            self.time_val = "09:15"
        self.action_val = self.action_cb.get() or "resume"
        self.enabled = bool(self.enabled_var.get())


class MusicSchedulerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("School Music Scheduler — редактор расписания")
        self.root.geometry("720x520")

        # Состояние плеера
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.mode_var = tk.StringVar(value="sequential")

        # Расписание
        self.schedule = []  # list of dicts: {time, action, enabled, last_date}
        self._set_default_schedule()
        # Попытка загрузить автосохранённое расписание
        self._load_autosave()

        # Инициализация pygame
        try:
            pygame.mixer.init()
        except Exception:
            # продолжаем, но звук может работать некорректно на некоторых системах без настроек
            print("Warning: pygame.mixer.init() failed — звук может не работать")

        # --- UI ---
        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=10, pady=8)

        self.folder_var = tk.StringVar(value="Папка не выбрана")
        tk.Label(top, textvariable=self.folder_var, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(top, text="Выбрать папку", command=self.select_folder).pack(side=tk.RIGHT)

        # Режим воспроизведения
        mode_frame = tk.Frame(root)
        mode_frame.pack(fill=tk.X, padx=10)
        tk.Radiobutton(mode_frame, text="По очереди", variable=self.mode_var, value="sequential").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Случайно", variable=self.mode_var, value="shuffle").pack(side=tk.LEFT, padx=8)

        # Кнопки плеера
        ctrl = tk.Frame(root)
        ctrl.pack(fill=tk.X, padx=10, pady=(6, 0))
        tk.Button(ctrl, text="Старт/Пауза", command=self.start_pause).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Стоп", command=self.stop).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Следующий", command=self.next_track).pack(side=tk.LEFT, padx=4)

        # Статус
        status_frame = tk.LabelFrame(root, text="Сейчас играет")
        status_frame.pack(fill=tk.X, padx=10, pady=8)
        self.track_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(value="Стоп")
        tk.Label(status_frame, textvariable=self.track_var, anchor="w").pack(fill=tk.X, padx=8, pady=(6, 2))
        tk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(fill=tk.X, padx=8, pady=(0, 6))

        # Расписание — Treeview
        sched_frame = tk.LabelFrame(root, text="Редактор расписания (двойной клик — редактировать)")
        sched_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        columns = ("time", "action", "enabled")
        self.tree = ttk.Treeview(sched_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("time", text="Время")
        self.tree.heading("action", text="Действие")
        self.tree.heading("enabled", text="Вкл")
        self.tree.column("time", width=100, anchor="center")
        self.tree.column("action", width=120, anchor="center")
        self.tree.column("enabled", width=50, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(4, 0), pady=6)

        # Скролл
        scroll = ttk.Scrollbar(sched_frame, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side=tk.LEFT, fill=tk.Y)

        # Кнопки для редактирования
        btn_frame = tk.Frame(sched_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=6)
        tk.Button(btn_frame, text="Добавить", width=14, command=self.add_schedule_dialog).pack(pady=3)
        tk.Button(btn_frame, text="Редактировать", width=14, command=self.edit_selected).pack(pady=3)
        tk.Button(btn_frame, text="Удалить", width=14, command=self.remove_selected).pack(pady=3)
        tk.Button(btn_frame, text="Вверх", width=14, command=lambda: self.move_selected(-1)).pack(pady=3)
        tk.Button(btn_frame, text="Вниз", width=14, command=lambda: self.move_selected(1)).pack(pady=3)
        tk.Button(btn_frame, text="Вкл/Выкл", width=14, command=self.toggle_selected_enabled).pack(pady=3)
        tk.Label(btn_frame, text="").pack(pady=4)
        tk.Button(btn_frame, text="Сохранить файл..", width=14, command=self.save_schedule_file).pack(pady=3)
        tk.Button(btn_frame, text="Загрузить файл..", width=14, command=self.load_schedule_file).pack(pady=3)
        tk.Button(btn_frame, text="Сбросить по умолчанию", width=14, command=self.reset_default).pack(pady=8)

        # Заполним дерево
        self._refresh_tree()

        # Циклы
        self.root.after(500, self._tick)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Привязка двойного клика
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

    # ---------------- UI: информация о папке и выбор ----------------
    def select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(SUPPORTED_EXTS)]
        if not files:
            messagebox.showwarning("Пусто", "В папке не найдено mp3/wav файлов.")
            return
        files.sort(key=str.lower)
        self.playlist = files
        self.current_index = -1
        self.folder_var.set(path)
        self.track_var.set("—")
        self.status_var.set("Готово к воспроизведению")

    # ---------------- Плеер ----------------
    def start_pause(self):
        if not self.playlist:
            messagebox.showinfo("Нет музыки", "Сначала выберите папку с музыкой.")
            return
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self._set_status("Пауза")
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True
            self._set_status("Воспроизведение")
            return
        if self.current_index == -1:
            self.current_index = 0 if self.mode_var.get() == "sequential" else random.randrange(len(self.playlist))
        self._play_current()

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.is_playing = False
        self.is_paused = False
        self._set_status("Стоп")

    def next_track(self):
        if not self.playlist:
            return
        if self.mode_var.get() == "sequential":
            self.current_index = (self.current_index + 1) % len(self.playlist)
        else:
            if len(self.playlist) > 1:
                nxt = self.current_index
                while nxt == self.current_index:
                    nxt = random.randrange(len(self.playlist))
                self.current_index = nxt
            else:
                self.current_index = 0
        self._play_current()

    def _play_current(self):
        try:
            track = self.playlist[self.current_index]
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.track_var.set(os.path.basename(track))
            self._set_status("Воспроизведение")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл:\n{e}")
            self.next_track()

    def _set_status(self, text: str):
        self.status_var.set(text)

    # ---------------- Расписание: добавление/редактирование ----------------
    def add_schedule_dialog(self):
        dlg = EditScheduleDialog(self.root, title="Добавить событие", time_val="09:15", action_val="resume", enabled=True)
        if dlg.time_val:
            item = {"time": dlg.time_val, "action": dlg.action_val, "enabled": dlg.enabled, "last_date": None}
            self.schedule.append(item)
            self._refresh_tree()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        it = self.schedule[idx]
        dlg = EditScheduleDialog(self.root, title="Редактировать событие", time_val=it["time"], action_val=it["action"], enabled=it.get("enabled", True))
        if dlg.time_val:
            it["time"] = dlg.time_val
            it["action"] = dlg.action_val
            it["enabled"] = dlg.enabled
            it["last_date"] = None
            self._refresh_tree()

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.schedule[idx]
        self._refresh_tree()

    def move_selected(self, direction: int):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.schedule):
            return
        self.schedule[idx], self.schedule[new_idx] = self.schedule[new_idx], self.schedule[idx]
        self._refresh_tree()
        # reselect
        self.tree.selection_set(str(new_idx))
        self.tree.focus(str(new_idx))

    def toggle_selected_enabled(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.schedule[idx]["enabled"] = not self.schedule[idx].get("enabled", True)
        self._refresh_tree()

    def _refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, it in enumerate(self.schedule):
            en = "Да" if it.get("enabled", True) else "Нет"
            act = "Пауза" if it["action"] == "pause" else "Воспроизвести"
            self.tree.insert("", "end", iid=str(i), values=(it["time"], act, en))

    # ----------------- Файловые операции для расписания -----------------
    def save_schedule_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Сохранить расписание как")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._schedule_serializable(), f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", f"Расписание сохранено: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_schedule_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Загрузить расписание")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Валидация
            new = []
            for it in data:
                if not isinstance(it, dict):
                    continue
                time = it.get("time")
                action = it.get("action")
                enabled = bool(it.get("enabled", True))
                if self._is_valid_time(time) and action in ("pause", "resume"):
                    new.append({"time": time, "action": action, "enabled": enabled, "last_date": None})
            if new:
                self.schedule = new
                self._refresh_tree()
                messagebox.showinfo("Загружено", "Расписание успешно загружено.")
            else:
                messagebox.showwarning("Пусто", "В файле не найдено корректных пунктов расписания.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def _schedule_serializable(self):
        out = []
        for it in self.schedule:
            out.append({"time": it["time"], "action": it["action"], "enabled": bool(it.get("enabled", True))})
        return out

    def reset_default(self):
        if not messagebox.askyesno("Сброс", "Сбросить расписание до школьного по умолчанию?"):
            return
        self._set_default_schedule()
        self._refresh_tree()

    def _set_default_schedule(self):
        # По умолчанию: включать на переменах, выключать во время уроков; после 16:05 — стоп, следующй день 09:15 включается
        # Включения (resume): 9:15, 9:25? — но по запросу ранее: на переменах включать. Подставим:
        # По описанию ранее: lessons and breaks timings were provided; составим расписание включений и выключений.
        self.schedule = [
            # 1-я перемена: 09:15 - 09:25 (включить в 09:15, выключить в 09:25)
            {"time": "09:15", "action": "resume", "enabled": True, "last_date": None},
            {"time": "09:25", "action": "pause", "enabled": True, "last_date": None},
            # 2-ая перемена: 10:10 - 10:20
            {"time": "10:10", "action": "resume", "enabled": True, "last_date": None},
            {"time": "10:20", "action": "pause", "enabled": True, "last_date": None},
            # 3-я перемена: 11:05 - 11:25 (20 min)
            {"time": "11:05", "action": "resume", "enabled": True, "last_date": None},
            {"time": "11:25", "action": "pause", "enabled": True, "last_date": None},
            # 4-я перемена: 12:10 - 12:30 (20 min)
            {"time": "12:10", "action": "resume", "enabled": True, "last_date": None},
            {"time": "12:30", "action": "pause", "enabled": True, "last_date": None},
            # 5-я перемена: 13:15 - 13:30 (15 min)
            {"time": "13:15", "action": "resume", "enabled": True, "last_date": None},
            {"time": "13:30", "action": "pause", "enabled": True, "last_date": None},
            # Полдень/факультативы: 14:15 - 14:25 (включить 14:15), выключить 14:25
            {"time": "14:15", "action": "resume", "enabled": True, "last_date": None},
            {"time": "14:25", "action": "pause", "enabled": True, "last_date": None},
            # Второй факультатив: 15:10 - 15:20
            {"time": "15:10", "action": "resume", "enabled": True, "last_date": None},
            {"time": "15:20", "action": "pause", "enabled": True, "last_date": None},
            # Окончательно: 16:05 — стоп (повторять каждый день)
            {"time": "16:05", "action": "pause", "enabled": True, "last_date": None},
            # Утренний старт следующего дня 09:15 — уже включаем (уже есть 09:15 в списке)
        ]

    # ----------------- Автосохранение -----------------
    def _load_autosave(self):
        try:
            if os.path.exists(AUTOSAVE_FILENAME):
                with open(AUTOSAVE_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                new = []
                for it in data:
                    time = it.get("time")
                    action = it.get("action")
                    enabled = bool(it.get("enabled", True))
                    if self._is_valid_time(time) and action in ("pause", "resume"):
                        new.append({"time": time, "action": action, "enabled": enabled, "last_date": None})
                if new:
                    self.schedule = new
        except Exception:
            pass

    def _save_autosave(self):
        try:
            with open(AUTOSAVE_FILENAME, "w", encoding="utf-8") as f:
                json.dump(self._schedule_serializable(), f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ----------------- Запуск расписания -----------------
    def _is_valid_time(self, s: str) -> bool:
        try:
            dt.datetime.strptime(s, "%H:%M")
            return True
        except Exception:
            return False

    def _run_action(self, action: str):
        if action == "pause":
            if self.is_playing and not self.is_paused:
                try:
                    pygame.mixer.music.pause()
                except Exception:
                    pass
                self.is_paused = True
                self._set_status("Пауза по расписанию")
        elif action == "resume":
            if self.is_paused:
                try:
                    pygame.mixer.music.unpause()
                except Exception:
                    pass
                self.is_paused = False
                self.is_playing = True
                self._set_status("Возобновлено по расписанию")
            elif not self.is_playing and self.playlist:
                if self.current_index == -1:
                    self.current_index = 0 if self.mode_var.get() == "sequential" else random.randrange(len(self.playlist))
                self._play_current()
                self._set_status("Старт по расписанию")

    def _tick(self):
        now = dt.datetime.now()
        hhmm = now.strftime("%H:%M")
        for it in self.schedule:
            if not it.get("enabled", True):
                continue
            if it.get("time") == hhmm and it.get("last_date") != now.date():
                self._run_action(it.get("action"))
                it["last_date"] = now.date()

        if self.is_playing and not self.is_paused:
            try:
                busy = pygame.mixer.music.get_busy()
            except Exception:
                busy = False
            if not busy:
                self.next_track()

        self.root.after(500, self._tick)

    def on_close(self):
        # Сохраним автосохранение
        self._save_autosave()
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MusicSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
