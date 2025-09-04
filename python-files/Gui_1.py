import socket
import tkinter as tk
from tkinter import messagebox

# Configurazione IP e porta dei dispositivi
DEVICE_1 = ("172.16.98.247", 5150)
DEVICE_2 = ("172.16.98.167", 5150)

# Comandi predefiniti da inviare (non visibili all'utente)
COMMAND_1 = "Chrome"
COMMAND_2 = "Chrome"

class TCPClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None

    def connect(self):
        # Chiudi la vecchia connessione se esiste
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2)
            self.socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            print(f"Errore connessione a {self.ip}:{self.port} -> {e}")
            self.socket = None
            return False

    def send(self, data):
        if self.socket:
            try:
                self.socket.sendall((data + "\r").encode())  # Aggiunge \r
                return True
            except Exception as e:
                print(f"Errore invio a {self.ip}:{self.port} -> {e}")
        return False

    def is_connected(self):
        return self.socket is not None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Controllo TCP/IP")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.client1 = TCPClient(*DEVICE_1)
        self.client2 = TCPClient(*DEVICE_2)

        # Stato connessione
        self.status_label1 = tk.Label(root, text="Dispositivo 1: Connessione...", fg="blue")
        self.status_label1.pack(pady=5)

        self.status_label2 = tk.Label(root, text="Dispositivo 2: Connessione...", fg="blue")
        self.status_label2.pack(pady=5)

        # Pulsanti di invio
        self.send_button1 = tk.Button(root, text="Invia a Dispositivo 1", command=self.send_to_device1)
        self.send_button1.pack(pady=10)

        self.send_button2 = tk.Button(root, text="Invia a Dispositivo 2", command=self.send_to_device2)
        self.send_button2.pack(pady=10)

        # Pulsante di riconnessione
        self.reconnect_button = tk.Button(root, text="Riconnetti", command=self.update_connection_status)
        self.reconnect_button.pack(pady=10)

        # Connessione iniziale
        self.update_connection_status()

    def update_connection_status(self):
        # Dispositivo 1
        if self.client1.connect():
            self.status_label1.config(text="Player 1: Connesso", fg="green")
        else:
            self.status_label1.config(text="Player 1: Non connesso", fg="red")

        # Dispositivo 2
        if self.client2.connect():
            self.status_label2.config(text="Dispositivo 2: Connesso", fg="green")
        else:
            self.status_label2.config(text="Dispositivo 2: Non connesso", fg="red")

    def send_to_device1(self):
        if not self.client1.send(COMMAND_1):
            messagebox.showerror("Errore", "Impossibile inviare al dispositivo 1.")

    def send_to_device2(self):
        if not self.client2.send(COMMAND_2):
            messagebox.showerror("Errore", "Impossibile inviare al dispositivo 2.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
