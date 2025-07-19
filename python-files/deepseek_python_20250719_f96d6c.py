class Piece:
    def __init__(self, color, position):
        self.color = color  # 'white' ili 'black'
        self.position = position  # npr. 'a1', 'e4' itd.
        self.has_moved = False
    
    def get_possible_moves(self, board):
        raise NotImplementedError("Subclasses must implement this method")
    
    def move(self, new_position):
        self.position = new_position
        self.has_moved = True
    
    def __repr__(self):
        return f"{self.color[0].upper()}{self.__class__.__name__[0]}"


class Pawn(Piece):
    def get_possible_moves(self, board):
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Pravci kretanja zavise od boje
        direction = 1 if self.color == 'white' else -1
        
        # Standardni potez
        if 0 <= y + direction < 8 and board.get_piece_at((x, y + direction)) is None:
            moves.append((x, y + direction))
            
            # Dupli potez na pocetku
            if not self.has_moved and board.get_piece_at((x, y + 2*direction)) is None:
                moves.append((x, y + 2*direction))
        
        # Dijagonalno za uzimanje figura
        for dx in [-1, 1]:
            if 0 <= x + dx < 8 and 0 <= y + direction < 8:
                piece = board.get_piece_at((x + dx, y + direction))
                if piece and piece.color != self.color:
                    moves.append((x + dx, y + direction))
        
        return moves


class Rook(Piece):
    def get_possible_moves(self, board):
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Horizontalno i vertikalno kretanje
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + i*dx, y + i*dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None:
                        moves.append((new_x, new_y))
                    else:
                        if piece.color != self.color:
                            moves.append((new_x, new_y))
                        break
                else:
                    break
        
        return moves


class Knight(Piece):
    def get_possible_moves(self, board):
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Svi moguci L potezi
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), 
                       (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                piece = board.get_piece_at((new_x, new_y))
                if piece is None or piece.color != self.color:
                    moves.append((new_x, new_y))
        
        return moves


class Bishop(Piece):
    def get_possible_moves(self, board):
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Dijagonalno kretanje
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + i*dx, y + i*dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None:
                        moves.append((new_x, new_y))
                    else:
                        if piece.color != self.color:
                            moves.append((new_x, new_y))
                        break
                else:
                    break
        
        return moves


class Queen(Piece):
    def get_possible_moves(self, board):
        # Kombinacija topa i lovca
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Smerovi kretanja (horizontalno, vertikalno i dijagonalno)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), 
                       (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_x, new_y = x + i*dx, y + i*dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None:
                        moves.append((new_x, new_y))
                    else:
                        if piece.color != self.color:
                            moves.append((new_x, new_y))
                        break
                else:
                    break
        
        return moves


class King(Piece):
    def get_possible_moves(self, board):
        moves = []
        x, y = ord(self.position[0]) - ord('a'), int(self.position[1]) - 1
        
        # Svi susedni kvadrati
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    piece = board.get_piece_at((new_x, new_y))
                    if piece is None or piece.color != self.color:
                        moves.append((new_x, new_y))
        
        # Rokada (dodati provere za rokadu)
        
        return moves


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_turn = 'white'
        self.game_over = False
    
    def setup_board(self):
        # Postavi crne figure
        self.grid[0][0] = Rook('black', 'a8')
        self.grid[0][1] = Knight('black', 'b8')
        self.grid[0][2] = Bishop('black', 'c8')
        self.grid[0][3] = Queen('black', 'd8')
        self.grid[0][4] = King('black', 'e8')
        self.grid[0][5] = Bishop('black', 'f8')
        self.grid[0][6] = Knight('black', 'g8')
        self.grid[0][7] = Rook('black', 'h8')
        
        for i in range(8):
            self.grid[1][i] = Pawn('black', f"{chr(97 + i)}8")
        
        # Postavi bele figure
        self.grid[7][0] = Rook('white', 'a1')
        self.grid[7][1] = Knight('white', 'b1')
        self.grid[7][2] = Bishop('white', 'c1')
        self.grid[7][3] = Queen('white', 'd1')
        self.grid[7][4] = King('white', 'e1')
        self.grid[7][5] = Bishop('white', 'f1')
        self.grid[7][6] = Knight('white', 'g1')
        self.grid[7][7] = Rook('white', 'h1')
        
        for i in range(8):
            self.grid[6][i] = Pawn('white', f"{chr(97 + i)}2")
    
    def get_piece_at(self, position):
        x, y = position
        return self.grid[y][x]
    
    def move_piece(self, from_pos, to_pos):
        from_x, from_y = ord(from_pos[0]) - ord('a'), int(from_pos[1]) - 1
        to_x, to_y = ord(to_pos[0]) - ord('a'), int(to_pos[1]) - 1
        
        piece = self.grid[from_y][from_x]
        if piece is None or piece.color != self.current_turn:
            return False
        
        possible_moves = piece.get_possible_moves(self)
        if (to_x, to_y) in possible_moves:
            # Provera sah i mat stanja (pojednostavljena)
            self.grid[to_y][to_x] = piece
            self.grid[from_y][from_x] = None
            piece.move(to_pos)
            
            # Promena igraca na potezu
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'
            return True
        
        return False
    
    def display(self):
        print("  a b c d e f g h")
        print(" +-----------------")
        for y in range(8):
            print(f"{8 - y}|", end="")
            for x in range(8):
                piece = self.grid[y][x]
                print(piece if piece else ".", end=" ")
            print(f"|{8 - y}")
        print(" +-----------------")
        print("  a b c d e f g h")


class Game:
    def __init__(self):
        self.board = Board()
    
    def play(self):
        print("Dobrodošli u šah!")
        print("Unesite potez u formatu 'e2 e4'")
        
        while not self.board.game_over:
            self.board.display()
            print(f"Na potezu: {self.board.current_turn}")
            
            move = input("Unesite potez: ").strip().lower()
            if move == 'quit':
                break
            
            try:
                from_pos, to_pos = move.split()
                if len(from_pos) != 2 or len(to_pos) != 2:
                    raise ValueError
                
                if self.board.move_piece(from_pos, to_pos):
                    print("Potez izvršen!")
                else:
                    print("Nevažeći potez, pokušajte ponovo.")
            except ValueError:
                print("Nevažeći unos. Unesite potez u formatu 'e2 e4'")
        
        print("Igra završena!")


if __name__ == "__main__":
    game = Game()
    game.play()