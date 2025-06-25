import tkinter as tk
from tkinter import messagebox, ttk

questions =  [
    {
        "question": "Що слід враховувати перед заміною процесора?",
        "options": ["Тип відеокарти", "Сумісність з сокетом материнської плати", "Операційна система", "Тип монітора"],
        "correct": 1
    },
    {
        "question": "Який компонент найбільше впливає на продуктивність у відеоіграх?",
        "options": ["Оперативна пам’ять", "Процесор", "Жорсткий диск", "Відеокарта"],
        "correct": 3
    },
    {
        "question": "Що означає термін 'Plug and Play'?",
        "options": ["Ручна установка драйвера", "Автоматичне розпізнавання пристрою", "Налаштування BIOS", "Потрібне перезавантаження"],
        "correct": 1
    },
    {
        "question": "Яка програма використовується для стрес-тесту процесора?",
        "options": ["CPU-Z", "FurMark", "Prime95", "CrystalDiskInfo"],
        "correct": 2
    },
    {
        "question": "Що слід зробити після встановлення нового модуля ОЗП?",
        "options": ["Оновити відеодрайвер", "Форматувати диск", "Перевірити у BIOS", "Змінити блок живлення"],
        "correct": 2
    },
    {
        "question": "Що таке BIOS?",
        "options": ["Графічна оболонка", "Операційна система", "Базова система вводу/виводу", "Формат файлів"],
        "correct": 2
    },
    {
        "question": "Який з пристроїв відповідає за зберігання даних постійно?",
        "options": ["ОЗП", "Процесор", "Жорсткий диск", "Відеокарта"],
        "correct": 2
    },
    {
        "question": "Що означає абревіатура GPU?",
        "options": ["Головний процесор", "Графічний процесор", "Загальна пам’ять", "Ігровий процесор"],
        "correct": 1
    },
    {
        "question": "Що слід перевірити перед купівлею нової відеокарти?",
        "options": ["Тип клавіатури", "Кількість USB портів", "Сумісність з материнською платою та БЖ", "Тип BIOS"],
        "correct": 2
    },
    {
        "question": "Яка функція блоку живлення?",
        "options": ["Охолодження системи", "Передача даних", "Подача живлення компонентам", "Запуск Windows"],
        "correct": 2
    },
    {
        "question": "Для чого потрібен термопастовий шар між CPU і кулером?",
        "options": ["Ізоляція", "Покращення теплопередачі", "Естетика", "Зменшення шуму"],
        "correct": 1
    },
    {
        "question": "Який тип пам’яті швидший?",
        "options": ["HDD", "DDR4", "SSD", "DVD"],
        "correct": 2
    },
    {
        "question": "Як називається роз’єм живлення для відеокарти?",
        "options": ["24-pin", "SATA", "PCIe", "HDMI"],
        "correct": 2
    },
    {
        "question": "Що робить утиліта MemTest86?",
        "options": ["Тестує відеокарту", "Перевіряє ОЗП на помилки", "Оновлює драйвери", "Моніторить температуру"],
        "correct": 1
    },
    {
        "question": "Який компонент обробляє більшість обчислень у ПК?",
        "options": ["ОЗП", "Процесор", "Материнська плата", "Блок живлення"],
        "correct": 1
    },
    {
        "question": "Що таке форм-фактор материнської плати?",
        "options": ["Швидкість роботи", "Розмір та розташування елементів", "Тип сокета", "Операційна система"],
        "correct": 1
    },
    {
        "question": "Як перевірити температуру компонентів ПК?",
        "options": ["Відкрити корпус", "Слухати шум", "Через спеціальну програму", "Перевірити екран"],
        "correct": 2
    },
    {
        "question": "Який порт зазвичай використовується для монітора?",
        "options": ["HDMI", "SATA", "USB", "RJ-45"],
        "correct": 0
    },
    {
        "question": "Що слід зробити перед встановленням нового жорсткого диска?",
        "options": ["Підключити інтернет", "Оновити BIOS", "Перевірити інтерфейс і живлення", "Замінити процесор"],
        "correct": 2
    },
    {
        "question": "Для чого використовується UEFI?",
        "options": ["Завантаження системи", "Мережеві налаштування", "Встановлення драйверів", "Запуск антивіруса"],
        "correct": 0
    }
]

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ Тест: Модернізація ПК")
        self.root.geometry("700x650")
        
        self.BG_COLOR = "#2a0a0a"
        self.FRAME_BG_COLOR = "#1a0000"
        self.TEXT_COLOR = "#f5f5f5"
        self.TITLE_COLOR = "#ff4d4d"
        self.BUTTON_BG = "#990000"
        self.BUTTON_ACTIVE_BG = "#cc0000"
        self.OPTION_BG = "#4d0f0f"
        self.OPTION_HOVER_BG = "#660000"
        self.CORRECT_BG = "#006400"
        self.INCORRECT_BG = "#b71c1c"
        self.CORRECT_FG = "#90ee90"
        self.INCORRECT_FG = "#ff8080"
        
        self.root.configure(bg=self.BG_COLOR)

        self.q_index = 0
        self.score = 0
        self.var = tk.IntVar()
        self.answered = False
        self.time_left = 30

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="💡 Тест на тему: Модернізація ПК", font=("Segoe UI", 20, "bold"),
                         bg=self.BG_COLOR, fg=self.TITLE_COLOR)
        title.pack(pady=20)

        self.progress_label = tk.Label(self.root, text="", font=("Segoe UI", 12),
                                       bg=self.BG_COLOR, fg=self.TEXT_COLOR)
        self.progress_label.pack()

        self.progressbar = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progressbar.pack(pady=5)

        self.timer_label = tk.Label(self.root, text="", font=("Segoe UI", 12, "italic"),
                                    bg=self.BG_COLOR, fg="#ff6666")
        self.timer_label.pack()

        self.frame = tk.Frame(self.root, bg=self.FRAME_BG_COLOR, bd=2, relief="groove")
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.question_label = tk.Label(self.frame, text="", wraplength=600, font=("Segoe UI", 14, "bold"),
                                       bg=self.FRAME_BG_COLOR, fg=self.TEXT_COLOR, justify="center")
        self.question_label.pack(pady=20, padx=10)

        self.options = []
        for i in range(4):
            rb = tk.Radiobutton(self.frame, text="", variable=self.var, value=i,
                                font=("Segoe UI", 12), bg=self.OPTION_BG, fg=self.TEXT_COLOR,
                                activebackground=self.OPTION_HOVER_BG, activeforeground=self.TEXT_COLOR,
                                anchor="w", justify="left", selectcolor=self.BUTTON_BG,
                                indicatoron=0, width=60, padx=10, pady=5, bd=3, relief="raised")
            rb.pack(pady=5, padx=20, ipady=5)
            self.options.append(rb)

        self.feedback_label = tk.Label(self.root, text="", font=("Segoe UI", 12, "italic"),
                                       bg=self.BG_COLOR, fg=self.TEXT_COLOR)
        self.feedback_label.pack(pady=10)

        self.next_button = tk.Button(self.root, text="✅ Перевірити", command=self.check_answer,
                                     font=("Segoe UI", 12, "bold"), bg=self.BUTTON_BG, fg="white",
                                     activebackground=self.BUTTON_ACTIVE_BG, activeforeground="white", 
                                     relief="raised", bd=3, padx=10, pady=5)
        self.next_button.pack(pady=10)

        self.load_question()
        self.update_timer()

    def load_question(self):
        self.var.set(-1)
        self.feedback_label.config(text="")
        self.answered = False
        self.time_left = 30
        self.next_button.config(text="✅ Перевірити", bg=self.BUTTON_BG, state="normal")

        q = questions[self.q_index]
        self.question_label.config(text=f"{self.q_index + 1}. {q['question']}")
        self.progress_label.config(text=f"Питання {self.q_index + 1} з {len(questions)}")
        self.progressbar["value"] = (self.q_index + 1) * (100 / len(questions))

        for i, option in enumerate(q["options"]):
            self.options[i].config(text=option, state="normal", bg=self.OPTION_BG, fg=self.TEXT_COLOR,
                                   activebackground=self.OPTION_HOVER_BG)

    def update_timer(self):
        if not self.answered:
            self.timer_label.config(text=f"⏳ Час: {self.time_left} с")
            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.feedback_label.config(text="❌ Час вийшов!", fg=self.INCORRECT_FG)
                self.disable_options()
                self.next_button.config(text="Продовжити ➔", bg=self.BUTTON_ACTIVE_BG)
                self.answered = True

    def check_answer(self):
        if self.answered:
            self.next_question()
            return

        selected = self.var.get()
        if selected == -1:
            messagebox.showwarning("Увага", "Оберіть відповідь перед тим, як продовжити.")
            return
        
        self.answered = True
        self.disable_options()
        self.next_button.config(text="Продовжити ➔", bg=self.BUTTON_ACTIVE_BG)
        
        correct_index = questions[self.q_index]["correct"]

        if selected == correct_index:
            self.score += 1
            self.feedback_label.config(text="✅ Правильно!", fg=self.CORRECT_FG)
            self.options[selected].config(bg=self.CORRECT_BG, activebackground=self.CORRECT_BG)
        else:
            correct_text = questions[self.q_index]['options'][correct_index]
            self.feedback_label.config(text=f"❌ Неправильно. Правильна відповідь: {correct_text}", fg=self.INCORRECT_FG)
            self.options[selected].config(bg=self.INCORRECT_BG, activebackground=self.INCORRECT_BG)
            self.options[correct_index].config(bg=self.CORRECT_BG, activebackground=self.CORRECT_BG)

    def disable_options(self):
        for rb in self.options:
            rb.config(state="disabled")

    def next_question(self):
        self.q_index += 1
        if self.q_index < len(questions):
            self.load_question()
            self.update_timer()
        else:
            messagebox.showinfo("Тест завершено!", f"Ваш результат: {self.score} з {len(questions)} правильних відповідей.")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=10, troughcolor='#4d1a1a', background='#ff4444')
    app = QuizApp(root)
    root.mainloop()