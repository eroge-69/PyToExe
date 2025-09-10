import tkinter as tk
from tkinter import messagebox
import random
import time

# -----------------------------
# Configuration
# -----------------------------
EMOJIS = ['🎁', '🎈', '🍰', '💐', '🎉', '🎊', '❤️', '🍭']
PAIRS = EMOJIS * 2

# -----------------------------
# Main App Class
# -----------------------------
class BirthdayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎂 Happy Birthday Phupi Jaan 🎉")
        self.root.geometry("700x750")
        self.root.configure(bg="#ffe6f0")
        self.cards = []
        self.flipped = []
        self.buttons = []
        self.lock = False

        self.start_screen()

    def start_screen(self):
        self.clear_screen()

        title = tk.Label(self.root, text="🎉 Happy Birthday Phupi Jaan! 🎉", font=("Helvetica", 28, "bold"),
                         fg="deeppink", bg="#ffe6f0")
        title.pack(pady=20)

        msg = tk.Label(self.root, text="Wishing you a day full of happiness, love and cake! 💖",
                       font=("Helvetica", 16), bg="#ffe6f0")
        msg.pack(pady=10)

        cake_btn = tk.Button(self.root, text="🎂 Cut the Cake", font=("Helvetica", 18, "bold"),
                             bg="#ff4081", fg="white", command=self.cake_animation)
        cake_btn.pack(pady=30)

    def cake_animation(self):
        self.clear_screen()

        cake_frame = tk.Frame(self.root, bg="#ffe6f0")
        cake_frame.pack(pady=40)

        label = tk.Label(cake_frame, text="🎂", font=("Helvetica", 150), bg="#ffe6f0")
        label.pack()

        flame_label = tk.Label(cake_frame, text="🕯️", font=("Helvetica", 40), bg="#ffe6f0")
        flame_label.pack()

        self.root.update()

        for _ in range(6):
            flame_label.config(text="🕯️" if _ % 2 == 0 else "")
            self.root.update()
            time.sleep(0.3)

        messagebox.showinfo("Cake Cut!", "Yay! Cake has been cut 🎂🎉")

        play_btn = tk.Button(self.root, text="🎮 Play Memory Game", font=("Helvetica", 18, "bold"),
                             bg="#7e57c2", fg="white", command=self.start_game)
        play_btn.pack(pady=30)

    def start_game(self):
        self.clear_screen()
        self.setup_game_board()

    def setup_game_board(self):
        self.cards = list(PAIRS)
        random.shuffle(self.cards)
        self.flipped = []
        self.buttons = []
        self.lock = False

        game_frame = tk.Frame(self.root, bg="#ffe6f0")
        game_frame.pack(pady=20)

        rows, cols = 4, 4
        for i in range(rows):
            for j in range(cols):
                btn = tk.Button(game_frame, text="❓", font=("Helvetica", 24, "bold"),
                                width=6, height=3,
                                bg="#f06292", fg="white",
                                activebackground="#f8bbd0",
                                command=lambda idx=i * cols + j: self.flip_card(idx))
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.buttons.append(btn)

    def flip_card(self, index):
        if self.lock or self.buttons[index]["text"] != "❓":
            return

        self.buttons[index]["text"] = self.cards[index]
        self.flipped.append(index)

        if len(self.flipped) == 2:
            self.lock = True
            self.root.after(1000, self.check_match)

    def check_match(self):
        idx1, idx2 = self.flipped
        if self.cards[idx1] == self.cards[idx2]:
            self.buttons[idx1]["state"] = "disabled"
            self.buttons[idx2]["state"] = "disabled"
        else:
            self.buttons[idx1]["text"] = "❓"
            self.buttons[idx2]["text"] = "❓"

        self.flipped = []
        self.lock = False

        if all(btn["state"] == "disabled" for btn in self.buttons):
            messagebox.showinfo("You Win!", "You matched all the cards! 🎊🎉")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# -----------------------------
# Run the App
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BirthdayApp(root)
    root.mainloop()
