
import random
import tkinter as tk
from tkinter import messagebox

# -------------------- Game Data -------------------- #
symbol_prompts = [
    ("A dove carrying an olive branch", "Peace"),
    ("A broken chain", "Freedom or breaking free"),
    ("A red rose", "Love or passion"),
    ("Stormy clouds", "Trouble or conflict"),
    ("A ladder", "Progress or spiritual ascent"),
    ("A locked door", "Secrets or obstacles"),
    ("An hourglass", "Time running out"),
    ("A mirror", "Self-reflection or truth"),
    ("A snake biting its tail", "Eternity or the cycle of life"),
    ("A heart with a crack in it", "Heartbreak or emotional pain")
]

random.shuffle(symbol_prompts)

# -------------------- Game Logic -------------------- #
class SymbolGame:
    def __init__(self, master):
        self.master = master
        master.title("Symbol Sleuth Showdown")
        self.score = 0
        self.index = 0

        self.label = tk.Label(master, text="Welcome to Symbol Sleuth!", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.prompt = tk.Label(master, text="", wraplength=400, font=("Helvetica", 14))
        self.prompt.pack(pady=10)

        self.entry = tk.Entry(master, font=("Helvetica", 14), width=40)
        self.entry.pack(pady=10)

        self.submit_button = tk.Button(master, text="Submit", command=self.check_answer)
        self.submit_button.pack(pady=10)

        self.feedback = tk.Label(master, text="", font=("Helvetica", 12))
        self.feedback.pack(pady=10)

        self.score_label = tk.Label(master, text=f"Score: {self.score}", font=("Helvetica", 12))
        self.score_label.pack(pady=5)

        self.next_question()

    def next_question(self):
        if self.index < len(symbol_prompts):
            self.entry.delete(0, tk.END)
            self.feedback.config(text="")
            symbol, _ = symbol_prompts[self.index]
            self.prompt.config(text=f"What does this symbol represent?\n{symbol}")
        else:
            messagebox.showinfo("Game Over", f"Well done! Your final score is {self.score}/{len(symbol_prompts)}.")
            self.master.quit()

    def check_answer(self):
        user_input = self.entry.get().strip().lower()
        correct_answer = symbol_prompts[self.index][1].lower()
        if correct_answer in user_input:
            self.score += 1
            self.feedback.config(text="✅ Correct!", fg="green")
        else:
            self.feedback.config(text=f"❌ Incorrect! Answer: {symbol_prompts[self.index][1]}", fg="red")

        self.index += 1
        self.score_label.config(text=f"Score: {self.score}")
        self.master.after(2000, self.next_question)

# -------------------- Run the Game -------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    game = SymbolGame(root)
    root.mainloop()
