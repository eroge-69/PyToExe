import tkinter as tk
from tkinter import messagebox
import random
import pickle
import os
from PIL import Image, ImageTk

BINGO_SAVE_FILE = "bingo_save.pkl"

class BingoCard:
    def __init__(self, frame, card):
        self.frame = frame
        self.card = card
        self.marked = [[False]*5 for _ in range(5)]
        self.marked[2][2] = True
        self.buttons = [[None]*5 for _ in range(5)]
        self.completed_bingos = set()
        self.points = 0  # <-- Add this line
        self.points_label = tk.Label(self.frame, text=f"Points: {self.points}", font=('Arial', 14, 'bold'))
        self.points_label.grid(row=6, column=0, columnspan=5, pady=10)
        self.create_card()

    def on_click(self, row, col):
        btn = self.buttons[row][col]
        current = btn.cget("bg")
        if current == "#9d43f8":
            btn.config(bg="lightgreen", state=tk.DISABLED)  # Disable after marking
            self.marked[row][col] = True

        else:
            btn.config(bg="#9d43f8")
            self.marked[row][col] = False
        self.check_and_alert_bingo()

    def save_state(self):
        with open(BINGO_SAVE_FILE, "wb") as f:
            pickle.dump({"card": self.card, "marked": self.marked}, f)

    def load_state(self):
        try:
            with open(BINGO_SAVE_FILE, "rb") as f:
                data = pickle.load(f)
            return data["card"], data["marked"]
        except FileNotFoundError:
            return None, None

    def check_and_alert_bingo(self):
        def is_bingo(seq):
            return all(seq)

        new_bingos = []
        new_bingos.extend(self._check_rows(is_bingo))
        new_bingos.extend(self._check_columns(is_bingo))
        new_bingos.extend(self._check_diagonals(is_bingo))

        for bingo in new_bingos:
            messagebox.showinfo("Bingo!", "You got a Bingo!")
            self.completed_bingos.add(bingo)
            self.points += 8  # <-- Add points for each bingo

        if self._check_blackout(is_bingo):
            messagebox.showinfo("Blackout!", "You got a Blackout! The whole card is full!")
            self.completed_bingos.add("blackout")
            self.points += 104  # <-- Add bonus points for blackout
            try:
                os.remove(BINGO_SAVE_FILE)
            except FileNotFoundError:
                pass

        self.points_label.config(text=f"Points: {self.points}")  # <-- Update points display

    def _check_rows(self, is_bingo):
        bingos = []
        for i in range(5):
            if is_bingo(self.marked[i]) and f"row{i}" not in self.completed_bingos:
                bingos.append(f"row{i}")
        return bingos

    def _check_columns(self, is_bingo):
        bingos = []
        for i in range(5):
            if is_bingo([self.marked[j][i] for j in range(5)]) and f"col{i}" not in self.completed_bingos:
                bingos.append(f"col{i}")
        return bingos

    def _check_diagonals(self, is_bingo):
        bingos = []
        if is_bingo([self.marked[i][i] for i in range(5)]) and "diag1" not in self.completed_bingos:
            bingos.append("diag1")
        if is_bingo([self.marked[i][4-i] for i in range(5)]) and "diag2" not in self.completed_bingos:
            bingos.append("diag2")
        return bingos

    def _check_blackout(self, is_bingo):
        return is_bingo([self.marked[row][col] for row in range(5) for col in range(5)]) and "blackout" not in self.completed_bingos

    def create_card(self):
        headers = ['B', 'I', 'N', 'G', 'O']
        for col, header in enumerate(headers):
            tk.Label(self.frame, text=header,bg="#b366ff", relief=tk.RIDGE, font=('Arial', 20, 'bold')).grid(row=0, column=col, padx=5, pady=5)
        for row in range(5):
            for col in range(5):
                value = get_cell_value(self.card, row, col)
                if value is None:
                    btn = tk.Button(self.frame, text='FREE', relief=tk.RIDGE, font=('Arial', 10), width=20, height=3, state=tk.DISABLED, bg="lightgreen")
                else:
                    btn = tk.Button(
                        self.frame,
                        relief=tk.RIDGE,
                        text=str(value),
                        font=('Arial', 10),
                        width=20,
                        height=3,
                        wraplength=150,
                        bg="#9d43f8",               # Light purple background
                        fg="white",                 # White text
                        command=lambda r=row, c=col: self.on_click(r, c)
                    )
                btn.grid(row=row+1, column=col, padx=2, pady=2)
                self.buttons[row][col] = btn

    def check_bingo(self):
        # Check rows and columns
        for i in range(5):
            if all(self.marked[i][j] for j in range(5)):
                return True
            if all(self.marked[j][i] for j in range(5)):
                return True
        # Check diagonals
        if all(self.marked[i][i] for i in range(5)):
            return True
        if all(self.marked[i][4-i] for i in range(5)):
            return True
        return False

def get_cell_value(card, row, col):
    # Return None for the center cell (FREE space)
    if row == 2 and col == 2:
        return None
    return card[row][col]

def create_card_frame(root, card):
    frame = tk.Frame(root, padx=50, pady=50, bd=2, relief=tk.RIDGE)
    frame.pack(side=tk.LEFT, padx=10, pady=10)
    BingoCard(frame, card)

def get_random_card(tasks):
    # Get 24 random tasks for the card (excluding the center)
    selected = random.sample(tasks, 24)
    card = []
    idx = 0
    for row in range(5):
        card_row = []
        for col in range(5):
            if row == 2 and col == 2:
                card_row.append("FREE")
            else:
                card_row.append(selected[idx])
                idx += 1
        card.append(card_row)
    return card

if __name__ == "__main__":
    root = tk.Tk()
    with open("bingo tasks.txt") as f:
        tasks = [line.strip() for line in f if line.strip()]
    # Try to load saved state
    temp_bingo = BingoCard(tk.Frame(root), [[None]*5 for _ in range(5)])
    card, marked = temp_bingo.load_state()
    if card is None:
        card = get_random_card(tasks)
        marked = None
    image = Image.open("pink clouds.jpeg")  # Use your image file path
    image = image.resize((1000, 600))  # Set your desired width and height here
    photo = ImageTk.PhotoImage(image)
    frame = tk.Frame(root, width=1000, height=600, bd=10, relief=tk.RIDGE, bg="#b366ff")
    frame.pack(side=tk.LEFT, padx=10, pady=10)
    # Place the image as background
    bg_label = tk.Label(frame, image=photo)
    bg_label.image = photo  # Keep a reference!
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bingo = BingoCard(frame, card)
    if marked:
        bingo.marked = marked
    for row in range(5):
        for col in range(5):
            if bingo.marked[row][col] and bingo.buttons[row][col]:
                bingo.buttons[row][col].config(bg="lightgreen")
            elif bingo.buttons[row][col]:
                bingo.buttons[row][col].config(bg="#9d43f8")

    def on_close():
        if "blackout" not in bingo.completed_bingos:
            bingo.save_state()
        root.destroy()

    exit_button = tk.Button(frame, relief=tk.RIDGE, bg="#b366ff", text="Exit", font=('Arial', 12, 'bold'), command=on_close)
    exit_button.place(relx=0.95, rely=1, anchor='se')  # Bottom right corner

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

