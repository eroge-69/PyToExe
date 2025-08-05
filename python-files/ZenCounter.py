
import tkinter as tk
from tkinter import ttk

class CardCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zen Card Counter")
        self.count = 0
        self.decks_remaining = 1

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(side=tk.LEFT, padx=20, pady=20)

        buttons = [
            ("2, 3, 7 (+1)", 1),
            ("4, 5, 6 (+2)", 2),
            ("10, J, Q, K (-2)", -2),
            ("Asso (-1)", -1),
        ]

        for text, value in buttons:
            btn = tk.Button(self.frame_buttons, text=text, width=20, height=2,
                            command=lambda v=value: self.update_count(v))
            btn.pack(pady=5)

        self.label_reminder = tk.Label(self.frame_buttons, text="8, 9 valgono 0")
        self.label_reminder.pack(pady=10)

        self.frame_display = tk.Frame(root)
        self.frame_display.pack(side=tk.RIGHT, padx=20, pady=20)

        self.label_count = tk.Label(self.frame_display, text=f"Conteggio Attuale: {self.count}", font=("Arial", 14))
        self.label_count.pack(pady=10)

        self.label_true_count = tk.Label(self.frame_display, text=f"True Count: {self.calculate_true_count()}", font=("Arial", 14))
        self.label_true_count.pack(pady=10)

        tk.Label(self.frame_display, text="Mazzi Rimanenti").pack()
        self.decks_selector = ttk.Combobox(self.frame_display, values=[i for i in range(1, 9)], state="readonly")
        self.decks_selector.current(0)
        self.decks_selector.bind("<<ComboboxSelected>>", self.change_decks)
        self.decks_selector.pack(pady=5)

        self.reset_button = tk.Button(self.frame_display, text="Reset", command=self.reset_count)
        self.reset_button.pack(pady=10)

    def update_count(self, value):
        self.count += value
        self.refresh_display()

    def calculate_true_count(self):
        return round(self.count / self.decks_remaining, 2)

    def change_decks(self, event):
        self.decks_remaining = int(self.decks_selector.get())
        self.refresh_display()

    def reset_count(self):
        self.count = 0
        self.refresh_display()

    def refresh_display(self):
        self.label_count.config(text=f"Conteggio Attuale: {self.count}")
        self.label_true_count.config(text=f"True Count: {self.calculate_true_count()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CardCounterApp(root)
    root.mainloop()
