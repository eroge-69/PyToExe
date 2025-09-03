import customtkinter as ctk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class TaskManagerApp:
    def __init__(self):
        # Настройка внешнего вида
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Менеджер задач - Python Portfolio App")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        self.tasks = []
        self.current_filter = "all"
        self.data_file = "tasks.json"
        
        self.load_tasks()
        self.setup_ui()
        
    def setup_ui(self):
        # Главный контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="📋 Менеджер задач", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Панель управления
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.pack(fill="x", pady=(0, 20))
        
        # Поле ввода новой задачи
        self.task_entry = ctk.CTkEntry(
            control_frame, 
            placeholder_text="Введите новую задачу...",
            font=ctk.CTkFont(size=14)
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Кнопка добавления
        add_btn = ctk.CTkButton(
            control_frame,
            text="Добавить",
            command=self.add_task,
            width=100
        )
        add_btn.pack(side="right")
        
        # Панель фильтров
        filter_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(filter_frame, text="Фильтр:").pack(side="left")
        
        filter_options = ["Все", "Активные", "Завершенные"]
        self.filter_var = ctk.StringVar(value="Все")
        
        for option in filter_options:
            radio = ctk.CTkRadioButton(
                filter_frame,
                text=option,
                variable=self.filter_var,
                value=option,
                command=self.apply_filter
            )
            radio.pack(side="left", padx=(20, 0))
        
        # Таблица задач
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Создаем Treeview с стилями
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       borderwidth=0)
        style.configure("Treeview.Heading", 
                       background="#3b3b3b",
                       foreground="white",
                       borderwidth=0)
        style.map("Treeview", background=[("selected", "#3b8ed0")])
        
        # Изменяем колонки - убираем колонку статуса как отдельную колонку
        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "task", "created", "completed", "status"),
            show="headings",
            height=15
        )
        
        # Настройка колонок - скрываем колонку id
        self.tree.heading("id", text="ID")
        self.tree.heading("task", text="Задача")
        self.tree.heading("created", text="Создана")
        self.tree.heading("completed", text="Завершена")
        self.tree.heading("status", text="Статус")
        
        self.tree.column("id", width=0, stretch=False)  # Скрываем колонку ID
        self.tree.column("task", width=400, anchor="w")
        self.tree.column("created", width=120, anchor="center")
        self.tree.column("completed", width=120, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка событий
        self.tree.bind("<Double-1>", self.on_task_double_click)
        self.tree.bind("<Delete>", self.delete_selected_task)
        
        # Панель статистики
        stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(20, 0))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Всего задач: 0 | Активных: 0 | Завершенных: 0",
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack()
        
        self.update_task_list()
        self.update_stats()
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Внимание", "Введите текст задачи!")
            return
        
        # Генерируем уникальный ID
        if self.tasks:
            new_id = max(task["id"] for task in self.tasks) + 1
        else:
            new_id = 1
        
        task = {
            "id": new_id,
            "text": task_text,
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_date": None
        }
        
        self.tasks.append(task)
        self.task_entry.delete(0, ctk.END)
        self.save_tasks()
        self.update_task_list()
        self.update_stats()
        
        messagebox.showinfo("Успех", "Задача добавлена!")
    
    def toggle_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M") if task["completed"] else None
                break
        
        self.save_tasks()
        self.update_task_list()
        self.update_stats()
    
    def delete_selected_task(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        
        # Получаем ID из скрытой колонки
        task_id = int(self.tree.item(selected[0])["values"][0])
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?"):
            self.tasks = [task for task in self.tasks if task["id"] != task_id]
            self.save_tasks()
            self.update_task_list()
            self.update_stats()
    
    def on_task_double_click(self, event):
        selected = self.tree.selection()
        if selected:
            # Получаем ID из скрытой колонки
            task_id = int(self.tree.item(selected[0])["values"][0])
            self.toggle_task(task_id)
    
    def apply_filter(self):
        filter_map = {
            "Все": "all",
            "Активные": "active",
            "Завершенные": "completed"
        }
        self.current_filter = filter_map[self.filter_var.get()]
        self.update_task_list()
    
    def update_task_list(self):
        # Очищаем список
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтруем задачи
        if self.current_filter == "active":
            filtered_tasks = [task for task in self.tasks if not task["completed"]]
        elif self.current_filter == "completed":
            filtered_tasks = [task for task in self.tasks if task["completed"]]
        else:
            filtered_tasks = self.tasks
        
        # Добавляем задачи в список
        for task in filtered_tasks:
            status_icon = "✅" if task["completed"] else "⏳"
            completed_date = task["completed_date"] if task["completed_date"] else "-"
            
            self.tree.insert("", "end", values=(
                task["id"],           # ID (скрытая колонка)
                task["text"],         # Задача
                task["created"],      # Дата создания
                completed_date,       # Дата завершения
                status_icon           # Статус (иконка)
            ))
    
    def update_stats(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        active = total - completed
        
        self.stats_label.configure(
            text=f"Всего задач: {total} | Активных: {active} | Завершенных: {completed}"
        )
    
    def save_tasks(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {e}")
    
    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
            self.tasks = []
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()