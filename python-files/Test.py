import tkinter as tk
from tkinter import ttk, messagebox

class CommunicationPsychologyTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Тест по психологии общения")
        self.root.geometry("800x600")
        
        # Создаем canvas для градиентного фона
        self.canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Рисуем градиентный фон
        self.draw_gradient("#44756d", "#f9258a")
        
        # Вопросы и варианты ответов
        self.questions = [
            {
                "question": "1. Что означает активное слушание в психологии общения?",
                "options": ["Просто молча слушать собеседника", "Слушать, понимать и реагировать", "Перебивать собеседника", "Думать о своем"],
                "correct": 1
            },
            {
                "question": "2. Какой элемент НЕ относится к невербальному общению?",
                "options": ["Жесты", "Тон голоса", "Поза тела", "Текст сообщения"],
                "correct": 3
            },
            {
                "question": "3. Что такое 'эмпатия' в общении?",
                "options": ["Понимать чувства другого", "Умение красиво говорить", "Навык убеждать", "Скрывать эмоции"],
                "correct": 0
            },
            {
                "question": "4. Какой стиль общения характеризуется доминированием?",
                "options": ["Агрессивный", "Пассивный", "Ассертивный", "Эмпатический"],
                "correct": 0
            },
            {
                "question": "5. Что такое 'обратная связь' в общении?",
                "options": ["Критика", "Реакция на сообщение", "Молчание", "Смена темы"],
                "correct": 1
            },
            {
                "question": "6. Как называется копирование жестов собеседника?",
                "options": ["Рефлексия", "Зеркалирование", "Проекция", "Идентификация"],
                "correct": 1
            },
            {
                "question": "7. Какой процент информации передается через слова?",
                "options": ["7%", "30%", "55%", "90%"],
                "correct": 0
            },
            {
                "question": "8. Что НЕ является барьером в общении?",
                "options": ["Эмпатия", "Стереотипы", "Недостаток внимания", "Языковые различия"],
                "correct": 0
            },
            {
                "question": "9. Как называется техника повторения слов собеседника?",
                "options": ["Рефрейминг", "Парафраз", "Интерпретация", "Резюмирование"],
                "correct": 1
            },
            {
                "question": "10. Какие вопросы помогают развить беседу?",
                "options": ["Закрытые", "Открытые", "Наводящие", "Риторические"],
                "correct": 1
            },
            {
                "question": "11. Что означает 'ассертивное поведение'?",
                "options": ["Уверенность без ущемления других", "Агрессивность", "Пассивность", "Манипуляции"],
                "correct": 0
            },
            {
                "question": "12. Как называется зона комфортного общения?",
                "options": ["Персональное пространство", "Социальная дистанция", "Интимная зона", "Публичная территория"],
                "correct": 0
            },
            {
                "question": "13. Что НЕ влияет на первое впечатление?",
                "options": ["Внешний вид", "Манера речи", "Социальный статус", "Цвет глаз"],
                "correct": 3
            },
            {
                "question": "14. Что такое 'конгруэнтность' в общении?",
                "options": ["Совпадение слов и жестов", "Быстрые ответы", "Красивая речь", "Навык переговоров"],
                "correct": 0
            },
            {
                "question": "15. Что снижает напряжение в конфликте?",
                "options": ["Я-высказывания", "Переход на личности", "Повышение голоса", "Игнорирование"],
                "correct": 0
            }
        ]
        
        self.current_question = 0
        self.score = 0
        self.time_left = 600  # 10 минут в секундах
        self.timer_running = False

        # Настройка стилей
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Используем тему 'clam' для лучшей видимости
        
        # Настройка цветов для элементов
        self.style.configure("TFrame", background="#333333", relief=tk.RAISED, borderwidth=2)
        self.style.configure("TLabel", background="#333333", foreground="#ffffff", font=("Arial", 12))
        self.style.configure("TRadiobutton", background="#333333", foreground="#ffffff", font=("Arial", 11))
        self.style.configure("TButton", font=("Arial", 12), padding=10, 
                            foreground="#ffffff", background="#555555")
        self.style.configure("Title.TLabel", font=("Arial", 18, "bold"), foreground="#ffffff")
        self.style.configure("Timer.TLabel", font=("Arial", 12, "bold"), foreground="#E74C3C")
        self.style.map("TButton", 
                      background=[("active", "#777777")],
                      foreground=[("active", "#ffffff")])
        
        self.show_title_screen()
    
    def draw_gradient(self, start_color, end_color):
        """Создает градиентный фон от start_color к end_color"""
        for i in range(800):
            # Интерполяция цвета
            r = int(int(start_color[1:3], 16) * (1 - i/800) + int(end_color[1:3], 16) * (i/800))
            g = int(int(start_color[3:5], 16) * (1 - i/800) + int(end_color[3:5], 16) * (i/800))
            b = int(int(start_color[5:7], 16) * (1 - i/800) + int(end_color[5:7], 16) * (i/800))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(i, 0, i, 600, fill=color)
    
    def show_title_screen(self):
        self.clear_window()
        
        title_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((400, 250), window=title_frame, anchor="center")
        
        ttk.Label(
            title_frame,
            text="Тест по психологии общения",
            style="Title.TLabel"
        ).pack(pady=20)
        
        ttk.Label(
            title_frame,
            text="У вас будет 10 минут, чтобы ответить на 15 вопросов",
            justify=tk.CENTER
        ).pack(pady=10)
        
        ttk.Label(
            title_frame,
            text="Тест содержит 15 вопросов с вариантами ответов",
            justify=tk.CENTER
        ).pack(pady=10)
        
        start_button = ttk.Button(
            title_frame,
            text="Начать тест",
            command=self.start_test
        )
        start_button.pack(pady=30)
    
    def start_test(self):
        self.clear_window()
        self.setup_test_interface()
        self.load_question()
        self.start_timer()
    
    def start_timer(self):
        self.timer_running = True
        self.update_timer()
    
    def stop_timer(self):
        self.timer_running = False
    
    def update_timer(self):
        if not self.timer_running:
            return
            
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Осталось времени: {mins:02d}:{secs:02d}")
        
        if self.time_left <= 0:
            self.stop_timer()
            messagebox.showinfo("Время вышло", "Время на прохождение теста истекло!")
            self.show_results()
            return
        
        self.time_left -= 1
        self.root.after(1000, self.update_timer)
    
    def setup_test_interface(self):
        self.main_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((400, 300), window=self.main_frame, anchor="center")
        
        # Таймер
        self.timer_label = ttk.Label(
            self.main_frame,
            style="Timer.TLabel"
        )
        self.timer_label.pack(pady=5)
        
        self.question_label = ttk.Label(self.main_frame, wraplength=700, style="TLabel")
        self.question_label.pack(pady=10)
        
        self.radio_var = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(
                self.main_frame,
                text="",
                variable=self.radio_var,
                value=i,
                style="TRadiobutton"
            )
            rb.pack(anchor=tk.W, pady=5)
            self.radio_buttons.append(rb)
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(self.main_frame, style="TFrame")
        button_frame.pack(pady=20)
        
        self.back_button = ttk.Button(
            button_frame,
            text="Назад",
            command=self.prev_question,
            state="disabled"  # На первом вопросе кнопка неактивна
        )
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        self.skip_button = ttk.Button(
            button_frame,
            text="Пропустить",
            command=self.skip_question
        )
        self.skip_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Далее",
            command=self.next_question
        )
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        self.finish_button = ttk.Button(
            button_frame,
            text="Завершить тест",
            command=self.confirm_finish_test
        )
        self.finish_button.pack(side=tk.LEFT, padx=10)
        
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            length=700,
            mode='determinate'
        )
        self.progress.pack(pady=10)
    
    def skip_question(self):
        """Пропустить текущий вопрос без ответа"""
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.show_results()
        else:
            self.load_question()
    
    def confirm_finish_test(self):
        """Подтверждение завершения теста"""
        if messagebox.askyesno("Подтверждение", 
                             "Вы уверены, что хотите завершить тест?\nТекущие результаты будут сохранены."):
            self.show_results()
    
    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.load_question()
    
    def clear_window(self):
        self.stop_timer()
        self.canvas.delete("all")
        self.draw_gradient("#44756d", "#f9258a")
    
    def load_question(self):
        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question]
            self.question_label.config(text=question_data["question"])
            
            for i in range(4):
                self.radio_buttons[i].config(text=question_data["options"][i])
            
            self.radio_var.set(-1)
            self.progress["value"] = (self.current_question / len(self.questions)) * 100
            
            # Обновляем состояние кнопок
            self.back_button.config(state="normal" if self.current_question > 0 else "disabled")
            self.next_button.config(text="Завершить тест" if self.current_question == len(self.questions) - 1 else "Далее")
        else:
            self.show_results()
    
    def next_question(self):
        if self.radio_var.get() == -1:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите ответ!")
            return
        
        if self.radio_var.get() == self.questions[self.current_question]["correct"]:
            self.score += 1
        
        self.current_question += 1
        self.load_question()
    
    def show_results(self):
        self.stop_timer()
        self.clear_window()
        
        result_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas.create_window((400, 250), window=result_frame, anchor="center")
        
        ttk.Label(
            result_frame,
            text="Результаты теста",
            style="Title.TLabel"
        ).pack(pady=10)
        
        percentage = (self.score / len(self.questions)) * 100
        grade, description, color = self.get_grade_description(percentage)
        
        score_label = ttk.Label(
            result_frame,
            text=f"Правильных ответов: {self.score} из {len(self.questions)} ({percentage:.1f}%)",
            font=("Arial", 14, "bold"),
            foreground=color
        )
        score_label.pack(pady=5)
        
        grade_label = ttk.Label(
            result_frame,
            text=f"Оценка: {grade}",
            font=("Arial", 16, "bold"),
            foreground=color
        )
        grade_label.pack(pady=5)
        
        feedback_label = ttk.Label(
            result_frame,
            text=description,
            wraplength=500,
            font=("Arial", 12),
            foreground=color,
            justify=tk.CENTER
        )
        feedback_label.pack(pady=10)
        
        details_frame = ttk.Frame(result_frame, style="TFrame")
        details_frame.pack(pady=10)
        
        ttk.Label(
            details_frame,
            text="Уровни оценивания:",
            font=("Arial", 10, "underline")
        ).pack()
        
        ttk.Label(
            details_frame,
            text="5 (Отлично) - 90-100%\n4 (Хорошо) - 70-89%\n3 (Удовлетворительно) - 50-69%\n2 (Неудовлетворительно) - 0-49%",
            font=("Arial", 10)
        ).pack()
        
        restart_button = ttk.Button(
            result_frame,
            text="Пройти тест снова",
            command=self.restart_test
        )
        restart_button.pack(pady=15)
    
    def get_grade_description(self, percentage):
        if percentage >= 90:
            return "5 (Отлично)", "Превосходный результат! Вы демонстрируете глубокое понимание психологии общения.", "#27AE60"
        elif percentage >= 70:
            return "4 (Хорошо)", "Хороший результат! Вы хорошо разбираетесь в основах психологии общения, но есть небольшие пробелы.", "#2E86C1"
        elif percentage >= 50:
            return "3 (Удовлетворительно)", "Удовлетворительный результат. Рекомендуется дополнительное изучение темы для улучшения знаний.", "#F39C12"
        else:
            return "2 (Неудовлетворительно)", "Результат ниже среднего. Рекомендуется серьезно изучить материалы по психологии общения.", "#E74C3C"
    
    def restart_test(self):
        self.current_question = 0
        self.score = 0
        self.time_left = 600
        self.start_test()

if __name__ == "__main__":
    root = tk.Tk()
    app = CommunicationPsychologyTest(root)
    root.mainloop()