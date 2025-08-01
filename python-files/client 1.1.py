import tkinter as tk
import tkinter.scrolledtext as st
import threading
import socket

class Messenger:
    def __init__(self, master, host='127.0.0.1', port=12345):
        self.master = master
        master.title("Vlink Chat 1.1")

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        self.chat_history = st.ScrolledText(master, state='disabled')
        self.chat_history.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(master, width=50)
        self.message_entry.pack(padx=10, pady=10)

        self.send_button = tk.Button(master, text="Отправить", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.sock.sendall(message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)
            self.display_message(f"Вы: {message}")

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    self.display_message(f"Другой пользователь: {data}")
            except:
                break

    def display_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, message + '\n')
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

root = tk.Tk()
messenger = Messenger(root)
root.mainloop()
