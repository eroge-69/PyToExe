# chess_gui.py
# A complete playable chess program with GUI (tkinter) for Windows
# Adds: Custom piece images (cartoon LFC legends), toggle between Unicode and images,
# full legal moves, basic AI (minimax + alpha-beta), themes, side/depth controls.

import copy
import time
import os
import tkinter as tk
from tkinter import messagebox

# --- Optional auto-resize with Pillow (recommended) ---
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------------------- Chess Engine Core ---------------------- #

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

VALS = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': 0
}

GLYPHS = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
}

DIRS_BISHOP = [(-1,-1), (-1,1), (1,-1), (1,1)]
DIRS_ROOK   = [(-1,0), (1,0), (0,-1), (0,1)]
DIRS_QUEEN  = DIRS_BISHOP + DIRS_ROOK
KNIGHT_STEPS = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

class GameState:
    def __init__(self):
        self.board = [[None]*8 for _ in range(8)]
        self.white_to_move = True
        self.castling = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1
        self.history = []

    @staticmethod
    def from_fen(fen: str):
        gs = GameState()
        parts = fen.split()
        board_fen, stm, castling, ep, half, full = parts
        rows = board_fen.split('/')
        for r, row in enumerate(rows):
            c = 0
            for ch in row:
                if ch.isdigit():
                    c += int(ch)
                else:
                    gs.board[r][c] = ch
                    c += 1
        gs.white_to_move = (stm == 'w')
        gs.castling = {k: False for k in ['K','Q','k','q']}
        if castling != '-':
            for k in castling:
                gs.castling[k] = True
        gs.en_passant = None if ep == '-' else GameState.algebraic_to_rc(ep)
        gs.halfmove = int(half)
        gs.fullmove = int(full)
        return gs

    @staticmethod
    def algebraic_to_rc(s):
        file = ord(s[0]) - ord('a')
        rank = 8 - int(s[1])
        return (rank, file)

    def king_pos(self, white: bool):
        target = 'K' if white else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == target:
                    return (r, c)
        return None

    def is_square_attacked(self, r, c, by_white: bool):
        # Pawns
        if by_white:
            for dc in (-1, 1):
                rr, cc = r+1, c+dc
                if in_bounds(rr, cc) and self.board[rr][cc] == 'P':
                    return True
        else:
            for dc in (-1, 1):
                rr, cc = r-1, c+dc
                if in_bounds(rr, cc) and self.board[rr][cc] == 'p':
                    return True
        # Knights
        for dr, dc in KNIGHT_STEPS:
            rr, cc = r+dr, c+dc
            if in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p == ('N' if by_white else 'n'):
                    return True
        # Bishops/Queens
        for dr, dc in DIRS_BISHOP:
            rr, cc = r+dr, c+dc
            while in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p in (('B','Q') if by_white else ('b','q')):
                        return True
                    break
                rr += dr; cc += dc
        # Rooks/Queens
        for dr, dc in DIRS_ROOK:
            rr, cc = r+dr, c+dc
            while in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p:
                    if p in (('R','Q') if by_white else ('r','q')):
                        return True
                    break
                rr += dr; cc += dc
        # Kings
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                rr, cc = r+dr, c+dc
                if in_bounds(rr, cc):
                    if self.board[rr][cc] == ('K' if by_white else 'k'):
                        return True
        return False

    def in_check(self, white: bool):
        kp = self.king_pos(white)
        if kp is None:
            return False
        return self.is_square_attacked(kp[0], kp[1], not white)

    def generate_pseudo_legal_moves(self):
        moves = []
        stm_white = self.white_to_move
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p or (p.isupper() != stm_white):
                    continue
                if p in ('P','p'):
                    self._gen_pawn(moves, r, c, p)
                elif p in ('N','n'):
                    self._gen_knight(moves, r, c, p)
                elif p in ('B','b'):
                    self._gen_slider(moves, r, c, p, DIRS_BISHOP)
                elif p in ('R','r'):
                    self._gen_slider(moves, r, c, p, DIRS_ROOK)
                elif p in ('Q','q'):
                    self._gen_slider(moves, r, c, p, DIRS_QUEEN)
                elif p in ('K','k'):
                    self._gen_king(moves, r, c, p)
        return moves

    def _gen_pawn(self, moves, r, c, p):
        white = p.isupper()
        dir = -1 if white else 1
        start_rank = 6 if white else 1
        promo_rank = 0 if white else 7
        rr = r + dir
        if in_bounds(rr, c) and self.board[rr][c] is None:
            if rr == promo_rank:
                for promo in ['Q','R','B','N']:
                    moves.append((r,c,rr,c,promo))
            else:
                moves.append((r,c,rr,c,None))
            if r == start_rank:
                rr2 = r + 2*dir
                if self.board[rr2][c] is None:
                    moves.append((r,c,rr2,c,'D'))
        for dc in (-1, 1):
            cc = c + dc
            rr = r + dir
            if not in_bounds(rr, cc):
                continue
            target = self.board[rr][cc]
            if target and (target.isupper() != white):
                if rr == promo_rank:
                    for promo in ['Q','R','B','N']:
                        moves.append((r,c,rr,cc,promo))
                else:
                    moves.append((r,c,rr,cc,None))
        if self.en_passant:
            er, ec = self.en_passant
            if r + dir == er and abs(c - ec) == 1:
                moves.append((r,c,er,ec,'E'))

    def _gen_knight(self, moves, r, c, p):
        white = p.isupper()
        for dr, dc in KNIGHT_STEPS:
            rr, cc = r+dr, c+dc
            if not in_bounds(rr, cc):
                continue
            target = self.board[rr][cc]
            if target is None or (target.isupper() != white):
                moves.append((r,c,rr,cc,None))

    def _gen_slider(self, moves, r, c, p, dirs):
        white = p.isupper()
        for dr, dc in dirs:
            rr, cc = r+dr, c+dc
            while in_bounds(rr, cc):
                target = self.board[rr][cc]
                if target is None:
                    moves.append((r,c,rr,cc,None))
                else:
                    if target.isupper() != white:
                        moves.append((r,c,rr,cc,None))
                    break
                rr += dr; cc += dc

    def _gen_king(self, moves, r, c, p):
        white = p.isupper()
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                rr, cc = r+dr, c+dc
                if not in_bounds(rr, cc):
                    continue
                target = self.board[rr][cc]
                if target is None or (target.isupper() != white):
                    moves.append((r,c,rr,cc,None))
        if white:
            if self.castling.get('K') and self.board[7][5] is None and self.board[7][6] is None:
                if not self.in_check(True) and not self.is_square_attacked(7,5,False) and not self.is_square_attacked(7,6,False):
                    moves.append((r,c,7,6,'C'))
            if self.castling.get('Q') and self.board[7][1] is None and self.board[7][2] is None and self.board[7][3] is None:
                if not self.in_check(True) and not self.is_square_attacked(7,2,False) and not self.is_square_attacked(7,3,False):
                    moves.append((r,c,7,2,'c'))
        else:
            if self.castling.get('k') and self.board[0][5] is None and self.board[0][6] is None:
                if not self.in_check(False) and not self.is_square_attacked(0,5,True) and not self.is_square_attacked(0,6,True):
                    moves.append((r,c,0,6,'C'))
            if self.castling.get('q') and self.board[0][1] is None and self.board[0][2] is None and self.board[0][3] is None:
                if not self.in_check(False) and not self.is_square_attacked(0,2,True) and not self.is_square_attacked(0,3,True):
                    moves.append((r,c,0,2,'c'))

    def make_move(self, move):
        r1,c1,r2,c2,flag = move
        piece = self.board[r1][c1]
        target = self.board[r2][c2]
        white = piece.isupper()
        prev = (self.castling.copy(), self.en_passant, self.halfmove, self.fullmove)
        self.history.append((r1,c1,r2,c2,flag,target,prev))

        if piece.upper() == 'P' or target is not None or (flag == 'E'):
            self.halfmove = 0
        else:
            self.halfmove += 1

        if flag == 'E':
            dir = -1 if white else 1
            self.board[r2 - dir][c2] = None

        self.board[r2][c2] = piece
        self.board[r1][c1] = None

        if flag in ('Q','R','B','N'):
            self.board[r2][c2] = flag if white else flag.lower()

        if flag == 'C':
            if white:
                self.board[7][5] = 'R'; self.board[7][7] = None
            else:
                self.board[0][5] = 'r'; self.board[0][7] = None
        elif flag == 'c':
            if white:
                self.board[7][3] = 'R'; self.board[7][0] = None
            else:
                self.board[0][3] = 'r'; self.board[0][0] = None

        if flag == 'D':
            dir = -1 if white else 1
            self.en_passant = (r2 - dir, c2)
        else:
            self.en_passant = None

        if piece == 'K':
            self.castling['K'] = False; self.castling['Q'] = False
        if piece == 'k':
            self.castling['k'] = False; self.castling['q'] = False

        if (r1, c1) == (7, 7) or (r2, c2) == (7, 7) and target == 'R':
            self.castling['K'] = False
        if (r1, c1) == (7, 0) or (r2, c2) == (7, 0) and target == 'R':
            self.castling['Q'] = False
        if (r1, c1) == (0, 7) or (r2, c2) == (0, 7) and target == 'r':
            self.castling['k'] = False
        if (r1, c1) == (0, 0) or (r2, c2) == (0, 0) and target == 'r':
            self.castling['q'] = False

        self.white_to_move = not self.white_to_move
        if not self.white_to_move:
            self.fullmove += 1

    def undo_move(self):
        if not self.history:
            return
        r1,c1,r2,c2,flag,captured,prev = self.history.pop()
        piece = self.board[r2][c2]
        white = piece.isupper()
        self.white_to_move = not self.white_to_move
        if self.white_to_move:
            self.fullmove -= 1
        if flag in ('Q','R','B','N'):
            piece = 'P' if white else 'p'
        self.board[r1][c1] = piece
        self.board[r2][c2] = captured
        if flag == 'E':
            dir = -1 if white else 1
            self.board[r2 - dir][c2] = 'p' if white else 'P'
        if flag == 'C':
            if white:
                self.board[7][7] = 'R'; self.board[7][5] = None
            else:
                self.board[0][7] = 'r'; self.board[0][5] = None
        if flag == 'c':
            if white:
                self.board[7][0] = 'R'; self.board[7][3] = None
            else:
                self.board[0][0] = 'r'; self.board[0][3] = None
        self.castling, self.en_passant, self.halfmove, self.fullmove = prev

    def legal_moves(self):
        legal = []
        for mv in self.generate_pseudo_legal_moves():
            self.make_move(mv)
            in_check = self.in_check(not self.white_to_move)
            if not in_check:
                legal.append(mv)
            self.undo_move()
        return legal

    def result(self):
        moves = self.legal_moves()
        if moves:
            if self.halfmove >= 100:
                return True, 'Draw by 50-move rule'
            return False, ''
        if self.in_check(self.white_to_move):
            return True, 'Checkmate! ' + ('Black' if self.white_to_move else 'White') + ' wins'
        else:
            return True, 'Stalemate'

    def evaluate(self):
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p: continue
                score += VALS[p]
                if p.upper() in ('N','B','Q'):
                    center_dist = (abs(3.5 - r) + abs(3.5 - c))
                    bonus = 6 - center_dist
                    score += bonus if p.isupper() else -bonus
                if p.upper() == 'P':
                    bonus = (6 - r) if p.isupper() else (r - 1)
                    score += 0.5 * (bonus if p.isupper() else -bonus)
        return score

    def best_move(self, depth, time_limit_ms=3000):
        start = time.time()
        alpha = -10_000_000
        beta = 10_000_000
        best = None
        best_score = alpha

        moves = self.legal_moves()
        def move_key(m):
            r1,c1,r2,c2,f = m
            cap = 1 if self.board[r2][c2] is not None or f in ('E',) else 0
            promo = 1 if f in ('Q','R','B','N') else 0
            return -(cap*2 + promo)
        moves.sort(key=move_key)

        for mv in moves:
            self.make_move(mv)
            score = -self._search(depth-1, -beta, -alpha, start, time_limit_ms)
            self.undo_move()
            if score > best_score:
                best_score = score; best = mv
            if best_score > alpha:
                alpha = best_score
            if time.time() - start > time_limit_ms/1000.0:
                break
        return best

    def _search(self, depth, alpha, beta, start, time_limit_ms):
        if time.time() - start > time_limit_ms/1000.0:
            return self.evaluate()
        finished, msg = self.result()
        if finished:
            if msg.startswith('Checkmate'):
                return -990000
            return 0
        if depth == 0:
            return self.evaluate()
        best = -10_000_000
        moves = self.legal_moves()
        def move_key(m):
            r1,c1,r2,c2,f = m
            cap = 1 if self.board[r2][c2] is not None or f in ('E',) else 0
            promo = 1 if f in ('Q','R','B','N') else 0
            return -(cap*2 + promo)
        moves.sort(key=move_key)
        for mv in moves:
            self.make_move(mv)
            score = -self._search(depth-1, -beta, -alpha, start, time_limit_ms)
            self.undo_move()
            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best

# ---------------------- GUI + Custom Pieces ---------------------- #

SQUARE_SIZE = 80
BOARD_SIZE = 8 * SQUARE_SIZE
FONT_FAMILY = 'Segoe UI Symbol'  # Windows font with chess glyphs

POP_ART_THEME = {
    'light': '#FFD166',
    'dark':  '#06D6A0',
    'bg':    '#073B4C',
    'highlight': '#EF476F',
    'move': '#118AB2',
}

CLASSIC_THEME = {
    'light': '#EEEED2',
    'dark':  '#769656',
    'bg':    '#333333',
    'highlight': '#BACA2B',
    'move': '#E07A5F',
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'liverpool')

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Chess (Python, Tkinter) – LFC Cartoon Pieces')
        self.theme = POP_ART_THEME

        self.gs = GameState.from_fen(START_FEN)
        self.human_is_white = True
        self.ai_depth = 3
        self.ai_thinking = False

        # --- Piece rendering mode ---
        self.use_images = False
        self.tk_images = {}   # cache: {'wP': PhotoImage, ...}

        # Layout
        self.frame = tk.Frame(root, bg=self.theme['bg'])
        self.frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame, width=BOARD_SIZE, height=BOARD_SIZE,
                                bg=self.theme['bg'], highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=8)

        controls = tk.Frame(self.frame, bg=self.theme['bg'])
        controls.grid(row=0, column=1, sticky='nw', padx=10)

        self.status_var = tk.StringVar()
        self.status = tk.Label(controls, textvariable=self.status_var, fg='white', bg=self.theme['bg'])
        self.status.pack(anchor='w', pady=(0,10))

        self.side_var = tk.StringVar(value='White')
        tk.Label(controls, text='Play as:', fg='white', bg=self.theme['bg']).pack(anchor='w')
        side_menu = tk.OptionMenu(controls, self.side_var, 'White', 'Black', command=self.on_side_change)
        side_menu.config(width=12)
        side_menu.pack(anchor='w', pady=(0,10))

        self.depth_var = tk.IntVar(value=self.ai_depth)
        tk.Label(controls, text='AI depth:', fg='white', bg=self.theme['bg']).pack(anchor='w')
        depth_menu = tk.OptionMenu(controls, self.depth_var, 1, 2, 3, 4, 5, command=self.on_depth_change)
        depth_menu.config(width=12)
        depth_menu.pack(anchor='w', pady=(0,10))

        self.theme_var = tk.StringVar(value='Pop Art')
        tk.Label(controls, text='Theme:', fg='white', bg=self.theme['bg']).pack(anchor='w')
        theme_menu = tk.OptionMenu(controls, self.theme_var, 'Pop Art', 'Classic', command=self.on_theme_change)
        theme_menu.config(width=12)
        theme_menu.pack(anchor='w', pady=(0,10))

        self.piece_mode_var = tk.StringVar(value='Unicode')
        tk.Label(controls, text='Pieces:', fg='white', bg=self.theme['bg']).pack(anchor='w')
        piece_menu = tk.OptionMenu(controls, self.piece_mode_var, 'Unicode', 'LFC Cartoons', command=self.on_piece_mode_change)
        piece_menu.config(width=12)
        piece_menu.pack(anchor='w', pady=(0,10))

        tk.Button(controls, text='New Game', command=self.new_game).pack(anchor='w', pady=(0,5))
        tk.Button(controls, text='Undo (Human)', command=self.undo_human).pack(anchor='w', pady=(0,5))
        tk.Button(controls, text='About', command=self.show_about).pack(anchor='w', pady=(0,5))

        self.canvas.bind('<Button-1>', self.on_click)

        self.selected = None
        self.legal_for_selected = []

        # Preload images if available
        if os.path.isdir(ASSETS_DIR):
            self.load_piece_images()

        self.draw()
        self.update_status()
        self.maybe_ai_move()

    # --------- Image loading ------------ #
    def load_piece_images(self):
        """Load PNGs from assets/liverpool for the 12 piece codes (w/b × P,N,B,R,Q,K)."""
        self.tk_images.clear()
        def load_one(code):
            # file name is like 'wP.png', 'bQ.png', etc.
            path = os.path.join(ASSETS_DIR, f"{code}.png")
            if not os.path.isfile(path):
                return None
            try:
                if PIL_AVAILABLE:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                else:
                    # Tkinter's PhotoImage supports PNG on Tk 8.6+ but no resize.
                    # Ensure your PNG is exactly SQUARE_SIZE x SQUARE_SIZE.
                    return tk.PhotoImage(file=path)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                return None

        for color in ('w','b'):
            for piece in ('P','N','B','R','Q','K'):
                code = color + piece
                img = load_one(code)
                if img:
                    self.tk_images[code] = img

    # --------- UI handlers ------------ #
    def on_piece_mode_change(self, *_):
        self.use_images = (self.piece_mode_var.get() == 'LFC Cartoons')
        # Try reload in case assets were just added
        if self.use_images:
            if not os.path.isdir(ASSETS_DIR):
                messagebox.showwarning('Assets missing',
                    f"Folder not found:\n{ASSETS_DIR}\n\nCreate it and add 12 PNGs named wP,wN,...,bK.")
                self.use_images = False
                self.piece_mode_var.set('Unicode')
            else:
                self.load_piece_images()
                # If any are missing, warn but still use what we have
                missing = [c for c in [a+b for a in 'wb' for b in 'PNBRQK'] if c not in self.tk_images]
                if missing:
                    messagebox.showinfo('Note',
                        f"Some piece images are missing: {', '.join(missing)}.\n"
                        "Those will fall back to Unicode.")
        self.draw()

    def on_theme_change(self, *_):
        self.theme = POP_ART_THEME if self.theme_var.get() == 'Pop Art' else CLASSIC_THEME
        self.frame.config(bg=self.theme['bg'])
        self.status.config(bg=self.theme['bg'])
        self.draw()

    def on_depth_change(self, *_):
        self.ai_depth = self.depth_var.get()

    def on_side_change(self, *_):
        self.human_is_white = (self.side_var.get() == 'White')
        self.maybe_ai_move()

    def new_game(self):
        self.gs = GameState.from_fen(START_FEN)
        self.selected = None
        self.legal_for_selected = []
        self.draw()
        self.update_status()
        self.maybe_ai_move()

    def undo_human(self):
        if self.gs.history:
            self.gs.undo_move()
            if self.gs.history:
                self.gs.undo_move()
            self.draw()
            self.update_status()

    def show_about(self):
        messagebox.showinfo(
            'About',
            'Chess in Python (Tkinter)\n'
            '• Full legal moves (castling, en passant, promotion)\n'
            '• Basic AI (minimax + alpha-beta)\n'
            '• Themes & LFC Cartoon Pieces toggle\n\n'
            'Place PNGs in assets/liverpool as wP,wN,wB,wR,wQ,wK,bP,...,bK.'
        )

    # --------- Gameplay ------------ #
    def on_click(self, event):
        if self.ai_thinking:
            return
        r = event.y // SQUARE_SIZE
        c = event.x // SQUARE_SIZE
        if not in_bounds(r, c):
            return
        p = self.gs.board[r][c]
        stm_white = self.gs.white_to_move
        human_turn = (stm_white == self.human_is_white)
        if not human_turn:
            return
        if self.selected is None:
            if p and (p.isupper() == self.human_is_white):
                self.selected = (r, c)
                self.legal_for_selected = [mv for mv in self.gs.legal_moves() if mv[0]==r and mv[1]==c]
        else:
            mv = None
            for cand in self.legal_for_selected:
                if cand[2] == r and cand[3] == c:
                    mv = cand
                    break
            if mv is None:
                if p and (p.isupper() == self.human_is_white):
                    self.selected = (r, c)
                    self.legal_for_selected = [mv for mv in self.gs.legal_moves() if mv[0]==r and mv[1]==c]
                else:
                    self.selected = None
                    self.legal_for_selected = []
                self.draw()
                return
            if mv[4] in ('Q','R','B','N'):
                promo = self.ask_promotion()
                mv = (mv[0], mv[1], mv[2], mv[3], promo)
            self.gs.make_move(mv)
            self.selected = None
            self.legal_for_selected = []
            self.draw()
            self.update_status()
            self.root.after(100, self.maybe_ai_move)
        self.draw()

    def ask_promotion(self):
        win = tk.Toplevel(self.root)
        win.title('Choose promotion')
        win.grab_set()
        choice = {'val': 'Q'}
        def set_choice(v):
            choice['val'] = v
            win.destroy()
        for piece in ['Q','R','B','N']:
            tk.Button(win, text=piece, width=6, command=lambda p=piece: set_choice(p)).pack(side='left', padx=5, pady=5)
        self.root.wait_window(win)
        return choice['val']

    def maybe_ai_move(self):
        finished, msg = self.gs.result()
        if finished:
            self.status_var.set(msg)
            return
        if self.gs.white_to_move != self.human_is_white:
            self.ai_thinking = True
            self.status_var.set('AI thinking…')
            self.root.update_idletasks()
            best = self.gs.best_move(self.ai_depth, time_limit_ms=5000)
            if best is None:
                finished, msg = self.gs.result()
                if finished:
                    self.status_var.set(msg)
            else:
                self.gs.make_move(best)
            self.ai_thinking = False
            self.draw()
            self.update_status()

    def update_status(self):
        stm = 'White' if self.gs.white_to_move else 'Black'
        finished, msg = self.gs.result()
        if finished:
            self.status_var.set(msg)
        else:
            self.status_var.set(f"{stm} to move  |  Depth {self.ai_depth}  |  Pieces: {self.piece_mode_var.get()}")

    # --------- Drawing ------------ #
    def draw(self):
        self.canvas.delete('all')
        # Squares
        for r in range(8):
            for c in range(8):
                is_light = (r + c) % 2 == 0
                color = self.theme['light'] if is_light else self.theme['dark']
                x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
                x1, y1 = x0+SQUARE_SIZE, y0+SQUARE_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
        # coords
        for c in range(8):
            file_char = chr(ord('a')+c)
            self.canvas.create_text(c*SQUARE_SIZE+5, 8*SQUARE_SIZE-5, text=file_char, anchor='sw', fill='black')
        for r in range(8):
            rank_char = str(8-r)
            self.canvas.create_text(5, r*SQUARE_SIZE+15, text=rank_char, anchor='nw', fill='black')
        # highlights
        if self.selected:
            r, c = self.selected
            x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
            self.canvas.create_rectangle(x0, y0, x0+SQUARE_SIZE, y0+SQUARE_SIZE,
                                         outline=self.theme['highlight'], width=4)
            for mv in self.legal_for_selected:
                rr, cc = mv[2], mv[3]
                cx, cy = cc*SQUARE_SIZE + SQUARE_SIZE//2, rr*SQUARE_SIZE + SQUARE_SIZE//2
                self.canvas.create_oval(cx-10, cy-10, cx+10, cy+10, fill=self.theme['move'], outline='')
        # pieces
        for r in range(8):
            for c in range(8):
                p = self.gs.board[r][c]
                if not p: continue
                x = c*SQUARE_SIZE + SQUARE_SIZE//2
                y = r*SQUARE_SIZE + SQUARE_SIZE//2
                code = ('w' if p.isupper() else 'b') + p.upper()
                if self.use_images and code in self.tk_images:
                    self.canvas.create_image(x, y, image=self.tk_images[code])
                else:
                    glyph = GLYPHS[p]
                    color = '#111111' if p.islower() else '#ffffff'
                    self.canvas.create_text(x+2, y+2, text=glyph,
                                            font=(FONT_FAMILY, SQUARE_SIZE//2 + 10), fill='#00000055')
                    self.canvas.create_text(x, y, text=glyph,
                                            font=(FONT_FAMILY, SQUARE_SIZE//2 + 10), fill=color)

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
