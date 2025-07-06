import math
import random

# Plansza 3x3
board = [" " for _ in range(9)]

def print_board():
    print("\nAktualna plansza:")
    for i in range(3):
        row = " | ".join(board[i*3:(i+1)*3])
        print(" " + row)
        if i < 2:
            print("---+---+---")
    print()

def check_winner(b, player):
    wins = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    return any(all(b[i] == player for i in combo) for combo in wins)

def is_full(b):
    return all(cell != " " for cell in b)

def minimax(b, depth, is_maximizing):
    if check_winner(b, "O"):
        return 1
    if check_winner(b, "X"):
        return -1
    if is_full(b):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if b[i] == " ":
                b[i] = "O"
                score = minimax(b, depth + 1, False)
                b[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if b[i] == " ":
                b[i] = "X"
                score = minimax(b, depth + 1, True)
                b[i] = " "
                best_score = min(score, best_score)
        return best_score

def ai_move(difficulty):
    if difficulty == 1:
        # Łatwy – losowy ruch
        move = random.choice([i for i in range(9) if board[i] == " "])
        board[move] = "O"

    elif difficulty == 2:
        # Średni – 50% szans na mądry ruch
        if random.random() < 0.5:
            ai_move(1)
        else:
            ai_move(3)

    elif difficulty == 3:
        # Trudny – pełny Minimax
        best_score = -math.inf
        move = None
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"
                score = minimax(board, 0, False)
                board[i] = " "
                if score > best_score:
                    best_score = score
                    move = i
        board[move] = "O"

def main():
    global board

    print("Grasz jako X. AI to O.")

    while True:
        # Wybór trudności
        while True:
            try:
                level = int(input("\nWybierz poziom trudności (1=łatwy, 2=średni, 3=trudny (Nie do pokonania): "))
                if level in [1, 2, 3]:
                    break
                else:
                    print("Wpisz 1, 2 lub 3.")
            except ValueError:
                print("Wpisz cyfrę.")

        board = [" " for _ in range(9)]
        print_board()

        while True:
            try:
                move = int(input("Wybierz pole (1-9): ")) - 1
                if board[move] != " ":
                    print("Pole zajęte!")
                    continue
                board[move] = "X"
            except (ValueError, IndexError):
                print("Niepoprawny ruch.")
                continue

            print_board()

            if check_winner(board, "X"):
                print("✅ Wygrałeś!")
                break
            if is_full(board):
                print("🤝 Remis!")
                break

            print("Ruch AI...")
            ai_move(level)
            print_board()

            if check_winner(board, "O"):
                print("💻 AI wygrało!")
                break
            if is_full(board):
                print("🤝 Remis!")
                break

        restart = input("Wciśnij Enter, aby zagrać ponownie lub wpisz Q, by wyjść: ").strip().lower()
        if restart == 'q':
            print("Do zobaczenia!")
            break

if __name__ == "__main__":
    main()
