import tkinter as tk
import random

class GuessNumberGame:
    def __init__(self, master):
        self.master = master
        master.title("Guess the Number Game")

        self.secret_number = random.randint(1, 100)
        self.attempts = 0

        self.label = tk.Label(master, text="Guess a number between 1 and 100:")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.guess_button = tk.Button(master, text="Guess", command=self.check_guess)
        self.guess_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

        self.reset_button = tk.Button(master, text="Reset", command=self.reset_game)
        self.reset_button.pack()

    def check_guess(self):
        try:
            guess = int(self.entry.get())
        except ValueError:
            self.result_label.config(text="Please enter a valid number.")
            return

        self.attempts += 1

        if guess < self.secret_number:
            self.result_label.config(text="Too low! Try again.")
        elif guess > self.secret_number:
            self.result_label.config(text="Too high! Try again.")
        else:
            self.result_label.config(text=f"Correct! You guessed it in {self.attempts} attempts.")

    def reset_game(self):
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.entry.delete(0, tk.END)
        self.result_label.config(text="Game reset! Guess a number between 1 and 100.")

if __name__ == "__main__":
    root = tk.Tk()
    game = GuessNumberGame(root)
    # Apply minimalism style and colors
    root.configure(bg="#f5f5f5")
    game.label.config(bg="#f5f5f5", fg="#333333", font=("Segoe UI", 12))
    game.entry.config(bg="#ffffff", fg="#333333", font=("Segoe UI", 12), relief="flat", highlightthickness=1, highlightbackground="#cccccc")
    game.guess_button.config(bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 11), relief="flat", activebackground="#388E3C")
    game.result_label.config(bg="#f5f5f5", fg="#333333", font=("Segoe UI", 11))
    game.reset_button.config(bg="#2196F3", fg="#ffffff", font=("Segoe UI", 11), relief="flat", activebackground="#1976D2")

    # Add more minimalism styled buttons
    hint_button = tk.Button(root, text="Hint", bg="#FFC107", fg="#333333", font=("Segoe UI", 11), relief="flat", activebackground="#FFA000")
    quit_button = tk.Button(root, text="Quit", bg="#E57373", fg="#ffffff", font=("Segoe UI", 11), relief="flat", activebackground="#C62828")

    hint_button.pack(pady=2)
    quit_button.pack(pady=2)

    def show_hint():
        if game.secret_number % 2 == 0:
            hint = "The number is even."
        else:
            hint = "The number is odd."
        game.result_label.config(text=hint)

    def quit_game():
        root.destroy()

    hint_button.config(command=show_hint)
    quit_button.config(command=quit_game)

    # Add numpad for number entry
    numpad_frame = tk.Frame(root, bg="#f5f5f5")
    numpad_frame.pack(pady=5)

    def numpad_insert(num):
        game.entry.insert(tk.END, str(num))

    buttons = [
        ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
        ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
        ('0', 3, 1)
    ]

    for (text, row, col) in buttons:
        btn = tk.Button(numpad_frame, text=text, width=4, height=2,
                        bg="#ffffff", fg="#333333", font=("Segoe UI", 11),
                        relief="flat", highlightthickness=1, highlightbackground="#cccccc",
                        command=lambda t=text: numpad_insert(t))
        btn.grid(row=row, column=col, padx=2, pady=2)

    # Add Ukrainian language support
    def set_ukrainian():
        game.label.config(text="Вгадайте число від 1 до 100:")
        game.guess_button.config(text="Вгадати")
        game.result_label.config(text="")
        game.reset_button.config(text="Скинути")
        hint_button.config(text="Підказка")
        quit_button.config(text="Вийти")

    def set_english():
        game.label.config(text="Guess a number between 1 and 100:")
        game.guess_button.config(text="Guess")
        game.result_label.config(text="")
        game.reset_button.config(text="Reset")
        hint_button.config(text="Hint")
        quit_button.config(text="Quit")

    lang_frame = tk.Frame(root, bg="#f5f5f5")
    lang_frame.pack(pady=2)
    ua_btn = tk.Button(lang_frame, text="UA", bg="#eeeeee", fg="#333333", font=("Segoe UI", 10),
                       relief="flat", command=set_ukrainian)
    en_btn = tk.Button(lang_frame, text="EN", bg="#eeeeee", fg="#333333", font=("Segoe UI", 10),
                       relief="flat", command=set_english)
    ua_btn.pack(side=tk.LEFT, padx=2)
    en_btn.pack(side=tk.LEFT, padx=2)

    # Make buttons wider by setting a larger width
    game.guess_button.config(width=16)
    game.reset_button.config(width=16)
    hint_button.config(width=16)
    quit_button.config(width=16)
    ua_btn.config(width=8)
    en_btn.config(width=8)

    # Make everything bigger: increase font sizes, button sizes, entry height, and padding
    big_font = ("Segoe UI", 18)
    big_btn_font = ("Segoe UI", 16)
    big_entry_font = ("Segoe UI", 18)

    game.label.config(font=big_font)
    game.entry.config(font=big_entry_font)
    game.guess_button.config(font=big_btn_font, height=2, width=20)
    game.result_label.config(font=big_btn_font)
    game.reset_button.config(font=big_btn_font, height=2, width=20)
    hint_button.config(font=big_btn_font, height=2, width=20)
    quit_button.config(font=big_btn_font, height=2, width=20)
    ua_btn.config(font=big_btn_font, width=10, height=2)
    en_btn.config(font=big_btn_font, width=10, height=2)

    # Make numpad buttons bigger
    for child in numpad_frame.winfo_children():
        child.config(font=big_btn_font, width=6, height=3)

    import pdb; pdb.set_trace()
    # Add backspace button to numpad
    backspace_btn = tk.Button(numpad_frame, text="⌫", width=6, height=3,
                              bg="#eeeeee", fg="#333333", font=big_btn_font,
                              relief="flat", highlightthickness=1, highlightbackground="#cccccc",
                              command=lambda: game.entry.delete(len(game.entry.get())-1, tk.END))
    backspace_btn.grid(row=3, column=0, padx=2, pady=2, columnspan=1)
    def numpad_backspace():
        current = game.entry.get()
        if current:
            game.entry.delete(len(current)-1, tk.END)

    backspace_btn = tk.Button(numpad_frame, text="⌫", width=6, height=3,
                              bg="#eeeeee", fg="#333333", font=big_btn_font,
                              relief="flat", highlightthickness=1, highlightbackground="#cccccc",
                              command=numpad_backspace)
    backspace_btn.grid(row=3, column=0, padx=2, pady=2, columnspan=1)

    # Optionally, add a clear button
    def numpad_clear():
        game.entry.delete(0, tk.END)

    clear_btn = tk.Button(numpad_frame, text="C", width=6, height=3,
                          bg="#eeeeee", fg="#333333", font=big_btn_font,
                          relief="flat", highlightthickness=1, highlightbackground="#cccccc",
                          command=numpad_clear)
    clear_btn.grid(row=3, column=2, padx=2, pady=2, columnspan=1)

    root.mainloop()