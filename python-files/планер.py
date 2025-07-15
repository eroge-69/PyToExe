import tkinter as tk
from tkinter import font as tkfont
import calendar
from datetime import datetime
import random
import time

class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Милый планер ✨")
        self.root.geometry("900x700")
        self.root.configure(bg="#FFFACD")
        
        # Мотивационные фразы
        self.motivational_phrases = [
            "Ты просто космос! 🌟",
            "Умница! Продолжай в том же духе! 💖",
            "Сегодня ты свернул горы! 🏔️",
            "Идеально! Ты заслужил печеньку! 🍪",
            "Ты - звезда! Сияй ярче! ✨"
        ]
        
        # Создаем основной интерфейс
        self.create_widgets()
        self.update_clock()  # Запускаем часы
        
    def create_widgets(self):
        # Пытаемся использовать Comic Sans MS, иначе системный шрифт
        try:
            self.title_font = tkfont.Font(family="Comic Sans MS", size=18, weight="bold")
            self.task_font = tkfont.Font(family="Comic Sans MS", size=14)
            self.calendar_font = tkfont.Font(family="Comic Sans MS", size=12)
            self.clock_font = tkfont.Font(family="Comic Sans MS", size=24, weight="bold")
        except:
            self.title_font = tkfont.Font(size=18, weight="bold")
            self.task_font = tkfont.Font(size=14)
            self.calendar_font = tkfont.Font(size=12)
            self.clock_font = tkfont.Font(size=24, weight="bold")
        
        # Верхняя панель с заголовком и часами
        header_frame = tk.Frame(self.root, bg="#FFFACD")
        header_frame.pack(fill=tk.X, pady=10)
        
        # Заголовок
        title_label = tk.Label(
            header_frame,
            text="Милый планер ✨",
            font=self.title_font,
            bg="#FFFACD",
            fg="#FF8C00"
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Часы
        self.clock_label = tk.Label(
            header_frame,
            text="",
            font=self.clock_font,
            bg="#FFFACD",
            fg="#FF8C00"
        )
        self.clock_label.pack(side=tk.RIGHT, padx=20)
        
        # Основной фрейм для календаря и задач
        main_frame = tk.Frame(self.root, bg="#FFFACD")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Календарь (левая часть)
        calendar_frame = tk.Frame(main_frame, bg="#FFFACD")
        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Панель управления календарем
        self.calendar_nav_frame = tk.Frame(calendar_frame, bg="#FFFACD")
        self.calendar_nav_frame.pack()
        
        self.prev_month_btn = tk.Button(
            self.calendar_nav_frame,
            text="◀",
            command=self.prev_month,
            bg="#FFD700",
            fg="black",
            font=self.calendar_font,
            relief=tk.FLAT,
            width=3
        )
        self.prev_month_btn.pack(side=tk.LEFT, padx=5)
        
        self.month_year_label = tk.Label(
            self.calendar_nav_frame,
            text="",
            font=self.calendar_font,
            bg="#FFFACD",
            fg="#FF8C00"
        )
        self.month_year_label.pack(side=tk.LEFT, padx=10)
        
        self.next_month_btn = tk.Button(
            self.calendar_nav_frame,
            text="▶",
            command=self.next_month,
            bg="#FFD700",
            fg="black",
            font=self.calendar_font,
            relief=tk.FLAT,
            width=3
        )
        self.next_month_btn.pack(side=tk.LEFT, padx=5)
        
        # Сетка календаря с крупными клетками
        self.calendar_grid_frame = tk.Frame(calendar_frame, bg="#FFFACD")
        self.calendar_grid_frame.pack(pady=10)
        
        # Текущая дата
        self.current_date = datetime.now()
        self.display_month(self.current_date.year, self.current_date.month)
        
        # Задания (правая часть)
        tasks_frame = tk.Frame(main_frame, bg="#FFFACD", padx=20)
        tasks_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tasks_title = tk.Label(
            tasks_frame,
            text="Сегодняшние задания:",
            font=self.title_font,
            bg="#FFFACD",
            fg="#FF8C00"
        )
        tasks_title.pack(pady=10)
        
        self.tasks = [
            {"name": "Заработок", "completed": False, "label": None, "var": tk.BooleanVar()},
            {"name": "Уход за собой", "completed": False, "label": None, "var": tk.BooleanVar()},
            {"name": "Изучение английского", "completed": False, "label": None, "var": tk.BooleanVar()},
            {"name": "Развитие", "completed": False, "label": None, "var": tk.BooleanVar()}
        ]
        
        for task in self.tasks:
            task_frame = tk.Frame(tasks_frame, bg="#FFFACD")
            task_frame.pack(anchor="w", pady=8)
            
            task["var"].set(False)
            cb = tk.Checkbutton(
                task_frame,
                variable=task["var"],
                command=lambda t=task: self.toggle_task(t),
                bg="#FFFACD",
                activebackground="#FFFACD",
                font=self.task_font
            )
            cb.pack(side=tk.LEFT)
            
            task["label"] = tk.Label(
                task_frame,
                text=task["name"],
                font=self.task_font,
                bg="#FFFACD",
                fg="#FF8C00",
                width=20,
                anchor="w"
            )
            task["label"].pack(side=tk.LEFT)
            
            task["label"].bind("<Button-1>", lambda e, t=task: self.toggle_task(t))
        
        # Мотивационная фраза и звездочка
        self.motivation_frame = tk.Frame(tasks_frame, bg="#FFFACD")
        self.motivation_frame.pack(pady=20)
        
        self.motivation_label = tk.Label(
            self.motivation_frame,
            text="",
            font=self.task_font,
            bg="#FFFACD",
            fg="#FF8C00",
            wraplength=250
        )
        self.motivation_label.pack()
        
        self.star_label = tk.Label(
            self.motivation_frame,
            text="",
            font=tkfont.Font(size=30),
            bg="#FFFACD",
            fg="#FFD700"
        )
        self.star_label.pack()
        
        self.update_calendar()
    
    def display_month(self, year, month):
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()
        
        month_name = calendar.month_name[month]
        self.month_year_label.config(text=f"{month_name} {year}")
        
        cal = calendar.monthcalendar(year, month)
        
        # Заголовки дней недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            tk.Label(
                self.calendar_grid_frame,
                text=day,
                font=self.calendar_font,
                bg="#FFFACD",
                fg="#FF8C00",
                width=6,
                height=2
            ).grid(row=0, column=i, padx=3, pady=3)
        
        # Крупные квадратные клетки
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_frame = tk.Frame(
                        self.calendar_grid_frame,
                        bg="#FFFFE0",
                        relief=tk.RAISED,
                        borderwidth=1,
                        width=60,
                        height=60
                    )
                    day_frame.grid(row=week_num, column=day_num, padx=3, pady=3)
                    day_frame.grid_propagate(False)
                    
                    date_label = tk.Label(
                        day_frame,
                        text=str(day),
                        font=self.calendar_font,
                        bg="#FFFFE0",
                        fg="black"
                    )
                    date_label.pack(expand=True)
                    
                    emoji_label = tk.Label(
                        day_frame,
                        text="",
                        font=tkfont.Font(size=14),
                        bg="#FFFFE0"
                    )
                    emoji_label.pack()
                    
                    day_frame.bind("<Button-1>", lambda e, d=day, m=month, y=year: self.select_day(y, m, d))
    
    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)
    
    def select_day(self, year, month, day):
        popup = tk.Toplevel(self.root)
        popup.title("Выбери эмодзи")
        popup.geometry("300x150")
        popup.configure(bg="#FFFACD")
        
        tk.Label(
            popup,
            text=f"{day} {calendar.month_name[month]} {year}",
            bg="#FFFACD",
            fg="#FF8C00",
            font=self.calendar_font
        ).pack(pady=10)
        
        emojis = ["⭐", "🎉", "💰", "❤️"]
        emoji_frame = tk.Frame(popup, bg="#FFFACD")
        emoji_frame.pack()
        
        for emoji in emojis:
            btn = tk.Button(
                emoji_frame,
                text=emoji,
                font=tkfont.Font(size=18),
                command=lambda e=emoji: self.set_emoji(year, month, day, e, popup),
                bg="#FFD700",
                relief=tk.FLAT,
                width=3
            )
            btn.pack(side=tk.LEFT, padx=10, pady=10)
    
    def set_emoji(self, year, month, day, emoji, popup):
        popup.destroy()
        messagebox.showinfo("Успешно!", f"Вы выбрали {emoji} для {day}.{month}.{year}")
    
    def prev_month(self):
        self.current_date = self.current_date.replace(
            month=self.current_date.month-1 if self.current_date.month > 1 else 12,
            year=self.current_date.year if self.current_date.month > 1 else self.current_date.year-1
        )
        self.update_calendar()
    
    def next_month(self):
        self.current_date = self.current_date.replace(
            month=self.current_date.month+1 if self.current_date.month < 12 else 1,
            year=self.current_date.year if self.current_date.month < 12 else self.current_date.year+1
        )
        self.update_calendar()
    
    def update_calendar(self):
        self.display_month(self.current_date.year, self.current_date.month)
    
    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        task["var"].set(task["completed"])
        
        if task["completed"]:
            task["label"].config(font=(self.task_font.actual("family"), self.task_font.actual("size"), "overstrike"))
        else:
            task["label"].config(font=self.task_font)
        
        all_completed = all(t["completed"] for t in self.tasks)
        if all_completed:
            self.show_motivation()
        else:
            self.hide_motivation()
    
    def show_motivation(self):
        self.star_label.config(text="⭐")
        phrase = random.choice(self.motivational_phrases)
        self.motivation_label.config(text=phrase)
    
    def hide_motivation(self):
        self.star_label.config(text="")
        self.motivation_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()