from tkinter import *

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("350x300")
        self.root.title("Python Quiz")

        self.questions = [
            "List is represented by\n(a) []\n(b) ()\n(c) {}\n(d) <>",
            "Which is unordered?\n(a) list\n(b) tuple\n(c) set\n(d) dictionaries"
        ]
        self.answers = ['a', 'c']

        self.current_question = 0
        self.score = 0

        Label(root, text="Python Quiz", font=('Arial', 20)).pack(pady=10)

        self.question_label = Label(root, text=self.questions[self.current_question], font=("Arial", 14), justify=LEFT)
        self.question_label.pack(pady=10)

        self.answer_var = StringVar()
        Entry(root, textvariable=self.answer_var, font=("Arial", 12)).pack(pady=5)

        Button(root, text="Submit", command=self.check_answer, font=("Arial", 12), width=12).pack(pady=5)

        self.result_label = Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

    def check_answer(self):
        user_answer = self.answer_var.get().strip().lower()
        self.answer_var.set("")
        if user_answer == self.answers[self.current_question]:
            self.score += 1
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.question_label.config(text=self.questions[self.current_question])
        else:
            self.result_label.config(text=f"Your score is {self.score}/{len(self.questions)}")
            self.question_label.config(text="Quiz Finished!")

if __name__ == "__main__":
    root = Tk()
    app = QuizApp(root)
    root.mainloop()
