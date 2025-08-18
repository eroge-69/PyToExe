import tkinter as tk
from tkinter import messagebox
import random

class GuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("350x250")
        self.root.configure(bg="#2c3e50")

        self.best_score = None
        self.reset_game()

        # Title
        self.title_label = tk.Label(root, text="🎲 Guess the Number!", 
                                    font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
        self.title_label.pack(pady=10)

        # Instructions
        self.label = tk.Label(root, text="Enter a number (1-100):", 
                              font=("Arial", 12), fg="#ecf0f1", bg="#2c3e50")
        self.label.pack(pady=5)

        # Entry
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(pady=5)

        # Guess button
        self.button = tk.Button(root, text="Guess", font=("Arial", 12, "bold"), 
                                bg="#27ae60", fg="white", command=self.check_guess)
        self.button.pack(pady=5)

        # Restart button
        self.restart_button = tk.Button(root, text="Restart", font=("Arial", 12, "bold"), 
                                        bg="#2980b9", fg="white", command=self.reset_game)
        self.restart_button.pack(pady=5)

        # Quit button
        self.quit_button = tk.Button(root, text="Quit", font=("Arial", 12, "bold"), 
                                     bg="#c0392b", fg="white", command=root.quit)
        self.quit_button.pack(pady=5)

        # Score label
        self.score_label = tk.Label(root, text="Best Score: None", 
                                    font=("Arial", 12), fg="yellow", bg="#2c3e50")
        self.score_label.pack(pady=10)

    def reset_game(self):
        self.secret = random.randint(1, 100)
        self.attempts = 0
        if hasattr(self, "entry"):
            self.entry.delete(0, tk.END)

    def check_guess(self):
        guess = self.entry.get()

        if not guess.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a number!")
            return

        guess = int(guess)
        self.attempts += 1

        if guess < self.secret:
            messagebox.showinfo("Result", "Too low! Try again.")
        elif guess > self.secret:
            messagebox.showinfo("Result", "Too high! Try again.")
        else:
            messagebox.showinfo("Winner!", 
                                f"🎉 Correct! The number was {self.secret}.\n"
                                f"You won in {self.attempts} tries!")
            if self.best_score is None or self.attempts < self.best_score:
                self.best_score = self.attempts
                self.score_label.config(text=f"Best Score: {self.best_score}")
            self.reset_game()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = GuessingGame(root)
    root.mainloop()
