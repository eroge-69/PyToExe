#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

class PortaCheckerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Verificador de Porta")
        self.master.geometry("500x400")
        self.servidor_ativo = False
        self.servidor_thread = None
        self.stop_event = threading.Event()

        # Campo de entrada
        self.porta_label = tk.Label(master, text="Porta (1-65535):")
        self.porta_label.pack(pady=(10, 0))
        self.porta_entry = tk.Entry(master)
        self.porta_entry.pack()

        # Botões
        self.verificar_btn = tk.Button(master, text="Verificar Porta", command=self.verificar_porta)
        self.verificar_btn.pack(pady=5)

        self.escutar_btn = tk.Button(master, text="Iniciar Servidor", command=self.iniciar_servidor)
        self.escutar_btn.pack(pady=5)

        self.parar_btn = tk.Button(master, text="Parar Servidor", command=self.parar_servidor, state=tk.DISABLED)
        self.parar_btn.pack(pady=5)

        # Área de saída
        self.output = scrolledtext.ScrolledText(master, height=15, width=60)
        self.output.pack(pady=(10, 0))
        self.output.config(state=tk.DISABLED)

    def log(self, msg):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def verificar_porta(self):
        porta = self._get_porta()
        if porta is None:
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        resultado = s.connect_ex(('127.0.0.1', porta))
        s.close()

        if resultado == 0:
            self.log(f"Porta {porta} está ATIVA (em uso).")
        else:
            self.log(f"Porta {porta} está INATIVA ou não está sendo usada.")

    def iniciar_servidor(self):
        porta = self._get_porta()
        if porta is None:
            return

        if self.servidor_ativo:
            self.log("Servidor já está em execução.")
            return

        self.stop_event.clear()
        self.servidor_thread = threading.Thread(target=self._servidor_tcp, args=(porta,), daemon=True)
        self.servidor_thread.start()
        self.servidor_ativo = True
        self.escutar_btn.config(state=tk.DISABLED)
        self.parar_btn.config(state=tk.NORMAL)
        self.log(f"Servidor escutando na porta {porta}...")

    def _servidor_tcp(self, porta):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('0.0.0.0', porta))
            server.listen(5)
            server.settimeout(1)

            while not self.stop_event.is_set():
                try:
                    conn, addr = server.accept()
                    self.log(f"Conexão recebida de {addr}")
                    conn.close()
                except socket.timeout:
                    continue
            server.close()
        except Exception as e:
            self.log(f"Erro ao iniciar o servidor: {e}")
            self.servidor_ativo = False
            self.escutar_btn.config(state=tk.NORMAL)
            self.parar_btn.config(state=tk.DISABLED)

    def parar_servidor(self):
        if not self.servidor_ativo:
            return
        self.stop_event.set()
        self.servidor_ativo = False
        self.escutar_btn.config(state=tk.NORMAL)
        self.parar_btn.config(state=tk.DISABLED)
        self.log("Servidor parado.")

    def _get_porta(self):
        try:
            porta = int(self.porta_entry.get())
            if 1 <= porta <= 65535:
                return porta
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite uma porta válida entre 1 e 65535.")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = PortaCheckerApp(root)
    root.mainloop()

