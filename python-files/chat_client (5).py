import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

PORT = 12345

class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("8up Sohbet Uygulaması")

        self.text_area = tk.Text(master)
        self.text_area.pack(padx=10, pady=10)

        self.input_field = tk.Entry(master)
        self.input_field.pack(padx=10, pady=5)
        self.input_field.bind("<Return>", self.send_message)

        self.connect_to_server()

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_ip = simpledialog.askstring("Bağlantı", "Sunucu IP veya adresini girin (örn: gentle-mangos-kneel.loca.lt)")
        try:
            self.sock.connect((server_ip, PORT))
        except:
            messagebox.showerror("Hata", "Sunucuya bağlanılamıyor")
            self.master.quit()
            return

        prompt = self.sock.recv(1024).decode()
        if prompt == "KULLANICI_ADI":
            self.nickname = simpledialog.askstring("Giriş", "Kullanıcı adınızı girin")
            self.sock.send(self.nickname.encode())

            if self.nickname == "admin":
                password = simpledialog.askstring("Şifre", "Admin şifresini girin", show='*')
                self.sock.send(password.encode())

        msg = self.sock.recv(1024).decode()
        if "BANLI_KULLANICI" in msg:
            messagebox.showerror("Banlı", "Sunucuya giriş izniniz yok")
            self.master.quit()
            return
        elif "YANLIŞ ŞİFRE" in msg:
            messagebox.showerror("Hatalı", "Admin şifresi yanlış")
            self.master.quit()
            return

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event):
        msg = self.input_field.get()
        if msg:
            formatted_msg = f"{self.nickname}: {msg}"
            self.sock.send(formatted_msg.encode())
            self.input_field.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                self.text_area.insert(tk.END, msg + "\n")
            except:
                break

root = tk.Tk()
app = ClientApp(root)
root.mainloop()
