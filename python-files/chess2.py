import pygame
import random
from copy import deepcopy

# Pygame başlatma
pygame.init()
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 16
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Satranç Oyunu - Hata Testi")
FONT = pygame.font.SysFont("arial", 24)

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (0, 255, 0, 100)
ERROR_COLOR = (255, 0, 0)
RED_PIECE = (255, 0, 0)  # Beyaz taşlar için kırmızı
BLUE_PIECE = (0, 0, 255)  # Siyah taşlar için mavi

# Taş resimleri (yedek kare çizimi)
PIECE_IMAGES = {}  # Resim dosyaları yok, karelerle çizilecek

class Piece:
    def __init__(self, color, symbol):
        if color not in ['white', 'black']:
            raise ValueError(f"Geçersiz renk: {color}")
        if not isinstance(symbol, str) or len(symbol) != 1:
            raise ValueError(f"Geçersiz sembol: {symbol}")
        self.color = color
        self.symbol = symbol
        self.has_moved = False

    def get_valid_moves(self, x, y, board):
        return []

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, 'Q' if color == 'white' else 'q')

    def get_valid_moves(self, x, y, board):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is None:
                    moves.append((nx, ny))
                elif board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, 'R' if color == 'white' else 'r')

    def get_valid_moves(self, x, y, board):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is None:
                    moves.append((nx, ny))
                elif board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, 'B' if color == 'white' else 'b')

    def get_valid_moves(self, x, y, board):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is None:
                    moves.append((nx, ny))
                elif board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, 'N' if color == 'white' else 'n')

    def get_valid_moves(self, x, y, board):
        deltas = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        moves = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is None or board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
        return moves

class King(Piece):
    def __init__(self, color):
        super().__init__(color, 'K' if color == 'white' else 'k')

    def get_valid_moves(self, x, y, board):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is None or board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
        # Rok hareketleri
        if not self.has_moved and not board.is_in_check(self.color):
            for rook_x, rook_y in [(0, y), (board.size-1, y)]:
                rook = board.board[rook_x][rook_y]
                if isinstance(rook, Rook) and rook.color == self.color and not rook.has_moved:
                    step = 1 if rook_x > x else -1
                    clear = True
                    for i in range(x + step, rook_x, step):
                        if board.board[i][y] is not None or board.is_threatened(self.color, i, y):
                            clear = False
                            break
                    if clear and not board.is_threatened(self.color, x + step, y) and not board.is_threatened(self.color, x + 2*step, y):
                        moves.append((x + 2*step, y))
        return moves

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, 'P' if color == 'white' else 'p')

    def get_valid_moves(self, x, y, board):
        direction = -1 if self.color == 'white' else 1
        moves = []
        # İleri hareket
        if 0 <= y + direction < board.size and board.board[x][y + direction] is None:
            moves.append((x, y + direction))
            # İlk hamlede iki kare ileri
            if not self.has_moved and 0 <= y + 2*direction < board.size and board.board[x][y + 2*direction] is None:
                moves.append((x, y + 2*direction))
        # Çapraz yakalama
        for dx in [-1, 1]:
            nx = x + dx
            ny = y + direction
            if 0 <= nx < board.size and 0 <= ny < board.size:
                if board.board[nx][ny] is not None and board.board[nx][ny].color != self.color:
                    moves.append((nx, ny))
                # En passant
                if board.last_move and board.last_move[2] == nx and board.last_move[3] == ny:
                    last_piece = board.board[nx][ny]
                    if isinstance(last_piece, Pawn) and abs(board.last_move[1] - board.last_move[3]) == 2:
                        moves.append((nx, ny))
        return moves

class Board:
    def __init__(self, size=16):
        if size < 8:
            raise ValueError("Tahta boyutu en az 8x8 olmalı!")
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.move_history = []

    def place_piece(self, piece, x, y):
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise ValueError(f"Geçersiz koordinatlar: ({x}, {y})")
        if not isinstance(piece, Piece):
            raise ValueError("Geçersiz taş tipi!")
        self.board[x][y] = piece

    def move_piece(self, x1, y1, x2, y2, promotion=None):
        if not (0 <= x1 < self.size and 0 <= y1 < self.size and 0 <= x2 < self.size and 0 <= y2 < self.size):
            raise ValueError("Geçersiz hamle koordinatları!")
        piece = self.board[x1][y1]
        if piece is None:
            raise ValueError(f"({x1}, {y1}) konumunda taş yok!")
        # En passant yakalama
        if isinstance(piece, Pawn) and x1 != x2 and self.board[x2][y2] is None:
            if not (board.last_move and board.last_move[2] == x2 and board.last_move[3] == y2 and isinstance(board.board[x2][y2], Pawn)):
                raise ValueError("Geçersiz en passant hamlesi!")
            self.board[x2][y1] = None
        # Rok
        if isinstance(piece, King) and abs(x2 - x1) == 2:
            rook_x = 0 if x2 < x1 else self.size - 1
            rook_new_x = x1 + 1 if x2 > x1 else x1 - 1
            if not isinstance(self.board[rook_x][y1], Rook) or self.board[rook_x][y1].has_moved:
                raise ValueError("Rok için geçersiz kale konumu veya kale hareket etmiş!")
            self.board[rook_new_x][y1] = self.board[rook_x][y1]
            self.board[rook_x][y1] = None
            self.board[rook_new_x][y1].has_moved = True
        # Piyon terfisi
        if isinstance(piece, Pawn) and (y2 == 0 or y2 == self.size - 1):
            if promotion not in [Queen, Rook, Bishop, Knight]:
                raise ValueError("Geçersiz terfi seçimi!")
            piece = promotion(piece.color)
        self.board[x1][y1] = None
        self.board[x2][y2] = piece
        piece.has_moved = True
        self.last_move = (x1, y1, x2, y2)
        self.move_history.append((x1, y1, x2, y2, piece))

    def find_king(self, color):
        for x in range(self.size):
            for y in range(self.size):
                piece = self.board[x][y]
                if isinstance(piece, King) and piece.color == color:
                    return x, y
        raise ValueError(f"{color.capitalize()} şah bulunamadı!")

    def is_in_check(self, color):
        try:
            king_pos = self.find_king(color)
        except ValueError as e:
            raise ValueError(f"Şah kontrolü başarısız: {e}")
        for x in range(self.size):
            for y in range(self.size):
                piece = self.board[x][y]
                if piece and piece.color != color:
                    if king_pos in piece.get_valid_moves(x, y, self):
                        return True
        return False

    def is_threatened(self, color, x, y):
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        for i in range(self.size):
            for j in range(self.size):
                piece = self.board[i][j]
                if piece and piece.color != color:
                    if (x, y) in piece.get_valid_moves(i, j, self):
                        return True
        return False

    def has_any_valid_move(self, color):
        for x1 in range(self.size):
            for y1 in range(self.size):
                piece = self.board[x1][y1]
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(x1, y1, self)
                    if not valid_moves:
                        continue
                    for x2, y2 in valid_moves:
                        backup = self.board[x2][y2]
                        self.move_piece(x1, y1, x2, y2)
                        if not self.is_in_check(color):
                            self.board[x1][y1] = piece
                            self.board[x2][y2] = backup
                            self.last_move = None
                            return True
                        self.board[x1][y1] = piece
                        self.board[x2][y2] = backup
                        self.last_move = None
        return False

    def evaluate(self):
        score = 0
        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        for x in range(self.size):
            for y in range(self.size):
                piece = self.board[x][y]
                if piece:
                    value = piece_values.get(piece.symbol.upper(), 0)
                    score += value if piece.color == 'white' else -value
        return score

    def validate_setup(self):
        expected_pieces = {
            'white': {'K': 1, 'Q': 1, 'R': 2, 'B': 2, 'N': 2, 'P': 8},
            'black': {'K': 1, 'Q': 1, 'R': 2, 'B': 2, 'N': 2, 'P': 8}
        }
        counts = {'white': {}, 'black': {}}
        for x in range(self.size):
            for y in range(self.size):
                piece = self.board[x][y]
                if piece:
                    counts[piece.color][piece.symbol] = counts[piece.color].get(piece.symbol, 0) + 1
        for color in expected_pieces:
            for symbol, expected_count in expected_pieces[color].items():
                actual_count = counts[color].get(symbol, 0)
                if actual_count != expected_count:
                    raise ValueError(f"{color.capitalize()} için {symbol} sayısı yanlış: beklenen {expected_count}, bulunan {actual_count}")

def setup_standard_board(board):
    sx, sy = (board.size - 8) // 2, (board.size - 8) // 2
    pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
    for i, piece_class in enumerate(pieces):
        board.place_piece(piece_class('black'), sx + i, sy)
        board.place_piece(Pawn('black'), sx + i, sy + 1)
    for i, piece_class in enumerate(pieces):
        board.place_piece(piece_class('white'), sx + i, sy + 7)
        board.place_piece(Pawn('white'), sx + i, sy + 6)
    board.validate_setup()

def minimax(board, depth, alpha, beta, maximizing):
    try:
        if depth == 0 or not board.has_any_valid_move('white' if maximizing else 'black'):
            return board.evaluate(), None
        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for x1 in range(board.size):
                for y1 in range(board.size):
                    piece = board.board[x1][y1]
                    if piece and piece.color == 'white':
                        for x2, y2 in piece.get_valid_moves(x1, y1, board):
                            backup = board.board[x2][y2]
                            board.move_piece(x1, y1, x2, y2)
                            eval, _ = minimax(board, depth - 1, alpha, beta, False)
                            board.board[x1][y1] = piece
                            board.board[x2][y2] = backup
                            board.last_move = None
                            if eval > max_eval:
                                max_eval = eval
                                best_move = (x1, y1, x2, y2)
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for x1 in range(board.size):
                for y1 in range(board.size):
                    piece = board.board[x1][y1]
                    if piece and piece.color == 'black':
                        for x2, y2 in piece.get_valid_moves(x1, y1, board):
                            backup = board.board[x2][y2]
                            board.move_piece(x1, y1, x2, y2)
                            eval, _ = minimax(board, depth - 1, alpha, beta, True)
                            board.board[x1][y1] = piece
                            board.board[x2][y2] = backup
                            board.last_move = None
                            if eval < min_eval:
                                min_eval = eval
                                best_move = (x1, y1, x2, y2)
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            return min_eval, best_move
    except Exception as e:
        print(f"Minimax hatası: {e}")
        return 0, None

def get_computer_move(board, color):
    try:
        _, move = minimax(deepcopy(board), 2, float('-inf'), float('inf'), False)
        if move is None:
            raise ValueError("Bilgisayar için geçerli hamle bulunamadı!")
        return move
    except Exception as e:
        print(f"Bilgisayar hamlesi hatası: {e}")
        return None

def get_promotion_choice():
    while True:
        choice = input("Piyon terfisi için taş seçin (Q/R/B/N): ").upper()
        if choice in ['Q', 'R', 'B', 'N']:
            return {'Q': Queen, 'R': Rook, 'B': Bishop, 'N': Knight}[choice]
        print("Geçersiz seçim! Lütfen Q, R, B veya N girin.")

def draw_board(screen, board, selected=None, valid_moves=[], error_msg=""):
    screen.fill(WHITE)
    for x in range(board.size):
        for y in range(board.size):
            color = LIGHT_SQUARE if (x + y) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if (x, y) in valid_moves:
                pygame.draw.rect(screen, HIGHLIGHT, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
            piece = board.board[x][y]
            if piece:
                if (piece.color, piece.symbol) in PIECE_IMAGES:
                    screen.blit(PIECE_IMAGES[(piece.color, piece.symbol)], (x * SQUARE_SIZE + 5, y * SQUARE_SIZE + 5))
                else:
                    # Yedek: Renkli kare çiz
                    piece_color = RED_PIECE if piece.color == 'white' else BLUE_PIECE
                    pygame.draw.rect(screen, piece_color, (x * SQUARE_SIZE + 10, y * SQUARE_SIZE + 10, SQUARE_SIZE - 20, SQUARE_SIZE - 20))
                    text = FONT.render(piece.symbol, True, BLACK)
                    screen.blit(text, (x * SQUARE_SIZE + 20, y * SQUARE_SIZE + 20))
    if selected:
        pygame.draw.rect(screen, (255, 0, 0), (selected[0] * SQUARE_SIZE, selected[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    if error_msg:
        text = FONT.render(error_msg, True, ERROR_COLOR)
        screen.blit(text, (10, HEIGHT - 60))
    try:
        if board.is_in_check('white' if board.move_history else 'black'):
            text = FONT.render(f"{'Kırmızı' if board.move_history else 'Mavi'} şah altında!", True, BLACK)
            screen.blit(text, (10, HEIGHT - 30))
    except ValueError as e:
        text = FONT.render(f"Şah kontrol hatası: {e}", True, ERROR_COLOR)
        screen.blit(text, (10, HEIGHT - 30))

def play_game(mode='pvp'):
    try:
        board = Board()
        setup_standard_board(board)
    except ValueError as e:
        print(f"Tahta kurulum hatası: {e}")
        text = FONT.render(f"Tahta kurulum hatası: {e}", True, ERROR_COLOR)
        SCREEN.blit(text, (10, HEIGHT - 90))
        pygame.display.flip()
        pygame.time.wait(2000)
        return
    turn = 'white'
    selected = None
    valid_moves = []
    error_msg = ""
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if mode == 'pvc' and turn == 'black':
                move = get_computer_move(board, turn)
                if move:
                    x1, y1, x2, y2 = move
                    promotion = None
                    if isinstance(board.board[x1][y1], Pawn) and (y2 == 0 or y2 == board.size - 1):
                        promotion = Queen  # Bilgisayar için varsayılan vezir
                    try:
                        board.move_piece(x1, y1, x2, y2, promotion)
                        print(f"Bilgisayar hamlesi: ({x1}, {y1}) -> ({x2}, {y2})")
                        turn = 'white'
                        error_msg = ""
                    except ValueError as e:
                        error_msg = f"Bilgisayar hamlesi hatası: {e}"
                else:
                    error_msg = "Bilgisayar için geçerli hamle yok!"
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if not (0 <= x < board.size and 0 <= y < board.size):
                    error_msg = "Tahta dışında tıklama!"
                    continue
                if selected:
                    if (x, y) in valid_moves:
                        promotion = None
                        if isinstance(board.board[selected[0]][selected[1]], Pawn) and (y == 0 or y == board.size - 1):
                            promotion = get_promotion_choice()
                        try:
                            board.move_piece(selected[0], selected[1], x, y, promotion)
                            if not board.is_in_check(turn):
                                turn = 'black' if turn == 'white' else 'white'
                                selected = None
                                valid_moves = []
                                error_msg = ""
                            else:
                                board.board[selected[0]][selected[1]] = board.board[x][y]
                                board.board[x][y] = None
                                board.last_move = None
                                error_msg = "Bu hamle şahı tehdit ediyor!"
                        except ValueError as e:
                            error_msg = f"Hamle hatası: {e}"
                    else:
                        selected = None
                        valid_moves = []
                        error_msg = "Geçersiz hamle!"
                else:
                    piece = board.board[x][y]
                    if piece and piece.color == turn:
                        selected = (x, y)
                        valid_moves = piece.get_valid_moves(x, y, board)
                        error_msg = ""
                    else:
                        error_msg = "Geçersiz taş seçimi veya sıra dışı!"

        draw_board(SCREEN, board, selected, valid_moves, error_msg)
        try:
            if not board.has_any_valid_move(turn):
                text = FONT.render(f"Mat! {'Kırmızı' if turn == 'white' else 'Mavi'} kaybetti." if board.is_in_check(turn) else "Pat! Oyun berabere.", True, BLACK)
                SCREEN.blit(text, (10, HEIGHT - 90))
                pygame.display.flip()
                pygame.time.wait(2000)
                break
        except ValueError as e:
            text = FONT.render(f"Oyun hatası: {e}", True, ERROR_COLOR)
            SCREEN.blit(text, (10, HEIGHT - 120))
            pygame.display.flip()
            pygame.time.wait(2000)
            break
        pygame.display.flip()
        clock.tick(60)

def main():
    print("Satranç Oyunu - Hata Testi")
    print("1. PvP (Oyuncuya Karşı Oyuncu)")
    print("2. PvC (Oyuncuya Karşı Bilgisayar)")
    while True:
        mode = input("Mod seçin (1 veya 2): ")
        if mode in ['1', '2']:
            break
        print("Geçersiz seçim! Lütfen 1 veya 2 girin.")
    try:
        play_game('pvp' if mode == '1' else 'pvc')
    except Exception as e:
        print(f"Oyun başlatılamadı: {e}")
        text = FONT.render(f"Oyun başlatılamadı: {e}", True, ERROR_COLOR)
        SCREEN.blit(text, (10, HEIGHT - 90))
        pygame.display.flip()
        pygame.time.wait(2000)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()