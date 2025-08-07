import tkinter as tk
from tkinter import messagebox
import random

class MathQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mathe-Quiz für Max")
        self.root.geometry("600x500")  # Anfangsgröße des Fensters
        self.root.resizable(False, False)  # Fenstergröße ist nicht in beide Richtungen veränderbar
#        self.root.configure(bg="orange")  # Hintergrundfarbe

        self.correct_count = 0
        self.incorrect_count = 0

        self.question_label = tk.Label(root, text="", font=("Arial", 28))
        self.question_label.pack(pady=20)

        self.answer_entry = tk.Entry(root, font=("Arial", 24), justify="center")
        self.answer_entry.pack(pady=20)

        self.check_button = tk.Button(root, text="Antwort prüfen", font=("Arial", 20), command=self.check_answer)
        self.check_button.pack(pady=20)

        self.feedback_label = tk.Label(root, text="", font=("Arial", 20))
        self.feedback_label.pack(pady=20)

        self.counter_frame = tk.Frame(root)
        self.counter_frame.pack(pady=10)

        self.correct_label = tk.Label(self.counter_frame, text="Richtig: 0", font=("Arial", 12), fg="green")
        self.correct_label.pack(side="left", padx=20)

        self.incorrect_label = tk.Label(self.counter_frame, text="Falsch: 0", font=("Arial", 12), fg="red")
        self.incorrect_label.pack(side="right", padx=20)

        self.stats_button = tk.Button(root, text="Statistik anzeigen", command=self.show_stats)
        self.stats_button.pack(pady=10)
        
        self.new_question()

    def new_question(self):
        self.num1 = random.randint(1, 10)
        self.num2 = random.randint(1, 10)
        self.operation = random.choice(['+', '-', '*'])

        if self.operation == '+':
            self.correct_result = self.num1 + self.num2
        elif self.operation == '-':
            self.correct_result = self.num1 - self.num2
        else:
            self.correct_result = self.num1 * self.num2

        self.question_label.config(text=f"{self.num1} {self.operation} {self.num2}?")
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def check_answer(self):
        try:
            user_answer = int(self.answer_entry.get())
            if user_answer == self.correct_result:
                self.correct_count += 1
                self.feedback_label.config(text="Richtig! Gut gemacht.", fg="green")
            else:
                self.incorrect_count += 1
                self.feedback_label.config(text=f"Falsch. Die richtige Antwort ist {self.correct_result}.", fg="red")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gib eine gültige Zahl ein.")
            return

        self.correct_label.config(text=f"Richtig: {self.correct_count}")
        self.incorrect_label.config(text=f"Falsch: {self.incorrect_count}")
        self.root.after(2000, self.new_question)

    def show_stats(self):
        total = self.correct_count + self.incorrect_count
        if total == 0:
            success_rate = 0
        else:
            success_rate = round((self.correct_count / total) * 100, 2)

        stats_message = (
            f"Statistik:\n\n"
            f"Richtige Antworten: {self.correct_count}\n"
            f"Falsche Antworten: {self.incorrect_count}\n"
            f"Gesamt: {total}\n"
            f"Erfolgsquote: {success_rate}%"
        )
        messagebox.showinfo("Statistik", stats_message)

# Start the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()
