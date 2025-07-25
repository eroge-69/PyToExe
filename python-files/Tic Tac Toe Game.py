import tkinter as tk
from tkinter import font

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("✨ Ultimate Tic Tac Toe ✨")
        self.window.configure(bg="#0f4c75")
        self.window.resizable(False, False)

        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'

        self.custom_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=16, weight="bold")

        self.create_ui()
        self.window.mainloop()

    def create_ui(self):
        self.label = tk.Label(self.window, text="🎮 Your Turn (X)", font=self.label_font, bg="#0f4c75", fg="#fff")
        self.label.grid(row=0, column=0, columnspan=3, pady=(20, 10))

        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.window, text='', font=self.custom_font, width=5, height=2,
                                bg="#bbe1fa", fg="#1b262c", activebackground="#3282b8",
                                relief="flat", bd=3,
                                command=lambda row=i, col=j: self.on_click(row, col))
                btn.grid(row=i+1, column=j, padx=5, pady=5)
                self.buttons[i][j] = btn

        self.reset_btn = tk.Button(self.window, text="🔄 Restart", font=self.label_font,
                                   command=self.reset_game,
                                   bg="#3282b8", fg="white", activebackground="#0f4c75",
                                   relief="flat", bd=3, width=10)
        self.reset_btn.grid(row=4, column=0, columnspan=3, pady=(10, 20))

    def on_click(self, row, col):
        if self.board[row][col] == '' and self.current_player == 'X':
            self.board[row][col] = 'X'
            self.buttons[row][col].config(text='X', state='disabled', disabledforeground="#ff2e63")
            if self.check_winner(self.board, 'X'):
                self.label.config(text="🏆 You Win!", fg="#f9ed69")
                self.disable_all()
                return
            elif self.is_draw(self.board):
                self.label.config(text="🤝 It's a Draw!", fg="#f9ed69")
                return
            self.current_player = 'O'
            self.label.config(text="🤖 AI's Turn (O)", fg="#fff")
            self.window.after(500, self.ai_move)

    def ai_move(self):
        best_score = -float('inf')
        best_move = None
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    self.board[i][j] = 'O'
                    score = self.minimax(self.board, 0, False)
                    self.board[i][j] = ''
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        if best_move:
            row, col = best_move
            self.board[row][col] = 'O'
            self.buttons[row][col].config(text='O', state='disabled', disabledforeground="#3fc1c9")
        if self.check_winner(self.board, 'O'):
            self.label.config(text="💥 AI Wins!", fg="#f67280")
            self.disable_all()
        elif self.is_draw(self.board):
            self.label.config(text="🤝 It's a Draw!", fg="#f9ed69")
        else:
            self.current_player = 'X'
            self.label.config(text="🎮 Your Turn (X)", fg="#fff")

    def minimax(self, board, depth, is_max):
        if self.check_winner(board, 'O'):
            return 1
        elif self.check_winner(board, 'X'):
            return -1
        elif self.is_draw(board):
            return 0

        if is_max:
            best = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'O'
                        score = self.minimax(board, depth+1, False)
                        board[i][j] = ''
                        best = max(best, score)
            return best
        else:
            best = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'X'
                        score = self.minimax(board, depth+1, True)
                        board[i][j] = ''
                        best = min(best, score)
            return best

    def check_winner(self, board, player):
        for i in range(3):
            if all(board[i][j] == player for j in range(3)):
                return True
            if all(board[j][i] == player for j in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)) or \
           all(board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def is_draw(self, board):
        return all(cell != '' for row in board for cell in row)

    def disable_all(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state='disabled')

    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.label.config(text="🎮 Your Turn (X)", fg="#fff")
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text='', state='normal')

if __name__ == '__main__':
    TicTacToe()
