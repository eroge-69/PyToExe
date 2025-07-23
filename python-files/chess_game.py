import tkinter as tk
from tkinter import messagebox
import chess
import random

# --- Constants ---
BOARD_SIZE = 480  # Size of the board in pixels
SQUARE_SIZE = BOARD_SIZE // 8
PIECE_UNICODE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# --- Dark Theme Colors ---
DARK_BG = "#2E2E2E"        # Dark gray background
LIGHT_FG = "#EAEAEA"       # Light gray foreground (text)
BOARD_LIGHT = "#B58863"     # Wood-like light squares (adjust if needed)
BOARD_DARK = "#5C4033"      # Wood-like dark squares (adjust if needed)
PIECE_LIGHT = "#FFFFFF"    # White pieces
PIECE_DARK = "#1E1E1E"     # Off-black pieces (contrast better than pure black sometimes)
HIGHLIGHT_COLOR = "#FFD700" # Gold/Yellow for selection
BUTTON_BG = "#444444"       # Darker button background
BUTTON_FG = LIGHT_FG
BUTTON_ACTIVE_BG = "#555555" # Slightly lighter when pressed
LABEL_FONT = ("Segoe UI", 12) # Use a potentially smoother font if available
TITLE_FONT = ("Segoe UI", 16, "bold")
BUTTON_FONT = ("Segoe UI", 10)
PIECE_FONT_FAMILY = "DejaVu Sans" # Good font for Unicode pieces if available

# --- Main Application Class ---
class ChessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Chess (Dark Theme)")
        self.geometry(f"{BOARD_SIZE + 50}x{BOARD_SIZE + 120}") # Increased height slightly for padding
        self.resizable(False, False)
        self.config(bg=DARK_BG) # Set main window background

        self.game_mode = None # '2P' or '1P'
        self.board = chess.Board()
        self.selected_square = None
        self.player_can_move = True # Used in 1P mode

        # --- Frames ---
        # Configure frames with dark background
        self.mode_selection_frame = tk.Frame(self, bg=DARK_BG)
        self.game_frame = tk.Frame(self, bg=DARK_BG)
        self.game_over_frame = tk.Frame(self, bg=DARK_BG)

        self._create_mode_selection_widgets()
        self._create_game_widgets()
        self._create_game_over_widgets()

        # --- Start with Mode Selection ---
        self.show_mode_selection()

    # --- Screen Management ---
    def show_mode_selection(self):
        self.game_frame.pack_forget()
        self.game_over_frame.pack_forget()
        self.mode_selection_frame.pack(pady=30, padx=20, fill="both", expand=True) # Add padding
        self.board = chess.Board() # Reset board
        self.selected_square = None
        self.player_can_move = True
        self.title("Python Chess - Select Mode")

    def show_game(self):
        self.mode_selection_frame.pack_forget()
        self.game_over_frame.pack_forget()
        self.game_frame.pack(pady=10, padx=10) # Add padding
        self.update_board_ui()
        self.update_status()
        self.title("Python Chess (Dark Theme)")

    def show_game_over(self, message):
        self.lbl_game_over_message.config(text=message)
        self.game_frame.pack_forget()
        self.mode_selection_frame.pack_forget()
        self.game_over_frame.pack(pady=50, padx=20, fill="both", expand=True) # Add padding
        self.title("Python Chess - Game Over")

    def _apply_button_style(self, button):
        """Applies consistent styling to buttons."""
        button.config(
            font=BUTTON_FONT,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=LIGHT_FG,
            relief=tk.FLAT, # Modern flat look
            borderwidth=1,
            pady=5 # Add vertical padding inside button
        )

    # --- Widget Creation ---
    def _create_mode_selection_widgets(self):
        tk.Label(
            self.mode_selection_frame,
            text="Select Game Mode:",
            font=TITLE_FONT,
            bg=DARK_BG,
            fg=LIGHT_FG
        ).pack(pady=(10, 20)) # Top and bottom padding

        btn_2p = tk.Button(
            self.mode_selection_frame,
            text="2 Players (Local)",
            width=20,
            command=lambda: self.start_game('2P')
        )
        self._apply_button_style(btn_2p)
        btn_2p.pack(pady=8)

        btn_1p = tk.Button(
            self.mode_selection_frame,
            text="1 Player vs Computer",
            width=20,
            command=lambda: self.start_game('1P')
        )
        self._apply_button_style(btn_1p)
        btn_1p.pack(pady=8)

        btn_exit_mode = tk.Button(
            self.mode_selection_frame,
            text="Exit",
            width=20,
            command=self.quit
        )
        self._apply_button_style(btn_exit_mode)
        btn_exit_mode.pack(pady=(25, 10))

    def _create_game_widgets(self):
        # Board Canvas - Set border to 0 and background for consistency
        self.canvas = tk.Canvas(
            self.game_frame,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg=DARK_BG,
            highlightthickness=0 # Remove canvas border
        )
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_square_click)

        # Status Label
        self.status_label = tk.Label(
            self.game_frame,
            text="",
            font=LABEL_FONT,
            bg=DARK_BG,
            fg=LIGHT_FG
        )
        self.status_label.pack(pady=8)

    def _create_game_over_widgets(self):
        self.lbl_game_over_message = tk.Label(
            self.game_over_frame,
            text="",
            font=TITLE_FONT,
            bg=DARK_BG,
            fg=LIGHT_FG
        )
        self.lbl_game_over_message.pack(pady=(20, 30))

        btn_restart = tk.Button(
            self.game_over_frame,
            text="Restart Game",
            width=15,
            command=self.show_mode_selection
        )
        self._apply_button_style(btn_restart)
        btn_restart.pack(pady=8)

        btn_exit_over = tk.Button(
            self.game_over_frame,
            text="Exit",
            width=15,
            command=self.quit
        )
        self._apply_button_style(btn_exit_over)
        btn_exit_over.pack(pady=8)

    # --- Game Initialization ---
    def start_game(self, mode):
        self.game_mode = mode
        self.show_game()

    # --- Board Drawing ---
    def update_board_ui(self):
        self.canvas.delete("all")
        self._draw_board_squares()
        self._draw_pieces()
        if self.selected_square is not None:
            self._highlight_square(self.selected_square, HIGHLIGHT_COLOR) # Use theme highlight

    def _draw_board_squares(self):
        for r in range(8):
            for c in range(8):
                # Use dark theme board colors
                color = BOARD_LIGHT if (r + c) % 2 == 0 else BOARD_DARK
                x0, y0 = c * SQUARE_SIZE, r * SQUARE_SIZE
                x1, y1 = x0 + SQUARE_SIZE, y0 + SQUARE_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="") # No outline between squares

    def _draw_pieces(self):
        for square_index in range(64):
            piece = self.board.piece_at(square_index)
            if piece:
                row, col = divmod(square_index, 8)
                tk_row = 7 - row # Convert chess row to tkinter row
                x, y = col * SQUARE_SIZE, tk_row * SQUARE_SIZE
                self._draw_unicode_piece(piece, x, y)

    def _draw_unicode_piece(self, piece, x, y):
         piece_char = PIECE_UNICODE.get(piece.symbol(), "?")
         # Use theme piece colors
         color = PIECE_LIGHT if piece.color == chess.WHITE else PIECE_DARK
         font_size = int(SQUARE_SIZE * 0.7) # Scale font size with board

         # Try preferred font first, then fallbacks
         try:
             self.canvas.create_text(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2,
                                    text=piece_char,
                                    font=(PIECE_FONT_FAMILY, font_size, "bold"),
                                    fill=color, anchor=tk.CENTER)
         except tk.TclError: # Font not found, fallback
              try:
                  self.canvas.create_text(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2,
                                     text=piece_char,
                                     font=("Arial", font_size, "bold"), # Common fallback
                                     fill=color, anchor=tk.CENTER)
              except tk.TclError: # Last resort default Tk font
                   self.canvas.create_text(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2,
                                     text=piece_char,
                                     font=(None, font_size, "bold"),
                                     fill=color, anchor=tk.CENTER)

    def _highlight_square(self, square_index, color):
        row, col = divmod(square_index, 8)
        tk_row = 7 - row
        x0, y0 = col * SQUARE_SIZE, tk_row * SQUARE_SIZE
        x1, y1 = x0 + SQUARE_SIZE, y0 + SQUARE_SIZE
        # Draw a slightly thicker outline for highlight
        self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, width=3)

    # --- User Interaction ---
    def _on_square_click(self, event):
        if not self.player_can_move:
            return

        col = event.x // SQUARE_SIZE
        if not (0 <= col < 8): return
        tk_row_click = event.y // SQUARE_SIZE
        if not (0 <= tk_row_click < 8): return

        row = 7 - tk_row_click
        square_index = chess.square(col, row)
        piece = self.board.piece_at(square_index)

        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square_index
                self.update_board_ui()
            # No else needed, just ignore clicks on empty/opponent squares for first click
        else:
            move = self._create_move(self.selected_square, square_index)
            is_legal_move = False
            try:
                is_legal_move = move in self.board.legal_moves
            except Exception as e:
                print(f"Error checking move legality: {e}")

            if is_legal_move:
                self._make_move(move)
                if self.game_mode == '1P' and self.board.turn == chess.BLACK and not self.board.is_game_over():
                    self.player_can_move = False
                    self.update_status()
                    self.status_label.config(text="Computer is thinking...")
                    self.after(500, self._make_computer_move)
            else:
                if square_index == self.selected_square: # Clicked selected square again to deselect
                     self.selected_square = None
                     self.update_board_ui()
                elif piece and piece.color == self.board.turn: # Clicked another own piece to switch selection
                    self.selected_square = square_index
                    self.update_board_ui()
                else: # Clicked invalid target or empty square, deselect
                    self.selected_square = None
                    self.update_board_ui()

    def _create_move(self, from_square, to_square):
        """ Creates a chess.Move object, handling promotion """
        piece = self.board.piece_at(from_square)
        move = chess.Move(from_square, to_square)

        if piece and piece.piece_type == chess.PAWN:
            if (piece.color == chess.WHITE and chess.square_rank(to_square) == 7) or \
               (piece.color == chess.BLACK and chess.square_rank(to_square) == 0):
                 move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
        return move

    # --- Game Logic ---
    def _make_move(self, move):
        try:
            self.board.push(move)
        except Exception as e:
             print(f"Error pushing move {move.uci()}: {e}")
             print(f"Board state:\n{self.board.fen()}")
             self.selected_square = None
             self.update_board_ui()
             self.update_status()
             return

        self.selected_square = None
        # Check status *before* potentially blocking UI thread with computer move
        is_over = self.check_game_status()
        # Update UI *after* pushing move
        self.update_board_ui()
        if not is_over:
             self.update_status()


    def _make_computer_move(self):
        if not self.board.is_game_over():
            try:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    computer_move = random.choice(legal_moves)
                    self._make_move(computer_move) # This will call update_status and check_game_status
                else:
                    print("Error: Computer has no legal moves but game not over?")
                    self.check_game_status()
            except Exception as e:
                 print(f"Error during computer move generation: {e}")
                 print(f"Board state:\n{self.board.fen()}")

        # Ensure player can move again ONLY if game is not over after computer's move
        if not self.board.is_game_over():
            self.player_can_move = True
            self.update_status() # Update status to show player's turn again
        else:
             self.player_can_move = False # Prevent moves after game over


    def update_status(self):
        if self.board.is_game_over():
            self.status_label.config(text="") # Clear status on game over screen
            return

        turn_color = "White" if self.board.turn == chess.WHITE else "Black"
        status = f"{turn_color}'s Turn"

        if self.board.is_check():
            status += " (Check!)"

        # Check if it's computer's turn to think (only in 1P mode)
        if self.game_mode == '1P' and self.board.turn == chess.BLACK and not self.player_can_move:
            # This state is brief, set explicitly in _on_square_click before `after` call
            # status = "Computer is thinking..." # Handled when triggering computer move
             pass # Keep the standard 'Black's Turn' or 'Black's Turn (Check!)'

        self.status_label.config(text=status)


    def check_game_status(self):
        """ Checks game status and transitions to game over screen if needed. Returns True if game is over, False otherwise. """
        if self.board.is_game_over():
             # Delay showing game over slightly to allow last move to render
             self.after(100, self._show_game_over_screen)
             return True # Indicate game is over

        return False # Game is not over

    def _show_game_over_screen(self):
        """ Calculates outcome and displays the game over screen. """
        outcome = self.board.outcome()
        if outcome:
            result_text = "Draw"
            if outcome.winner == chess.WHITE:
                result_text = "White Wins"
            elif outcome.winner == chess.BLACK:
                result_text = "Black Wins"

            termination_reason = ""
            if outcome.termination == chess.Termination.CHECKMATE:
                termination_reason = "by Checkmate!"
            elif outcome.termination == chess.Termination.STALEMATE:
                termination_reason = "by Stalemate"
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                termination_reason = "by Insufficient Material"
            elif outcome.termination == chess.Termination.SEVENTYFIVE_MOVES:
                termination_reason = "by 75 Move Rule"
            elif outcome.termination == chess.Termination.FIVEFOLD_REPETITION:
                termination_reason = "by Fivefold Repetition"
            # Add other specific reasons if desired

            message = f"{result_text} {termination_reason}"
            self.show_game_over(message.strip())
        else:
             # Fallback if outcome is None but board says game over
             print("Game is over but no outcome determined? Board FEN:", self.board.fen())
             self.show_game_over("Game Over - Unknown Reason")


# --- Run the Application ---
if __name__ == "__main__":
    # You still need python-chess installed:
    # pip install python-chess

    app = ChessApp()
    app.mainloop()