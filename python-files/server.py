import socket, threading, random, time, json

HOST = '0.0.0.0'
PORT = 9999
FPS = 1

MAPS = [f"Map {i}" for i in range(1, 21)]
GAMEMODES = {
    1: "Classic Tag", 2: "Freeze Tag", 3: "Infection", 4: "Reverse Tag", 5: "Elimination Tag",
    6: "Random Swapper", 7: "King of the Hill", 8: "Stealth Mode", 9: "Tag Bomb", 10: "Blind Tag",
    11: "Zombie Horde", 12: "Tag Chain", 13: "Hunter and Prey", 14: "Capture Tag",
    15: "Relay Tag", 16: "Sniper Tag", 17: "Mirror Mode", 18: "Trap Tag", 19: "Madness Mode",
    20: "Dual Taggers"
}

class Player:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn
        self.is_it = False
        self.frozen = False
        self.infected = False
        self.alive = True
        self.captures = 0
        self.xp = 0

    def to_dict(self):
        return {
            'name': self.name, 'is_it': self.is_it, 'frozen': self.frozen,
            'infected': self.infected, 'alive': self.alive,
            'captures': self.captures, 'xp': self.xp
        }

class TagServer:
    def __init__(self):
        self.players = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()
        print("Server listening...")
        threading.Thread(target=self.accept_clients, daemon=True).start()
        self.current_map = None
        self.current_mode = None
        self.bomb_holder = None
        self.bomb_timer = 0
        self.hill_holder = None

    def accept_clients(self):
        while True:
            conn, addr = self.server.accept()
            conn.sendall(b"NAME?\n")
            name = conn.recv(1024).decode().strip()
            player = Player(name, conn)
            self.players.append(player)
            print(f"{name} joined.")
            threading.Thread(target=self.listen, args=(player,), daemon=True).start()
            if len(self.players) >= 2:
                self.start_game()

    def broadcast(self, data):
        for p in self.players:
            try:
                p.conn.sendall((json.dumps(data) + "\n").encode())
            except:
                pass

    def listen(self, player):
        while True:
            try:
                msg = player.conn.recv(1024).decode().strip()
                if not msg: break
                data = json.loads(msg)
                self.handle(player, data)
            except:
                break
        player.alive = False

    def handle(self, player, data):
        cmd, val = data.get('cmd'), data.get('val')
        if cmd == 'vote_map':
            player.vote_map = val
        elif cmd == 'vote_mode':
            player.vote_mode = val
        elif cmd == 'tag':
            player.vote_tag = val

    def start_game(self):
        self.voting_phase()
        self.game_loop()

    def voting_phase(self):
        map_choices = random.sample(MAPS, 3)
        mode_choices = random.sample(list(GAMEMODES.keys()), 3)
        self.broadcast({'phase': 'voting_map', 'options': map_choices})
        while any(not hasattr(p, 'vote_map') for p in self.players): time.sleep(0.1)
        winner_map = max(self.players, key=lambda p: p.vote_map).vote_map
        self.current_map = winner_map

        self.broadcast({'phase': 'voting_mode', 'options': [GAMEMODES[m] for m in mode_choices]})
        while any(not hasattr(p, 'vote_mode') for p in self.players): time.sleep(0.1)
        chosen = max(self.players, key=lambda p: p.vote_mode).vote_mode
        self.current_mode = next(k for k, v in GAMEMODES.items() if v == chosen)

        self.broadcast({'phase': 'start', 'map': self.current_map, 'mode': GAMEMODES[self.current_mode]})

    def game_loop(self):
        while sum(p.alive for p in self.players) > 1:
            self.play_round()
            time.sleep(1.0 / FPS)
        winner = next((p.name for p in self.players if p.alive), "No one")
        self.broadcast({'phase': 'gameover', 'winner': winner})

    def play_round(self):
        for p in self.players:
            p.xp += 1
        self.broadcast({'phase': 'update', 'players': [p.to_dict() for p in self.players]})

if __name__ == "__main__":
    TagServer()
    while True:
        time.sleep(1)
