import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe (AI Edition)")
        self.root.configure(bg="#f5f5dc")
        self.player_symbol = ""
        self.ai_symbol = ""

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.board = [["" for _ in range(3)] for _ in range(3)]

        self.create_choice_menu()

    def create_choice_menu(self):
        self.choice_frame = tk.Frame(self.root, bg="#f5f5dc")
        self.choice_frame.pack(pady=30)

        title = tk.Label(self.choice_frame, text="Choose Your Symbol", font=("Arial", 18, "bold"), bg="#f5f5dc")
        title.pack(pady=10)

        btn_x = tk.Button(self.choice_frame, text="Play as X", font=("Arial", 14), bg="#87cefa", fg="black",
                          width=12, command=lambda: self.set_symbols("X"))
        btn_x.pack(pady=5)

        btn_o = tk.Button(self.choice_frame, text="Play as O", font=("Arial", 14), bg="#ffa07a", fg="black",
                          width=12, command=lambda: self.set_symbols("O"))
        btn_o.pack(pady=5)

    def set_symbols(self, symbol):
        self.player_symbol = symbol
        self.ai_symbol = "O" if symbol == "X" else "X"
        self.choice_frame.destroy()
        self.draw_board()
        if self.player_symbol == "O":
            self.root.after(300, self.ai_move)

    def draw_board(self):
        self.board_frame = tk.Frame(self.root, bg="#f5f5dc")
        self.board_frame.pack()

        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.board_frame, text="", font=("Arial", 32), width=5, height=2,
                                bg="#e6e6fa", fg="#333", activebackground="#dcdcdc",
                                command=lambda x=i, y=j: self.make_move(x, y))
                btn.grid(row=i, column=j, padx=4, pady=4)
                self.buttons[i][j] = btn

        self.restart_button = tk.Button(self.root, text="Restart", font=("Arial", 12, "bold"), bg="#90ee90", fg="black",
                                        command=self.restart_game)
        self.restart_button.pack(pady=15)

    def make_move(self, i, j):
        if self.board[i][j] == "":
            self.board[i][j] = self.player_symbol
            self.buttons[i][j].config(text=self.player_symbol, state="disabled")

            if self.check_winner(self.player_symbol):
                messagebox.showinfo("Game Over", "🎉 You Win!")
                self.disable_all()
                return

            if self.is_full():
                messagebox.showinfo("Game Over", "🤝 It's a Draw!")
                return

            self.root.after(300, self.ai_move)

    def ai_move(self):
        best_score = -float('inf')
        best_move = None

        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = self.ai_symbol
                    score = self.minimax(False)
                    self.board[i][j] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        if best_move:
            i, j = best_move
            self.board[i][j] = self.ai_symbol
            self.buttons[i][j].config(text=self.ai_symbol, state="disabled")

            if self.check_winner(self.ai_symbol):
                messagebox.showinfo("Game Over", "😈 AI Wins!")
                self.disable_all()
            elif self.is_full():
                messagebox.showinfo("Game Over", "🤝 It's a Draw!")

    def minimax(self, is_maximizing):
        winner = self.get_winner()
        if winner == self.ai_symbol:
            return 1
        elif winner == self.player_symbol:
            return -1
        elif self.is_full():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = self.ai_symbol
                        score = self.minimax(False)
                        self.board[i][j] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = self.player_symbol
                        score = self.minimax(True)
                        self.board[i][j] = ""
                        best_score = min(score, best_score)
            return best_score

    def get_winner(self):
        for symbol in [self.player_symbol, self.ai_symbol]:
            if self.check_winner(symbol):
                return symbol
        return None

    def check_winner(self, symbol):
        b = self.board
        return any(
            all(b[i][j] == symbol for j in range(3)) for i in range(3)
        ) or any(
            all(b[i][j] == symbol for i in range(3)) for j in range(3)
        ) or all(
            b[i][i] == symbol for i in range(3)
        ) or all(
            b[i][2 - i] == symbol for i in range(3)
        )

    def is_full(self):
        return all(self.board[i][j] != "" for i in range(3) for j in range(3))

    def disable_all(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state="disabled")

    def restart_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.board_frame.destroy()
        self.restart_button.destroy()
        self.create_choice_menu()

def main():
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()

if __name__ == "__main__":
    main()
