import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class TankBlitzTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Танки Блиц - Статистика сессии")
        self.root.geometry("400x400")  # Увеличили высоту для новых кнопок
        self.root.resizable(False, False)
        
        # Инициализация данных сессии
        self.reset_session()
        
        # Стили
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        
        # Создание интерфейса
        self.create_widgets()
        
    def reset_session(self, battles=None):
        if battles is not None:
            self.battles = battles
            self.recalculate_stats()
        else:
            self.battles = []
            self.session_stats = {
                "total_battles": 0,
                "total_damage": 0,
                "wins": 0
            }
    
    def recalculate_stats(self):
        """Пересчитывает статистику на основе списка боев"""
        self.session_stats = {
            "total_battles": len(self.battles),
            "total_damage": sum(battle['damage'] for battle in self.battles),
            "wins": sum(1 for battle in self.battles if battle['result'])
        }
    
    def create_widgets(self):
        # Заголовок
        header = ttk.Label(
            self.root, 
            text="Статистика игровой сессии", 
            style="Header.TLabel"
        )
        header.pack(pady=10)
        
        # Поля ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, fill='x', padx=20)
        
        ttk.Label(input_frame, text="Урон в бою:").grid(row=0, column=0, sticky='w')
        self.damage_entry = ttk.Entry(input_frame, width=10)
        self.damage_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Результат:").grid(row=1, column=0, sticky='w', pady=10)
        self.result_var = tk.StringVar(value="win")
        ttk.Radiobutton(input_frame, text="Победа", variable=self.result_var, value="win").grid(row=1, column=1, sticky='w')
        ttk.Radiobutton(input_frame, text="Поражение", variable=self.result_var, value="loss").grid(row=1, column=2, sticky='w')
        
        # Кнопки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Добавить бой", command=self.add_battle).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Сбросить сессию", command=self.reset_session_confirm).pack(side='left', padx=5)
        
        # Новые кнопки для работы с файлами
        file_btn_frame = ttk.Frame(self.root)
        file_btn_frame.pack(pady=5)
        
        ttk.Button(file_btn_frame, text="Сохранить сессию", command=self.save_session).pack(side='left', padx=5)
        ttk.Button(file_btn_frame, text="Загрузить сессию", command=self.load_session).pack(side='left', padx=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.root, text="Текущая статистика сессии")
        stats_frame.pack(pady=15, fill='x', padx=20)
        
        stats_labels = [
            ("Количество боев:", "battles"),
            ("Средний урон:", "avg_damage"),
            ("Процент побед:", "win_rate"),
            ("Суммарный урон:", "total_damage")
        ]
        
        self.stats_vars = {}
        for i, (label_text, var_name) in enumerate(stats_labels):
            ttk.Label(stats_frame, text=label_text).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            self.stats_vars[var_name] = tk.StringVar(value="0")
            ttk.Label(stats_frame, textvariable=self.stats_vars[var_name]).grid(
                row=i, column=1, sticky='e', padx=10, pady=5)
        
        # Обновить статистику
        self.update_stats_display()
        
    def add_battle(self):
        damage = self.damage_entry.get()
        
        if not damage.isdigit():
            messagebox.showerror("Ошибка", "Укажите числовое значение для урона")
            return
            
        damage = int(damage)
        is_win = self.result_var.get() == "win"
        
        # Добавить бой в сессию
        self.battles.append({
            "damage": damage,
            "result": is_win
        })
        
        # Обновить статистику
        self.session_stats["total_battles"] += 1
        self.session_stats["total_damage"] += damage
        if is_win:
            self.session_stats["wins"] += 1
            
        # Обновить интерфейс
        self.update_stats_display()
        self.damage_entry.delete(0, tk.END)
        
    def update_stats_display(self):
        total = self.session_stats["total_battles"]
        wins = self.session_stats["wins"]
        total_damage = self.session_stats["total_damage"]
        
        # Рассчет статистики
        avg_damage = total_damage / total if total > 0 else 0
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # Обновление значений
        self.stats_vars["battles"].set(total)
        self.stats_vars["avg_damage"].set(f"{avg_damage:.2f}")
        self.stats_vars["win_rate"].set(f"{win_rate:.2f}%")
        self.stats_vars["total_damage"].set(total_damage)
        
    def reset_session_confirm(self):
        if messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены что хотите сбросить текущую сессию? Все данные будут потеряны"
        ):
            self.reset_session()
            self.update_stats_display()
            messagebox.showinfo("Сброс", "Сессия успешно сброшена")
    
    def save_session(self):
        """Сохраняет текущую сессию в файл JSON"""
        if not self.battles:
            messagebox.showwarning("Пустая сессия", "Нет данных для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить сессию"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.battles, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Сессия сохранена в файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def load_session(self):
        """Загружает сессию из файла JSON"""
        if self.battles:
            if not messagebox.askyesno(
                "Подтверждение", 
                "Текущая сессия будет потеряна. Продолжить загрузку?"
            ):
                return
                
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите файл сессии"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                battles = json.load(f)
                
            # Проверка формата данных
            if not isinstance(battles, list):
                raise ValueError("Неправильный формат данных")
                
            for battle in battles:
                if 'damage' not in battle or 'result' not in battle:
                    raise ValueError("Отсутствуют обязательные поля")
                
            self.reset_session(battles)
            self.update_stats_display()
            messagebox.showinfo("Успех", f"Сессия загружена из файла:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TankBlitzTracker(root)
    root.mainloop()
