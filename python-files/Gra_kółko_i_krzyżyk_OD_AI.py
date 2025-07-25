import random
import json
import os
import sys
import socket
import threading

SETTINGS_FILE = 'tictactoe_settings.json'
STATS_FILE = 'tictactoe_stats.json'

DEFAULT_SETTINGS = {
    "volume": 5,
    "ai_difficulty": "medium",
    "ai_algorithm": "minimax"
}
DEFAULT_STATS = {}

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default.copy()
    return default.copy()

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def draw_board(b):
    print()
    def color(sym):
        if sym == 'X': return f"\033[91mX\033[0m"
        if sym == 'O': return f"\033[94mO\033[0m"
        return sym

    for i in range(3):
        row = [color(b[3*i+j]) if b[3*i+j] else str(3*i+j+1) for j in range(3)]
        print(" " + " | ".join(row))
        if i < 2:
            print("---+---+---")
    print()

def check_win(b, p):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    return any(b[a]==b[c]==b[d]==p for a,c,d in wins)

def board_full(b):
    return all(cell is not None for cell in b)

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
    elif difficulty == 'medium' and random.random() < 0.5:
        return random.choice(moves)
    best_score, best_move = -2, None
    for m in moves:
        b[m] = ai_piece
        score = minimax(b, 0, False, ai_piece, human_piece)
        b[m] = None
        if score > best_score:
            best_score, best_move = score, m
    return best_move

def ensure_account(name, stats):
    stats.setdefault(name, {"W":0, "R":0, "P":0})

def play_game(mode, settings, stats):
    board = [None]*9
    starter = None

    if mode == '1':
        name = input("Wpisz swoje imie: ")
        ensure_account(name, stats)
        player, ai = 'X','O'
        sel = input("Kto zaczyna? (1) Gracz (2) AI (3) Losowo: ")
        starter = 'player' if sel=='1' else 'ai' if sel=='2' else random.choice(['player','ai'])
        cur = starter

    elif mode == '2':
        p1 = input("Imie gracza 1: "); ensure_account(p1, stats)
        p2 = input("Imie gracza 2: "); ensure_account(p2, stats)
        sel = input(f"Kto zaczyna? (1) {p1} (2) {p2} (3) Losowo: ")
        cur = p1 if sel=='1' else p2 if sel=='2' else random.choice([p1, p2])

    elif mode == '3':
        sel = input("Kto zaczyna? (1) AI X (2) AI O (3) Losowo: ")
        cur = 'X' if sel=='1' else 'O' if sel=='2' else random.choice(['X','O'])

    else:
        return

    while True:
        draw_board(board)
        if mode == '1':
            if cur == 'player':
                move = input("Ruch: ")
                if not move.isdigit() or not 1<=int(move)<=9 or board[int(move)-1] is not None:
                    print("Niepoprawny ruch."); continue
                board[int(move)-1] = player
                if check_win(board, player):
                    print("Wygrywasz!"); stats[name]["W"] += 1; break
                if board_full(board):
                    print("Remis!"); stats[name]["R"] +=1; break
                cur = 'ai'
            else:
                print("Ruch AI...")
                m = get_ai_move(board, ai, player, settings['ai_difficulty'], settings['ai_algorithm'])
                print(f"AI wybralo pole: {m+1}")
                board[m] = ai
                if check_win(board, ai):
                    print("AI wygrywa!"); stats[name]["P"] += 1; break
                if board_full(board):
                    print("Remis!"); stats[name]["R"] +=1; break
                cur = 'player'

        elif mode == '2':
            print(f"Tura: {cur}")
            move = input("Ruch: ")
            if not move.isdigit() or not 1<=int(move)<=9 or board[int(move)-1] is not None:
                print("Niepoprawny ruch."); continue
            piece = 'X' if cur == p1 else 'O'
            board[int(move)-1] = piece
            if check_win(board, piece):
                print(f"{cur} wygrywa!"); stats[cur]["W"] += 1
                opp = p1 if cur==p2 else p2
                stats[opp]["P"] +=1; break
            if board_full(board):
                print("Remis!"); stats[p1]["R"]+=1; stats[p2]["R"]+=1; break
            cur = p1 if cur==p2 else p2

        else:
            print(f"Tura AI: {cur}")
            opp = 'O' if cur=='X' else 'X'
            m = get_ai_move(board, cur, opp, settings['ai_difficulty'], settings['ai_algorithm'])
            print(f"AI {cur} wybralo pole: {m+1}")
            board[m] = cur
            if check_win(board, cur):
                print(f"AI {cur} wygrywa!"); break
            if board_full(board):
                print("Remis!"); break
            cur = opp

    draw_board(board)
    save_json(STATS_FILE, stats)

def play_pvp_game(p1, p2, settings, stats, starter=None):
    board = [None]*9
    cur = starter if starter else random.choice([p1, p2])
    while True:
        draw_board(board)
        print(f"Tura: {cur}")
        move = input("Ruch: ")
        if not move.isdigit() or not 1<=int(move)<=9 or board[int(move)-1] is not None:
            print("Niepoprawny ruch."); continue
        piece = 'X' if cur == p1 else 'O'
        board[int(move)-1] = piece
        if check_win(board, piece):
            print(f"{cur} wygrywa!")
            stats[cur]["W"] += 1
            opp = p1 if cur==p2 else p2
            stats[opp]["P"] +=1
            draw_board(board)
            return cur
        if board_full(board):
            print("Remis!")
            stats[p1]["R"]+=1
            stats[p2]["R"]+=1
            draw_board(board)
            return None
        cur = p1 if cur==p2 else p2

def tournament_pvp(settings, stats):
    print("\n--- TURNIEJ GRACZ VS GRACZ ---")
    p1 = input("Imie gracza 1: "); ensure_account(p1, stats)
    p2 = input("Imie gracza 2: "); ensure_account(p2, stats)
    while True:
        n_games = input("Ile gier? (3 lub 5): ")
        if n_games in ['3', '5']:
            n_games = int(n_games)
            break
        print("Wybierz 3 lub 5.")
    wins = {p1: 0, p2: 0}
    for i in range(1, n_games+1):
        print(f"\n--- Gra {i} z {n_games} ---")
        starter = p1 if i % 2 == 1 else p2  # naprzemienne rozpoczynanie
        winner = play_pvp_game(p1, p2, settings, stats, starter)
        if winner:
            wins[winner] += 1
        print(f"Stan: {p1} {wins[p1]} - {p2} {wins[p2]}")
        if wins[p1] > n_games//2 or wins[p2] > n_games//2:
            break
    print("\n=== KONIEC TURNIEJU ===")
    if wins[p1] > wins[p2]:
        print(f"Zwycięzca turnieju: {p1} ({wins[p1]}:{wins[p2]})")
    elif wins[p2] > wins[p1]:
        print(f"Zwycięzca turnieju: {p2} ({wins[p2]}:{wins[p1]})")
    else:
        print("Remis w turnieju!")
    save_json(STATS_FILE, stats)
    input("Wcisnij Enter...")

def settings_menu(settings):
    while True:
        print("\n--- USTAWIENIA ---")
        print(f"1. Glosnosc: {settings['volume']}")
        print(f"2. Poziom AI: {settings['ai_difficulty']}")
        print(f"3. Algorytm AI: {settings['ai_algorithm']}")
        print("4. Powrot")
        ch = input("Wybierz: ")
        if ch=='1':
            v = input("Nowa (0-10): ")
            if v.isdigit() and 0<=int(v)<=10: settings['volume']=int(v)
        elif ch=='2':
            d = input("Poziom (easy/medium/hard): ")
            if d in ['easy','medium','hard']: settings['ai_difficulty']=d
        elif ch=='3':
            a = input("Algorytm (minimax/optimized): ")
            if a in ['minimax','optimized']: settings['ai_algorithm']=a
        elif ch=='4':
            save_json(SETTINGS_FILE, settings); break

def show_creators():
    print("\n--- TWORCY ---")
    print("Producent: Fire Frog FF Studio")
    print("Wydawca: Fire Frog FF Studio")
    input("Wcisnij Enter...")

def show_ranking(stats):
    print("\n--- RANKING GRACZY ---")
    if not stats:
        print("Brak statystyk."); input("Enter..."); return
    players = []
    for name, d in stats.items():
        total = d["W"] + d["R"] + d["P"]
        win_rate = (d["W"] / total) * 100 if total > 0 else 0
        players.append((name, d["W"], d["R"], d["P"], total, win_rate))

    players.sort(key=lambda x: (-x[1], x[0]))
    print(f"{'Gracz':<15}{'W':<4}{'R':<4}{'P':<4}{'Razem':<6}{'Wygrane %':<10}")
    print("-"*50)
    for n,w,r,p,t,wr in players:
        print(f"{n:<15}{w:<4}{r:<4}{p:<4}{t:<6}{wr:>7.1f} %")
    input("Wcisnij Enter...")

# --- SERWER I KLIENT SIECIOWY ---

def send_msg(sock, msg):
    sock.sendall((msg + "\n").encode())

def recv_msg(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            raise ConnectionError("Rozłączono")
        data += chunk
    return data.decode().strip()

def play_network_server(settings):
    host = "0.0.0.0"
    port = 65432
    print(f"Uruchamianie serwera na porcie {port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("Oczekiwanie na połączenie klienta...")
        conn, addr = s.accept()
        with conn:
            print(f"Połączono z {addr}")
            board = [None]*9
            cur = 'X'  # serwer zawsze X, klient O
            while True:
                draw_board(board)
                if cur == 'X':
                    while True:
                        move = input("Twój ruch (1-9): ")
                        if not move.isdigit() or not 1<=int(move)<=9 or board[int(move)-1] is not None:
                            print("Niepoprawny ruch."); continue
                        break
                    board[int(move)-1] = 'X'
                    send_msg(conn, move)
                    if check_win(board, 'X'):
                        print("Wygrałeś!")
                        send_msg(conn, "WIN")
                        break
                    if board_full(board):
                        print("Remis!")
                        send_msg(conn, "DRAW")
                        break
                    cur = 'O'
                else:
                    print("Czekam na ruch przeciwnika...")
                    move = recv_msg(conn)
                    if move == "WIN":
                        print("Przeciwnik wygrał!")
                        break
                    if move == "DRAW":
                        print("Remis!")
                        break
                    idx = int(move)-1
                    board[idx] = 'O'
                    cur = 'X'
            draw_board(board)
            input("Wciśnij Enter, aby wrócić do menu...")

def play_network_client(settings):
    host = input("Podaj IP serwera: ")
    port = 65432
    print(f"Łączenie z serwerem {host}:{port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        board = [None]*9
        cur = 'X'
        while True:
            draw_board(board)
            if cur == 'X':
                print("Czekam na ruch przeciwnika...")
                move = recv_msg(s)
                if move == "WIN":
                    print("Przeciwnik wygrał!")
                    break
                if move == "DRAW":
                    print("Remis!")
                    break
                idx = int(move)-1
                board[idx] = 'X'
                cur = 'O'
            else:
                while True:
                    move = input("Twój ruch (1-9): ")
                    if not move.isdigit() or not 1<=int(move)<=9 or board[int(move)-1] is not None:
                        print("Niepoprawny ruch."); continue
                    break
                board[int(move)-1] = 'O'
                send_msg(s, move)
                if check_win(board, 'O'):
                    print("Wygrałeś!")
                    send_msg(s, "WIN")
                    break
                if board_full(board):
                    print("Remis!")
                    send_msg(s, "DRAW")
                    break
                cur = 'X'
        draw_board(board)
        input("Wciśnij Enter, aby wrócić do menu...")

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
        print("7. Ranking")
        print("8. Turniej Gracz vs Gracz")
        print("9. Serwer sieciowy (gra przez LAN)")
        print("10. Klient sieciowy (gra przez LAN)")
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
            print("Do zobaczenia!"); sys.exit()
        elif choice=='7':
            show_ranking(stats)
        elif choice=='8':
            tournament_pvp(settings, stats)
        elif choice=='9':
            play_network_server(settings)
        elif choice=='10':
            play_network_client(settings)
        else:
            print("Niepoprawny wybor.")

if __name__ == '__main__':
    main_menu()