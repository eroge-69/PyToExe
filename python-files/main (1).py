import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

# Conexão com o banco de dados
conn = sqlite3.connect("academia.db")
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    pagamento TEXT,
    vencimento TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS frequencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf TEXT,
    data TEXT,
    FOREIGN KEY (cpf) REFERENCES alunos(cpf)
)
""")
conn.commit()

# Funções
def cadastrar_aluno():
    def salvar():
        nome = entry_nome.get()
        cpf = entry_cpf.get()
        pagamento = entry_pagamento.get()
        vencimento = entry_vencimento.get()
        try:
            cursor.execute("INSERT INTO alunos VALUES (?, ?, ?, ?)", (cpf, nome, pagamento, vencimento))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Aluno {nome} cadastrado!")
            janela.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "CPF já cadastrado.")

    janela = tk.Toplevel()
    janela.title("Cadastrar Aluno")

    tk.Label(janela, text="Nome:").pack()
    entry_nome = tk.Entry(janela)
    entry_nome.pack()

    tk.Label(janela, text="CPF:").pack()
    entry_cpf = tk.Entry(janela)
    entry_cpf.pack()

    tk.Label(janela, text="Forma de Pagamento:").pack()
    entry_pagamento = tk.Entry(janela)
    entry_pagamento.pack()

    tk.Label(janela, text="Vencimento (dd/mm/aaaa):").pack()
    entry_vencimento = tk.Entry(janela)
    entry_vencimento.pack()

    tk.Button(janela, text="Salvar", command=salvar).pack()

def registrar_frequencia():
    def registrar():
        cpf = entry_cpf.get()
        cursor.execute("SELECT nome FROM alunos WHERE cpf = ?", (cpf,))
        aluno = cursor.fetchone()
        if aluno:
            hoje = datetime.date.today().strftime("%d/%m/%Y")
            cursor.execute("INSERT INTO frequencias (cpf, data) VALUES (?, ?)", (cpf, hoje))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Frequência registrada para {aluno[0]} em {hoje}")
            janela.destroy()
        else:
            messagebox.showerror("Erro", "Aluno não encontrado.")

    janela = tk.Toplevel()
    janela.title("Registrar Frequência")

    tk.Label(janela, text="CPF do Aluno:").pack()
    entry_cpf = tk.Entry(janela)
    entry_cpf.pack()

    tk.Button(janela, text="Registrar", command=registrar).pack()

def listar_alunos():
    janela = tk.Toplevel()
    janela.title("Lista de Alunos")

    texto = tk.Text(janela)
    texto.pack()

    cursor.execute("SELECT nome, vencimento FROM alunos")
    for nome, vencimento in cursor.fetchall():
        venc = datetime.datetime.strptime(vencimento, "%d/%m/%Y").date()
        hoje = datetime.date.today()
        status = "✅ Em dia" if venc >= hoje else "❌ Vencido"
        texto.insert(tk.END, f"{nome} | Vencimento: {vencimento} | Status: {status}\n")

def ver_frequencia():
    def consultar():
        cpf = entry_cpf.get()
        cursor.execute("SELECT nome FROM alunos WHERE cpf = ?", (cpf,))
        aluno = cursor.fetchone()
        if aluno:
            texto.delete("1.0", tk.END)
            texto.insert(tk.END, f"Frequência de {aluno[0]}:\n")
            cursor.execute("SELECT data FROM frequencias WHERE cpf = ?", (cpf,))
            for (data,) in cursor.fetchall():
                texto.insert(tk.END, f"- {data}\n")
        else:
            messagebox.showerror("Erro", "Aluno não encontrado.")

    janela = tk.Toplevel()
    janela.title("Ver Frequência")

    tk.Label(janela, text="CPF do Aluno:").pack()
    entry_cpf = tk.Entry(janela)
    entry_cpf.pack()

    tk.Button(janela, text="Consultar", command=consultar).pack()

    texto = tk.Text(janela)
    texto.pack()

# Interface principal
root = tk.Tk()
root.title("Sistema de Academia")

tk.Label(root, text="🏋️ Sistema de Academia", font=("Arial", 16)).pack(pady=10)

tk.Button(root, text="Cadastrar Aluno", width=30, command=cadastrar_aluno).pack(pady=5)
tk.Button(root, text="Registrar Frequência", width=30, command=registrar_frequencia).pack(pady=5)
tk.Button(root, text="Listar Alunos e Vencimentos", width=30, command=listar_alunos).pack(pady=5)
tk.Button(root, text="Ver Frequência de Aluno", width=30, command=ver_frequencia).pack(pady=5)
tk.Button(root, text="Sair", width=30, command=root.quit).pack(pady=20)

root.mainloop()
conn.close()
print('Hello world!')