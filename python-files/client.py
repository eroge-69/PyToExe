import socket, threading, json, time

HOST = '127.0.0.1'
PORT = 9999

def listen(sock):
    while True:
        data = sock.recv(4096).decode().strip().split('\n')
        for msg in data:
            if not msg: continue
            obj = json.loads(msg)
            handle(obj, sock)

def handle(obj, sock):
    phase = obj.get('phase')
    if phase == 'voting_map':
        choice = vote_input("map", obj['options'])
        sock.sendall(json.dumps({'cmd':'vote_map','val':choice}).encode())
    elif phase == 'voting_mode':
        choice = vote_input("mode", obj['options'])
        sock.sendall(json.dumps({'cmd':'vote_mode','val':choice}).encode())
    elif phase == 'start':
        print(f"Game started on map {obj['map']} mode {obj['mode']}")
    elif phase == 'update':
        print("Players:", obj['players'])
        it = next(p for p in obj['players'] if p['is_it'])
        if it['name'] == NAME:
            others = [p['name'] for p in obj['players'] if p['alive'] and p['name'] != NAME]
            if others:
                choice = vote_input("tag", others)
                sock.sendall(json.dumps({'cmd':'tag','val':choice}).encode())
    elif phase == 'gameover':
        print("Game Over! Winner:", obj['winner'])
        exit()

def vote_input(topic, options):
    print(f"Choose {topic}:")
    for i, o in enumerate(options, 1):
        print(f"{i}. {o}")
    while True:
        c = input("Choice: ")
        if c.isdigit() and 1 <= int(c) <= len(options):
            return options[int(c)-1]

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    NAME = input("Enter your name: ")
    sock.recv(1024)
    sock.sendall(NAME.encode())
    threading.Thread(target=listen, args=(sock,), daemon=True).start()
    while True:
        time.sleep(1)
