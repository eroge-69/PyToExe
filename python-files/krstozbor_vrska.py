
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import random
import re


def create_empty_grid(width, height):
    return [[" " for _ in range(width)] for _ in range(height)]


def place_first_word(grid, word, width, height):
    start_row = height // 2
    start_col = (width - len(word)) // 2
    for i, letter in enumerate(word):
        grid[start_row][start_col + i] = letter
    positions = [(start_row, start_col + i) for i in range(len(word))]
    return positions


def find_cross_position(grid, word, width, height, placed_words):
    for placed_word, positions in placed_words:
        for i, letter in enumerate(word):
            for j, (r, c) in enumerate(positions):
                if word[i] == grid[r][c]:
                    # Try vertical
                    start_r = r - i
                    if 0 <= start_r and start_r + len(word) <= height:
                        fits = True
                        for k in range(len(word)):
                            row = start_r + k
                            if grid[row][c] not in (" ", word[k]):
                                fits = False
                                break
                        if fits:
                            for k in range(len(word)):
                                grid[start_r + k][c] = word[k]
                            return [(start_r + k, c) for k in range(len(word))]
                    # Try horizontal
                    start_c = c - i
                    if 0 <= start_c and start_c + len(word) <= width:
                        fits = True
                        for k in range(len(word)):
                            col = start_c + k
                            if grid[r][col] not in (" ", word[k]):
                                fits = False
                                break
                        if fits:
                            for k in range(len(word)):
                                grid[r][start_c + k] = word[k]
                            return [(r, start_c + k) for k in range(len(word))]
    return None


def generate_crossword(words, width, height):
    grid = create_empty_grid(width, height)
    placed = []
    first_word = words[0]
    positions = place_first_word(grid, first_word, width, height)
    placed.append((first_word, positions))
    for word in words[1:]:
        pos = find_cross_position(grid, word, width, height, placed)
        if pos:
            placed.append((word, pos))
    return grid


def show_crossword(grid, words):
    result_win = tk.Toplevel()
    result_win.title("🧩 Вкрстеница")

    frame = tk.Frame(result_win)
    frame.pack(padx=10, pady=10)

    height = len(grid)
    width = len(grid[0])

    text_grid = tk.Text(frame, font=("Courier New", 16), width=width * 2, height=height + 2)
    for row in grid:
        text_grid.insert(tk.END, " ".join(row) + "\n")
    text_grid.config(state=tk.DISABLED)
    text_grid.grid(row=0, column=0, padx=10)

    label = tk.Label(frame, text="Зборови за пронаоѓање:", font=("Arial", 14, "bold"))
    label.grid(row=0, column=1, sticky="nw")

    word_list = tk.Text(frame, font=("Arial", 14), height=len(words), width=20)
    for word in words:
        word_list.insert(tk.END, word + "\n")
    word_list.config(state=tk.DISABLED)
    word_list.grid(row=0, column=2, sticky="nw")


def get_words_and_size():
    input_win = tk.Tk()
    input_win.title("Внеси зборови и големина")

    tk.Label(input_win, text="Внеси зборови (еден под друг):", font=("Arial", 12)).pack(pady=(10, 0))
    word_text = tk.Text(input_win, height=15, width=30)
    word_text.pack(pady=5)

    tk.Label(input_win, text="Внеси големина на мрежата (ширина x висина):", font=("Arial", 12)).pack()
    size_entry = tk.Entry(input_win)
    size_entry.pack(pady=5)

    def on_submit():
        raw_words = word_text.get("1.0", tk.END).strip().split("\n")
        words = [w.strip().upper() for w in raw_words if w.strip()]
        size_str = size_entry.get().lower().replace(" ", "")
        match = re.match(r"(\d+)x(\d+)", size_str)
        if not match:
            messagebox.showerror("Грешка", "Внеси големина во формат 10x10 или 12x6")
            return
        width, height = map(int, match.groups())
        if not words:
            messagebox.showerror("Грешка", "Внеси барем еден збор.")
            return
        input_win.destroy()
        grid = generate_crossword(words, width, height)
        show_crossword(grid, words)

    def on_clear():
        word_text.delete("1.0", tk.END)
        size_entry.delete(0, tk.END)

    def on_exit():
        input_win.destroy()

    btn_frame = tk.Frame(input_win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Креирај", command=on_submit, font=("Arial", 12)).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Ликни", command=on_clear, font=("Arial", 12)).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Излез", command=on_exit, font=("Arial", 12)).grid(row=0, column=2, padx=5)

    input_win.mainloop()


if __name__ == "__main__":
    get_words_and_size()
