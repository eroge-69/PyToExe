import chess
import chess.engine
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import traceback
import sys

try:
    # --- Create the main Tk root ---
    root = tk.Tk()
    root.title("Stockfish Chess GUI")
    root.attributes('-topmost', True)  # Always on top

    # --- Ask user to select images folder ---
    image_folder = filedialog.askdirectory(title="Select folder containing chess piece PNGs")
    if not image_folder:
        messagebox.showerror("Error", "No folder selected. Exiting.")
        root.destroy()
        sys.exit()

    # --- Ask user which color to play ---
    user_color = simpledialog.askstring("Choose Color", "Do you want to play as White or Black? (W/B)").strip().lower()
    if user_color in ['w', 'white']:
        play_white = True
    elif user_color in ['b', 'black']:
        play_white = False
    else:
        messagebox.showerror("Error", "Invalid choice. Exiting.")
        root.destroy()
        sys.exit()

    # --- Ask user to select Stockfish engine ---
    engine_path = filedialog.askopenfilename(title="Select Stockfish engine executable")
    if not engine_path:
        messagebox.showerror("Error", "No engine selected. Exiting.")
        root.destroy()
        sys.exit()

    # --- Initialize chess board and Stockfish ---
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    # --- Load piece images dynamically ---
    piece_files = {
        'P':'wP.png', 'N':'wN.png', 'B':'wB.png', 'R':'wR.png', 'Q':'wQ.png', 'K':'wK.png',
        'p':'bP.png', 'n':'bN.png', 'b':'bB.png', 'r':'bR.png', 'q':'bQ.png', 'k':'bK.png'
    }

    piece_images = {}
    for p, fname in piece_files.items():
        try:
            img = Image.open(f'{image_folder}/{fname}')
            img = img.resize((64,64), resample=Image.LANCZOS)
            piece_images[p] = ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {fname}:\n{e}")
            root.destroy()
            sys.exit()

    # --- GUI setup ---
    turn_label = tk.Label(root, text="Turn: White", font=("Consolas",14))
    turn_label.pack()

    board_frame = tk.Frame(root)
    board_frame.pack()

    cells = []
    cell_labels = []

    size = 64  # fixed size for squares
    for r in range(8):
        row_cells = []
        row_lbls = []
        for c in range(8):
            frame = tk.Frame(board_frame, width=size, height=size)
            frame.grid_propagate(False)
            frame.grid(row=r, column=c)
            lbl = tk.Label(frame, bg="bisque" if (r+c)%2==0 else "sienna")
            lbl.place(x=0, y=0, width=size, height=size)
            row_cells.append(frame)
            row_lbls.append(lbl)
        cells.append(row_cells)
        cell_labels.append(row_lbls)

    selected_square = None
    redo_stack = []
    flipped = False  # Track board orientation

    # --- Functions ---
    def check_game_over():
        if board.is_checkmate():
            if board.turn == play_white:
                messagebox.showinfo("Checkmate", "You lost! Checkmate!")
            else:
                messagebox.showinfo("Checkmate", "You won! Checkmate!")
            root.quit()
        elif board.is_stalemate() or board.is_insufficient_material():
            messagebox.showinfo("Draw", "The game is a draw!")
            root.quit()

    def update_board():
        for r in range(8):
            for c in range(8):
                draw_r = 7-r if flipped else r
                draw_c = 7-c if flipped else c
                sq = chess.square(c, 7-r)
                piece = board.piece_at(sq)
                lbl = cell_labels[draw_r][draw_c]
                lbl.config(image="", text="")
                if piece:
                    lbl.config(image=piece_images[piece.symbol()])
        turn_label.config(text="Turn: " + ("White" if board.turn else "Black"))
        check_game_over()

    def reset_square_colors():
        for r in range(8):
            for c in range(8):
                cell_labels[r][c].config(bg="bisque" if (r+c)%2==0 else "sienna")

    def stockfish_move():
        if not board.is_game_over():
            best = engine.play(board, chess.engine.Limit(depth=10))
            board.push(best.move)
            redo_stack.clear()  # any new move clears redo stack
            update_board()

    def on_click(r,c):
        global selected_square
        # map click to actual square based on flipped
        board_r = 7-r if flipped else r
        board_c = 7-c if flipped else c
        sq = chess.square(board_c, 7-board_r)
        piece = board.piece_at(sq)

        if board.turn != play_white:
            return

        if selected_square is None:
            if piece and piece.color == board.turn:
                selected_square = sq
                cell_labels[r][c].config(bg="yellow")
        else:
            move = chess.Move(selected_square, sq)
            if move in board.legal_moves:
                board.push(move)
                redo_stack.clear()  # new move clears redo stack
                selected_square = None
                reset_square_colors()
                update_board()

                if board.turn != play_white and not board.is_game_over():
                    root.after(1000, stockfish_move)
            else:
                selected_square = None
                reset_square_colors()
                update_board()

    # --- Rewind last move ---
    def rewind_move():
        if len(board.move_stack) >= 2:
            stockfish_move_undone = board.pop()
            user_move_undone = board.pop()
            redo_stack.append(user_move_undone)
            redo_stack.append(stockfish_move_undone)
            update_board()
        elif len(board.move_stack) == 1:
            redo_stack.append(board.pop())
            update_board()
        else:
            messagebox.showinfo("Rewind", "No moves to undo.")

    # --- Redo last undone move ---
    def redo_move():
        if redo_stack:
            moves_to_redo = redo_stack.copy()
            redo_stack.clear()
            for move in moves_to_redo:
                board.push(move)
            update_board()
        else:
            messagebox.showinfo("Redo", "No moves to redo.")

    # --- Flip board ---
    def flip_board():
        global flipped
        flipped = not flipped
        update_board()

    # --- Bind clicks ---
    for r in range(8):
        for c in range(8):
            cell_labels[r][c].bind("<Button-1>", lambda e,r=r,c=c: on_click(r,c))

    # --- Add buttons ---
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    rewind_btn = tk.Button(btn_frame, text="Rewind Move", command=rewind_move)
    rewind_btn.pack(side=tk.LEFT, padx=5)

    redo_btn = tk.Button(btn_frame, text="Redo Move", command=redo_move)
    redo_btn.pack(side=tk.LEFT, padx=5)

    flip_btn = tk.Button(btn_frame, text="Flip Board", command=flip_board)
    flip_btn.pack(side=tk.LEFT, padx=5)

    # --- If user is Black, let Stockfish start with delay ---
    if not play_white:
        root.after(1000, stockfish_move)

    update_board()
    root.mainloop()
    engine.quit()

except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"{e}\n\nTraceback:\n{traceback.format_exc()}")
    root.destroy()
    sys.exit(1)
