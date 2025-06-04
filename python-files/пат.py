import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

# --- Test Data ---
QUESTIONS = [
    {"type": "single", "question": "Психология — это наука о ...", "options": ["человеческой душе", "животных", "растениях", "технике"], "answer": 0},
    {"type": "single", "question": "Кто считается основателем научной психологии?", "options": ["Зигмунд Фрейд", "Иван Павлов", "Вильгельм Вундт", "Карл Юнг"], "answer": 2},
    {"type": "single", "question": "Эмпатия — это способность ...", "options": ["понимать эмоции других", "читать книги", "быстро бегать", "играть на музыкальных инструментах"], "answer": 0},
    {"type": "single", "question": "Когнитивная психология изучает ...", "options": ["мышление и память", "физическую силу", "цвет глаз", "рост человека"], "answer": 0},
    {"type": "single", "question": "Как называется психологический эксперимент с собакой и звонком?", "options": ["Эксперимент Вундта", "Эксперимент Павлова", "Эксперимент Фрейда", "Эксперимент Милгрэма"], "answer": 1},
    {"type": "multiple", "question": "Какие из перечисленных — методы психологии?", "options": ["Наблюдение", "Эксперимент", "Гадание", "Анкетирование"], "answer": [0, 1, 3]},
    {"type": "multiple", "question": "Какие чувства относятся к базовым?", "options": ["Радость", "Грусть", "Скука", "Страх"], "answer": [0, 1, 3]},
    {"type": "multiple", "question": "Что изучает психология развития?", "options": ["Изменения личности с возрастом", "Рост волос", "Формирование привычек", "Пищеварение"], "answer": [0, 2]},
    {"type": "multiple", "question": "Что характерно для стресса?", "options": ["Тревога", "Повышенная энергия", "Расслабление", "Раздражительность"], "answer": [0, 1, 3]},
    {"type": "multiple", "question": "Как можно справиться с тревогой?", "options": ["Медитация", "Алкоголь", "Физическая активность", "Здоровый сон"], "answer": [0, 2, 3]},
    {"type": "input", "question": "Как называется наука о поведении и психике человека?", "answer": "психология"},
    {"type": "input", "question": "Какое имя носит основатель психоанализа?", "answer": "фрейд"},
    {"type": "input", "question": "Перечислите одну из функций сознания.", "answer": "контроль"},
    {"type": "input", "question": "Какое главное чувство противоположно страху?", "answer": "смелость"},
    {"type": "input", "question": "Как называется способность понимать другого человека?", "answer": "эмпатия"}
]

INSTRUCTION_TEXT = (
    "Добро пожаловать в тест по психологии!\n\n"
    "Всего 15 вопросов:\n"
    "- 5 с одним вариантом ответа\n"
    "- 5 с несколькими вариантами ответа\n"
    "- 5 вписываемых\n\n"
    "У вас есть 15 минут\n"
    "Перед ответом хорошо подумайте и только потом отвечайте.\n"
    "В конце нажмите 'Завершить' для получения оценки.\n"
    "Удачи!"
)

BG_GRADIENT_TOP = "#d6e8fa"
BG_GRADIENT_BOTTOM = "#f0f4f9"
CARD_BG = "#ffffff"
PRIMARY = "#337ab7"
SECONDARY = "#5bc0de"
BTN_BG = "#337ab7"
BTN_FG = "#ffffff"
ACTIVE_BG = "#265a88"
ENTRY_BG = "#f7fafc"
RADIO_BG = "#f7fafc"
CHECK_BG = "#f7fafc"
HOVER_BG = "#e0e8f5"
HOVER_FG = "#114477"
SELECT_BG = "#b8d1f3"
SELECT_FG = "#09365a"
FINAL_BG = "#e7eef7"

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)
        self.after(1, self.lower)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        (r1, g1, b1) = self.winfo_rgb(self.color1)
        (r2, g2, b2) = self.winfo_rgb(self.color2)
        r_ratio = float(r2 - r1) / limit if limit else 0
        g_ratio = float(g2 - g1) / limit if limit else 0
        b_ratio = float(b2 - b1) / limit if limit else 0
        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%04x%04x%04x" % (nr, ng, nb)
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

class ModernTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Психологический тест")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        try:
            self.root.iconbitmap('psychology.ico')
        except:
            pass

        self.gradient = GradientFrame(root, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM)
        self.gradient.pack(fill="both", expand=True)
        self.gradient.bind("<Configure>", self._on_resize)
        self.root.after(1, self.gradient.lower)

        self.init_state()
        self.create_widgets()
        self.run_timer()
        self.show_instructions()

    def _on_resize(self, event):
        self.gradient._draw_gradient()

    def init_state(self):
        self.timer_seconds = 15 * 60
        self.questions_order = list(range(len(QUESTIONS)))
        random.shuffle(self.questions_order)
        self.questions = []
        self.answers = [None] * len(QUESTIONS)
        self.option_orders = [None] * len(QUESTIONS)
        self.last_selected = [None] * len(QUESTIONS)
        for idx in self.questions_order:
            q = dict(QUESTIONS[idx])
            if q["type"] in ("single", "multiple"):
                orig_options = list(q["options"])
                option_idx = list(range(len(orig_options)))
                random.shuffle(option_idx)
                q["options"] = [orig_options[i] for i in option_idx]
                if q["type"] == "single":
                    q["answer"] = option_idx.index(q["answer"])
                else:
                    q["answer"] = [option_idx.index(i) for i in q["answer"]]
                self.option_orders[self.questions_order.index(idx)] = option_idx
            self.questions.append(q)
        self.current_question = 0
        self.test_started = False

    def create_widgets(self):
        self.header = tk.Label(self.root, text="Психологический тест", font=("Helvetica", 22, "bold"),
                               bg=BG_GRADIENT_TOP, fg=PRIMARY)
        self.header.place(relx=0.5, y=40, anchor="center")

        self.timer_label = tk.Label(self.root, text="", font=("Helvetica", 14, "bold"),
                                   bg=BG_GRADIENT_TOP, fg=SECONDARY)
        self.timer_label.place(relx=0.5, y=85, anchor="center")

        self.card = tk.Frame(self.root, bg=CARD_BG, bd=0, relief="groove", highlightthickness=1, highlightbackground="#e5e9f2")
        self.card.place(relx=0.5, rely=0.53, anchor="center", relwidth=0.82, relheight=0.72)

        self.nav_frame = tk.Frame(self.root, bg=BG_GRADIENT_BOTTOM)
        self.nav_frame.place(relx=0.5, rely=0.96, anchor="s", relwidth=0.6, height=48)

        self.prev_btn = tk.Button(self.nav_frame, text="⟵ Назад", font=("Helvetica", 13), command=self.prev_question,
                                  bg=BTN_BG, fg=BTN_FG, activebackground=ACTIVE_BG, activeforeground=BTN_FG, bd=0,
                                  padx=24, pady=8, cursor="hand2")
        self.next_btn = tk.Button(self.nav_frame, text="Вперед ⟶", font=("Helvetica", 13), command=self.next_question,
                                  bg=BTN_BG, fg=BTN_FG, activebackground=ACTIVE_BG, activeforeground=BTN_FG, bd=0,
                                  padx=24, pady=8, cursor="hand2")
        self.finish_btn = tk.Button(self.nav_frame, text="Завершить", font=("Helvetica", 13, "bold"), command=self.finish_test,
                                    bg=SECONDARY, fg=BTN_FG, activebackground=PRIMARY, activeforeground=BTN_FG, bd=0,
                                    padx=24, pady=8, cursor="hand2")

        self.prev_btn.pack(side="left", padx=7)
        self.next_btn.pack(side="left", padx=7)
        self.finish_btn.pack(side="left", padx=7)  # Always show the finish button

        self.widgets = {}
        self.update_nav_buttons()

    def show_instructions(self):
        for widget in self.card.winfo_children():
            widget.destroy()

        self.timer_label.config(text=f"⏰ Время теста: 15:00")

        instruction_lbl = tk.Label(self.card, text=INSTRUCTION_TEXT, font=("Helvetica", 16),
                                 wraplength=700, justify="center", bg=CARD_BG, fg="#333333")
        instruction_lbl.pack(pady=50, padx=20, expand=True)

        start_btn = tk.Button(self.card, text="Начать тест", font=("Helvetica", 16, "bold"), 
                             command=self.start_test, bg=SECONDARY, fg=BTN_FG, 
                             activebackground=PRIMARY, activeforeground=BTN_FG,
                             bd=0, padx=30, pady=12, cursor="hand2")
        start_btn.pack(pady=20)

        self.prev_btn.pack_forget()
        self.next_btn.pack_forget()
        self.finish_btn.pack_forget()

    def start_test(self):
        self.test_started = True
        self.show_question(self.current_question)
        self.update_nav_buttons()

    def run_timer(self):
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def update_timer(self):
        while self.timer_seconds > 0 and self.timer_running:
            if self.test_started:
                mins, secs = divmod(self.timer_seconds, 60)
                self.timer_label.config(text=f"⏰ Осталось времени: {mins:02}:{secs:02}")
            time.sleep(1)
            self.timer_seconds -= 1
        if self.timer_seconds <= 0 and self.timer_running and self.test_started:
            self.root.after(0, self.finish_test)

    def show_question(self, idx):
        for widget in self.card.winfo_children():
            widget.destroy()

        q = self.questions[idx]

        container = tk.Frame(self.card, bg=CARD_BG)
        container.pack(fill="both", expand=True)

        # Remove scrollbars completely for questions (so they never show)
        scrollable_frame = container

        # Вставляем пояснение для multiple-вопросов
        question_text = q['question']
        if q["type"] == "multiple":
            question_text += " (Выберите несколько вариантов ответа)"

        question_lbl = tk.Label(scrollable_frame, text=f"Вопрос {idx+1}: {question_text}",
                              font=("Helvetica", 16, "bold"), wraplength=700, justify="left", 
                              bg=CARD_BG, fg=PRIMARY, anchor="w")
        question_lbl.pack(anchor="nw", pady=(15, 12), padx=15, fill="x")

        self.widgets[idx] = []

        if q["type"] == "single":
            displayed_options = q["options"]
            answer = self.answers[idx]

            var = tk.IntVar(value=answer if answer is not None else -1)

            def on_select():
                selected = var.get()
                self.save_answer(idx, selected)

            for i, opt in enumerate(displayed_options):
                frame = tk.Frame(scrollable_frame, bg=CARD_BG)
                frame.pack(anchor="w", pady=7, padx=55, fill="x")

                rb = tk.Radiobutton(frame, variable=var, value=i, command=on_select,
                                   text=opt, font=("Helvetica", 14), bg=CARD_BG, 
                                   fg="#202124", selectcolor=RADIO_BG, activebackground=CARD_BG,
                                   activeforeground="#202124", highlightthickness=0,
                                   indicatoron=0, bd=2, relief="ridge", width=50,
                                   anchor="w", padx=10)
                rb.pack(side="left", fill="x", expand=True)
                rb.bind("<Enter>", lambda e, b=rb: e.widget.config(bg=HOVER_BG))
                rb.bind("<Leave>", lambda e, b=rb: e.widget.config(bg=CARD_BG))
                self.widgets[idx].append(rb)

        elif q["type"] == "multiple":
            displayed_options = q["options"]
            answer = self.answers[idx] or []
            vars = [tk.IntVar(value=1 if i in answer else 0) for i in range(len(displayed_options))]

            def on_toggle(i):
                current = self.answers[idx] or []
                new_sel = current.copy()
                if vars[i].get() == 1:
                    if i not in new_sel:
                        new_sel.append(i)
                else:
                    if i in new_sel:
                        new_sel.remove(i)
                self.save_answer(idx, new_sel)

            for i, opt in enumerate(displayed_options):
                frame = tk.Frame(scrollable_frame, bg=CARD_BG)
                frame.pack(anchor="w", pady=7, padx=55, fill="x")

                cb = tk.Checkbutton(frame, variable=vars[i], command=lambda i=i: on_toggle(i),
                                   text=opt, font=("Helvetica", 14), bg=CARD_BG, 
                                   fg="#202124", selectcolor=CHECK_BG, activebackground=CARD_BG,
                                   activeforeground="#202124", highlightthickness=0,
                                   indicatoron=0, bd=2, relief="ridge", width=50,
                                   anchor="w", padx=10)
                cb.pack(side="left", fill="x", expand=True)
                cb.bind("<Enter>", lambda e, b=cb: e.widget.config(bg=HOVER_BG))
                cb.bind("<Leave>", lambda e, b=cb: e.widget.config(bg=CARD_BG))
                self.widgets[idx].append(cb)

        elif q["type"] == "input":
            var = tk.StringVar(value=self.answers[idx] if self.answers[idx] is not None else "")
            frame = tk.Frame(scrollable_frame, bg=CARD_BG)
            frame.pack(anchor="w", pady=22, padx=55, fill="x")
            entry = tk.Entry(frame, textvariable=var, font=("Helvetica", 14), 
                           bg=ENTRY_BG, fg="#202124", highlightthickness=1, 
                           highlightbackground=SECONDARY, relief="flat", 
                           insertbackground=PRIMARY, width=50)
            entry.pack(side="left", fill="x", expand=True, ipady=6)
            entry.bind("<KeyRelease>", lambda e, idx=idx, var=var: self.save_answer(idx, var.get().strip()))
            self.widgets[idx].append(entry)

        self.update_nav_buttons()

    def save_answer(self, idx, value):
        self.answers[idx] = value

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question(self.current_question)
        self.update_nav_buttons()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question(self.current_question)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        if not self.test_started:
            return

        if self.current_question == 0:
            self.prev_btn.config(state="disabled")
        else:
            self.prev_btn.config(state="normal")

        if self.current_question < len(self.questions) - 1:
            self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="disabled")

        # Always show finish button and enable on any question
        self.finish_btn.config(state="normal")
        if not self.finish_btn.winfo_ismapped():
            self.finish_btn.pack(side="left", padx=7)

    def finish_test(self):
        self.timer_running = False
        score = self.calculate_score()
        rating = self.calculate_rating(score)
        percent = int(round(score / len(self.questions) * 100))
        self.show_final_screen(score, rating, percent)

    def calculate_score(self):
        score = 0
        for idx, q in enumerate(self.questions):
            ans = self.answers[idx]
            if q["type"] == "single":
                if ans == q["answer"]:
                    score += 1
            elif q["type"] == "multiple":
                if ans is not None and sorted(ans) == sorted(q["answer"]):
                    score += 1
            elif q["type"] == "input":
                if ans is not None and q["answer"].lower() in ans.lower():
                    score += 1
        return score

    def calculate_rating(self, score):
        if score >= 13:
            return "5"
        elif score >= 10:
            return "4"
        elif score >= 7:
            return "3"
        elif score >= 4:
            return "2"
        else:
            return "1"

    def restart_test(self):
        self.card.destroy()
        self.nav_frame.destroy()
        self.timer_label.place_forget()
        self.header.place_forget()
        self.init_state()
        self.create_widgets()
        self.timer_label.place(relx=0.5, y=85, anchor="center")
        self.header.place(relx=0.5, y=40, anchor="center")
        self.timer_seconds = 15 * 60
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        self.show_instructions()

    def show_final_screen(self, score, rating, percent):
        for widget in self.card.winfo_children():
            widget.destroy()
        self.prev_btn.pack_forget()
        self.next_btn.pack_forget()
        self.finish_btn.pack_forget()
        self.timer_label.place_forget()
        self.card.configure(bg=FINAL_BG)

        result_text = (
            f"Тест завершён!\n\n"
            f"Ваш результат: {score} из {len(self.questions)}\n"
            f"Оценка по 5-балльной шкале: {rating}\n"
            f"Процент правильных ответов: {percent}%\n"
        )

        colors = {
            "5": "#2ecc40", "4": "#ffdc00", "3": "#ffa500", "2": "#ff4136", "1": "#b10dc9"
        }
        color = colors.get(rating, PRIMARY)

        result_lbl = tk.Label(self.card, text=result_text, font=("Helvetica", 20, "bold"),
                             bg=FINAL_BG, fg=color, justify="center", wraplength=700, anchor="center")
        result_lbl.place(relx=0.5, rely=0.4, anchor="center")

        btn_frame = tk.Frame(self.card, bg=FINAL_BG)
        btn_frame.place(relx=0.5, rely=0.65, anchor="center")

        restart_btn = tk.Button(btn_frame, text="Пройти тест заново", font=("Helvetica", 15, "bold"), 
                              command=self.restart_test, bg=SECONDARY, fg=BTN_FG, 
                              activebackground=PRIMARY, activeforeground=BTN_FG, 
                              bd=0, padx=30, pady=15, cursor="hand2")
        restart_btn.pack(side="left", padx=10)

        exit_btn = tk.Button(btn_frame, text="Выйти", font=("Helvetica", 15, "bold"), 
                           command=self.root.destroy, bg=BTN_BG, fg=BTN_FG, 
                           activebackground=PRIMARY, activeforeground=BTN_FG, 
                           bd=0, padx=30, pady=15, cursor="hand2")
        exit_btn.pack(side="left", padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTestApp(root)
    root.mainloop()