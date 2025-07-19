import random
import json
import os
import sys

SETTINGS_FILE = 'tictactoe_settings.json'
STATS_FILE = 'tictactoe_stats.json'

DEFAULT_SETTINGS = {
    "volume": 5,
    "ai_difficulty": "medium",       # easy, medium, hard
    "ai_algorithm": "minimax"        # minimax, optimized
}
DEFAULT_STATS = {}

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default.copy()
    else:
        return default.copy()

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def draw_board(b):
    print()
    for i in range(3):
        row = [b[3*i+j] or str(3*i+j+1) for j in range(3)]
        print(" " + " | ".join(row))
        if i < 2:
            print("---+---+---")
    print()

def check_win(b, p):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for a, c, d in wins:
        if b[a] == b[c] == b[d] == p:
            return True
    return False

def board_full(b):
    return all(b[i] is not None for i in range(9))

def minimax(b, depth, is_max, player, opponent):
    if check_win(b, opponent): return -1
    if check_win(b, player): return 1
    if board_full(b): return 0
    scores = []
    for i in range(9):
        if b[i] is None:
            b[i] = player if is_max else opponent
            score = minimax(b, depth+1, not is_max, player, opponent)
            b[i] = None
            scores.append(score)
    return max(scores) if is_max else min(scores)

def get_ai_move(b, ai_piece, human_piece, difficulty, algorithm):
    moves = [i for i in range(9) if b[i] is None]
    if difficulty == 'easy':
        return random.choice(moves)
    elif difficulty == 'medium':
        if random.random() < 0.5:
            return random.choice(moves)
    best_score = -2
    best_move = None
    for m in moves:
        b[m] = ai_piece
        score = minimax(b, 0, False, ai_piece, human_piece)
        b[m] = None
        if score > best_score:
            best_score = score
            best_move = m
    return best_move

def ensure_account(name, stats):
    if name not in stats:
        stats[name] = {"W":0, "R":0, "P":0}

def play_game(mode, settings, stats):
    board = [None]*9
    p1, p2 = None, None
    starter = None

    if mode == '1':
        name = input("Wpisz swoje imie: ")
        ensure_account(name, stats)
        player_piece, ai_piece = ('X','O')

        print("Kto ma zaczac? (1) Gracz (2) AI (3) Losowo")
        sel = input("Wybierz: ")
        if sel == '1': starter = 'player'
        elif sel == '2': starter = 'ai'
        else: starter = random.choice(['player', 'ai'])

        cur = starter

    elif mode == '2':
        p1 = input("Imie gracza 1: ")
        ensure_account(p1, stats)
        p2 = input("Imie gracza 2: ")
        ensure_account(p2, stats)
        players = [p1, p2]

        print("Kto ma zaczac? (1) " + p1 + " (2) " + p2 + " (3) Losowo")
        sel = input("Wybierz: ")
        if sel == '1': cur = p1
        elif sel == '2': cur = p2
        else: cur = random.choice(players)

    elif mode == '3':
        print("Kto ma zaczac? (1) AI X (2) AI O (3) Losowo")
        sel = input("Wybierz: ")
        if sel == '1': cur = 'X'
        elif sel == '2': cur = 'O'
        else: cur = random.choice(['X','O'])

    else:
        return

    while True:
        draw_board(board)
        if mode == '1':
            if cur == 'player':
                move = input("Ruch: ")
                if not move.isdigit() or not (1<=int(move)<=9) or board[int(move)-1] is not None:
                    print("Niepoprawny ruch.")
                    continue
                board[int(move)-1] = player_piece
                if check_win(board, player_piece):
                    print("Wygrales!")
                    stats[name]["W"] += 1
                    break
                if board_full(board):
                    print("Remis!")
                    stats[name]["R"] += 1
                    break
                cur = 'ai'
            else:
                print("Ruch AI...")
                m = get_ai_move(board, ai_piece, player_piece, settings['ai_difficulty'], settings['ai_algorithm'])
                print(f"AI wybralo pole: {m+1}")
                board[m] = ai_piece
                if check_win(board, ai_piece):
                    print("AI wygralo!")
                    stats[name]["P"] += 1
                    break
                if board_full(board):
                    print("Remis!")
                    stats[name]["R"] += 1
                    break
                cur = 'player'

        elif mode == '2':
            print(f"Tura: {cur}")
            move = input("Ruch: ")
            if not move.isdigit() or not (1<=int(move)<=9) or board[int(move)-1] is not None:
                print("Niepoprawny ruch.")
                continue
            piece = 'X' if cur==p1 else 'O'
            board[int(move)-1] = piece
            if check_win(board, piece):
                print(f"{cur} wygral!")
                stats[cur]["W"] += 1
                stats[p1 if cur == p2 else p2]["P"] += 1
                break
            if board_full(board):
                print("Remis!")
                stats[p1]["R"] += 1
                stats[p2]["R"] += 1
                break
            cur = p2 if cur == p1 else p1

        else:
            print(f"Tura AI: {cur}")
            m = get_ai_move(board, cur, 'O' if cur == 'X' else 'X', settings['ai_difficulty'], settings['ai_algorithm'])
            print(f"AI {cur} wybralo pole: {m+1}")
            board[m] = cur
            if check_win(board, cur):
                print(f"AI {cur} wygralo")
                break
            if board_full(board): print("Remis!"); break
            cur = 'O' if cur == 'X' else 'X'

    draw_board(board)
    save_json(STATS_FILE, stats)

def settings_menu(settings):
    while True:
        print("\n--- USTAWIENIA ---")
        print(f"1. Glosnosc: {settings['volume']}")
        print(f"2. Poziom AI: {settings['ai_difficulty']}")
        print(f"3. Algorytm AI: {settings['ai_algorithm']}")
        print("4. Powrot")
        ch = input("Wybierz: ")
        if ch=='1':
            vol = input("Nowa glosnosc (0-10): ")
            if vol.isdigit() and 0<=int(vol)<=10: settings['volume']=int(vol)
        elif ch=='2':
            d = input("Poziom AI (easy/medium/hard): ")
            if d in ['easy','medium','hard']: settings['ai_difficulty']=d
        elif ch=='3':
            a = input("Algorytm (minimax/optimized): ")
            if a in ['minimax','optimized']: settings['ai_algorithm']=a
        elif ch=='4':
            save_json(SETTINGS_FILE, settings)
            break

def show_creators():
    print("\n--- TWORCY ---")
    print("Producent: Fire Frog FF Studio")
    print("Wydawca: Fire Frog FF Studio")
    input("\nWcisnij Enter...")

def main_menu():
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    stats = load_json(STATS_FILE, DEFAULT_STATS)
    while True:
        print("\n==== KOLKO I KRZYZYK ====")
        print("1. Singleplayer")
        print("2. Lokalny Multiplayer")
        print("3. Symulacja AI")
        print("4. Tworcy")
        print("5. Ustawienia")
        print("6. Wyjscie")
        choice = input("Wybierz opcje: ")
        if choice in ['1','2','3']:
            play_game(choice, settings, stats)
        elif choice=='4':
            show_creators()
        elif choice=='5':
            settings_menu(settings)
        elif choice=='6':
            save_json(STATS_FILE, stats)
            save_json(SETTINGS_FILE, settings)
            print("Do zobaczenia!")
            sys.exit()
        else:
            print("Niepoprawny wybor.")

if __name__ == '__main__':
    main_menu()
