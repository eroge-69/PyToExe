# Tic Tac Toe game in Python

def print_board(board):
    print("\n")
    for row in board:
        print(" | ".join(row))
        print("-" * 5)
    print("\n")

def check_winner(board, player):
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def tic_tac_toe():
    board = [[" " for _ in range(3)] for _ in range(3)]
    players = ["X", "O"]
    turn = 0

    print("Welcome to Tic Tac Toe!\n")
    print_board(board)

    while True:
        player = players[turn % 2]
        print(f"Player {player}'s turn.")
        
        try:
            row = int(input("Enter row (0-2): "))
            col = int(input("Enter col (0-2): "))
        except ValueError:
            print("Invalid input! Please enter numbers between 0 and 2.")
            continue

        if row not in range(3) or col not in range(3):
            print("Out of range! Please choose between 0 and 2.")
            continue

        if board[row][col] != " ":
            print("Cell already taken! Try again.")
            continue

        board[row][col] = player
        print_board(board)

        if check_winner(board, player):
            print(f"🎉 Player {player} wins!")
            break
        elif is_full(board):
            print("It's a draw!")
            break

        turn += 1

if __name__ == "__main__":
    tic_tac_toe()

