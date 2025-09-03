import socket
import threading
import random

players = {}   # name -> {conn, code, stats}
lobbies = {}   # code -> [player names]

def init_stats():
    return {
        "Troops": 200,
        "Supplies": 50,
        "Morale": 100,
        "BattlesWon": 0
    }

def broadcast(lobby_code, message):
    """Send a message to everyone in a lobby"""
    if lobby_code in lobbies:
        for pname in lobbies[lobby_code]:
            players[pname]["conn"].send((message + "\n").encode())

def find_lobby(name):
    for lc, plist in lobbies.items():
        if name in plist:
            return lc
    return None

def handle_client(conn, addr):
    conn.send(b"Welcome to Napoleonic Wars!\nEnter your name: ")
    name = conn.recv(1024).decode().strip()

    # Assign friend code and stats
    code = str(1000 + len(players))
    players[name] = {"conn": conn, "code": code, "stats": init_stats()}
    conn.send(f"Your friend code: {code}\n".encode())
    conn.send(b"Type MENU to see your options.\n")

    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break

        cmd = data.upper()

        if cmd == "MENU":
            conn.send(b"Options: HOST | JOIN <code> | BATTLE | REST | INSPECT | C <msg> | EXIT\n")

        elif cmd == "HOST":
            lobbies[code] = [name]
            conn.send(b"Lobby created. Waiting for friend to join...\n")

        elif cmd.startswith("JOIN"):
            parts = data.split()
            if len(parts) == 2:
                join_code = parts[1]
                if join_code in lobbies:
                    lobbies[join_code].append(name)
                    host = lobbies[join_code][0]
                    conn.send(f"You joined {host}'s lobby!\n".encode())
                    players[host]["conn"].send(f"{name} joined your lobby!\n".encode())
                else:
                    conn.send(b"Lobby not found.\n")
            else:
                conn.send(b"Usage: JOIN <code>\n")

        elif cmd == "BATTLE":
            lobby_code = find_lobby(name)
            if not lobby_code:
                conn.send(b"You are not in a lobby.\n")
                continue

            outcome = random.choice(["win", "loss", "stalemate"])
            for pname in lobbies[lobby_code]:
                stats = players[pname]["stats"]
                if outcome == "win":
                    stats["Troops"] -= 20
                    stats["Morale"] += 10
                    stats["BattlesWon"] += 1
                elif outcome == "loss":
                    stats["Troops"] -= 50
                    stats["Morale"] -= 20
                else:  # stalemate
                    stats["Troops"] -= 30
                    stats["Morale"] -= 10
            broadcast(lobby_code, f"Battle fought! Outcome: {outcome.upper()}.")

        elif cmd == "REST":
            stats = players[name]["stats"]
            stats["Supplies"] += 20
            stats["Morale"] += 5
            conn.send(b"You rested and gained supplies + morale.\n")

        elif cmd == "INSPECT":
            stats = players[name]["stats"]
            msg = (f"Troops: {stats['Troops']} | "
                   f"Supplies: {stats['Supplies']} | "
                   f"Morale: {stats['Morale']} | "
                   f"Battles Won: {stats['BattlesWon']}")
            conn.send((msg + "\n").encode())

        elif data.startswith("C "):  # Chat command
            lobby_code = find_lobby(name)
            if not lobby_code:
                conn.send(b"You are not in a lobby.\n")
                continue
            chat_msg = data[2:].strip()
            if chat_msg:
                broadcast(lobby_code, f"[{name}]: {chat_msg}")

        elif cmd == "EXIT":
            conn.send(b"Goodbye!\n")
            break

        else:
            conn.send(b"Unknown command. Type MENU to see options.\n")

    conn.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen()
    print("Server running on port 12345...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start()
