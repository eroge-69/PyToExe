import tkinter as tk
from tkinter import messagebox
import random

# klasa gry (Saper)
class Minesweeper:

    #informacje bazowe
    def __init__(self, master, rows=12, cols=12):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.frame = tk.Frame(master)
        self.frame.pack()
        self.setup_start_screen()

    # ekran startowy (pobranie wartosci)
    def setup_start_screen(self):
        tk.Label(self.frame, text="Ile min?").pack(pady=5)
        self.bomb_entry = tk.Entry(self.frame, bg="#444", fg="#fff")
        self.bomb_entry.pack(pady=5)
        tk.Button(self.frame, text="Start", command=self.start_game).pack(pady=5)

    # poczatek gry
    def start_game(self):
        self.mines = int(self.bomb_entry.get())
        max_mines = self.rows * self.cols - 1
        if not (1 <= self.mines <= max_mines):
            raise ValueError

        self.frame.destroy()  # Usuń ekran startowy
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False

        self.place_mines()
        self.calculate_numbers()
        self.create_buttons()

    # ustawianie min na losowych pozycjach planszy
    def place_mines(self):
        positions = random.sample(range(self.rows * self.cols), self.mines)
        for pos in positions:
            r, c = divmod(pos, self.cols)
            self.grid[r][c] = -1 # na tablicy r na c 0 sa puste a -1 to miny

    # sprawdza klatki na miny
    def calculate_numbers(self):
        for r in range(self.rows):
            for c in range(self.cols):
                # czy tutaj jest mina
                if self.grid[r][c] == -1:
                    continue
                count = 0
                # czy wokol sa miny
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        # wspolrzedne dla sasiednich pol
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc] == -1:
                                count += 1
                self.grid[r][c] = count

    # postawic przyciski siatki
    def create_buttons(self):
        for r in range(self.rows):
            for c in range(self.cols):
                original_color = "#ddd"
                btn = tk.Button(
                    self.master, bg=original_color, bd=0, highlightthickness=0,
                    text="", width=2, height=1,
                    command=lambda row=r, col=c: self.reveal(row, col)
                )
                btn.original_bg = original_color
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#888"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=b.original_bg))

                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn
                
    # pokaz pole (funkcja poddstawowa)
    def reveal(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return

        self.revealed[r][c] = True
        if self.grid[r][c] == -1: # miny
            self.buttons[r][c].config(text=" ", bg="red")

            self.game_over = True
            self.reveal_all_mines("red")
            messagebox.showinfo("Game Over", "Boom! Trafiłeś na minę.")
        else: # puste pola
            self.buttons[r][c].config(
                text=str(self.grid[r][c]) if self.grid[r][c] > 0 else "",
                bg="#aaa", relief=tk.SUNKEN
            )
            self.buttons[r][c].original_bg = "#aaa"
            if self.grid[r][c] == 0: # pola bez liczby
                self.reveal_adjacent_blanks(r, c)
            self.check_win()

    # pokaz sasiednie pola
    def reveal_adjacent_blanks(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if not self.revealed[nr][nc] and self.grid[nr][nc] != -1:
                        self.reveal(nr, nc)

    # pokaz miny (koniec)
    def reveal_all_mines(self, color):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.buttons[r][c].config(text="X", font=(32), bg=color)

    # sprawdz czy wygrana
    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.revealed[r][c] and self.grid[r][c] != -1:
                    return
        self.game_over = True
        self.reveal_all_mines("lime")
        messagebox.showinfo("You Win", "Gratulacje!")

# funkcja glowna (odpala gre)

if __name__ == "__main__":
    t = tk.Tk()
    t.title("Saper")
    Minesweeper(t)
    t.mainloop()
