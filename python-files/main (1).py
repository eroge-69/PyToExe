import numpy as np
import random

# Convert the list of lists to a numpy matrix
INITIAL_BOARD = np.array([
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
])

# A simple AI with basic board evaluation
PIECE_VALUES = {
    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000, 
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    '.': 0
}

def print_board(current_board):
    print('  a b c d e f g h')
    print('  ---------------')
    for i, row in enumerate(current_board):
        print(8 - i, '|' + ' '.join(row) + '|')
    print('  ---------------')

def is_path_clear(board, start_row, start_col, end_row, end_col):
    """Checks if the path between two squares is clear for sliding pieces (Rook, Bishop, Queen)."""
    step_row = np.sign(end_row - start_row)
    step_col = np.sign(end_col - start_col)

    current_row = start_row + step_row
    current_col = start_col + step_col

    while current_row != end_row or current_col != end_col:
        if board[current_row, current_col] != '.':
            return False
        current_row += step_row
        current_col += step_col
    return True

def is_valid_pawn_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    row_diff = end_row - start_row
    col_diff = end_col - start_col
    
    # White pawn moves
    if piece.isupper():
        if player_color == "Black": return False # Trying to move opponent's piece
        # One square forward
        if col_diff == 0 and row_diff == -1 and board[end_row, end_col] == '.':
            return True
        # Two squares forward (from start position)
        if start_row == 6 and col_diff == 0 and row_diff == -2 and board[end_row, end_col] == '.' and board[start_row - 1, start_col] == '.':
            return True
        # Capture diagonally
        if abs(col_diff) == 1 and row_diff == -1 and board[end_row, end_col].islower():
            return True
    
    # Black pawn moves
    else:
        if player_color == "White": return False # Trying to move opponent's piece
        # One square forward
        if col_diff == 0 and row_diff == 1 and board[end_row, end_col] == '.':
            return True
        # Two squares forward (from start position)
        if start_row == 1 and col_diff == 0 and row_diff == 2 and board[end_row, end_col] == '.' and board[start_row + 1, start_col] == '.':
            return True
        # Capture diagonally
        if abs(col_diff) == 1 and row_diff == 1 and board[end_row, end_col].isupper():
            return True
    
    return False

def is_valid_rook_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    is_same_row = start_row == end_row
    is_same_col = start_col == end_col

    if not (is_same_row or is_same_col):
        return False # Not a straight line move
    
    return is_path_clear(board, start_row, start_col, end_row, end_col)

def is_valid_knight_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

def is_valid_bishop_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)

    if row_diff != col_diff:
        return False # Not a diagonal move
    
    return is_path_clear(board, start_row, start_col, end_row, end_col)

def is_valid_queen_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    return is_valid_rook_move(board, start_row, start_col, end_row, end_col, piece, player_color) or \
           is_valid_bishop_move(board, start_row, start_col, end_row, end_col, piece, player_color)

def is_valid_king_move(board, start_row, start_col, end_row, end_col, piece, player_color):
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)
    return row_diff <= 1 and col_diff <= 1

def move_piece_on_board(current_board, start_pos, end_pos):
    """Executes a move on the board without validation (validation happens before calling this)."""
    start_col = ord(start_pos[0]) - ord('a')
    start_row = 8 - int(start_pos[1])
    end_col = ord(end_pos[0]) - ord('a')
    end_row = 8 - int(end_pos[1])

    piece = current_board[start_row, start_col]
    current_board[end_row, end_col] = piece
    current_board[start_row, start_col] = '.'
    return True

def check_and_execute_move(current_board, start_pos, end_pos, player_color):
    """
    Parses and validates a move, then executes it if legal.
    Returns True if the move was successful, False otherwise.
    """
    try:
        start_col = ord(start_pos[0]) - ord('a')
        start_row = 8 - int(start_pos[1])
        end_col = ord(end_pos[0]) - ord('a')
        end_row = 8 - int(end_pos[1])
    except (ValueError, IndexError):
        print("Invalid format. Use algebraic notation (e.g., 'e2 e4').")
        return False

    if not all(0 <= coord < 8 for coord in [start_row, start_col, end_row, end_col]):
        print("Invalid move: Coordinates are outside the board.")
        return False

    piece = current_board[start_row, start_col]

    if piece == '.':
        print("Invalid move: No piece at the starting square.")
        return False
        
    # Check if the correct player's piece is being moved
    if (player_color == "White" and piece.islower()) or \
       (player_color == "Black" and piece.isupper()):
        print(f"Invalid move: It's {player_color}'s turn to move, but you selected an opponent's piece.")
        return False
    
    # Check if the destination square contains a piece of the same color
    target_piece = current_board[end_row, end_col]
    if target_piece != '.' and ((piece.isupper() and target_piece.isupper()) or \
                                 (piece.islower() and target_piece.islower())):
        print("Invalid move: Cannot capture your own piece.")
        return False

    # Validate move based on piece type
    piece_type = piece.lower()
    is_legal_move_rule = False
    if piece_type == 'p':
        is_legal_move_rule = is_valid_pawn_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    elif piece_type == 'r':
        is_legal_move_rule = is_valid_rook_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    elif piece_type == 'n':
        is_legal_move_rule = is_valid_knight_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    elif piece_type == 'b':
        is_legal_move_rule = is_valid_bishop_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    elif piece_type == 'q':
        is_legal_move_rule = is_valid_queen_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    elif piece_type == 'k':
        is_legal_move_rule = is_valid_king_move(current_board, start_row, start_col, end_row, end_col, piece, player_color)
    
    if not is_legal_move_rule:
        print("Invalid move: This piece cannot move that way.")
        return False

    # If all checks pass, move the piece
    move_piece_on_board(current_board, start_pos, end_pos)
    return True

def evaluate_board(current_board):
    """Evaluates the board state from White's perspective."""
    score = 0
    for row in range(8):
        for col in range(8):
            piece = current_board[row, col]
            if piece.isupper(): # White piece
                score += PIECE_VALUES.get(piece, 0)
            elif piece.islower(): # Black piece
                score -= PIECE_VALUES.get(piece, 0)
    return score

def get_all_legal_moves(board, color):
    """
    Generates all legal moves for a given color.
    Returns a list of tuples: [(start_pos_alg, end_pos_alg), ...]
    """
    legal_moves = []
    for start_row in range(8):
        for start_col in range(8):
            piece = board[start_row, start_col]
            if piece == '.':
                continue
            
            is_correct_color = (color == "Black" and piece.islower()) or \
                               (color == "White" and piece.isupper())

            if is_correct_color:
                for end_row in range(8):
                    for end_col in range(8):
                        start_pos_alg = chr(ord('a') + start_col) + str(8 - start_row)
                        end_pos_alg = chr(ord('a') + end_col) + str(8 - end_row)

                        # Temporarily make the move on a copy to check legality
                        temp_board = board.copy()
                        if check_and_execute_move(temp_board, start_pos_alg, end_pos_alg, color):
                            legal_moves.append((start_pos_alg, end_pos_alg))
                            
    return legal_moves

def ai_move(board, player_color):
    """
    AI player logic: Finds and executes the "best" move based on a simple evaluation.
    """
    print("AI is thinking...")
    
    legal_moves = get_all_legal_moves(board, player_color)
    
    if not legal_moves:
        print("No legal moves for the AI. It might be checkmate or stalemate.")
        return False
    
    best_move = None
    # Black minimizes the score, White maximizes.
    best_score = float('inf') if player_color == "Black" else float('-inf')

    for start_pos_alg, end_pos_alg in legal_moves:
        temp_board = board.copy()
        
        # Apply the move to the temporary board
        move_piece_on_board(temp_board, start_pos_alg, end_pos_alg)
        
        score = evaluate_board(temp_board)

        if player_color == "Black": # AI wants to minimize White's score (maximize negative score)
            if score < best_score:
                best_score = score
                best_move = (start_pos_alg, end_pos_alg)
        else: # AI is White (maximizes its own score)
            if score > best_score:
                best_score = score
                best_move = (start_pos_alg, end_pos_alg)
    
    # If no 'best' move was found (e.g., all moves yield same score, or issue)
    # fall back to a random choice to ensure AI can always move
    if best_move is None:
        best_move = random.choice(legal_moves)
        
    start_pos_alg, end_pos_alg = best_move
    print(f"AI plays: {start_pos_alg} to {end_pos_alg}")
    
    # Execute the chosen move on the actual board
    move_piece_on_board(board, start_pos_alg, end_pos_alg)
    return True

def main():
    board = INITIAL_BOARD.copy() # Start with a fresh board
    turn = 0
    
    player_choice = input("Do you want to play as White (you go first) or Black (AI goes first)? (w/b): ").lower()
    
    is_human_white = (player_choice == 'w')
    
    if player_choice == 'b':
        print("You will play as Black. AI plays White.")
        
    else:
        print("You will play as White. AI plays Black.")

    while True:
        print_board(board)
        player_color = "White" if turn % 2 == 0 else "Black"

        print(f"\n{player_color}'s turn.")
        
        is_current_turn_human = (player_color == "White" and is_human_white) or \
                                 (player_color == "Black" and not is_human_white)
        
        if is_current_turn_human:
            move_input = input("Enter your move (e.g., 'e2 e4') or 'q' to quit: ")
            if move_input.lower() == 'q':
                break
            
            move = move_input.split()
            if len(move) != 2:
                print("Invalid input format. Please use 'start end'.")
                continue
                
            start, end = move
            
            if check_and_execute_move(board, start, end, player_color):
                turn += 1
            # If check_and_execute_move returns False, the turn doesn't increment, allowing the same player to try again.
        else: # AI's turn
            if ai_move(board, player_color):
                turn += 1
            else:
                print("Game Over!")
                break # AI could not make a legal move (checkmate or stalemate)

if __name__ == "__main__":
    main()

