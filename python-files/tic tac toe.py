import tkinter as tk
from tkinter import messagebox, simpledialog
import random

class TicTacToeAI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Choose X or O")
        self.root.configure(bg="#1e1e1e")

        self.difficulty = tk.StringVar(value="Hard")
        self.player_score = 0
        self.ai_score = 0
        self.player_symbol = "X"
        self.ai_symbol = "O"
        self.current_turn = "X"

        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        self.ask_symbol()
        self.create_widgets()
        self.update_score()

    def ask_symbol(self):
        symbol = simpledialog.askstring("Choose Side", "Do you want to be X or O?", initialvalue="X")
        if symbol and symbol.upper() in ["X", "O"]:
            self.player_symbol = symbol.upper()
            self.ai_symbol = "O" if self.player_symbol == "X" else "X"
        else:
            self.player_symbol = "X"
            self.ai_symbol = "O"
        self.current_turn = "X"
        if self.ai_symbol == "X":
            self.root.after(300, self.ai_move)

    def create_widgets(self):
        tk.Label(self.root, text="Tic Tac Toe", font=("Arial", 20), bg="#1e1e1e", fg="white").grid(row=0, column=0, columnspan=3, pady=10)

        self.score_label = tk.Label(self.root, text="", font=("Arial", 14), fg="white", bg="#1e1e1e")
        self.score_label.grid(row=1, column=0, columnspan=3)

        tk.Label(self.root, text="Difficulty:", font=("Arial", 12), bg="#1e1e1e", fg="white").grid(row=2, column=0)
        difficulty_menu = tk.OptionMenu(self.root, self.difficulty, "Easy", "Medium", "Hard")
        difficulty_menu.config(bg="#333", fg="white", font=("Arial", 12), highlightthickness=0)
        difficulty_menu["menu"].config(bg="#333", fg="white")
        difficulty_menu.grid(row=2, column=1, columnspan=2, pady=5)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.root, text="", font=("Arial", 36), width=5, height=2,
                                bg="#333", fg="white", activebackground="#555",
                                command=lambda r=r, c=c: self.player_move(r, c))
                btn.grid(row=r+3, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

        tk.Button(self.root, text="Restart Game", font=("Arial", 12), width=13,
                  bg="#444", fg="white", command=self.reset_board).grid(row=6, column=0, pady=10)

        tk.Button(self.root, text="Reset All", font=("Arial", 12), width=13,
                  bg="#444", fg="white", command=self.reset_all).grid(row=6, column=2, pady=10)

    def update_score(self):
        self.score_label.config(text=f"You ({self.player_symbol}): {self.player_score}   AI ({self.ai_symbol}): {self.ai_score}")

    def player_move(self, r, c):
        if self.buttons[r][c]["text"] == "" and self.current_turn == self.player_symbol:
            self.make_move(r, c, self.player_symbol)
            if self.check_winner(self.player_symbol):
                self.player_score += 1
                self.show_result("You win!")
                return
            if self.is_draw():
                self.show_result("It's a draw!")
                return
            self.current_turn = self.ai_symbol
            self.root.after(300, self.ai_move)

    def ai_move(self):
        if self.difficulty.get() == "Easy":
            move = self.get_random_move()
        elif self.difficulty.get() == "Medium":
            move = self.get_medium_move()
        else:
            move = self.get_best_move()

        if move:
            r, c = move
            self.make_move(r, c, self.ai_symbol)
            if self.check_winner(self.ai_symbol):
                self.ai_score += 1
                self.show_result("AI wins!")
            elif self.is_draw():
                self.show_result("It's a draw!")
            self.current_turn = self.player_symbol

    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        return random.choice(empty) if empty else None

    def get_medium_move(self):
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = self.ai_symbol
                    if self.check_winner(self.ai_symbol):
                        self.board[r][c] = ""
                        return (r, c)
                    self.board[r][c] = ""
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = self.player_symbol
                    if self.check_winner(self.player_symbol):
                        self.board[r][c] = ""
                        return (r, c)
                    self.board[r][c] = ""
        return self.get_random_move()

    def get_best_move(self):
        best_score = -float("inf")
        move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = self.ai_symbol
                    score = self.minimax(0, False)
                    self.board[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, depth, is_maximizing):
        if self.check_static_winner(self.ai_symbol):
            return 1
        if self.check_static_winner(self.player_symbol):
            return -1
        if self.is_draw():
            return 0

        if is_maximizing:
            best = -float("inf")
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = self.ai_symbol
                        best = max(best, self.minimax(depth + 1, False))
                        self.board[r][c] = ""
            return best
        else:
            best = float("inf")
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = self.player_symbol
                        best = min(best, self.minimax(depth + 1, True))
                        self.board[r][c] = ""
            return best

    def make_move(self, r, c, player):
        self.board[r][c] = player
        self.buttons[r][c].config(text=player)

    def check_winner(self, player):
        return self.check_static_winner(player)

    def check_static_winner(self, player):
        b = self.board
        for i in range(3):
            if all(b[i][j] == player for j in range(3)) or all(b[j][i] == player for j in range(3)):
                return True
        if all(b[i][i] == player for i in range(3)) or all(b[i][2 - i] == player for i in range(3)):
            return True
        return False

    def is_draw(self):
        return all(self.board[r][c] != "" for r in range(3) for c in range(3))

    def show_result(self, result):
        messagebox.showinfo("Game Over", result)
        self.reset_board()

    def reset_board(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="")
        self.update_score()
        self.current_turn = "X"
        if self.ai_symbol == "X":
            self.root.after(300, self.ai_move)

    def reset_all(self):
        self.player_score = 0
        self.ai_score = 0
        self.reset_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeAI(root)
    root.mainloop()
