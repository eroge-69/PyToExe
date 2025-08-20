
# Online Python - IDE, Editor, Compiler, Interpreter

def sum(a, b):
    return (a + b)

a = int(input('Enter 1st number: '))
b = int(input('Enter 2nd number: '))

print(f'Sum of {a} and {b} is {sum(a, b)}')
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# ---------------- BANCO DE DADOS ---------------- #
conn = sqlite3.connect("estoque.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL
)
""")
conn.commit()


# ---------------- FUNÇÕES ---------------- #
def cadastrar_produto():
    codigo = entry_codigo.get()
    nome = entry_nome.get()
    try:
        preco = float(entry_preco.get())
        quantidade = int(entry_quantidade.get())
    except ValueError:
        messagebox.showerror("Erro", "Preço e quantidade devem ser numéricos.")
        return
    
    try:
        cursor.execute("INSERT INTO produtos (codigo, nome, preco, quantidade) VALUES (?, ?, ?, ?)",
                       (codigo, nome, preco, quantidade))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        atualizar_estoque()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Já existe um produto com esse código.")


def entrada_mercadoria():
    codigo = entry_codigo.get()
    try:
        quantidade = int(entry_quantidade.get())
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser numérica.")
        return
    
    cursor.execute("SELECT quantidade FROM produtos WHERE codigo = ?", (codigo,))
    result = cursor.fetchone()
    if result:
        nova_qtd = result[0] + quantidade
        cursor.execute("UPDATE produtos SET quantidade = ? WHERE codigo = ?", (nova_qtd, codigo))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Entrada registrada. Novo estoque: {nova_qtd}")
        atualizar_estoque()
    else:
        messagebox.showerror("Erro", "Produto não encontrado.")


def saida_mercadoria():
    codigo = entry_codigo.get()
    try:
        quantidade = int(entry_quantidade.get())
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser numérica.")
        return
    
    cursor.execute("SELECT quantidade FROM produtos WHERE codigo = ?", (codigo,))
    result = cursor.fetchone()
    if result:
        if result[0] >= quantidade:
            nova_qtd = result[0] - quantidade
            cursor.execute("UPDATE produtos SET quantidade = ? WHERE codigo = ?", (nova_qtd, codigo))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Saída registrada. Novo estoque: {nova_qtd}")
            atualizar_estoque()
        else:
            messagebox.showwarning("Aviso", "Estoque insuficiente.")
    else:
        messagebox.showerror("Erro", "Produto não encontrado.")


def atualizar_estoque():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT codigo, nome, preco, quantidade FROM produtos")
    for p in cursor.fetchall():
        tree.insert("", "end", values=p)


def relatorio_baixo_estoque():
    limite = 5
    cursor.execute("SELECT codigo, nome, quantidade FROM produtos WHERE quantidade <= ?", (limite,))
    produtos = cursor.fetchall()
    if produtos:
        msg = "\n".join([f"{p[1]} (cód: {p[0]}) - qtd: {p[2]}" for p in produtos])
    else:
        msg = "Nenhum produto com baixo estoque."
    messagebox.showinfo("Relatório - Baixo Estoque", msg)


def relatorio_valor_total():
    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    total = cursor.fetchone()[0]
    total = total if total else 0
    messagebox.showinfo("Relatório - Valor Total", f"Valor total em estoque: R${total:.2f}")


# ---------------- INTERFACE ---------------- #
root = tk.Tk()
root.title("Controle de Estoque")
root.geometry("700x500")

frame_form = tk.Frame(root)
frame_form.pack(pady=10)

tk.Label(frame_form, text="Código:").grid(row=0, column=0, padx=5, pady=5)
entry_codigo = tk.Entry(frame_form)
entry_codigo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
entry_nome = tk.Entry(frame_form)
entry_nome.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Preço:").grid(row=2, column=0, padx=5, pady=5)
entry_preco = tk.Entry(frame_form)
entry_preco.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Quantidade:").grid(row=3, column=0, padx=5, pady=5)
entry_quantidade = tk.Entry(frame_form)
entry_quantidade.grid(row=3, column=1, padx=5, pady=5)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Cadastrar Produto", command=cadastrar_produto).grid(row=0, column=0, padx=5)
tk.Button(frame_buttons, text="Entrada", command=entrada_mercadoria).grid(row=0, column=1, padx=5)
tk.Button(frame_buttons, text="Saída", command=saida_mercadoria).grid(row=0, column=2, padx=5)
tk.Button(frame_buttons, text="Baixo Estoque", command=relatorio_baixo_estoque).grid(row=0, column=3, padx=5)
tk.Button(frame_buttons, text="Valor Total", command=relatorio_valor_total).grid(row=0, column=4, padx=5)

# Tabela de estoque
tree = ttk.Treeview(root, columns=("Código", "Nome", "Preço", "Quantidade"), show="headings")
tree.heading("Código", text="Código")
tree.heading("Nome", text="Nome")
tree.heading("Preço", text="Preço")
tree.heading("Quantidade", text="Quantidade")
tree.pack(expand=True, fill="both", pady=10)

atualizar_estoque()

root.mainloop()

# Fecha conexão ao sair
conn.close()
