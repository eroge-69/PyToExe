import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class GradientFrame(tk.Canvas):
    def __init__(self, parent, colors=("#4B0082", "#FFA500"), **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs, highlightthickness=0)
        self.colors = colors
        self.bind("<Configure>", self._draw_gradient)
        self._draw_gradient()

    def _draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        
        self.delete("gradient")  # Очищаем предыдущий градиент
        
        # Создаем вертикальный градиент от цвета 1 к цвету 2
        for y in range(height):
            ratio = y / height
            r = int(int(self.colors[0][1:3], 16) * (1 - ratio) + int(self.colors[1][1:3], 16) * ratio)
            g = int(int(self.colors[0][3:5], 16) * (1 - ratio) + int(self.colors[1][3:5], 16) * ratio)
            b = int(int(self.colors[0][5:7], 16) * (1 - ratio) + int(self.colors[1][5:7], 16) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, y, width, y, tags=("gradient",), fill=color)

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тест по Python и Pascal")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)

        self.white_bg = "#FFFFFF"  # Определяем белый цвет фона
        self.root.configure(bg=self.white_bg) # Устанавливаем белый цвет как основной фон root

        # Создаем градиентный фон
        self.gradient_frame = GradientFrame(
            root,
            colors=("#4B0082", "#FFA500"),  # Фиолетовый к оранжевому
            bg=self.white_bg # Устанавливаем белый цвет фона для градиента
        )
        self.gradient_frame.pack(fill="both", expand=True)

        # Основной контейнер для виджетов
        self.main_container = tk.Frame(self.gradient_frame, bg=self.white_bg)  # Белый фон
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=550)

        self.questions = [
            {
                "type": "text",
                "question": "1. Как называется функция, используемая для вывода информации на экран в Python?",
                "answer": "print"
            },
            {
                "type": "text",
                "question": "2. Какой оператор используется для присваивания значения переменной?",
                "answer": "="
            },
            {
                "type": "multiple_choice",
                "question": "3. Какие из перечисленных типов данных являются изменяемыми (mutable) в Python? (Выберите все подходящие варианты)",
                "options": ["int", "list", "tuple", "dict", "str"],
                "correct_indices": [1, 3]
            },
            {
                "type": "multiple_choice",
                "question": "4. Какие из перечисленных ключевых слов используются для создания циклов в Python? (Выберите все подходящие варианты)",
                "options": ["if", "for", "while", "else", "loop"],
                "correct_indices": [1, 2]
            },
            {
                "type": "multiple_choice",
                "question": "5. Какие из перечисленных символов используются для комментирования кода в Python? (Выберите все подходящие варианты)",
                "options": ["//", "/* */", "#", "--", "''' '''"],
                "correct_indices": [2, 4]
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "6. Как открыть файл в режиме чтения?",
                "options": ["open(\"file.txt\", \"r\")", "open(\"file.txt\", \"read\")", "open(\"file.txt\", \"w\")", "open(\"file.txt\", \"a\")"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "7. Какой метод удаляет элемент из списка по значению?",
                "options": [".pop()", ".remove()", ".delete()", ".clear()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "8. Какой оператор вывода в Pascal?",
                "options": ["print()", "writeln()", "echo()", "output()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "9. Как объявить переменную в Pascal?",
                "options": ["var x = 10;", "int x := 10;", "x: integer = 10;", "var x: integer;"],
                "correct_index": 3
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "10. Как записать условие if в Pascal?",
                "options": ["if (x > 10) then", "if x > 10:", "if {x > 10} then", "when x > 10 then"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "11. Какой цикл есть в Pascal, но отсутствует в Python?",
                "options": ["for", "while", "repeat ... until", "loop"],
                "correct_index": 2
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "12. Как объявить массив в Pascal?",
                "options": ["array [1..10] of integer;", "list = [1, 2, 3]", "int arr[10];", "array (1 to 10) as integer"],
                "correct_index": 0
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "13. Какой оператор используется для ввода данных?",
                "options": ["input()", "readln()", "scan()", "get()"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "14. Как завершить программу в Pascal?",
                "options": ["exit", "end.", "stop", "break"],
                "correct_index": 1
            },
            {
                "type": "single_choice",  # Изменено на single_choice
                "question": "15. Как записать комментарий в Pascal?",
                "options": ["# Комментарий", "// Комментарий", "/* Комментарий */", "-- Комментарий"],
                "correct_index": 1
            }
        ]

        self.current_question = 0
        self.score = 0
        self.user_answers = [None] * len(self.questions)
        self.time_left = 6 * 60  # 6 минут в секундах
        self.timer_running = False

        self.create_widgets()
        self.show_welcome_frame()

    def create_widgets(self):
        # Фреймы для разных состояний приложения
        self.welcome_frame = tk.Frame(self.main_container, bg=self.white_bg)
        self.quiz_frame = tk.Frame(self.main_container, bg=self.white_bg)
        self.result_frame = tk.Frame(self.main_container, bg=self.white_bg)

        # Виджеты для экрана приветствия
        self.welcome_label = tk.Label(
            self.welcome_frame,
            text="Добро пожаловать на тест по языку Python и Pascal!\n\n"
                 "Вам предстоит ответить на 15 вопросов разного типа.\n"
                 "На выполнение теста отводится 6 минут.\n"
                 "Пожалуйста, внимательно читайте вопросы и отвечайте обдуманно.\n\n"
                 "Ваш результат будет представлен в виде процентного соотношения правильных ответов.\n\nУдачи!",
            font=("Arial", 20),
            justify="center",
            fg='black', # Цвет текста
            bg=self.white_bg # Белый фон
        )
        self.welcome_label.pack(pady=50)

        self.start_button = tk.Button(
            self.welcome_frame,
            text="Начать тест",
            command=self.start_test,
            bg='#4CAF50',
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.start_button.pack(pady=20)

        # Виджеты для теста
        self.timer_label = tk.Label(
            self.quiz_frame,
            text="Осталось времени: 6:00",
            font=("Arial", 24, "bold"),
            fg='black', # Цвет текста
            bg=self.white_bg # Белый фон
        )
        self.timer_label.pack(pady=10)

        self.question_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 20),
            wraplength=1000,
            justify="center",
            fg='black',  # Цвет текста
            bg=self.white_bg # Белый фон
        )
        self.question_label.pack(pady=20)

        self.answer_frame = tk.Frame(self.quiz_frame, bg=self.white_bg)
        self.answer_frame.pack()

        self.nav_frame = tk.Frame(self.quiz_frame, bg=self.white_bg)
        self.nav_frame.pack(pady=20)

        self.prev_button = tk.Button(
            self.nav_frame,
            text="Назад",
            command=self.prev_question,
            state=tk.DISABLED,
            bg='#59E900',
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            self.nav_frame,
            text="Вперед",
            command=self.next_question,
            bg="#59E900",
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.progress_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 20),
            fg='black', # Цвет текста
            bg=self.white_bg # Белый фон
        )
        self.progress_label.pack(pady=10)

        # Виджеты для экрана результатов
        self.result_label = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 24),
            justify="center",
            fg='black',  # Цвет текста
            bg=self.white_bg # Белый фон
        )
        self.result_label.pack(pady=50)

        self.restart_button = tk.Button(
            self.result_frame,
            text="Тест заново",
            command=self.restart_test,
            bg='#4CAF50',
            fg='black',
            font=('Arial', 20),
            relief=tk.RAISED,
            border=3
        )
        self.restart_button.pack(pady=20)

    def show_welcome_frame(self):
        self.quiz_frame.pack_forget()
        self.result_frame.pack_forget()
        self.welcome_frame.pack(fill="both", expand=True)

    def show_quiz_frame(self):
        self.welcome_frame.pack_forget()
        self.result_frame.pack_forget()
        self.quiz_frame.pack(fill="both", expand=True)
        self.show_question()

    def show_result_frame(self):
        self.welcome_frame.pack_forget()
        self.quiz_frame.pack_forget()
        self.result_frame.pack(fill="both", expand=True)

    def start_test(self):
        self.reset_test()
        self.show_quiz_frame()
        self.time_left = 6 * 60
        self.timer_running = True
        self.update_timer()

    def reset_test(self):
        """Сброс всех результатов и начало теста заново"""
        self.current_question = 0
        self.score = 0
        self.user_answers = [None] * len(self.questions)
        self.time_left = 6 * 60
        self.timer_running = False
        self.timer_label.config(fg='black')

    def restart_test(self):
        """Обработчик кнопки 'Тест заново'"""
        self.start_test()

    def update_timer(self):
        if self.timer_running:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.config(text=f"Осталось времени: {minutes:02d}:{seconds:02d}")

            if self.time_left <= 60:
                self.timer_label.config(fg='red')
            else:
                self.timer_label.config(fg='black')

            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.finish_quiz()

    def show_question(self):
        # Очистка предыдущих ответов
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        question = self.questions[self.current_question]
        self.question_label.config(text=question["question"])
        self.progress_label.config(text=f"Вопрос {self.current_question + 1} из {len(self.questions)}")

        if question["type"] == "text":
            self.show_text_input(question)
        elif question["type"] == "multiple_choice":
            self.show_multiple_choice(question)
        elif question["type"] == "single_choice":
            self.show_single_choice(question)

        self.update_button_states()

    def show_text_input(self, question):
        self.answer_entry = tk.Entry(self.answer_frame, font=("Arial", 20), bg=self.white_bg)
        self.answer_entry.pack(pady=10)
        if self.user_answers[self.current_question] is not None:
            self.answer_entry.insert(0, self.user_answers[self.current_question])

    def show_multiple_choice(self, question):
        self.choice_vars = [tk.BooleanVar(value=False) for _ in range(len(question["options"]))]
        self.check_buttons = []

        for i, option in enumerate(question["options"]):
            cb = tk.Checkbutton(self.answer_frame, text=option, variable=self.choice_vars[i],
                                font=("Arial", 16), bg=self.white_bg, selectcolor=self.white_bg)
            cb.pack(anchor="w", padx=50)
            self.check_buttons.append(cb)

        if self.user_answers[self.current_question]:
            for i, val in enumerate(self.user_answers[self.current_question]):
                self.choice_vars[i].set(val)


    def show_single_choice(self, question):
        self.radio_var = tk.IntVar(value=-1) # Изначально ничего не выбрано
        self.radio_buttons = []

        for i, option in enumerate(question["options"]):
            rb = tk.Radiobutton(self.answer_frame, text=option, variable=self.radio_var, value=i,
                                font=("Arial", 16), bg=self.white_bg, selectcolor=self.white_bg)
            rb.pack(anchor="w", padx=50)
            self.radio_buttons.append(rb)

        if self.user_answers[self.current_question] is not None:
            self.radio_var.set(self.user_answers[self.current_question])

    def update_button_states(self):
        self.prev_button.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.next_button.config(text="Завершить" if self.current_question == len(self.questions) - 1 else "Вперед")

    def prev_question(self):
        self.save_answer() #Сохраняем текущий ответ
        self.current_question -= 1
        self.show_question()

    def next_question(self):
        self.save_answer()
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.finish_quiz()

    def save_answer(self):
        question = self.questions[self.current_question]
        if question["type"] == "text":
            self.user_answers[self.current_question] = self.answer_entry.get()
        elif question["type"] == "multiple_choice":
             self.user_answers[self.current_question] = [var.get() for var in self.choice_vars]
        elif question["type"] == "single_choice":
            self.user_answers[self.current_question] = self.radio_var.get()

    def finish_quiz(self):
        self.timer_running = False
        # Сохраняем последний ответ
        self.save_answer()
        # Расчет результатов
        correct = 0
        for i, question in enumerate(self.questions):
            if question["type"] == "text":
                if self.user_answers[i] and self.user_answers[i].lower().strip() == question["answer"].lower().strip():
                    correct += 1
            elif question["type"] == "multiple_choice":
                correct_indices = question["correct_indices"]
                user_choices = self.user_answers[i]

                if user_choices is None: #Если пользователь ничего не выбрал - сразу неправильно
                    continue

                selected_indices = [j for j, selected in enumerate(user_choices) if selected]
                if set(selected_indices) == set(correct_indices):
                    correct += 1
            elif question["type"] == "single_choice":
                if self.user_answers[i] == question["correct_index"]:
                    correct += 1

        percentage = (correct / len(self.questions)) * 100
        result_text = f"Правильных ответов: {correct} из {len(self.questions)}\nПроцент: {percentage:.1f}%"
        if percentage >= 90:
            result = "5!"
        elif percentage >= 70:
            result = "4!"
        elif percentage >= 50:
            result = "3!"
        else:
            result = "2!"
        result_text = f"Правильных ответов: {correct} из {len(self.questions)}\nПроцент: {percentage:.1f}%\nОценка: {result}"

        self.result_label.config(text=result_text)
        self.show_result_frame()

        self.result_label.config(text=result_text)
        self.show_result_frame()
        self.result_label.config(text=result_text)
        self.show_result_frame()



def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()