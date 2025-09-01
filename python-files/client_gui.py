import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

# Sunucu bilgileri
HOST = '0.0.0.0'  # Buraya sunucunun IP'sini yaz
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Tkinter GUI
root = tk.Tk()
root.title("WhatsApp Python Clone")
root.geometry("400x600")

nickname = simpledialog.askstring("Nickname", "İsminizi girin", parent=root)

# Mesaj gösterme alanı
messages_frame = scrolledtext.ScrolledText(root, wrap=tk.WORD)
messages_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
messages_frame.config(state='disabled')

# Mesaj giriş alanı
entry_message = tk.Entry(root)
entry_message.pack(side=tk.LEFT, padx=(10,0), pady=10, fill=tk.X, expand=True)

def send_message():
    message = entry_message.get()
    if message:
        client.send(f"{nickname}: {message}".encode('utf-8'))
        entry_message.delete(0, tk.END)

send_button = tk.Button(root, text="Gönder", command=send_message)
send_button.pack(side=tk.RIGHT, padx=(0,10), pady=10)

# Mesajları alma
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            messages_frame.config(state='normal')
            messages_frame.insert(tk.END, message + "\n")
            messages_frame.yview(tk.END)
            messages_frame.config(state='disabled')
        except:
            print("Sunucuya bağlanılamıyor!")
            client.close()
            break

threading.Thread(target=receive, daemon=True).start()
root.mainloop()
