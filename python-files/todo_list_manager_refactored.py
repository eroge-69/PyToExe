import tkinter as tk
import json
import os
import sys
import uuid
import re
from PIL import Image, ImageTk
from datetime import datetime

# ==========================================
#  Утилита для преобразования приоритета в римскую цифру
# ==========================================
def to_roman(n):
    roman_map = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
    return roman_map.get(n, str(n))


# ==========================================
#  Хранилище задач (загрузка/сохранение JSON)
# ==========================================
class TodoStorage:
    def __init__(self, filepath):
        self.filepath = filepath
        self.todos = []
        self.locked = {}  # словарь {task_id: True/False} для блокировки удаления
        self.collapsed_groups = {}  # {(done, priority): bool}

    def load(self):
        self.collapsed_groups = {}
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                raw_groups = data.get('collapsed_groups', {})
                self.collapsed_groups = {
                    tuple(map(lambda x: int(x) if x.isdigit() else x == 'True', k.split(':'))): v
                    for k, v in raw_groups.items()
                }
                self.todos = data.get('todos', [])
                self.locked = {k: v for k, v in data.get('locked_delete_buttons', {}).items()}
                # Убедимся, что у каждой задачи есть нужные поля
                for todo in self.todos:
                    todo.setdefault('id', str(uuid.uuid4()))
                    todo.setdefault('created_at', datetime.now().isoformat())
                    todo.setdefault('completed_at', None)
                    todo.setdefault('priority', 3)
                    todo.setdefault('done', False)
                    todo.setdefault('subtasks', [])
                    todo.setdefault('due_date', None)
            except Exception:
                self.todos = []
                self.locked = {}
        else:
            # Если файла нет — инициализируем пустой список
            self.todos = []
            self.locked = {}

    def save(self):
        data = {
            'todos': self.todos,
            'locked_delete_buttons': self.locked,
            'collapsed_groups': {f"{k[0]}:{k[1]}": v for k, v in self.collapsed_groups.items()}
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


# ==========================================
#  Менеджер иконок (подгружает и кеширует)
# ==========================================
class ImageManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.img_cache = {}

    def load_icons(self, image_paths, sizes):
        for name, rel_path in image_paths.items():
            self.img_cache[name] = {"loaded": False}
            path = os.path.join(self.base_dir, rel_path)
            if os.path.exists(path):
                try:
                    original = Image.open(path)
                    for size_name, size in sizes.items():
                        self.img_cache[name][size_name] = ImageTk.PhotoImage(
                            original.resize(size, Image.Resampling.LANCZOS)
                        )
                    self.img_cache[name]["loaded"] = True
                except Exception:
                    pass
        return self.img_cache


# ==========================================
#  Основной класс: управление интерфейсом и логикой
# ==========================================
class TodoListManager:
    def __init__(self, master, storage, img_cache):
        self.master = master
        self.storage = storage
        self.img_cache = img_cache

        self.progress_labels = {}  # {task_id: (label_widget, created_datetime, due_datetime)}
        self.update_timer_interval = 1000  # обновление прогресс-бара: 1 секунда

        # Настройка окна
        self.master.title("TODO LIST")
        self.master.geometry("500x600")
        self.master.config(bg="#253B3A")

        # Строим интерфейс и загружаем исходные данные
        self._build_ui()
        self.storage.load()
        self._populate()

        # Запускаем таймер обновления прогресса
        self.master.after(self.update_timer_interval, self._update_due_progress)

    # ------------------------------------------
    #  Сборка пользовательского интерфейса
    # ------------------------------------------
    def _build_ui(self):
        # Верхняя строка: спиннер + поля даты/времени
        top_frame = tk.Frame(self.master, bg="#253B3A")
        top_frame.pack(anchor="nw", padx=10, pady=(5, 0), fill="x")

        # Спиннер
        self.spinner_symbols = ['|', '/', '—', '\\']
        self.spinner_index = 0
        self.spinner_label = tk.Label(
            top_frame, text=self.spinner_symbols[0],
            bg="#253B3A", fg="#7A9C8E", font=("Consolas", 14)
        )
        self.spinner_label.pack(side="left", padx=(0, 8))
        self._animate_spinner()

        # Поле ввода даты (DD:MM)
        self.date_label = tk.Label(
            top_frame, text="DD:MM",
            font=("Arial", 10), bg="#253B3A", fg="#7A9C8E"
        )
        self.date_label.pack(side="left")
        self.date_entry = tk.Entry(
            top_frame, width=6, font=("Arial", 12),
            bg="#202531", fg="#FAE89E", insertbackground="white", relief="flat"
        )
        self.date_entry.insert(0, "--:--")
        self.date_entry.pack(side="left", padx=(2, 6))

        # Поле ввода времени (HH:MM)
        self.time_label = tk.Label(
            top_frame, text="HH:MM",
            font=("Arial", 10), bg="#253B3A", fg="#7A9C8E"
        )
        self.time_label.pack(side="left")
        self.time_entry = tk.Entry(
            top_frame, width=6, font=("Arial", 12),
            bg="#202531", fg="#FAE89E", insertbackground="white", relief="flat"
        )
        self.time_entry.insert(0, "--:--")
        self.time_entry.pack(side="left", padx=(2, 6))

        # Строка ввода новой задачи: текст + кнопка "+"
        self.task_frame = tk.Frame(self.master, bg="#253B3A")
        self.task_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.todo_entry = tk.Entry(
            self.task_frame, font=("Arial", 12),
            bg="#202531", fg="#FAE89E", insertbackground="white", relief="flat"
        )
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.todo_entry.bind("<Return>", lambda e: self._add_todo())

        self.add_button = tk.Label(
            self.task_frame, bg="#253B3A", width=36, height=36
        )
        if self.img_cache['add_icon']['loaded']:
            self.add_button.config(image=self.img_cache['add_icon']['normal'])
        self.add_button.bind(
            "<ButtonRelease-1>",
            lambda e: self._add_todo() if self.add_button.winfo_containing(e.x_root, e.y_root) == self.add_button else None
        )
        self.add_button.bind("<Enter>", lambda e: self._on_hover(self.add_button, 'add_icon', 'hover'))
        self.add_button.bind("<Leave>", lambda e: self._on_hover(self.add_button, 'add_icon', 'normal'))
        self.add_button.pack(side="right")

        # Канвас + фрейм для списка задач с прокруткой колёсиком
        self.canvas = tk.Canvas(self.master, bg="#253B3A", highlightthickness=0)
        self.inner_frame = tk.Frame(self.canvas, bg="#253B3A")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=lambda *args: None)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ------------------------------------------
    #  Анимация спиннера (обновление каждые 100 мс)
    # ------------------------------------------
    def _animate_spinner(self):
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_symbols)
        self.spinner_label.config(text=self.spinner_symbols[self.spinner_index])
        self.master.after(100, self._animate_spinner)

    # ------------------------------------------
    #  Hover-эффект для иконок (увеличение)
    # ------------------------------------------
    def _on_hover(self, widget, icon_key, size_key):
        if self.img_cache[icon_key]['loaded']:
            widget.config(image=self.img_cache[icon_key][size_key])

    # ------------------------------------------
    #  Добавление новой задачи
    # ------------------------------------------
    def _add_todo(self):
        text = self.todo_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        due_date = None

        def clean_input(s):
            return re.sub(r'[^0-9]', ' ', s)

        if text:
            # Пытаемся собрать дату и время — допускаем любой разделитель
            date_parts = clean_input(date_str).split()
            time_parts = clean_input(time_str).split()
            if len(date_parts) >= 2 and len(time_parts) >= 2:
                try:
                    d, m = map(int, date_parts[:2])
                    h, mi = map(int, time_parts[:2])
                    now = datetime.now()
                    due = datetime(year=now.year, month=m, day=d, hour=h, minute=mi)
                    due_date = due.isoformat()
                except Exception:
                    due_date = None

            new_todo = {
                'id': str(uuid.uuid4()),
                'text': text,
                'done': False,
                'created_at': datetime.now().isoformat(),
                'completed_at': None,
                'priority': 3,
                'subtasks': [],
                'due_date': due_date
            }
            self.storage.todos.append(new_todo)
            self.storage.save()
            self._populate()

        # Сброс поля ввода
        self.todo_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, "--:--")
        self.time_entry.delete(0, 'end')
        self.time_entry.insert(0, "--:--")

    # ------------------------------------------
    #  Обновление прогресс-бара дедлайна (каждую секунду)
    # ------------------------------------------
    def _update_due_progress(self):
        now = datetime.now()
        for tid, (lbl, created, due) in self.progress_labels.items():
            try:
                if not lbl.winfo_exists():
                    continue
                total = (due - created).total_seconds()
                elapsed = (now - created).total_seconds()
                ratio = max(0, min(1, elapsed / total)) if total > 0 else 1
                bars = int(ratio * 21)
                # Прогресс: символы ▯▮, 21 сегмент, обрамлено ┃
                progress_text = '┃' + '▯' * bars + '▮' * (21 - bars) + '┃'
                lbl.config(
                    text=progress_text,
                    fg="#E99536" if now > due else "#FAE89E"
                )
            except:
                continue
        self.master.after(self.update_timer_interval, self._update_due_progress)

    # ------------------------------------------
    #  Заполнение списка задач
    # ------------------------------------------
    def _populate(self):
        # Очищаем всё внутри inner_frame
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Считываем состояния групп
        self.collapsed_groups = self.storage.collapsed_groups

        # Сортировка: сначала по done, затем по priority, затем по дате (created/ completed)
        sorted_todos = sorted(
            self.storage.todos,
            key=lambda x: (
                x['done'],
                x['priority'],
                datetime.fromisoformat(x['completed_at']) if x['done'] and x.get('completed_at') else datetime.fromisoformat(x['created_at'])
            )
        )

        # Группируем по (done, priority)
        grouped = {}
        for todo in sorted_todos:
            key = (todo['done'], todo['priority'])
            grouped.setdefault(key, []).append(todo)

        # Отображаем каждую группу
        for (done, priority), todos in grouped.items():
            # Сортировка внутри группы
            if done:
                todos.sort(
                    key=lambda x: datetime.fromisoformat(x.get("completed_at", x["created_at"])),
                    reverse=True
                )
            else:
                todos.sort(key=lambda x: datetime.fromisoformat(x["created_at"]))

            # Разделитель (полоса)
            separator = tk.Frame(self.inner_frame, bg="#1C2A2A", height=1)
            separator.pack(fill="x", pady=8)

            # Заголовок группы
            if done:
                label_text = "ЗАВЕРШЁННЫЕ ЗАДАЧИ"
            else:
                label_text = f"Активные задачи | приоритет {priority}"
            icon_key = 'collapse_up_icon' if not self.collapsed_groups.get((done, priority)) else 'collapse_down_icon'
            icon_img = self.img_cache[icon_key]['normal'] if self.img_cache[icon_key]['loaded'] else None

            header = tk.Label(
                self.inner_frame,
                text=f"  {label_text} ({len(todos)})",
                image=icon_img,
                compound="left",
                bg="#1C2A2A", fg="#7A9C8E",
                font=("Arial", 9, "bold")
            )
            header.bind("<Button-1>", lambda e, key=(done, priority): self._toggle_group(key))
            header.pack(fill="x", padx=10, pady=(0, 5), anchor="w")

            if not self.collapsed_groups.get((done, priority)):
                for todo in todos:
                    self._create_item(todo)

    # ------------------------------------------
    #  Переключение свернутости группы
    # ------------------------------------------
    def _toggle_group(self, key):
        self.storage.collapsed_groups[key] = not self.storage.collapsed_groups.get(key, False)
        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Создание одного элемента (одной задачи)
    # ------------------------------------------
    def _create_item(self, todo):
        def format_date(dt):
            months = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
            return dt.strftime("%d.") + months[dt.month - 1] + dt.strftime(".%y • %H:%M")

        # Контейнер для одной задачи
        f = tk.Frame(self.inner_frame, bg="#253B3A", relief="flat", bd=0)
        f.pack(fill="x", pady=2)

        readonly = todo['done']

        # --- Чекбокс (галочка) ---
        chk_img = 'checkbox_checked' if todo['done'] else 'checkbox_unchecked'
        chk = tk.Label(f, bg="#253B3A", width=36, height=36)
        if self.img_cache[chk_img]['loaded']:
            chk.config(image=self.img_cache[chk_img]['normal'])
        chk.bind("<Enter>", lambda e: self._on_hover(chk, chk_img, 'hover'))
        chk.bind("<Leave>", lambda e: self._on_hover(chk, chk_img, 'normal'))
        chk.bind(
            "<ButtonRelease-1>",
            lambda e: self._toggle_done(todo) if chk.winfo_containing(e.x_root, e.y_root) == chk else None
        )
        chk.pack(side="left", padx=5)

        # --- Текст задачи ---
        text = tk.Label(
            f, text=todo['text'],
            font=("Arial", 11),
            bg="#253B3A",
            fg="#FAE89E" if not readonly else "#98906D"
        )
        text.pack(side="left", padx=5, fill="x", expand=True)
        if not readonly:
            text.bind("<Double-Button-1>", lambda e: self._edit_task(todo, f, text))

        # --- Приоритет (римо́м) только для активных ---
        if not readonly and not todo['done']:
            pri = tk.Label(
                f, text=to_roman(todo['priority']),
                bg="#253B3A", fg="#7A9C8E", font=("Arial", 10)
            )
            pri.pack(side="left")
            pri.bind("<Button-1>", lambda e: self._change_priority(todo, +1))
            pri.bind("<Button-3>", lambda e: self._change_priority(todo, -1))

        # --- Кнопка удаления (или блокировки) ---
        del_icon_key = 'lock_icon' if self.storage.locked.get(todo['id']) else 'delete_icon'
        del_btn = tk.Label(f, bg="#253B3A", width=36, height=36)
        if self.img_cache[del_icon_key]['loaded']:
            del_btn.config(image=self.img_cache[del_icon_key]['normal'])
        if not self.storage.locked.get(todo['id']):
            del_btn.bind(
                "<ButtonRelease-1>",
                lambda e: self._delete(todo) if del_btn.winfo_containing(e.x_root, e.y_root) == del_btn else None
            )
        del_btn.bind(
            "<ButtonRelease-3>",
            lambda e: self._toggle_lock(todo, del_btn) if del_btn.winfo_containing(e.x_root, e.y_root) == del_btn else None
        )
        del_btn.bind("<Enter>", lambda e: self._on_hover(del_btn, del_icon_key, 'hover'))
        del_btn.bind("<Leave>", lambda e: self._on_hover(del_btn, del_icon_key, 'normal'))
        del_btn.pack(side="right", padx=5)

        # --- Контейнер подзадач ---
        subtask_container = tk.Frame(self.inner_frame, bg="#253B3A")
        subtask_container.pack(fill="x")
        self._render_subtasks(subtask_container, todo)

        # Кнопка для добавления подзадач
        add_sub_btn = tk.Button(
            f, text="+", font=("Arial", 10),
            bg="#2C4746", fg="#FAE89E",
            relief="flat",
            command=lambda t=todo, c=subtask_container: self._add_subtask(t, c)
        )
        add_sub_btn.pack(side="left", padx=5)

        # --- Блок даты + дедлайна + прогресс-бар ---
        # Сначала строка с датой создания и (если есть) датой выполнения
        try:
            created = datetime.fromisoformat(todo['created_at'])
            if todo.get('completed_at'):
                completed = datetime.fromisoformat(todo['completed_at'])
                date_text = format_date(created) + " — " + format_date(completed)
            else:
                date_text = format_date(created)
            date_label = tk.Label(
                self.inner_frame, text=date_text,
                font=("Arial", 8), bg="#253B3A", fg="#98906D"
            )
            date_label.pack(anchor="w", padx=50)
        except:
            pass

        # Затем — если есть due_date, показываем дедлайн + прогресс-бар в ОДНОЙ строке
        if todo.get('due_date'):
            try:
                due = datetime.fromisoformat(todo['due_date'])
                now = datetime.now()
                total = (due - created).total_seconds()
                elapsed = (now - created).total_seconds()
                ratio = max(0, min(1, elapsed / total)) if total > 0 else 1
                bars = int(ratio * 21)
                progress_text = '┃' + '▯' * bars + '▮' * (21 - bars) + '┃'

                due_frame = tk.Frame(self.inner_frame, bg="#253B3A")
                due_frame.pack(fill="x", padx=50)

                due_label = tk.Label(
                    due_frame, text=f"Дедлайн: {due.strftime('%d.%m • %H:%M')}",
                    font=("Arial", 8), bg="#253B3A", fg="#FAE89E"
                )
                due_label.pack(side="left")

                bar_label = tk.Label(
                    due_frame, text=progress_text,
                    font=("Courier", 11), bg="#253B3A",
                    fg="#E99536" if now > due else "#FAE89E"
                )
                bar_label.pack(side="right")

                # Сохраняем в словаре, чтобы обновлять каждую секунду, но только для активных (не выполненных) задач
                if not todo['done']:
                    self.progress_labels[todo['id']] = (bar_label, created, due)
            except:
                pass

    # ------------------------------------------
    #  Логика «галочки» (выполнено/не выполнено)
    # ------------------------------------------
    def _toggle_done(self, todo):
        if todo['done']:
            # Если уже выполнена — снимаем
            todo['done'] = False
            todo['completed_at'] = None
        else:
            # Если есть невыполненные подзадачи — отменяем
            if any(not sub.get('done') for sub in todo.get('subtasks', [])):
                return
            # Иначе ставим выполнено
            todo['done'] = True
            todo['completed_at'] = datetime.now().isoformat()

        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Удаление задачи
    # ------------------------------------------
    def _delete(self, todo):
        self.storage.todos = [t for t in self.storage.todos if t['id'] != todo['id']]
        self.storage.locked.pop(todo['id'], None)
        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Блокировка/разблокировка удаления
    # ------------------------------------------
    def _toggle_lock(self, todo, button):
        tid = todo['id']
        locked = self.storage.locked.get(tid, False)
        new_locked = not locked
        self.storage.locked[tid] = new_locked

        icon = 'lock_icon' if new_locked else 'delete_icon'
        if self.img_cache[icon]['loaded']:
            button.config(image=self.img_cache[icon]['normal'])

        button.unbind("<ButtonRelease-1>")
        if not new_locked:
            button.bind(
                "<ButtonRelease-1>",
                lambda e: self._delete(todo) if button.winfo_containing(e.x_root, e.y_root) == button else None
            )

        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Изменение приоритета
    # ------------------------------------------
    def _change_priority(self, todo, delta):
        todo['priority'] = max(1, min(5, todo['priority'] + delta))
        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Редактирование задачи (текст + дата/время)
    # ------------------------------------------
    def _edit_task(self, todo, frame, label_widget):
        label_widget.pack_forget()
        entry = tk.Entry(frame, font=("Arial", 11), bg="#202531", fg="#FAE89E", insertbackground="white")
        entry.insert(0, todo['text'])
        entry.pack(fill="x", padx=5, pady=(0, 2))
        entry.focus_set()

        # Контейнер для даты и времени под строкой текста
        due_container = tk.Frame(frame, bg="#253B3A")
        due_container.pack(fill="x", padx=5, pady=(0, 2))

        date_label = tk.Label(due_container, text="DD:MM", font=("Arial", 10), bg="#253B3A", fg="#7A9C8E")
        date_label.pack(side="left")
        date_entry = tk.Entry(due_container, width=6, font=("Arial", 12), bg="#202531", fg="#FAE89E", insertbackground="white", relief="flat")
        date_entry.pack(side="left", padx=(2, 6))

        time_label = tk.Label(due_container, text="HH:MM", font=("Arial", 10), bg="#253B3A", fg="#7A9C8E")
        time_label.pack(side="left")
        time_entry = tk.Entry(due_container, width=6, font=("Arial", 12), bg="#202531", fg="#FAE89E", insertbackground="white", relief="flat")
        time_entry.pack(side="left", padx=(2, 6))

        # Если ранее дедлайн был задан, заполняем поля
        if todo.get("due_date"):
            try:
                dt = datetime.fromisoformat(todo['due_date'])
                date_entry.insert(0, dt.strftime("%d.%m"))
                time_entry.insert(0, dt.strftime("%H:%M"))
            except:
                date_entry.insert(0, "--:--")
                time_entry.insert(0, "--:--")
        else:
            date_entry.insert(0, "--:--")
            time_entry.insert(0, "--:--")

        # Функция сохранения изменений
        def save():
            new_text = entry.get().strip()
            if new_text:
                todo['text'] = new_text
            # Обработка даты/времени
            try:
                d_parts = re.sub(r'[^0-9]', ' ', date_entry.get()).split()
                t_parts = re.sub(r'[^0-9]', ' ', time_entry.get()).split()
                if len(d_parts) >= 2 and len(t_parts) >= 2:
                    d, m = map(int, d_parts[:2])
                    h, mi = map(int, t_parts[:2])
                    now = datetime.now()
                    todo['due_date'] = datetime(now.year, m, d, h, mi).isoformat()
                else:
                    todo['due_date'] = None
            except:
                todo['due_date'] = None

            self.storage.save()
            self._populate()

        # Функция отмены (просто перерисовывает список)
        def cancel():
            self._populate()

        entry.bind("<Return>", lambda e: save())
        entry.bind("<Escape>", lambda e: cancel())
        date_entry.bind("<Return>", lambda e: save())
        date_entry.bind("<Escape>", lambda e: cancel())
        time_entry.bind("<Return>", lambda e: save())
        time_entry.bind("<Escape>", lambda e: cancel())

    # ------------------------------------------
    #  Рендер подзадач внутри задачи
    # ------------------------------------------
    def _render_subtasks(self, parent_frame, todo):
        if 'subtasks' in todo and todo['subtasks']:
            for sub in todo['subtasks']:
                sub_f = tk.Frame(parent_frame, bg="#253B3A", bd=0)
                sub_f.pack(fill="x", padx=40, pady=(2, 2))

                # Чекбокс подзадачи
                sub_chk_icon = 'checkbox_checked' if sub.get('done') else 'checkbox_unchecked'
                sub_chk = tk.Label(sub_f, bg="#253B3A")
                if self.img_cache[sub_chk_icon]['loaded']:
                    sub_chk.config(image=self.img_cache[sub_chk_icon]['normal'])
                sub_chk.pack(side="left", padx=5)
                sub_chk.bind("<Button-1>", lambda e, s=sub: self._toggle_subtask(todo, s))

                # Текст подзадачи (слева-выравнено)
                sub_text = tk.Label(
                    sub_f, text=sub["text"],
                    font=("Arial", 10),
                    bg="#253B3A",
                    fg="#FAE89E" if not sub.get("done") else "#98906D",
                    anchor="w"
                )
                sub_text.pack(side="left", padx=5, fill="x", expand=True)
                sub_text.bind("<Double-Button-1>", lambda e, s=sub: self._edit_subtask(todo, s, sub_text))

                # Кнопка удаления подзадачи (символ "—")
                remove_btn = tk.Button(
                    sub_f, text="—",
                    font=("Arial", 10),
                    bg="#2C4746", fg="#FAE89E",
                    relief="flat",
                    command=lambda s=sub: self._delete_subtask(todo, s)
                )
                remove_btn.pack(side="right", padx=5)

    # ------------------------------------------
    #  Логика подзадачи: переключение статуса
    # ------------------------------------------
    def _toggle_subtask(self, todo, sub):
        sub['done'] = not sub.get('done', False)
        self.storage.save()
        self._populate()

    # ------------------------------------------
    #  Редактирование текста подзадачи
    # ------------------------------------------
    def _edit_subtask(self, todo, sub, label_widget):
        label_widget.pack_forget()
        frame = label_widget.master
        entry = tk.Entry(frame, font=("Arial", 10), bg="#202531", fg="#FAE89E", insertbackground="white")
        entry.insert(0, sub['text'])
        entry.pack(side="left", fill="x", expand=True)
        entry.focus_set()

        def save_sub():
            new_text = entry.get().strip()
            if new_text:
                sub['text'] = new_text
            self.storage.save()
            self._populate()

        entry.bind("<Return>", lambda e: save_sub())
        entry.bind("<FocusOut>", lambda e: save_sub())

    # ------------------------------------------
    #  Добавление новой подзадачи
    # ------------------------------------------
    def _add_subtask(self, todo, container):
        # Если уже есть поле ввода — ничего не делаем
        for child in container.winfo_children():
            if isinstance(child, tk.Entry):
                return

        entry = tk.Entry(
            container, font=("Arial", 10),
            bg="#202531", fg="#FAE89E", insertbackground="white"
        )
        entry.pack(fill="x", padx=40, pady=(2, 2))
        entry.focus_set()

        def save():
            text = entry.get().strip()
            if text:
                todo.setdefault('subtasks', []).append({'text': text, 'done': False})
                self.storage.save()
                self._populate()

        entry.bind("<Return>", lambda e: save())
        entry.bind("<Escape>", lambda e: self._populate())

    # ------------------------------------------
    #  Удаление подзадачи
    # ------------------------------------------
    def _delete_subtask(self, todo, sub):
        if 'subtasks' in todo:
            todo['subtasks'].remove(sub)
            self.storage.save()
            self._populate()


# ==========================================
#  Запуск приложения
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()

    # Путь к каталогам (в режиме PyInstaller _MEIPASS)
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))

    image_paths = {
        'add_icon':             'images/add_icon.png',
        'delete_icon':          'images/delete_icon.png',
        'edit_icon':            'images/edit_icon.png',
        'lock_icon':            'images/lock_icon.png',
        'checkbox_checked':     'images/checkbox_checked.png',
        'checkbox_unchecked':   'images/checkbox_unchecked.png',
        'collapse_up_icon':     'images/collapse_up.png',
        'collapse_down_icon':   'images/collapse_down.png',
    }

    icon_sizes = {
        'normal': (32, 32),
        'hover':  (36, 36)
    }

    image_loader = ImageManager(base_path)
    images = image_loader.load_icons(image_paths, icon_sizes)

    storage = TodoStorage("todo_list.json")
    storage.load()

    app = TodoListManager(root, storage, images)
    root.mainloop()
