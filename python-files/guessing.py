import tkinter as tk
from tkinter import messagebox

class GuessingGame:
    def __init__(self, master, filepath):
        self.master = master
        self.master.title("Guessing Game")

        # Load lines from file, stripping whitespace and ignoring empty lines
        with open(filepath, 'r') as f:
            self.lines = [line.strip() for line in f if line.strip()]
        
        self.remaining = set(self.lines)
        
        # GUI elements
        self.label_info = tk.Label(master, text=f"Lines left to guess: {len(self.remaining)}")
        self.label_info.pack(pady=10)

        self.entry_guess = tk.Entry(master, width=50)
        self.entry_guess.pack(pady=5)
        self.entry_guess.focus_set()

        self.button_submit = tk.Button(master, text="Submit Guess", command=self.check_guess)
        self.button_submit.pack(pady=5)

        self.label_feedback = tk.Label(master, text="")
        self.label_feedback.pack(pady=10)

    def check_guess(self):
        guess = self.entry_guess.get().strip()
        if not guess:
            self.label_feedback.config(text="Please enter a guess.")
            return

        # Check case-insensitively
        guess_lower = guess.lower()
        matched_line = None
        for line in self.remaining:
            if line.lower() == guess_lower:
                matched_line = line
                break
        
        if matched_line:
            self.remaining.remove(matched_line)
            self.label_feedback.config(text=f"Correct! You guessed: '{matched_line}'")
            self.label_info.config(text=f"Lines left to guess: {len(self.remaining)}")
        else:
            self.label_feedback.config(text=f"'{guess}' is not correct. Try again.")

        self.entry_guess.delete(0, tk.END)

        if len(self.remaining) == 0:
            messagebox.showinfo("Congratulations!", "You've guessed all lines!")
            self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()

    # Replace 'lines.txt' with your text file path
    game = GuessingGame(root, 'lines.txt')

    root.mainloop()
