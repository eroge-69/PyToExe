import random
import time
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board):
    print("\033[1;32m")  # Green text
    print("      TIC TAC TOE SIMULATION\n")
    print("         1   2   3")
    for i, row in enumerate(board):
        print(f"      {i + 1}  " + " | ".join(row))
        if i < 2:
            print("        ---+---+---")
    print("\n\033[0m")  # Reset color

def check_winner(board, player):
    wins = [
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)]
    ]
    return any(all(board[r][c] == player for r, c in combo) for combo in wins)

def get_empty(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]

def play_one_game(delay=0.15):
    board = [[" "]*3 for _ in range(3)]
    player = "X"
    turns = 0

    while True:
        clear()
        print_board(board)
        print(f"   GAME #{play_one_game.game_count} - TURN {turns + 1}: {player} THINKING...\n")
        time.sleep(delay)

        move = random.choice(get_empty(board))
        board[move[0]][move[1]] = player

        if check_winner(board, player):
            clear()
            print_board(board)
            print(f"   RESULT: PLAYER {player} WINS!\n")
            return player

        if not get_empty(board):
            clear()
            print_board(board)
            print("   RESULT: DRAW\n")
            return "draw"

        player = "O" if player == "X" else "X"
        turns += 1

play_one_game.game_count = 1

def joshua_simulation(total_games=30, delay=0.15):
    results = {"X": 0, "O": 0, "draw": 0}

    print("\033[1;32m")
    print("JOSHUA: LEARNING GAME STRATEGY...")
    print("       SIMULATING GLOBAL THERMONUCLEAR WAR")
    print("       LAUNCH CODE OVERRIDE: ENABLED\n")
    print("\033[0m")
    time.sleep(3)

    for _ in range(total_games):
        result = play_one_game(delay=delay)
        results[result] += 1
        play_one_game.game_count += 1
        time.sleep(1)

    clear()
    print("\033[1;32m")
    print("JOSHUA: ANALYSIS COMPLETE.")
    print("-----------------------------")
    print(f" TOTAL GAMES SIMULATED : {total_games}")
    print(f" X WINS                : {results['X']}")
    print(f" O WINS                : {results['O']}")
    print(f" DRAWS                 : {results['draw']}")
    print("\n")
    time.sleep(2)

    # The iconic moment
    print("A STRANGE GAME.")
    time.sleep(2)
    print("THE ONLY WINNING MOVE IS...")
    time.sleep(2)
    print("...NOT TO PLAY.\n")
    time.sleep(2)
    print("HOW ABOUT A NICE GAME OF CHESS?")
    print("\033[0m")  # Reset color

# Start the WarGames simulation
joshua_simulation(total_games=30, delay=0.2)
