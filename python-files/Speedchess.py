import tkinter as tk
import chess
import random
from tkinter import messagebox


class ChessApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Schachspiel")

        # Initialisierung der Attribute
        self.check_count = 0
        self.time_left = 120  # 2 Minuten in Sekunden
        self.game_over = False
        self.selected_square = None

        # Erstellen eines Frames für das Schachbrett und das Scoreboard
        self.frame = tk.Frame(self.master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.frame, width=400, height=400)  # Höhe für das Schachbrett
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_square_click)

        # Scoreboard
        self.score_label = tk.Label(self.master, text=f"Schach: {self.check_count}", font=("Arial", 16))
        self.score_label.pack(side=tk.BOTTOM)  # Scoreboard am unteren Rand

        # Timer
        self.timer_label = tk.Label(self.master, text=self.format_time(self.time_left), font=("Arial", 16))
        self.timer_label.pack(side=tk.BOTTOM)  # Timer am unteren Rand

        # Reset-Button
        self.reset_button = tk.Button(self.master, text="Neustart", command=self.reset_game, state=tk.DISABLED)
        self.reset_button.pack(side=tk.BOTTOM)  # Reset-Button am unteren Rand

        self.reset_game()  # Spiel zurücksetzen und initialisieren

    def reset_game(self):
        """Setzt das Schachbrett zurück und startet eine neue Partie."""
        self.board = chess.Board()  # Setze das Schachbrett auf die Anfangsposition
        self.start_random_position()  # Mische das Brett zu Beginn
        self.game_over = False
        self.check_count = 0  # Zurücksetzen des Schachzählers
        self.score_label.config(text=f"Schach: {self.check_count}")  # Scoreboard zurücksetzen
        self.time_left = 120  # Timer zurücksetzen
        self.timer_label.config(text=self.format_time(self.time_left))  # Timer zurücksetzen
        self.reset_button.config(state=tk.DISABLED)  # Reset-Button deaktivieren
        self.update_board()  # Brett aktualisieren
        self.update_timer()  # Timer starten

    def start_random_position(self):
        """Macht eine zufällige Anzahl von Zügen, um das Brett zu mischen."""
        for _ in range(random.randint(5, 15)):  # Zufällige Anzahl von Zügen zwischen 5 und 15
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                move = random.choice(legal_moves)
                self.board.push(move)

    def on_square_click(self, event):
        if self.game_over:
            return

        x, y = event.x // 50, 7 - (event.y // 50)
        square = chess.square(x, y)

        if self.selected_square is None:
            # Wähle ein Stück aus, wenn es das eigene ist
            if self.board.piece_at(square) is not None and self.board.piece_at(square).color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)  # Führe den Zug aus
                self.update_board()

                if self.board.is_check():
                    self.check_count += 1  # Erhöhe den Schach-Zähler
                    self.update_scoreboard()  # Aktualisiere das Scoreboard
                    self.display_check_message()  # Zeige die Schach-Nachricht an

                self.black_turn()  # Lass den Gegner ziehen
                self.selected_square = None  # Zurücksetzen der Auswahl
        self.update_board()

    def black_turn(self):
        if self.game_over:
            return

        legal_moves = list(self.board.legal_moves)
        if legal_moves:
            move = random.choice(legal_moves)
            self.board.push(move)

            if self.board.is_check():
                self.check_count += 1  # Erhöhe den Schach-Zähler
                self.update_scoreboard()  # Aktualisiere das Scoreboard

        self.update_board()

    def update_scoreboard(self):
        self.score_label.config(text=f"Schach: {self.check_count}")  # Aktualisiere die Anzeige

    def display_check_message(self):
        messagebox.showinfo("Schach!", "Der König steht im Schach!")

    def end_game(self):
        self.game_over = True
        self.reset_button.config(state=tk.NORMAL)  # Aktivieren des Reset-Buttons
        messagebox.showinfo("Spiel beendet", f"Die Zeit ist abgelaufen!\nSchachanzahl: {self.check_count}")

    def format_time(self, seconds):
        """Formatiert die Zeit in Minuten und Sekunden."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=self.format_time(self.time_left))  # Aktualisiere die Anzeige
            self.time_left -= 1
            self.master.after(1000, self.update_timer)  # Aktualisiere den Timer jede Sekunde
        else:
            self.end_game()  # Beende das Spiel, wenn die Zeit abgelaufen ist

    def get_piece_unicode(self, piece):
        if piece is None:
            return ""
        unicode_map = {
            chess.PAWN: "♙" if piece.color == chess.WHITE else "♟",
            chess.ROOK: "♖" if piece.color == chess.WHITE else "♜",
            chess.KNIGHT: "♘" if piece.color == chess.WHITE else "♞",
            chess.BISHOP: "♗" if piece.color == chess.WHITE else "♝",
            chess.QUEEN: "♕" if piece.color == chess.WHITE else "♛",
            chess.KING: "♔" if piece.color == chess.WHITE else "♚",
        }
        return unicode_map[piece.piece_type]

    def update_board(self):
        self.canvas.delete("all")
        for square in chess.SQUARES:
            x, y = chess.square_file(square), chess.square_rank(square)
            color = "white" if (x + y) % 2 == 0 else "gray"
            self.canvas.create_rectangle(x * 50, (7 - y) * 50, (x + 1) * 50, (7 - y + 1) * 50, fill=color)

            piece = self.board.piece_at(square)
            if piece is not None:
                piece_color = "red" if piece.color == chess.BLACK else "black"
                self.canvas.create_text(x * 50 + 25, (7 - y) * 50 + 25, text=self.get_piece_unicode(piece),
                                        font=("Arial", 24), fill=piece_color)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()