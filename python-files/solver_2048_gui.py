
import tkinter as tk
from tkinter import messagebox
import copy

DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']

class Game2048AI:
    def __init__(self, board):
        self.board = board

    def get_best_move(self):
        best_score = -float('inf')
        best_move = None
        for move in DIRECTIONS:
            new_board, moved = self.execute_move(move, self.board)
            if moved:
                score = self.evaluate(new_board)
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move or "No valid moves"

    def evaluate(self, board):
        empty_cells = sum(row.count(0) for row in board)
        max_tile = max(max(row) for row in board)
        return empty_cells + max_tile

    def execute_move(self, direction, board):
        def merge(row):
            non_zero = [num for num in row if num != 0]
            merged = []
            skip = False
            for i in range(len(non_zero)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                    merged.append(non_zero[i] * 2)
                    skip = True
                else:
                    merged.append(non_zero[i])
            return merged + [0] * (len(row) - len(merged))

        moved = False
        new_board = copy.deepcopy(board)

        if direction == 'UP':
            for col in range(4):
                merged = merge([board[row][col] for row in range(4)])
                for row in range(4):
                    if new_board[row][col] != merged[row]:
                        moved = True
                    new_board[row][col] = merged[row]

        elif direction == 'DOWN':
            for col in range(4):
                merged = merge([board[row][col] for row in reversed(range(4))])
                for row in range(4):
                    if new_board[3 - row][col] != merged[row]:
                        moved = True
                    new_board[3 - row][col] = merged[row]

        elif direction == 'LEFT':
            for row in range(4):
                merged = merge(board[row])
                if new_board[row] != merged:
                    moved = True
                new_board[row] = merged

        elif direction == 'RIGHT':
            for row in range(4):
                merged = merge(list(reversed(board[row])))
                merged = list(reversed(merged))
                if new_board[row] != merged:
                    moved = True
                new_board[row] = merged

        return new_board, moved

def run_gui():
    root = tk.Tk()
    root.title("2048 Solver")

    entries = [[None for _ in range(4)] for _ in range(4)]

    def get_board():
        board = []
        for i in range(4):
            row = []
            for j in range(4):
                val = entries[i][j].get()
                try:
                    row.append(int(val) if val else 0)
                except:
                    row.append(0)
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, str(row[-1]))
            board.append(row)
        return board

    def on_solve():
        board = get_board()
        ai = Game2048AI(board)
        move = ai.get_best_move()
        messagebox.showinfo("Лучший ход", f"Жми: {move}")

    for i in range(4):
        for j in range(4):
            e = tk.Entry(root, width=4, font=('Arial', 20), justify='center')
            e.grid(row=i, column=j, padx=5, pady=5)
            entries[i][j] = e

    solve_button = tk.Button(root, text="Рассчитать лучший ход", command=on_solve, font=('Arial', 14))
    solve_button.grid(row=4, column=0, columnspan=4, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
