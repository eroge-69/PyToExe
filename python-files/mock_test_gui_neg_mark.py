import tkinter as tk
from tkinter import messagebox, simpledialog
import json, time

# -----------------------------
# Load Questions from JSON file
# -----------------------------
def load_questions(filename="questions.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)['questions']
    except:
        messagebox.showerror("Error", "Questions file not found or invalid!")
        return []

# -----------------------------
# Quiz Application Class
# -----------------------------
class MockTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mock Test Application")
        self.root.geometry("600x400")

        self.questions = load_questions()
        self.current_q = 0
        self.score = 0
        self.answers = []

        self.start_time = None
        self.max_time = 0
        self.time_left = 0

        # Default marking scheme
        self.correct_mark = 1
        self.negative_mark = 0

        self.create_start_screen()

    def create_start_screen(self):
        self.clear_window()

        tk.Label(self.root, text="Welcome to Mock Test", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(self.root, text="Enter maximum time (minutes):", font=("Arial", 12)).pack()
        self.time_entry = tk.Entry(self.root)
        self.time_entry.pack(pady=10)

        tk.Button(self.root, text="Set Marking Scheme & Start Test", command=self.set_marking_and_start, font=("Arial", 12, "bold"), bg="green", fg="white").pack(pady=20)

    def set_marking_and_start(self):
        try:
            minutes = int(self.time_entry.get())
            self.max_time = minutes * 60
            self.time_left = self.max_time
        except:
            messagebox.showerror("Error", "Enter valid number of minutes!")
            return

        # Ask user for marking scheme
        self.correct_mark = simpledialog.askfloat("Marking Scheme", "Marks for correct answer:", minvalue=0.1, initialvalue=1)
        self.negative_mark = simpledialog.askfloat("Marking Scheme", "Negative marks for wrong answer:", minvalue=0.0, initialvalue=0)

        if not self.questions:
            messagebox.showerror("Error", "No questions available!")
            return

        self.start_time = time.time()
        self.show_question()
        self.update_timer()

    def show_question(self):
        self.clear_window()
        if self.current_q < len(self.questions):
            q = self.questions[self.current_q]

            tk.Label(self.root, text=f"Q{self.current_q+1}: {q['question']}", wraplength=500, justify="left", font=("Arial", 12, "bold")).pack(pady=20)

            self.selected = tk.StringVar()
            for option in q['options']:
                tk.Radiobutton(self.root, text=option, variable=self.selected, value=option, font=("Arial", 11)).pack(anchor="w")

            tk.Button(self.root, text="Next", command=self.next_question, bg="blue", fg="white").pack(pady=20)
        else:
            self.show_result()

    def next_question(self):
        selected_ans = self.selected.get()
        correct_ans = self.questions[self.current_q]['answer']
        self.answers.append((selected_ans, correct_ans))

        if selected_ans == correct_ans:
            self.score += self.correct_mark
        elif selected_ans != "":
            self.score -= self.negative_mark
        # unattempted = 0

        self.current_q += 1
        self.show_question()

    def update_timer(self):
        if self.time_left > 0 and self.current_q < len(self.questions):
            mins, secs = divmod(self.time_left, 60)
            self.root.title(f"Mock Test - Time Left: {mins:02}:{secs:02}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            messagebox.showinfo("Time Over", "Your test time is finished!")
            self.show_result()

    def show_result(self):
        self.clear_window()
        total_q = len(self.questions)
        accuracy = (self.score / (total_q * self.correct_mark)) * 100 if total_q else 0
        time_taken = int(time.time() - self.start_time)

        tk.Label(self.root, text="Test Completed!", font=("Arial", 18, "bold"), fg="green").pack(pady=20)
        tk.Label(self.root, text=f"Score: {self.score}/{total_q * self.correct_mark}", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Accuracy: {accuracy:.2f}%", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Time Taken: {time_taken} seconds", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Time Left: {self.time_left} seconds", font=("Arial", 14)).pack(pady=5)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MockTestApp(root)
    root.mainloop()
