
import socket
import tkinter as tk
from PIL import Image, ImageTk
import io

SERVER_IP = '127.0.0.1'  # Replace with the actual IP of the host
PORT = 5001
PASSWORD = "secure123"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.send(PASSWORD.encode())

if client.recv(1024) != b"AUTH_SUCCESS":
    print("[!] Authentication failed.")
    client.close()
    exit()

root = tk.Tk()
root.title("VimalsRemote Viewer")
label = tk.Label(root)
label.pack()

def receive():
    try:
        size = int(client.recv(16).strip())
        data = b''
        while len(data) < size:
            data += client.recv(4096)
        img = Image.open(io.BytesIO(data))
        img = ImageTk.PhotoImage(img)
        label.config(image=img)
        label.image = img
    except Exception as e:
        print("Error:", e)
    root.after(100, receive)

receive()
root.mainloop()
