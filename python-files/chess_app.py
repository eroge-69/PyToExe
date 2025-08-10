"""
Simple Chess App (Windows desktop) - single-file Python PySide6 application
Features (MVP):
- Click-to-move GUI board (select source then destination)
- Legal-move highlighting
- Move list (algebraic SAN)
- Play vs Stockfish engine (requires a Stockfish binary placed beside this script or path configured)
- Human vs Human on same machine
- Undo, Save PGN, Load PGN
- Adjustable engine move time (ms)

Dependencies:
- Python 3.8+
- PySide6
- python-chess

Install:
    pip install PySide6 python-chess

Run:
    python chess_app.py

Place a Stockfish binary named `stockfish.exe` (or `stockfish`) in the same folder, or change ENGINE_PATH below.

This file is intentionally single-file for easy packaging with PyInstaller:
    pyinstaller --onefile chess_app.py

"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QFileDialog, QMessageBox, QSpinBox, QComboBox
)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt, Signal, QObject

import chess
import chess.pgn

# === Config ===
ENGINE_PATH = "stockfish.exe"  # change path if needed
DEFAULT_ENGINE_MOVETIME_MS = 500

# Unicode pieces (white and black)
UNICODE_PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# Helper: map chess square to row/col for GUI grid
def square_to_coords(square_index):
    # chess.SQUARES: a1=0 ... h8=63. We'll render with rank 8 at top (row 0)
    file = chess.square_file(square_index)  # 0..7 (a..h)
    rank = chess.square_rank(square_index)  # 0..7 (1..8)
    row = 7 - rank
    col = file
    return row, col

def coords_to_square(row, col):
    rank = 7 - row
    file = col
    return chess.square(file, rank)

# === Engine wrapper ===
class StockfishEngine(QObject):
    bestmove_signal = Signal(str)

    def __init__(self, path=ENGINE_PATH):
        super().__init__()
        self.path = path
        self.proc = None
        self.lock = threading.Lock()
        self.reader_thread = None
        self.running = False

    def start(self):
        if self.proc:
            return True
        if not Path(self.path).exists():
            return False
        try:
            self.proc = subprocess.Popen([self.path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            # init
            self._send_line('uci')
            time.sleep(0.05)
            return True
        except Exception as e:
            print('Engine start failed:', e)
            self.proc = None
            return False

    def _read_loop(self):
        try:
            while self.proc and self.running:
                line = self.proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                # parse bestmove
                if line.startswith('bestmove'):
                    parts = line.split()
                    if len(parts) >= 2:
                        self.bestmove_signal.emit(parts[1])
        except Exception as e:
            print('Engine read loop error:', e)

    def _send_line(self, s: str):
        try:
            if not self.proc:
                return
            self.proc.stdin.write(s + '\n')
            self.proc.stdin.flush()
        except Exception as e:
            print('Engine send failed:', e)

    def set_position(self, board: chess.Board):
        fen = board.fen()
        self._send_line(f'position fen {fen}')

    def go_movetime(self, ms: int):
        self._send_line(f'go movetime {int(ms)}')

    def stop(self):
        if self.proc:
            self.running = False
            try:
                self._send_line('quit')
            except:
                pass
            self.proc = None

    def is_available(self):
        return Path(self.path).exists()

# === Main Application ===
class ChessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chess — PySide6')
        self.resize(900, 600)

        self.board = chess.Board()
        self.selected_square = None
        self.buttons = {}  # (row,col) -> QPushButton

        # Engine
        self.engine = StockfishEngine()
        self.engine.bestmove_signal.connect(self.on_engine_bestmove)
        self.playing_vs_engine = False
        self.engine_thinking = False
        self.engine_movetime_ms = DEFAULT_ENGINE_MOVETIME_MS

        # UI setup
        main_layout = QHBoxLayout()

        left_col = QVBoxLayout()
        board_widget = QWidget()
        board_layout = QGridLayout()
        board_layout.setSpacing(0)
        board_widget.setLayout(board_layout)

        btn_font = QFont('Segoe UI Emoji', 32)

        for row in range(8):
            for col in range(8):
                btn = QPushButton('')
                btn.setFixedSize(64, 64)
                btn.setFont(btn_font)
                btn.setFocusPolicy(Qt.NoFocus)
                board_layout.addWidget(btn, row, col)
                self.buttons[(row, col)] = btn
                btn.clicked.connect(self._make_on_click(row, col))

        left_col.addWidget(board_widget)

        # Controls under board
        ctrl_row = QHBoxLayout()
        self.undo_btn = QPushButton('Undo')
        self.undo_btn.clicked.connect(self.on_undo)
        ctrl_row.addWidget(self.undo_btn)

        self.new_btn = QPushButton('New Game')
        self.new_btn.clicked.connect(self.on_new_game)
        ctrl_row.addWidget(self.new_btn)

        self.save_btn = QPushButton('Save PGN')
        self.save_btn.clicked.connect(self.on_save_pgn)
        ctrl_row.addWidget(self.save_btn)

        self.load_btn = QPushButton('Load PGN')
        self.load_btn.clicked.connect(self.on_load_pgn)
        ctrl_row.addWidget(self.load_btn)

        left_col.addLayout(ctrl_row)

        main_layout.addLayout(left_col)

        # Right side: move list + engine options
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel('Moves'))
        self.move_list = QListWidget()
        right_col.addWidget(self.move_list)

        # Engine controls
        right_col.addWidget(QLabel('Engine'))
        eng_row = QHBoxLayout()
        self.vs_engine_combo = QComboBox()
        self.vs_engine_combo.addItems(['Human vs Human', 'Play vs Engine'])
        self.vs_engine_combo.currentIndexChanged.connect(self.on_mode_change)
        eng_row.addWidget(self.vs_engine_combo)

        right_col.addLayout(eng_row)

        eng_opts = QHBoxLayout()
        eng_opts.addWidget(QLabel('Move time (ms):'))
        self.movetime_spin = QSpinBox()
        self.movetime_spin.setRange(50, 20000)
        self.movetime_spin.setValue(self.engine_movetime_ms)
        self.movetime_spin.valueChanged.connect(self.on_movetime_change)
        eng_opts.addWidget(self.movetime_spin)

        right_col.addLayout(eng_opts)

        start_eng_btn = QPushButton('Start Engine (check path)')
        start_eng_btn.clicked.connect(self.on_start_engine)
        right_col.addWidget(start_eng_btn)

        right_col.addStretch()

        # Status bar label
        self.status_label = QLabel('Ready')
        right_col.addWidget(self.status_label)

        main_layout.addLayout(right_col)

        self.setLayout(main_layout)

        self.update_board_ui()

    # === UI helpers ===
    def _make_on_click(self, row, col):
        def handler():
            self.on_square_clicked(row, col)
        return handler

    def on_square_clicked(self, row, col):
        sq = coords_to_square(row, col)
        piece = self.board.piece_at(sq)
        # If nothing selected and clicked on a friendly piece -> select
        if self.selected_square is None:
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = sq
                self.highlight_legal_moves(sq)
            else:
                # clicked empty or opponent
                pass
        else:
            # try make move from selected_square -> sq
            move = chess.Move(self.selected_square, sq)
            if move in self.board.legal_moves:
                self.make_move(move)
                self.selected_square = None
                self.clear_highlights()
                # If playing vs engine and it's engine's turn, ask engine
                if self.playing_vs_engine and self.board.turn == chess.BLACK:
                    self.request_engine_move()
            else:
                # If clicked another friendly piece, change selection
                if piece is not None and piece.color == self.board.turn:
                    self.selected_square = sq
                    self.highlight_legal_moves(sq)
                else:
                    # invalid target
                    self.selected_square = None
                    self.clear_highlights()
            
        self.update_board_ui()

    def highlight_legal_moves(self, from_sq):
        self.clear_highlights()
        for mv in self.board.legal_moves:
            if mv.from_square == from_sq:
                r, c = square_to_coords(mv.to_square)
                btn = self.buttons[(r, c)]
                btn.setStyleSheet('background-color: #a0e7a0')
        # highlight from
        r0, c0 = square_to_coords(from_sq)
        self.buttons[(r0, c0)].setStyleSheet('background-color: #f4d06f')

    def clear_highlights(self):
        for row in range(8):
            for col in range(8):
                btn = self.buttons[(row, col)]
                self._set_square_color(btn, row, col)

    def _set_square_color(self, btn: QPushButton, row: int, col: int):
        light = (row + col) % 2 == 0
        if light:
            btn.setStyleSheet('background-color: #f0d9b5')
        else:
            btn.setStyleSheet('background-color: #b58863')

    def update_board_ui(self):
        for square in chess.SQUARES:
            row, col = square_to_coords(square)
            btn = self.buttons[(row, col)]
            piece = self.board.piece_at(square)
            if piece is None:
                btn.setText('')
            else:
                btn.setText(UNICODE_PIECES[piece.symbol()])
            self._set_square_color(btn, row, col)
        # update move list
        self.move_list.clear()
        game = chess.pgn.Game()
        node = game
        temp_board = chess.Board()
        for mv in self.board.move_stack:
            node = node.add_variation(mv)
        exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
        pgn_text = game.accept(exporter)
        # quick parse moves into list
        san_moves = []
        temp_board = chess.Board()
        for mv in self.board.move_stack:
            san = temp_board.san(mv)
            san_moves.append(san)
            temp_board.push(mv)
        # display with move numbers
        lines = []
        i = 0
        while i < len(san_moves):
            num = i//2 + 1
            white = san_moves[i]
            black = san_moves[i+1] if i+1 < len(san_moves) else ''
            self.move_list.addItem(f'{num}. {white} {black}')
            i += 2

    # === Game actions ===
    def make_move(self, move: chess.Move):
        # handle promotions: if move is promotion without piece set, default to Queen
        if chess.Move.null() == move:
            return
        if move.promotion is None and self.board.is_legal(move) and chess.square_rank(move.to_square) in (0,7) and self.board.piece_at(move.from_square).piece_type == chess.PAWN:
            # promotion required — default to queen
            move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
        self.board.push(move)
        self.update_board_ui()
        self.status_label.setText(f"Turn: {'White' if self.board.turn==chess.WHITE else 'Black'}")

    def on_undo(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()
            # if playing vs engine, also pop engine move (to revert to human's turn)
            if self.playing_vs_engine and len(self.board.move_stack) > 0 and self.board.turn == chess.BLACK:
                # try to pop one more (best-effort)
                try:
                    self.board.pop()
                except Exception:
                    pass
            self.update_board_ui()

    def on_new_game(self):
        self.board.reset()
        self.selected_square = None
        self.update_board_ui()
        self.status_label.setText('New game')

    def on_save_pgn(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save PGN', filter='PGN Files (*.pgn)')
        if not path:
            return
        game = chess.pgn.Game()
        node = game
        for mv in self.board.move_stack:
            node = node.add_variation(mv)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(game))
        QMessageBox.information(self, 'Saved', f'Saved PGN to: {path}')

    def on_load_pgn(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open PGN', filter='PGN Files (*.pgn)')
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                game = chess.pgn.read_game(f)
            board = game.board()
            self.board.reset()
            for mv in game.mainline_moves():
                self.board.push(mv)
            self.update_board_ui()
            QMessageBox.information(self, 'Loaded', f'Loaded PGN from: {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load PGN: {e}')

    # === Engine interactions ===
    def on_mode_change(self, idx):
        self.playing_vs_engine = (idx == 1)
        self.status_label.setText('Mode: ' + ('Play vs Engine' if self.playing_vs_engine else 'Human vs Human'))
        # start engine if mode is vs engine and engine binary available
        if self.playing_vs_engine and not self.engine.is_available():
            QMessageBox.warning(self, 'Engine missing', f'Stockfish binary not found at {self.engine.path}. Please download and put it next to this script, or change ENGINE_PATH in the source.')

    def on_movetime_change(self, val):
        self.engine_movetime_ms = val

    def on_start_engine(self):
        ok = self.engine.start()
        if ok:
            QMessageBox.information(self, 'Engine', 'Engine started successfully (listening).')
        else:
            QMessageBox.critical(self, 'Engine', f'Could not start engine binary at: {self.engine.path}')

    def request_engine_move(self):
        if not self.engine.start():
            QMessageBox.critical(self, 'Engine', 'Engine not available. Place stockfish binary and press "Start Engine".')
            return
        # send position
        self.engine.set_position(self.board)
        self.engine.go_movetime(self.engine_movetime_ms)
        self.engine_thinking = True
        self.status_label.setText('Engine thinking...')

    def on_engine_bestmove(self, uci_move: str):
        # Called from engine reader thread via signal
        try:
            mv = chess.Move.from_uci(uci_move)
            if mv in self.board.legal_moves:
                # Execute on main thread using Qt signal/slot, but this method runs on main thread due to signal
                self.board.push(mv)
                self.update_board_ui()
                self.status_label.setText('Engine moved')
            else:
                print('Engine suggested illegal move', uci_move)
        except Exception as e:
            print('Failed to apply engine move:', e)
        finally:
            self.engine_thinking = False

# === Launch ===

def main():
    app = QApplication(sys.argv)

    # Optional: set dark palette by default
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)

    w = ChessApp()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
