import os
import sqlite3
import secrets
import string
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from cryptography.fernet import Fernet
import csv

ARQUIVO_CHAVE = "chave.key"
BANCO_DADOS = "senhas.db"
SENHA_MESTRA = "1234"

def gerar_chave():
    chave = Fernet.generate_key()
    with open(ARQUIVO_CHAVE, "wb") as file:
        file.write(chave)

def carregar_chave():
    with open(ARQUIVO_CHAVE, "rb") as file:
        return file.read()

def criptografar(texto):
    f = Fernet(carregar_chave())
    return f.encrypt(texto.encode()).decode()

def descriptografar(texto):
    f = Fernet(carregar_chave())
    return f.decrypt(texto.encode()).decode()

def inicializar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico TEXT NOT NULL,
            usuario TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def inserir_senha(servico, usuario, senha):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    senha_criptografada = criptografar(senha)
    cursor.execute("INSERT INTO senhas (servico, usuario, senha) VALUES (?, ?, ?)", (servico, usuario, senha_criptografada))
    conn.commit()
    conn.close()

def buscar_senhas(filtro=""):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("SELECT id, servico, usuario, senha FROM senhas WHERE servico LIKE ?", (f"%{filtro}%",))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def excluir_senha(id_senha):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM senhas WHERE id = ?", (id_senha,))
    conn.commit()
    conn.close()

def exportar_csv():
    dados = buscar_senhas()
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if caminho:
        with open(caminho, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Serviço", "Usuário", "Senha"])
            for _, servico, usuario, senha_cripto in dados:
                writer.writerow([servico, usuario, descriptografar(senha_cripto)])
        messagebox.showinfo("Exportado", f"Senhas exportadas para {caminho}")

def importar_csv():
    caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if caminho:
        with open(caminho, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                inserir_senha(row["Serviço"], row["Usuário"], row["Senha"])
        messagebox.showinfo("Importado", f"Senhas importadas de {caminho}")

class GerenciadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Senhas Moderno")

        self.filtro_var = tk.StringVar()
        self.filtro_var.trace_add("write", self.atualizar_lista)

        ttk.Entry(root, textvariable=self.filtro_var).pack(fill="x", padx=10, pady=5)

        self.lista = tk.Listbox(root, height=12)
        self.lista.pack(fill="both", expand=True, padx=10)
        self.lista.bind("<<ListboxSelect>>", self.mostrar_detalhes)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Adicionar", command=self.adicionar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Copiar Senha", command=self.copiar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar", command=exportar_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Importar", command=importar_csv).pack(side="left", padx=5)

        self.atualizar_lista()

    def atualizar_lista(self, *_):
        self.lista.delete(0, tk.END)
        self.itens = buscar_senhas(self.filtro_var.get())
        for item in self.itens:
            self.lista.insert(tk.END, f"{item[1]} ({item[2]})")

    def mostrar_detalhes(self, event=None):
        sel = self.lista.curselection()
        if sel:
            i = sel[0]
            id_senha, servico, usuario, senha_cripto = self.itens[i]
            senha = descriptografar(senha_cripto)
            messagebox.showinfo("Detalhes", f"Serviço: {servico}
Usuário: {usuario}
Senha: {senha}")

    def adicionar(self):
        servico = simpledialog.askstring("Serviço", "Nome do serviço:")
        if not servico:
            return
        usuario = simpledialog.askstring("Usuário", "Nome de usuário:")
        if not usuario:
            return
        senha = gerar_senha()
        inserir_senha(servico, usuario, senha)
        messagebox.showinfo("Senha Gerada", f"Senha para {servico}:
{senha}")
        self.atualizar_lista()

    def excluir(self):
        sel = self.lista.curselection()
        if sel:
            i = sel[0]
            id_senha = self.itens[i][0]
            if messagebox.askyesno("Confirmação", "Deseja excluir esta senha?"):
                excluir_senha(id_senha)
                self.atualizar_lista()

    def copiar(self):
        sel = self.lista.curselection()
        if sel:
            i = sel[0]
            senha = descriptografar(self.itens[i][3])
            self.root.clipboard_clear()
            self.root.clipboard_append(senha)
            messagebox.showinfo("Copiado", "Senha copiada para área de transferência.")

def login():
    senha = simpledialog.askstring("Senha Mestra", "Digite a senha mestra:", show="*")
    if senha == SENHA_MESTRA:
        if not os.path.exists(ARQUIVO_CHAVE):
            gerar_chave()
        inicializar_banco()
        app = ttk.Window(themename="darkly")
        GerenciadorApp(app)
        app.mainloop()
    else:
        messagebox.showerror("Erro", "Senha mestra incorreta.")

if __name__ == "__main__":
    login()