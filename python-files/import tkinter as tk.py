import tkinter as tk
from tkinter import messagebox
import random

class MathQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mathe-Quiz für Max")
        self.root.geometry("600x400")  # Anfangsgröße des Fensters
        self.root.resizable(True, True)  # Fenstergröße ist in beide Richtungen veränderbar

        self.question_label = tk.Label(root, text="", font=("Arial", 20))
        self.question_label.pack(pady=20)

        self.answer_entry = tk.Entry(root, font=("Arial", 24), justify="center")
        self.answer_entry.pack(pady=20)

        self.check_button = tk.Button(root, text="Antwort prüfen", font=("Arial", 20), command=self.check_answer)
        self.check_button.pack(pady=20)

        self.feedback_label = tk.Label(root, text="", font=("Arial", 20))
        self.feedback_label.pack(pady=20)

        self.new_question()

    def new_question(self):
        self.num1 = random.randint(1, 20)
        self.num2 = random.randint(1, 20)
        self.operation = random.choice(['+', '-', '*'])

        if self.operation == '+':
            self.correct_result = self.num1 + self.num2
        elif self.operation == '-':
            self.correct_result = self.num1 - self.num2
        else:
            self.correct_result = self.num1 * self.num2

        self.question_label.config(text=f"Was ist {self.num1} {self.operation} {self.num2}?")
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def check_answer(self):
        try:
            user_answer = int(self.answer_entry.get())
            if user_answer == self.correct_result:
                self.feedback_label.config(text="Richtig! Gut gemacht.", fg="green")
            else:
                self.feedback_label.config(text=f"Falsch. Die richtige Antwort ist {self.correct_result}.", fg="red")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gib eine gültige Zahl ein.")
        self.root.after(2000, self.new_question)

# Start the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()
