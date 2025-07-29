import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TaskPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Планер задач")
        self.root.geometry("1000x600")

        # Инициализация данных
        self.data_file = "tasks.json"
        self.users_file = "users.json"
        self.current_user = None
        self.tasks = []
        self.users = []

        # Загрузка данных
        self.load_data()

        # Создание интерфейса
        self.create_login_ui()

    def load_data(self):
        """Загрузка данных из файлов"""
        # Загрузка пользователей
        if os.path.exists(self.users_file):
            with open(self.users_file, "r", encoding="utf-8") as f:
                self.users = json.load(f)

        # Загрузка задач
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)

    def save_data(self):
        """Сохранение данных в файлы"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def create_login_ui(self):
        """Создание интерфейса входа"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Вход в систему", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Имя пользователя:").grid(row=1, column=0, sticky="e", pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="e", pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        ttk.Button(frame, text="Войти", command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Регистрация", command=self.create_register_ui).grid(row=4, column=0, columnspan=2,
                                                                                    pady=5)

    def create_register_ui(self):
        """Создание интерфейса регистрации"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Регистрация", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Имя пользователя:").grid(row=1, column=0, sticky="e", pady=5)
        self.reg_username_entry = ttk.Entry(frame)
        self.reg_username_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="e", pady=5)
        self.reg_password_entry = ttk.Entry(frame, show="*")
        self.reg_password_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Подтвердите пароль:").grid(row=3, column=0, sticky="e", pady=5)
        self.reg_confirm_entry = ttk.Entry(frame, show="*")
        self.reg_confirm_entry.grid(row=3, column=1, pady=5)

        ttk.Button(frame, text="Зарегистрироваться", command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Назад", command=self.create_login_ui).grid(row=5, column=0, columnspan=2, pady=5)

    def login(self):
        """Обработка входа пользователя"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        for user in self.users:
            if user["username"] == username and user["password"] == password:
                self.current_user = username
                self.create_main_ui()
                return

        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

    def register(self):
        """Обработка регистрации пользователя"""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Имя пользователя и пароль не могут быть пустыми")
            return

        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        for user in self.users:
            if user["username"] == username:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")
                return

        self.users.append({
            "username": username,
            "password": password
        })

        self.save_data()
        messagebox.showinfo("Успех", "Регистрация прошла успешно")
        self.create_login_ui()

    def create_main_ui(self):
        """Создание основного интерфейса приложения"""
        self.clear_window()

        # Панель управления
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill="x")

        ttk.Button(control_frame, text="Добавить задачу", command=self.open_add_task_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Показать график", command=self.show_stats).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Выйти", command=self.logout).pack(side="right", padx=5)

        # Фильтры
        filter_frame = ttk.Frame(self.root, padding="10")
        filter_frame.pack(fill="x")

        ttk.Label(filter_frame, text="Фильтры:").pack(side="left")

        self.status_filter = ttk.Combobox(filter_frame, values=["Все", "Новая", "В работе", "Завершена", "Отложена"])
        self.status_filter.set("Все")
        self.status_filter.pack(side="left", padx=5)

        self.priority_filter = ttk.Combobox(filter_frame, values=["Все", "Низкий", "Средний", "Высокий", "Критичный"])
        self.priority_filter.set("Все")
        self.priority_filter.pack(side="left", padx=5)

        self.complexity_filter = ttk.Combobox(filter_frame, values=["Все", "Простая", "Средняя", "Сложная"])
        self.complexity_filter.set("Все")
        self.complexity_filter.pack(side="left", padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).pack(side="left", padx=5)

        # Таблица задач
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_task_tree()

    def create_task_tree(self):
        """Создание таблицы задач"""
        # Удаляем старую таблицу, если она существует
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        # Создаем новую таблицу
        columns = ("id", "title", "status", "priority", "complexity", "created", "deadline", "completed_date",
                   "description")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")

        # Настраиваем заголовки
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("status", text="Статус")
        self.tree.heading("priority", text="Приоритет")
        self.tree.heading("complexity", text="Сложность")
        self.tree.heading("created", text="Дата создания")
        self.tree.heading("deadline", text="Срок выполнения")
        self.tree.heading("completed_date", text="Дата завершения")
        self.tree.heading("description", text="Описание")

        # Настраиваем ширину столбцов
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=150)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("priority", width=100, anchor="center")
        self.tree.column("complexity", width=100, anchor="center")
        self.tree.column("created", width=100, anchor="center")
        self.tree.column("deadline", width=100, anchor="center")
        self.tree.column("completed_date", width=100, anchor="center")
        self.tree.column("description", width=200)

        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(expand=True, fill="both")

        # Заполняем таблицу данными
        self.update_task_tree()

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_task)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_task)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_task())

    def update_task_tree(self, tasks=None):
        """Обновление таблицы задач"""
        if tasks is None:
            tasks = [task for task in self.tasks if task["user"] == self.current_user]

        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем новыми данными
        for task in tasks:
            self.tree.insert("", "end", values=(
                task["id"],
                task["title"],
                task["status"],
                task["priority"],
                task["complexity"],
                task["created"],
                task["deadline"],
                task.get("completed_date", "-"),  # Дата завершения (если есть)
                task["description"]
            ))

    def apply_filters(self):
        """Применение фильтров"""
        status = self.status_filter.get()
        priority = self.priority_filter.get()
        complexity = self.complexity_filter.get()

        filtered_tasks = []

        for task in self.tasks:
            if task["user"] != self.current_user:
                continue

            status_match = (status == "Все") or (task["status"] == status)
            priority_match = (priority == "Все") or (task["priority"] == priority)
            complexity_match = (complexity == "Все") or (task["complexity"] == complexity)

            if status_match and priority_match and complexity_match:
                filtered_tasks.append(task)

        self.update_task_tree(filtered_tasks)

    def open_add_task_dialog(self):
        """Открытие диалогового окна добавления задачи"""
        self.task_dialog = tk.Toplevel(self.root)
        self.task_dialog.title("Добавить задачу")
        self.task_dialog.geometry("500x550")
        self.task_dialog.grab_set()

        self.create_task_form(self.task_dialog, mode="add")

    def edit_selected_task(self):
        """Редактирование выбранной задачи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return

        task_id = self.tree.item(selected_item)["values"][0]
        task = next((t for t in self.tasks if t["id"] == task_id), None)

        if not task:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return

        self.task_dialog = tk.Toplevel(self.root)
        self.task_dialog.title("Редактировать задачу")
        self.task_dialog.geometry("500x550")
        self.task_dialog.grab_set()

        self.create_task_form(self.task_dialog, mode="edit", task=task)

    def create_task_form(self, parent, mode, task=None):
        """Создание формы для добавления/редактирования задачи"""
        frame = ttk.Frame(parent, padding="20")
        frame.pack(expand=True, fill="both")

        # Поля формы
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", pady=5)
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky="nw", pady=5)
        description_text = tk.Text(frame, height=5, width=30)
        description_text.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Статус:").grid(row=2, column=0, sticky="w", pady=5)
        status_var = tk.StringVar()
        status_combobox = ttk.Combobox(frame, textvariable=status_var,
                                       values=["Новая", "В работе", "Завершена", "Отложена"])
        status_combobox.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Приоритет:").grid(row=3, column=0, sticky="w", pady=5)
        priority_var = tk.StringVar()
        priority_combobox = ttk.Combobox(frame, textvariable=priority_var,
                                         values=["Низкий", "Средний", "Высокий", "Критичный"])
        priority_combobox.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Сложность:").grid(row=4, column=0, sticky="w", pady=5)
        complexity_var = tk.StringVar()
        complexity_combobox = ttk.Combobox(frame, textvariable=complexity_var,
                                           values=["Простая", "Средняя", "Сложная"])
        complexity_combobox.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Срок выполнения (ГГГГ-ММ-ДД):").grid(row=5, column=0, sticky="w", pady=5)
        deadline_entry = ttk.Entry(frame)
        deadline_entry.grid(row=5, column=1, sticky="ew", pady=5)

        # Если редактирование, заполняем поля
        if mode == "edit" and task:
            title_entry.insert(0, task["title"])
            description_text.insert("1.0", task["description"])
            status_var.set(task["status"])
            priority_var.set(task["priority"])
            complexity_var.set(task["complexity"])
            deadline_entry.insert(0, task["deadline"])

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        if mode == "add":
            ttk.Button(button_frame, text="Добавить",
                       command=lambda: self.save_task(
                           mode, None, title_entry.get(), description_text.get("1.0", "end-1c"),
                           status_var.get(), priority_var.get(), complexity_var.get(), deadline_entry.get()
                       )).pack(side="left", padx=5)
        else:
            ttk.Button(button_frame, text="Сохранить",
                       command=lambda: self.save_task(
                           mode, task["id"], title_entry.get(), description_text.get("1.0", "end-1c"),
                           status_var.get(), priority_var.get(), complexity_var.get(), deadline_entry.get()
                       )).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Отмена", command=parent.destroy).pack(side="left", padx=5)

    def save_task(self, mode, task_id, title, description, status, priority, complexity, deadline):
        """Сохранение задачи"""
        if not title:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым")
            return

        # Проверка формата даты (если указана)
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
                return

        if mode == "add":
            # Генерируем новый ID
            new_id = max([task["id"] for task in self.tasks], default=0) + 1

            task_data = {
                "id": new_id,
                "user": self.current_user,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "complexity": complexity,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "deadline": deadline,
                "completed_date": None
            }

            # Если задача сразу "Завершена", ставим дату
            if status == "Завершена":
                task_data["completed_date"] = datetime.now().strftime("%Y-%m-%d")

            self.tasks.append(task_data)
        else:
            # Обновляем существующую задачу
            for task in self.tasks:
                if task["id"] == task_id and task["user"] == self.current_user:
                    # Если статус изменился на "Завершена", обновляем дату
                    if task["status"] != "Завершена" and status == "Завершена":
                        task["completed_date"] = datetime.now().strftime("%Y-%m-%d")
                    # Если статус изменился с "Завершена", очищаем дату
                    elif task["status"] == "Завершена" and status != "Завершена":
                        task["completed_date"] = None

                    task.update({
                        "title": title,
                        "description": description,
                        "status": status,
                        "priority": priority,
                        "complexity": complexity,
                        "deadline": deadline
                    })
                    break

        self.save_data()
        self.update_task_tree()
        self.task_dialog.destroy()

    def delete_selected_task(self):
        """Удаление выбранной задачи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return

        task_id = self.tree.item(selected_item)["values"][0]

        if messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить эту задачу?"):
            self.tasks = [task for task in self.tasks if
                          not (task["id"] == task_id and task["user"] == self.current_user)]
            self.save_data()
            self.update_task_tree()

    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_stats(self):
        """Отображение статистики задач в виде графика"""
        if not self.tasks:
            messagebox.showinfo("Информация", "Нет данных для отображения")
            return

        # Фильтрация задач текущего пользователя
        user_tasks = [task for task in self.tasks if task["user"] == self.current_user]

        if not user_tasks:
            messagebox.showinfo("Информация", "Нет задач для отображения")
            return

        # Создаем окно для графика
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика задач")
        stats_window.geometry("800x600")

        # Создаем график
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

        # График по статусам
        status_counts = {}
        for task in user_tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        ax1.bar(status_counts.keys(), status_counts.values(), color='skyblue')
        ax1.set_title("Распределение по статусам")
        ax1.set_ylabel("Количество задач")

        # График по приоритетам
        priority_counts = {}
        for task in user_tasks:
            priority = task["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        ax2.bar(priority_counts.keys(), priority_counts.values(), color='lightgreen')
        ax2.set_title("Распределение по приоритетам")
        ax2.set_ylabel("Количество задач")

        # Встраиваем график в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

        # Кнопка закрытия
        ttk.Button(stats_window, text="Закрыть", command=stats_window.destroy).pack(pady=10)

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.create_login_ui()

    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskPlannerApp(root)
    root.mainloop()
