import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

PORT = 5555
BUFFER_SIZE = 1024

# --- Nickname bekérése ---
nickname = simpledialog.askstring("Nickname", "Add meg a neved:")

# --- GUI létrehozása ---
root = tk.Tk()
root.title("LAN Chat")

chat_area = scrolledtext.ScrolledText(root, state='disabled', width=50, height=20)
chat_area.pack(padx=10, pady=10)

message_entry = tk.Entry(root, width=50)
message_entry.pack(padx=10, pady=(0,10))

# --- Küldés esemény ---
def send_message(event=None):
    msg = f"{nickname}: {message_entry.get()}"
    message_entry.delete(0, tk.END)
    try:
        client_socket.send(msg.encode('utf-8'))
        # Saját üzenet megjelenítése azonnal
        chat_area.config(state='normal')
        chat_area.insert(tk.END, msg + '\n')
        chat_area.yview(tk.END)
        chat_area.config(state='disabled')
    except:
        chat_area.config(state='normal')
        chat_area.insert(tk.END, "Hiba az üzenet küldésénél!\n")
        chat_area.config(state='disabled')

message_entry.bind("<Return>", send_message)

# --- Üzenetek fogadása ---
def receive_messages():
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            chat_area.config(state='normal')
            chat_area.insert(tk.END, msg + '\n')
            chat_area.yview(tk.END)
            chat_area.config(state='disabled')
        except:
            break

# --- Szerver létrehozása ---
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen()
    clients = []

    def handle_client(client):
        while True:
            try:
                msg = client.recv(BUFFER_SIZE)
                for c in clients:
                    if c != client:
                        c.send(msg)
            except:
                if client in clients:
                    clients.remove(client)
                client.close()
                break

    def accept_clients():
        while True:
            client, addr = server.accept()
            clients.append(client)
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()

    threading.Thread(target=accept_clients, daemon=True).start()

    # Broadcast a szerver jelenlétét
    def broadcast_server():
        b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        b.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                b.sendto(b"CHAT_SERVER", ('<broadcast>', PORT))
                threading.Event().wait(1)
            except:
                break

    threading.Thread(target=broadcast_server, daemon=True).start()

    # Szerver IP kiírása GUI-ban
    server_ip = socket.gethostbyname(socket.gethostname())
    ip_label = tk.Label(root, text=f"Szerver IP: {server_ip}")
    ip_label.pack()
    return server

# --- Kérjük be a csatlakozni kívánt IP-t ---
server_ip = simpledialog.askstring("Csatlakozás", "Add meg a szerver IP-címét (hagyd üresen, ha saját szervert indítasz):")

if server_ip:
    # Ha megadtak IP-t, próbáljunk csatlakozni
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, PORT))
    except:
        messagebox.showerror("Hiba", f"Nem lehet csatlakozni a {server_ip} címhez!")
        exit()
else:
    # Ha nincs IP, mi leszünk a szerver
    start_server()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', PORT))

# --- Üzenetek fogadása külön szálon ---
threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()