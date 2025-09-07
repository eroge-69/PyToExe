# othello_scenario_gui.py  (fixed 0-based 8x8 version)

import tkinter as tk
from tkinter import messagebox

# --- Model helpers -----------------------------------------------------------

def new_empty_board():
    # 8x8, 0-based indexing
    return [["E"] * 8 for _ in range(8)]

def set_starting_position(board):
    # Clear
    for r in range(8):
        for c in range(8):
            board[r][c] = "E"
    # Standard Othello start (0-based):
    # centers: (3,3)=W, (4,4)=W, (3,4)=B, (4,3)=B
    board[3][3] = "W"
    board[4][4] = "W"
    board[3][4] = "B"
    board[4][3] = "B"

def board_to_string(board, player):
    """
    65 chars: player ('W'/'B') + 64 board squares in row-major.
    Internal: 'E','W','B' -> String: 'E','O','X'
    """
    s = player
    for r in range(8):
        for c in range(8):
            ch = board[r][c]
            s += "O" if ch == "W" else "X" if ch == "B" else "E"
    return s

def string_to_board(pos_str):
    """
    Parse 65-char string (player + 64 with E/O/X) to (board, player).
    """
    if len(pos_str) != 65:
        raise ValueError("Position string must be exactly 65 characters.")
    player = pos_str[0]
    if player not in ("W", "B"):
        raise ValueError("First character must be 'W' or 'B'.")
    board = new_empty_board()
    idx = 1
    for r in range(8):
        for c in range(8):
            ch = pos_str[idx]
            if ch == "O":
                board[r][c] = "W"
            elif ch == "X":
                board[r][c] = "B"
            elif ch == "E":
                board[r][c] = "E"
            else:
                raise ValueError("Board characters must be E, O, or X.")
            idx += 1
    return board, player

# --- GUI ---------------------------------------------------------------------

class OthelloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Othello Position Builder")

        self.board = new_empty_board()
        set_starting_position(self.board)
        self.player = tk.StringVar(value="W")      # player to move
        self.brush = tk.StringVar(value="cycle")   # 'W', 'B', 'E', or 'cycle'

        container = tk.Frame(root, padx=8, pady=8)
        container.pack()

        self.board_frame = tk.Frame(container, bg="#0a5f2e", bd=4, relief="ridge")
        self.board_frame.grid(row=0, column=0, sticky="n")

        self.buttons = [[None]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                b = tk.Button(
                    self.board_frame,
                    width=3, height=1,
                    font=("Segoe UI Symbol", 18),
                    command=lambda rr=r, cc=c: self.on_click(rr, cc),
                    bg="#2f9e44", activebackground="#2b8a3e",
                    relief="flat"
                )
                b.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = b

        right = tk.Frame(container, padx=10)
        right.grid(row=0, column=1, sticky="nw")

        # Player to move
        tk.Label(right, text="Player to move:").grid(row=0, column=0, sticky="w")
        pm = tk.Frame(right)
        pm.grid(row=1, column=0, sticky="w", pady=(0,8))
        tk.Radiobutton(pm, text="White (W)", value="W", variable=self.player, command=self.refresh_output).pack(side="left")
        tk.Radiobutton(pm, text="Black (B)", value="B", variable=self.player, command=self.refresh_output).pack(side="left")

        # Brush
        tk.Label(right, text="Brush:").grid(row=2, column=0, sticky="w")
        bm = tk.Frame(right)
        bm.grid(row=3, column=0, sticky="w", pady=(0,8))
        tk.Radiobutton(bm, text="Cycle (E → B → W)", value="cycle", variable=self.brush).pack(anchor="w")
        tk.Radiobutton(bm, text="Empty (E)", value="E", variable=self.brush).pack(anchor="w")
        tk.Radiobutton(bm, text="Black (B)", value="B", variable=self.brush).pack(anchor="w")
        tk.Radiobutton(bm, text="White (W)", value="W", variable=self.brush).pack(anchor="w")

        # Presets
        presets = tk.Frame(right)
        presets.grid(row=4, column=0, sticky="w", pady=(0,8))
        tk.Button(presets, text="Starting position", command=self.apply_start).pack(side="left", padx=(0,6))
        tk.Button(presets, text="Clear board", command=self.clear_board).pack(side="left")

        # Position string output
        tk.Label(right, text="Position string (65 chars):").grid(row=5, column=0, sticky="w")
        out_row = tk.Frame(right)
        out_row.grid(row=6, column=0, sticky="we", pady=(2,6))
        self.pos_entry = tk.Entry(out_row, width=70)
        self.pos_entry.pack(side="left", fill="x", expand=True)
        tk.Button(out_row, text="Copy", command=self.copy_to_clipboard).pack(side="left", padx=6)

        # Load from string
        in_row = tk.Frame(right)
        in_row.grid(row=7, column=0, sticky="we", pady=(6,0))
        tk.Button(in_row, text="Load from string → board", command=self.load_from_string).pack(side="left")

        self.render_board()
        self.refresh_output()

    # --- UI actions ----------------------------------------------------------

    def apply_start(self):
        set_starting_position(self.board)
        self.render_board()
        self.refresh_output()

    def clear_board(self):
        for r in range(8):
            for c in range(8):
                self.board[r][c] = "E"
        self.render_board()
        self.refresh_output()

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.pos_entry.get())
        self.root.update()

    def load_from_string(self):
        s = self.pos_entry.get().strip().upper()
        try:
            board, player = string_to_board(s)
        except Exception as e:
            messagebox.showerror("Invalid string", str(e))
            return
        self.board = board
        self.player.set(player)
        self.render_board()
        self.refresh_output()

    def on_click(self, r, c):
        mode = self.brush.get()
        cur = self.board[r][c]
        if mode == "cycle":
            nxt = {"E":"B", "B":"W", "W":"E"}[cur]
            self.board[r][c] = nxt
        else:
            self.board[r][c] = mode
        self.update_button(r, c)
        self.refresh_output()

    # --- Rendering -----------------------------------------------------------

    def update_button(self, r, c):
        val = self.board[r][c]
        btn = self.buttons[r][c]
        if val == "E":
            btn.config(text=" ")
        elif val == "B":
            btn.config(text="●")  # black disc
        elif val == "W":
            btn.config(text="○")  # white disc
        else:
            btn.config(text="?")

    def render_board(self):
        for r in range(8):
            for c in range(8):
                self.update_button(r, c)

    def refresh_output(self):
        s = board_to_string(self.board, self.player.get())
        self.pos_entry.delete(0, tk.END)
        self.pos_entry.insert(0, s)

# --- Main --------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()
