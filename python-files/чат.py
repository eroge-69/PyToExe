# main.py
# -*- coding: utf-8 -*-
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Танзимот
IS_SERVER = True  # True = қабулкунанда, False = фиристанда
PORT = 3
ADDR = "00:1A:7D:DA:71:13"  # MAC-и дастгоҳи дигар (барои клиент)

sock = None

def start_server():
    global sock
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.bind(("", PORT))
    sock.listen(1)
    status_label.config(text="Интизори пайвастшавӣ...")
    client, addr = sock.accept()
    status_label.config(text="Пайваст шуд!")
    threading.Thread(target=receive, args=(client,)).start()

def connect_client():
    global sock
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.connect((ADDR, PORT))
    status_label.config(text="Пайваст шуд!")
    threading.Thread(target=receive, args=(sock,)).start()

def receive(s):
    while True:
        try:
            data = s.recv(1024).decode("utf-8")
            chat.insert(tk.END, "Дигар: " + data + "\n")
        except:
            break

def send():
    msg = entry.get()
    if msg:
        sock.send(msg.encode("utf-8"))
        chat.insert(tk.END, "Шумо: " + msg + "\n")
        entry.delete(0, tk.END)

# UI
root = tk.Tk()
root.title("ChatSiel")
root.geometry("400x500")
root.configure(bg="#e5ddd5")

status_label = tk.Label(root, text="Статус: Номаълум", bg="#075e54", fg="white", font=("Arial", 12))
status_label.pack(fill=tk.X)

chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 11))
chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(padx=10, pady=5, fill=tk.X)

send_btn = tk.Button(root, text="Фиристодан", bg="#25d366", fg="white", font=("Arial", 12), command=send)
send_btn.pack(padx=10, pady=5, fill=tk.X)

# Оғоз
if IS_SERVER:
    threading.Thread(target=start_server).start()
else:
    threading.Thread(target=connect_client).start()

root.mainloop()
