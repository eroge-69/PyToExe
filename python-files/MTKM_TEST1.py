import tkinter as tk
from tkinter import messagebox, ttk
import time
import random

class VariantSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор варианта теста")
        self.root.geometry("400x200")
        
        self.label = tk.Label(root, text="Выберите вариант теста:", font=("Arial", 16))
        self.label.pack(pady=30)
        
        self.variant_frame = tk.Frame(root)
        self.variant_frame.pack(pady=20)
        
        self.variant1_btn = tk.Button(self.variant_frame, text="Вариант 1", 
                                     command=self.select_variant1, width=15, height=2)
        self.variant1_btn.pack(side="left", padx=20)
        
        self.variant2_btn = tk.Button(self.variant_frame, text="Вариант 2", 
                                     command=self.select_variant2, width=15, height=2)
        self.variant2_btn.pack(side="left", padx=20)
        
        self.selected_variant = None
    
    def select_variant1(self):
        self.selected_variant = 1
        self.root.destroy()
    
    def select_variant2(self):
        self.selected_variant = 2
        self.root.destroy()

class TestApp:
    def __init__(self, root, variant):
        self.root = root
        self.variant = variant
        self.root.title(f"Входной контроль по материаловедению - Вариант {variant}")
        self.root.geometry("900x650")
        
        # Все вопросы (50 вопросов)
        self.all_questions = [
            # Вариант 1 (25 вопросов)
            {
                "question": "1. Что откладывается по оси ординат диаграммы растяжения?",
                "options": ["P кгс", "∆ℓ мм", "F₀ мм"],
                "answer": 0
            },
            {
                "question": "2. Какая длина образца называется расчетной длиной?",
                "options": ["ℓ₁", "ℓ₂", "ℓ₀"],
                "answer": 2
            },
            {
                "question": "3. Какая из приведенных характеристик оценивает пластичные свойства металлов?",
                "options": ["σ₀,₂", "ψ", "σв"],
                "answer": 1
            },
            {
                "question": "4. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σв", "σпц", "σ₀,₂"],
                "answer": 1
            },
            {
                "question": "5. Какая из приведенных характеристик возрастает с увеличением содержания углерода в стали?",
                "options": ["δ", "σ₀,₂", "Ψ"],
                "answer": 1
            },
            {
                "question": "6. С повышением содержания углерода в стали σв:",
                "options": ["Увеличивается", "Не изменяется", "Уменьшается"],
                "answer": 0
            },
            {
                "question": "7. По какой формуле определяют длину плоского длинного разрывного образца?",
                "options": ["ℓ₀ = 5,65√F₀", "ℓ₀ = 11,3√F₀", "ℓ₀ = 10d"],
                "answer": 1
            },
            {
                "question": "8. Какая из приведенных характеристик оценивает пластические свойства металла?",
                "options": ["σ₀,₂", "σпц", "Ψ"],
                "answer": 2
            },
            {
                "question": "9. Какая диаграмма растяжения соответствует малоуглеродистой стали?",
                "options": ["Диаграмма с площадкой текучести", "Диаграмма без площадки текучести", "Обе диаграммы"],
                "answer": 0
            },
            {
                "question": "10. Где происходит начало образования шейки на образце на диаграмме растяжения?",
                "options": ["В точке максимальной нагрузки", "В точке предела текучести", "В точке предела пропорциональности"],
                "answer": 0
            },
            {
                "question": "11. Что откладывается по оси абсцисс диаграммы растяжения?",
                "options": ["∆ℓ мм", "F мм²", "P кгс"],
                "answer": 0
            },
            {
                "question": "12. Какая из приведенных величин уменьшается с увеличением содержания углерода в стали?",
                "options": ["δ", "σ₀,₂", "σпц"],
                "answer": 0
            },
            {
                "question": "13. Какие показатели характеризуют пластические свойства металлов?",
                "options": ["δ; Ψ", "σ₀,₂; σв", "σпц; σ₀,₀₅"],
                "answer": 0
            },
            {
                "question": "14. По какой формуле определяется расчетная длина короткого плоского образца?",
                "options": ["ℓ₀ = 5d", "ℓ₀ = 5,65√F₀", "ℓ₀ = 11,3√F₀"],
                "answer": 2
            },
            {
                "question": "15. По какой формуле определяется остаточная деформация для вычисления условного предела текучести?",
                "options": ["δ = ∆ℓ / ℓ₀ × 100%", "∆ℓ = ℓк - ℓ₀", "∆ℓ = 0,2% ℓ₀"],
                "answer": 2
            },
            {
                "question": "16. Какая из приведенных характеристик уменьшается с увеличением содержания углерода в стали?",
                "options": ["δ₅", "σ₀,₂", "σв"],
                "answer": 0
            },
            {
                "question": "17. Как определяется абсолютное удлинение образца по диаграмме растяжения?",
                "options": ["По оси нагрузки P", "По оси удлинения ∆ℓ", "По расчетной длине"],
                "answer": 1
            },
            {
                "question": "18. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σпц", "σв", "σ₀,₂"],
                "answer": 0
            },
            {
                "question": "19. Какая из приведенных величин уменьшается с увеличением содержания углерода в стали?",
                "options": ["Ψ", "σ₀,₂", "σв"],
                "answer": 0
            },
            {
                "question": "20. По какой формуле определяется остаточная деформация для вычисления условного предела текучести?",
                "options": ["∆ℓ = ℓк - ℓ₀", "∆ℓ = 0,2% ℓ₀", "δ = ∆ℓ / ℓ₀ × 100%"],
                "answer": 1
            },
            {
                "question": "21. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["700 МПа", "500 МПа", "360 МПа"],
                "answer": 0
            },
            {
                "question": "22. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σ₀,₂", "σпц", "σв"],
                "answer": 1
            },
            {
                "question": "23. По какой формуле определяют длину плоского длинного разрывного образца?",
                "options": ["ℓ₀ = 5,65√F₀", "ℓ₀ = 10d", "ℓ₀ = 11,3√F₀"],
                "answer": 2
            },
            {
                "question": "24. В какой стали (по данным испытания на растяжение) меньше углерода?",
                "options": ["δ₅ = 10%", "δ₅ = 19%", "δ₅ = 28%"],
                "answer": 2
            },
            {
                "question": "25. Где происходит начало образования шейки на образце по диаграмме растяжения?",
                "options": ["В точке предела упругости", "В точке предела текучести", "В точке максимальной нагрузки"],
                "answer": 2
            },
            
            # Вариант 2 (25 вопросов)
            {
                "question": "26. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σ₀,₂", "σв", "δ₅"],
                "answer": 0
            },
            {
                "question": "27. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["σ₀,₂ = 450 МПа", "σ₀,₂ = 340 МПа", "σ₀,₂ = 250 МПа"],
                "answer": 0
            },
            {
                "question": "28. Какая длина образца называется расчетной длиной?",
                "options": ["ℓ₁", "ℓ₂", "ℓ₀"],
                "answer": 2
            },
            {
                "question": "29. С повышением содержания углерода в стали σв:",
                "options": ["Не изменяется", "Уменьшается", "Увеличивается"],
                "answer": 2
            },
            {
                "question": "30. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["Ψ = 30%", "Ψ = 45%", "Ψ = 60%"],
                "answer": 0
            },
            {
                "question": "31. Какая диаграмма растяжения соответствует высокоуглеродистой стали?",
                "options": ["Диаграмма с площадкой текучести", "Диаграмма без площадки текучести", "Обе диаграммы"],
                "answer": 1
            },
            {
                "question": "32. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σв", "σпц", "σ₀,₂"],
                "answer": 1
            },
            {
                "question": "33. Какая из приведенных характеристик возрастает с увеличением содержания углерода в стали?",
                "options": ["δ", "σ₀,₂", "Ψ"],
                "answer": 1
            },
            {
                "question": "34. Как определить абсолютное удлинение образца по диаграмме растяжения?",
                "options": ["По оси нагрузки P", "По оси удлинения ∆ℓ", "По диаметру образца"],
                "answer": 1
            },
            {
                "question": "35. Какая из приведенных диаграмм растяжения соответствует высокоуглеродистой стали?",
                "options": ["Диаграмма с выраженной площадкой текучести", "Диаграмма без площадки текучести", "Диаграмма с большим удлинением"],
                "answer": 1
            },
            {
                "question": "36. Что откладывается по оси абсцисс диаграммы растяжения?",
                "options": ["P кгс", "∆ℓ мм", "F мм²"],
                "answer": 1
            },
            {
                "question": "37. По какой формуле определяется остаточная деформация для вычисления условного предела текучести?",
                "options": ["δ = ∆ℓ / ℓ₀ × 100%", "∆ℓ = ℓк - ℓ₀", "∆ℓ = 0,2% ℓ₀"],
                "answer": 2
            },
            {
                "question": "38. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["Ψ = 30%", "Ψ = 45%", "Ψ = 60%"],
                "answer": 0
            },
            {
                "question": "39. Как определить абсолютное удлинение образца по диаграмме растяжения?",
                "options": ["По нагрузке P", "По удлинению ∆ℓ", "По расчетной длине"],
                "answer": 1
            },
            {
                "question": "40. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["σ₀,₂ = 450 МПа", "σ₀,₂ = 340 МПа", "σ₀,₂ = 250 МПа"],
                "answer": 0
            },
            {
                "question": "41. Какая из приведенных характеристик оценивает упругие свойства металла?",
                "options": ["σпц", "σв", "σ₀,₂"],
                "answer": 0
            },
            {
                "question": "42. Какая из приведенных характеристик возрастает с увеличением содержания углерода в стали?",
                "options": ["δ", "σ₀,₂", "Ψ"],
                "answer": 1
            },
            {
                "question": "43. Как определить абсолютное удлинение образца по диаграмме растяжения?",
                "options": ["По оси P", "По оси ∆ℓ", "По площади поперечного сечения"],
                "answer": 1
            },
            {
                "question": "44. Какая из приведенных диаграмм растяжения соответствует высокоуглеродистой стали?",
                "options": ["С площадкой текучести", "Без площадки текучести", "С большим равномерным удлинением"],
                "answer": 1
            },
            {
                "question": "45. Что откладывается по оси абсцисс диаграммы растяжения?",
                "options": ["P кгс", "∆ℓ мм", "F мм²"],
                "answer": 1
            },
            {
                "question": "46. По какой формуле определяется остаточная деформация для вычисления условного предела текучести?",
                "options": ["δ = ∆ℓ / ℓ₀ × 100%", "∆ℓ = ℓк - ℓ₀", "∆ℓ = 0,2% ℓ₀"],
                "answer": 2
            },
            {
                "question": "47. В какой стали (по данным испытания на растяжение) больше углерода?",
                "options": ["Ψ = 30%", "Ψ = 45%", "Ψ = 60%"],
                "answer": 0
            },
            {
                "question": "48. Как определить абсолютное удлинение образца по диаграмме растяжения?",
                "options": ["По максимальной нагрузке", "По удлинению ∆ℓ", "По расчетной длине"],
                "answer": 1
            },
            {
                "question": "49. В какой стали (по данных испытания на растяжение) больше углерода?",
                "options": ["σ₀,₂ = 450 МПа", "σ₀,₂ = 340 МПа", "σ₀,₂ = 250 МПа"],
                "answer": 0
            },
            {
                "question": "50. Какая длина образца называется расчетной длиной?",
                "options": ["Начальная длина", "Конечная длина", "ℓ₀"],
                "answer": 2
            }
        ]
        
        # Выбираем вопросы в зависимости от варианта
        if variant == 1:
            self.questions = self.all_questions[0:25]  # Вопросы 1-25
        else:
            self.questions = self.all_questions[25:50]  # Вопросы 26-50
        
        self.current_question = 0
        self.user_answers = [None] * len(self.questions)
        self.skipped = []
        self.start_time = time.time()
        self.time_limit = 15 * 60  # 15 минут в секундах
        
        self.create_widgets()
        self.show_question()
        self.update_timer()

    def create_widgets(self):
        # Фрейм для таймера и информации о варианте
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10, fill="x")
        
        self.variant_label = tk.Label(self.top_frame, text=f"Вариант {self.variant}", 
                                     font=("Arial", 12, "bold"))
        self.variant_label.pack(side="left", padx=20)
        
        self.timer_label = tk.Label(self.top_frame, text="Осталось времени: 15:00", 
                                   font=("Arial", 12), fg="red")
        self.timer_label.pack(side="right", padx=20)
        
        # Фрейм для вопроса
        self.question_frame = tk.Frame(self.root)
        self.question_frame.pack(pady=20, fill="both", expand=True, padx=20)
        
        self.question_label = tk.Label(self.question_frame, text="", 
                                      font=("Arial", 12, "bold"), wraplength=800, justify="left")
        self.question_label.pack(pady=15, anchor="w")
        
        # Переменная для хранения выбранного ответа
        self.answer_var = tk.IntVar(value=-1)
        
        # Фрейм для вариантов ответа
        self.answers_frame = tk.Frame(self.question_frame)
        self.answers_frame.pack(pady=15, fill="both", expand=True)
        
        self.answer_buttons = []
        for i in range(3):
            btn = tk.Radiobutton(self.answers_frame, text="", variable=self.answer_var, 
                                value=i, font=("Arial", 11), wraplength=750, justify="left")
            btn.pack(anchor="w", pady=8, padx=20)
            self.answer_buttons.append(btn)
        
        # Фрейм для кнопок навигации
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=20)
        
        self.prev_btn = tk.Button(self.nav_frame, text="← Предыдущий", command=self.prev_question,
                                 font=("Arial", 10), width=12)
        self.prev_btn.pack(side="left", padx=5)
        
        self.skip_btn = tk.Button(self.nav_frame, text="Пропустить", command=self.skip_question,
                                 font=("Arial", 10), width=12)
        self.skip_btn.pack(side="left", padx=5)
        
        self.next_btn = tk.Button(self.nav_frame, text="Следующий →", command=self.next_question,
                                 font=("Arial", 10), width=12)
        self.next_btn.pack(side="left", padx=5)
        
        self.finish_btn = tk.Button(self.nav_frame, text="Завершить тест", command=self.finish_test,
                                   font=("Arial", 10, "bold"), bg="#ff6b6b", fg="white", width=15)
        self.finish_btn.pack(side="left", padx=20)
        
        # Статусная строка
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x", pady=10)
        
        self.progress = ttk.Progressbar(self.status_frame, orient="horizontal", 
                                       length=400, mode="determinate")
        self.progress.pack(pady=5)
        
        self.status_label = tk.Label(self.status_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def show_question(self):
        if 0 <= self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            self.question_label.config(text=q["question"])
            
            for i, btn in enumerate(self.answer_buttons):
                btn.config(text=f"{chr(65+i)}) {q['options'][i]}")
            
            # Восстановить предыдущий ответ если есть
            if self.user_answers[self.current_question] is not None:
                self.answer_var.set(self.user_answers[self.current_question])
            else:
                self.answer_var.set(-1)
            
            self.update_status()
            
            # Обновить состояние кнопок навигации
            self.prev_btn.config(state="normal" if self.current_question > 0 else "disabled")
            self.next_btn.config(state="normal" if self.current_question < len(self.questions) - 1 else "disabled")

    def next_question(self):
        self.save_answer()
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()

    def prev_question(self):
        self.save_answer()
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def skip_question(self):
        if self.current_question not in self.skipped:
            self.skipped.append(self.current_question)
        self.save_answer()
        # Переходим к следующему вопросу, если он есть
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            # Если это последний вопрос, переходим к первому пропущенному
            if self.skipped:
                self.current_question = self.skipped[0]
                self.show_question()

    def save_answer(self):
        if self.answer_var.get() != -1:
            self.user_answers[self.current_question] = self.answer_var.get()
            if self.current_question in self.skipped:
                self.skipped.remove(self.current_question)

    def update_status(self):
        answered = sum(1 for ans in self.user_answers if ans is not None)
        total = len(self.questions)
        progress_value = (answered / total) * 100
        
        self.progress["value"] = progress_value
        
        status = f"Вопрос {self.current_question + 1} из {total} | Ответов: {answered}/{total}"
        if self.skipped:
            status += f" | Пропущено: {len(self.skipped)}"
        
        self.status_label.config(text=status)

    def update_timer(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        # Меняем цвет в зависимости от оставшегося времени
        if minutes < 2:
            color = "red"
        elif minutes < 5:
            color = "orange"
        else:
            color = "black"
        
        self.timer_label.config(text=f"Осталось времени: {minutes:02d}:{seconds:02d}", fg=color)
        
        if remaining <= 0:
            self.force_finish = True
            self.finish_test()
        else:
            self.root.after(1000, self.update_timer)

    def finish_test(self):
        self.save_answer()
        
        # Проверка на неотвеченные вопросы
        unanswered = [i+1 for i, ans in enumerate(self.user_answers) if ans is None]
        if unanswered and not hasattr(self, 'force_finish'):
            response = messagebox.askyesno(
                "Неотвеченные вопросы", 
                f"Вы не ответили на вопросы: {', '.join(map(str, unanswered))}\n"
                "Вы уверены, что хотите завершить тест?"
            )
            if not response:
                return
        
        self.show_results()

    def show_results(self):
        # Создаем новое окно для результатов
        results_window = tk.Toplevel(self.root)
        results_window.title("Результаты теста")
        results_window.geometry("800x600")
        
        # Подсчет результатов
        correct = 0
        total = len(self.questions)
        
        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            if user_ans == q["answer"]:
                correct += 1
        
        percentage = (correct / total) * 100
        
        # Определение оценки
        if percentage < 50:
            grade = "2 (Неудовлетворительно)"
            grade_color = "red"
        elif percentage < 75:
            grade = "3 (Удовлетворительно)"
            grade_color = "orange"
        elif percentage < 95:
            grade = "4 (Хорошо)"
            grade_color = "blue"
        else:
            grade = "5 (Отлично)"
            grade_color = "green"
        
        # Заголовок с результатами
        result_frame = tk.Frame(results_window)
        result_frame.pack(pady=15, fill="x", padx=20)
        
        result_label = tk.Label(result_frame, 
                               text=f"РЕЗУЛЬТАТЫ ТЕСТА (Вариант {self.variant})",
                               font=("Arial", 16, "bold"))
        result_label.pack(pady=10)
        
        stats_text = f"Правильных ответов: {correct} из {total}\n"
        stats_text += f"Процент выполнения: {percentage:.1f}%\n"
        stats_text += f"Оценка: {grade}"
        
        stats_label = tk.Label(result_frame, text=stats_text, font=("Arial", 14),
                             justify="center", fg=grade_color)
        stats_label.pack(pady=10)
        
        # Фрейм для детализации
        details_frame = tk.Frame(results_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Создаем treeview для отображения результатов
        tree_scroll = tk.Scrollbar(details_frame)
        tree_scroll.pack(side="right", fill="y")
        
        tree = ttk.Treeview(details_frame, columns=("Question", "YourAnswer", "Correct", "Status"), 
                           show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)
        
        tree.heading("Question", text="Вопрос")
        tree.heading("YourAnswer", text="Ваш ответ")
        tree.heading("Correct", text="Правильный ответ")
        tree.heading("Status", text="Статус")
        
        tree.column("Question", width=400)
        tree.column("YourAnswer", width=150)
        tree.column("Correct", width=150)
        tree.column("Status", width=100)
        
        # Добавляем данные
        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            question_short = f"{i+1}. {q['question'][:50]}..." if len(q['question']) > 50 else f"{i+1}. {q['question']}"
            
            if user_ans is None:
                user_answer_text = "Не отвечен"
                status = "Пропущен"
                status_color = "orange"
            else:
                user_answer_text = f"{chr(65+user_ans)}) {q['options'][user_ans]}"
                correct_answer_text = f"{chr(65+q['answer'])}) {q['options'][q['answer']]}"
                
                if user_ans == q["answer"]:
                    status = "✓ Правильно"
                    status_color = "green"
                else:
                    status = "✗ Неправильно"
                    status_color = "red"
            
            tree.insert("", "end", values=(
                question_short, 
                user_answer_text, 
                correct_answer_text, 
                status
            ))
        
        tree.pack(fill="both", expand=True)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(results_window)
        button_frame.pack(pady=15)
        
        # Кнопка справочных материалов для тех, кто получил 2
        if percentage < 50:
            materials_btn = tk.Button(
                button_frame, 
                text="Справочные материалы", 
                command=lambda: self.show_materials(results_window),
                font=("Arial", 11),
                bg="#4CAF50",
                fg="white",
                width=20
            )
            materials_btn.pack(side="left", padx=10)
        
        close_btn = tk.Button(button_frame, text="Закрыть", 
                             command=self.root.destroy,
                             font=("Arial", 11),
                             width=15)
        close_btn.pack(side="left", padx=10)

    def show_materials(self, parent_window):
        materials_window = tk.Toplevel(parent_window)
        materials_window.title("Справочные материалы")
        materials_window.geometry("700x500")
        
        # Создаем Notebook (вкладки)
        notebook = ttk.Notebook(materials_window)
        
        # Вкладка 1: Основные понятия
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Основные понятия")
        
        text1 = tk.Text(tab1, wrap="word", font=("Arial", 11), padx=10, pady=10)
        text1.insert("1.0", """ОСНОВНЫЕ ПОНЯТИЯ МАТЕРИАЛОВЕДЕНИЯ

1. Механические свойства материалов:
   - Прочность - способность материала сопротивляться разрушению
   - Пластичность - способность материала деформироваться без разрушения
   - Упругость - способность материала восстанавливать форму после снятия нагрузки

2. Основные характеристики:
   - σ (сигма) - нормальное напряжение [МПа]
   - ε (эпсилон) - относительная деформация
   - δ (дельта) - относительное удлинение [%]
   - ψ (пси) - относительное сужение [%]

3. Критические точки диаграммы растяжения:
   - σпц - предел пропорциональности
   - σуп - предел упругости  
   - σт - предел текучести
   - σв - временное сопротивление (предел прочности)
   - σ0,2 - условный предел текучести""")
        text1.config(state="disabled")
        text1.pack(fill="both", expand=True)
        
        # Вкладка 2: Диаграмма растяжения
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Диаграмма растяжения")
        
        text2 = tk.Text(tab2, wrap="word", font=("Arial", 11), padx=10, pady=10)
        text2.insert("1.0", """ДИАГРАММА РАСТЯЖЕНИЯ

Оси диаграммы:
- По оси ординат откладывается НАГРУЗКА (P) [кгс, Н]
- По оси абсцисс откладывается УДЛИНЕНИЕ (Δℓ) [мм]

Участки диаграммы:
1. Упругая деформация (до σуп)
2. Пластическая деформация
3. Образование шейки (максимальная нагрузка)
4. Разрушение

Характеристики диаграммы:
- Площадка текучести - характерна для малоуглеродистой стали
- Плавный переход - характерен для высокоуглеродистой стали
- Максимальная нагрузка соответствует σв
- Начало образования шейки - в точке максимальной нагрузки""")
        text2.config(state="disabled")
        text2.pack(fill="both", expand=True)
        
        # Вкладка 3: Влияние углерода
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Влияние углерода")
        
        text3 = tk.Text(tab3, wrap="word", font=("Arial", 11), padx=10, pady=10)
        text3.insert("1.0", """ВЛИЯНИЕ УГЛЕРОДА НА СВОЙСТВА СТАЛИ

С увеличением содержания углерода в стали:

УВЕЛИЧИВАЮТСЯ:
- Предел прочности (σв)
- Предел текучести (σт, σ0,2)
- Твердость (HB, HRC)

УМЕНЬШАЮТСЯ:
- Относительное удлинение (δ)
- Относительное сужение (ψ)
- Ударная вязкость (KCU)

ИЗМЕНЯЕТСЯ:
- Характер диаграммы растяжения
  (исчезает площадка текучести)

Практические следствия:
- Низкоуглеродистые стали (до 0,25% C) - высокая пластичность
- Среднеуглеродистые стали (0,25-0,6% C) - баланс прочности и пластичности
- Высокоуглеродистые стали (свыше 0,6% C) - высокая прочность, низкая пластичность""")
        text3.config(state="disabled")
        text3.pack(fill="both", expand=True)
        
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        close_btn = tk.Button(materials_window, text="Закрыть", 
                             command=materials_window.destroy,
                             font=("Arial", 11))
        close_btn.pack(pady=10)

def main():
    # Сначала выбираем вариант
    root = tk.Tk()
    variant_selector = VariantSelection(root)
    root.mainloop()
    
    if variant_selector.selected_variant:
        # Запускаем тест с выбранным вариантом
        root = tk.Tk()
        app = TestApp(root, variant_selector.selected_variant)
        root.mainloop()

if __name__ == "__main__":
    main()