# -*- coding: utf-8 -*-
import Tkinter as tk
import random

class CrosswordApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Крстозбор Деде")
        self.words = []
        self.rows = 10
        self.cols = 10

        self.create_input_window()

    def create_input_window(self):
        self.clear_window()
        tk.Label(self.root, text="Внеси зборови (секој во нов ред):").pack()
        self.text_entry = tk.Text(self.root, height=10, width=30)
        self.text_entry.pack()

        tk.Label(self.root, text="Големина (на пр. 10x8):").pack()
        self.size_entry = tk.Entry(self.root)
        self.size_entry.pack()

        tk.Button(self.root, text="Направи", command=self.make_crossword).pack(pady=5)

    def make_crossword(self):
        words_text = self.text_entry.get("1.0", tk.END).strip()
        self.words = [word.strip().upper() for word in words_text.splitlines() if word.strip()]
        size_text = self.size_entry.get().lower().replace(" ", "")
        try:
            if 'x' in size_text:
                parts = size_text.split('x')
                self.rows = int(parts[1])
                self.cols = int(parts[0])
            else:
                self.rows = self.cols = int(size_text)
        except:
            self.rows = self.cols = 10

        self.create_puzzle_window()

    def create_puzzle_window(self):
        self.clear_window()

        puzzle = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]

        for word in self.words:
            placed = False
            for _ in range(100):
                direction = random.choice(['H', 'V'])
                if direction == 'H':
                    row = random.randint(0, self.rows - 1)
                    col = random.randint(0, self.cols - len(word))
                    if all(puzzle[row][col + i] in [' ', word[i]] for i in range(len(word))):
                        for i in range(len(word)):
                            puzzle[row][col + i] = word[i]
                        placed = True
                        break
                else:
                    row = random.randint(0, self.rows - len(word))
                    col = random.randint(0, self.cols - 1)
                    if all(puzzle[row + i][col] in [' ', word[i]] for i in range(len(word))):
                        for i in range(len(word)):
                            puzzle[row + i][col] = word[i]
                        placed = True
                        break

        frame = tk.Frame(self.root)
        frame.pack()

        for r in range(self.rows):
            for c in range(self.cols):
                letter = puzzle[r][c]
                e = tk.Entry(frame, width=2, justify='center', font=("Arial", 12))
                e.grid(row=r, column=c)
                e.insert(0, letter)
                e.config(state='disabled')

        tk.Button(self.root, text="Освежи", command=self.create_puzzle_window).pack(side='left', padx=10, pady=10)
        tk.Button(self.root, text="Промени", command=self.create_input_window).pack(side='right', padx=10, pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CrosswordApp()
    app.run()
