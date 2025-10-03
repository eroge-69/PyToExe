import tkinter as tk
from tkinter import messagebox

class TwentyOneDotsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("21 Dots Game")

        self.dots = 21
        self.choice = tk.IntVar(value=1)

        # Title
        tk.Label(root, text="21 Dots", font=("Arial", 20, "bold")).pack(pady=10)

        # Dot display
        self.dots_frame = tk.Frame(root)
        self.dots_frame.pack(pady=10)
        self.update_dots()

        # Choice buttons
        tk.Label(root, text="Choose how many dots to erase:").pack()
        choice_frame = tk.Frame(root)
        choice_frame.pack(pady=5)

        for num in [1, 2, 3]:
            tk.Radiobutton(
                choice_frame,
                text=str(num),
                variable=self.choice,
                value=num
            ).pack(side="left", padx=10)

        # Action buttons
        action_frame = tk.Frame(root)
        action_frame.pack(pady=10)

        self.erase_button = tk.Button(
            action_frame, text="Erase", width=10, command=self.erase_dots
        )
        self.erase_button.pack(side="left", padx=5)

        tk.Button(
            action_frame, text="Reset", width=10, command=self.reset_game
        ).pack(side="left", padx=5)

    def update_dots(self):
        # Clear old dots
        for widget in self.dots_frame.winfo_children():
            widget.destroy()

        # Display remaining dots
        for i in range(self.dots):
            dot = tk.Label(self.dots_frame, text="●", font=("Arial", 16), fg="blue")
            dot.grid(row=i // 7, column=i % 7, padx=5, pady=5)

    def erase_dots(self):
        if self.dots > 0:
            self.dots = max(0, self.dots - self.choice.get())
            self.update_dots()
        if self.dots == 0:
            messagebox.showinfo("Game Over", "All dots are gone!")

    def reset_game(self):
        self.dots = 21
        self.update_dots()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = TwentyOneDotsGame(root)
    root.mainloop()
