import tkinter as tk
from tkinter import messagebox

# --- Constants for styling and layout ---
BOARD_SIZE = 7
CELL_SIZE = 60
MARGIN = 20
DISCARD_AREA_WIDTH = 150

# --- Colors ---
COLOR_BG = "#D2B48C"        # Tan for the board background
COLOR_MARBLE = "#8B4513"    # SaddleBrown for marbles
COLOR_EMPTY = "#DEB887"     # BurlyWood for empty holes
COLOR_SELECTED = "#FF4500"  # OrangeRed for a selected marble

class BrainvitaGUI:
    """A GUI application for the Brainvita (Peg Solitaire) game."""

    def __init__(self, master):
        self.master = master
        self.master.title("Brainvita Game")
        self.master.resizable(False, False)
        self.master.config(bg=COLOR_BG)

        # --- Game State Variables ---
        self.selected_marble = None
        self.board_state = []
        self.discarded_count = 0

        # --- Main Canvas for Drawing ---
        canvas_width = BOARD_SIZE * CELL_SIZE + MARGIN * 2 + DISCARD_AREA_WIDTH
        canvas_height = BOARD_SIZE * CELL_SIZE + MARGIN * 2
        self.canvas = tk.Canvas(
            master,
            width=canvas_width,
            height=canvas_height,
            bg=COLOR_BG,
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # --- Reset Button ---
        reset_button = tk.Button(
            master,
            text="Reset Game",
            font=("Arial", 12, "bold"),
            command=self.reset_game
        )
        reset_button.pack(pady=(0, 10))

        # --- Initialize and draw the game ---
        self.setup_board()
        self.draw_board()

    def setup_board(self):
        """Initializes the board to the standard starting configuration."""
        # Board Legend: -1 = Invalid spot, 0 = Empty hole, 1 = Marble
        self.board_state = [
            [-1, -1, 1, 1, 1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1],
            [ 1,  1, 1, 1, 1,  1,  1],
            [ 1,  1, 1, 0, 1,  1,  1], # Center hole is empty
            [ 1,  1, 1, 1, 1,  1,  1],
            [-1, -1, 1, 1, 1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1]
        ]
        self.selected_marble = None
        self.discarded_count = 0

    def draw_board(self):
        """Draws the entire game board and the discarded marbles panel."""
        self.canvas.delete("all")

        # Draw the main game board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board_state[row][col] != -1: # Don't draw invalid corners
                    x1 = col * CELL_SIZE + MARGIN
                    y1 = row * CELL_SIZE + MARGIN
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE

                    # Draw the empty hole first
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=COLOR_EMPTY, width=2, outline=COLOR_MARBLE)

                    # If there's a marble, draw it on top
                    if self.board_state[row][col] == 1:
                        is_selected = (self.selected_marble == (row, col))
                        color = COLOR_SELECTED if is_selected else COLOR_MARBLE
                        self.canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill=color, outline="black")
        
        # Draw the discarded marbles panel on the right
        self.draw_discarded_panel()

    def draw_discarded_panel(self):
        """Draws the visual representation of discarded marbles."""
        discard_area_x = BOARD_SIZE * CELL_SIZE + MARGIN * 2
        
        self.canvas.create_text(
            discard_area_x + DISCARD_AREA_WIDTH / 2,
            MARGIN + 10,
            text="Discarded",
            font=("Arial", 16, "bold"),
            fill="black"
        )
        # Draw each discarded marble in a grid
        for i in range(self.discarded_count):
            row = i // 4
            col = i % 4
            d_cell_size = 30
            x1 = discard_area_x + 15 + col * d_cell_size
            y1 = MARGIN + 40 + row * d_cell_size
            self.canvas.create_oval(x1, y1, x1 + d_cell_size - 5, y1 + d_cell_size - 5, fill=COLOR_MARBLE, outline="black")

    def on_canvas_click(self, event):
        """Handles user clicks to select marbles and make moves."""
        col = (event.x - MARGIN) // CELL_SIZE
        row = (event.y - MARGIN) // CELL_SIZE

        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE) or self.board_state[row][col] == -1:
            self.selected_marble = None # Clicked outside board
        
        elif self.selected_marble:
            start_row, start_col = self.selected_marble
            if self.is_valid_move(start_row, start_col, row, col):
                self.make_move(start_row, start_col, row, col)
            self.selected_marble = None # Deselect after attempting a move
        
        elif self.board_state[row][col] == 1:
            self.selected_marble = (row, col) # Select a marble

        self.draw_board()
        self.master.after(100, self.check_game_over) # Brief delay to allow board to redraw

    def is_valid_move(self, r1, c1, r2, c2):
        """Checks if a move from (r1, c1) to (r2, c2) is a valid jump."""
        if self.board_state[r2][c2] != 0:
            return False # Destination must be empty

        # A valid jump is always two spaces away, horizontally or vertically
        is_horizontal_jump = (abs(c1 - c2) == 2 and r1 == r2)
        is_vertical_jump = (abs(r1 - r2) == 2 and c1 == c2)

        if not (is_horizontal_jump or is_vertical_jump):
            return False

        # Find the marble being jumped over
        jumped_row = (r1 + r2) // 2
        jumped_col = (c1 + c2) // 2
        
        # There must be a marble in the middle to jump over
        return self.board_state[jumped_row][jumped_col] == 1

    def make_move(self, r1, c1, r2, c2):
        """Executes a valid move and updates the board state."""
        jumped_row = (r1 + r2) // 2
        jumped_col = (c1 + c2) // 2

        self.board_state[r1][c1] = 0  # Starting spot is now empty
        self.board_state[jumped_row][jumped_col] = 0  # Jumped marble is removed
        self.board_state[r2][c2] = 1  # Destination now has the marble
        
        self.discarded_count += 1

    def check_game_over(self):
        """Checks for win (1 marble left) or loss (no more moves) conditions."""
        marbles_left = sum(row.count(1) for row in self.board_state)

        if marbles_left == 1:
            messagebox.showinfo("Congratulations!", "You did it!")
            self.reset_game()
            return
            
        if not self.any_valid_moves_left():
            messagebox.showwarning("Game Over", f"No more possible moves.\nMarbles left: {marbles_left}")
            self.reset_game()
            
    def any_valid_moves_left(self):
        """Scans the entire board to see if any valid moves exist."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board_state[r][c] == 1: # For each marble...
                    # ...check the four possible jump directions
                    for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                        end_r, end_c = r + dr, c + dc
                        if (0 <= end_r < BOARD_SIZE and 0 <= end_c < BOARD_SIZE and
                            self.is_valid_move(r, c, end_r, end_c)):
                            return True # Found at least one valid move
        return False # No valid moves found anywhere

    def reset_game(self):
        """Resets the game to its initial state."""
        self.setup_board()
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = BrainvitaGUI(root)
    root.mainloop()
