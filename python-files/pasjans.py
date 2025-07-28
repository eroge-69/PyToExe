import tkinter as tk
import random

class Card:
    def __init__(self, value, button):
        self.value = value
        self.button = button
        self.revealed = True

class PyramidSolitaire:
    def __init__(self, root):
        self.root = root
        self.root.title("Pasjans Piramida")
        self.deck = list(range(1, 14)) * 4
        random.shuffle(self.deck)
        self.cards = []
        self.selected = []

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.status = tk.Label(root, text="Zaznacz dwie karty o sumie 13")
        self.status.pack()

        self.draw_cards()

    def draw_cards(self):
        for r in range(5):  # 5 rzędów
            row = []
            for c in range(r + 1):
                val = self.deck.pop()
                btn = tk.Button(self.frame, text=str(val), width=4, height=2,
                                command=lambda v=val, x=r, y=c: self.card_clicked(v, x, y))
                btn.grid(row=r, column=c + (5 - r))
                row.append(Card(val, btn))
            self.cards.append(row)

    def card_clicked(self, val, r, c):
        card = self.cards[r][c]
        if card in self.selected:
            self.selected.remove(card)
            card.button.config(bg='SystemButtonFace')
        else:
            self.selected.append(card)
            card.button.config(bg='lightblue')

        if len(self.selected) == 2:
            self.check_selected()

    def check_selected(self):
        sum_val = sum(card.value for card in self.selected)
        if sum_val == 13:
            for card in self.selected:
                card.button.destroy()
        self.selected.clear()
        self.status.config(text="Zaznacz dwie karty o sumie 13")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyramidSolitaire(root)
    root.mainloop()
