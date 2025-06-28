import tkinter as tk
from tkinter import messagebox
import pandas as pd
import msoffcrypto
import io
import threading

PASSWORD = "123456aaa"
EXCEL_FILE = "dars14_protected.xlsx"
TEST_DURATION = 600  # in seconds (e.g., 10 minutes)

def decrypt_excel(file_path, password):
    decrypted = io.BytesIO()
    with open(file_path, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=password)
        office_file.decrypt(decrypted)
    return decrypted

def load_questions():
    decrypted_file = decrypt_excel(EXCEL_FILE, PASSWORD)
    df = pd.read_excel(decrypted_file)
    questions = []
    for _, row in df.iterrows():
        question_text = row["سوال"]
        options = row["گزینه‌ها"].split(",")
        correct_answer = int(row["گزینه صحیح"]) - 1
        questions.append((question_text, options, correct_answer))
    return questions

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Application")

        self.questions = load_questions()
        self.total_questions = len(self.questions)
        self.current_question = 0
        self.selected_answers = [None] * self.total_questions
        self.score = 0

        self.create_widgets()
        self.display_question()
        self.start_timer(TEST_DURATION)

    def create_widgets(self):
        self.timer_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.timer_label.pack()

        self.remaining_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.remaining_label.pack()

        self.question_label = tk.Label(self.root, text="", wraplength=500, font=("Arial", 14, "bold"))
        self.question_label.pack(pady=20)

        self.var = tk.IntVar()
        self.options_buttons = []
        for i in range(4):
            btn = tk.Radiobutton(self.root, text="", variable=self.var, value=i, font=("Arial", 12))
            self.options_buttons.append(btn)
            btn.pack(anchor="w")

        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=10)
        self.prev_button = tk.Button(self.nav_frame, text="سؤال قبلی", command=self.prev_question)
        self.prev_button.grid(row=0, column=0, padx=5)
        self.submit_button = tk.Button(self.nav_frame, text="ثبت پاسخ", command=self.next_question)
        self.submit_button.grid(row=0, column=1, padx=5)

    def display_question(self):
        question, options, _ = self.questions[self.current_question]
        self.question_label.config(text=f"سؤال {self.current_question + 1}: {question}")

        for i, option in enumerate(options):
            self.options_buttons[i].config(text=option)

        self.var.set(-1 if self.selected_answers[self.current_question] is None else self.selected_answers[self.current_question])

        self.remaining_label.config(text=f"تعداد سؤالات باقی‌مانده: {self.total_questions - self.current_question - 1}")

    def next_question(self):
        self.selected_answers[self.current_question] = self.var.get()

        if self.current_question < self.total_questions - 1:
            self.current_question += 1
            self.display_question()
        else:
            self.evaluate()

    def prev_question(self):
        if self.current_question > 0:
            self.selected_answers[self.current_question] = self.var.get()
            self.current_question -= 1
            self.display_question()

    def evaluate(self):
        self.score = 0
        result_details = []
        for i, (question, _, correct_answer) in enumerate(self.questions):
            if self.selected_answers[i] == correct_answer:
                self.score += 1
                result_details.append(f"سؤال {i+1}: درست")
            else:
                result_details.append(f"سؤال {i+1}: نادرست")

        total = self.total_questions
        percent = (self.score / total) * 100
        final_score = (self.score / total) * 20

        messagebox.showinfo("نتیجه آزمون", f"امتیاز: {self.score}/{total}\nدرصد: {percent:.2f}%\nنمره نهایی: {final_score:.2f} از 20\n\nنتیجه هر سؤال:\n" + "\n".join(result_details))
        self.root.quit()

    def start_timer(self, seconds):
        def countdown():
            for remaining in range(seconds, -1, -1):
                mins, secs = divmod(remaining, 60)
                time_format = f"زمان باقی‌مانده: {mins:02}:{secs:02}"
                self.timer_label.config(text=time_format)
                self.root.update()
                if remaining == 0:
                    self.evaluate()
                self.root.after(1000)

        threading.Thread(target=countdown, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
