import socket
import threading
import tkinter as tk
from tkinter import ttk
import time

BROADCAST_PORT = 50000
PING_INTERVAL = 2
TIMEOUT = 5

class Peer:
    def __init__(self, ip):
        self.ip = ip
        self.last_seen = time.time()

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Ping Monitor")
        self.peers = {}

        self.tree = ttk.Treeview(root, columns=("IP", "Status"), show="headings")
        self.tree.heading("IP", text="IP-адрес")
        self.tree.heading("Status", text="Статус")
        self.tree.pack(fill="both", expand=True)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", BROADCAST_PORT))

        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.broadcast, daemon=True).start()
        self.update_gui()

    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data == b"ping":
                    self.sock.sendto(b"pong", addr)
                elif data == b"pong":
                    ip = addr[0]
                    if ip not in self.peers:
                        self.peers[ip] = Peer(ip)
                    else:
                        self.peers[ip].last_seen = time.time()
            except:
                pass

    def broadcast(self):
        while True:
            self.sock.sendto(b"ping", ("<broadcast>", BROADCAST_PORT))
            time.sleep(PING_INTERVAL)

    def update_gui(self):
        now = time.time()
        self.tree.delete(*self.tree.get_children())
        for ip, peer in self.peers.items():
            status = "🟢 Online" if now - peer.last_seen < TIMEOUT else "🔴 Offline"
            self.tree.insert("", "end", values=(ip, status))
        self.root.after(1000, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()