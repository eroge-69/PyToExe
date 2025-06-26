import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from datetime import datetime

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("💬 Chat entre potes")
        self.master.geometry("600x500")
        self.master.configure(bg="#2c2f33")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.pseudo = simpledialog.askstring("Pseudo", "Entre ton pseudo :", parent=self.master)
        if not self.pseudo:
            self.master.destroy()
            return

        self.build_gui()
        self.connect_to_server()

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def build_gui(self):
        self.chat_label = tk.Label(self.master, text="💬 Discussion", bg="#2c2f33", fg="#ffffff", font=("Helvetica", 14, "bold"))
        self.chat_label.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, state='disabled', bg="#23272a", fg="#ffffff", font=("Consolas", 12))
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.entry_field = tk.Entry(self.master, bg="#40444b", fg="#ffffff", font=("Helvetica", 12))
        self.entry_field.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry_field.bind("<Return>", self.send_message)

    def connect_to_server(self):
        try:
            self.client_socket.connect(("localhost", 12345))
            self.client_socket.recv(1024)  # message "Entrez votre pseudo"
            self.client_socket.send(self.pseudo.encode())
        except Exception as e:
            self.display_message(f"❌ Erreur de connexion : {e}")
            self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.display_message(message)
            except:
                self.display_message("❌ Déconnecté du serveur.")
                self.client_socket.close()
                break

    def send_message(self, event=None):
        message = self.entry_field.get()
        if message:
            timestamp = datetime.now().strftime("%H:%M")
            self.display_message(f"🕒 {timestamp} | Vous : {message}", local=True)
            try:
                self.client_socket.send(message.encode())
                if message.lower() == "/quit":
                    self.master.destroy()
            except:
                self.display_message("❌ Erreur d'envoi.")
            self.entry_field.delete(0, tk.END)

    def display_message(self, message, local=False):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)  # scroll automatique

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
