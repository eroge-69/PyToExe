import tkinter as tk
from tkinter import messagebox
import csv
import os

# Arquivo do banco
ARQUIVO_BANCO = "banco.csv"

# Criar banco se não existir
if not os.path.exists(ARQUIVO_BANCO):
    with open(ARQUIVO_BANCO, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Código", "Nome", "Quantidade", "Preço"])

# Função para gerar novo código
def gerar_codigo():
    with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
        leitor = list(csv.reader(f))
        return len(leitor)

# Função para cadastrar produto
def cadastrar_produto(nome, qtd, preco):
    if not nome or not qtd or not preco:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    codigo = gerar_codigo()
    with open(ARQUIVO_BANCO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([codigo, nome, qtd, preco])
    messagebox.showinfo("Sucesso", f"Produto {nome} cadastrado com código {codigo}!")

# Tela de Cadastro
def tela_cadastro():
    cadastro = tk.Toplevel(root)
    cadastro.title("Cadastrar Produto")
    cadastro.geometry("300x250")

    tk.Label(cadastro, text="Nome:").pack()
    nome_entry = tk.Entry(cadastro)
    nome_entry.pack()

    tk.Label(cadastro, text="Quantidade:").pack()
    qtd_entry = tk.Entry(cadastro)
    qtd_entry.pack()

    tk.Label(cadastro, text="Preço R$:").pack()
    preco_entry = tk.Entry(cadastro)
    preco_entry.pack()

    tk.Button(cadastro, text="Incluir", command=lambda: cadastrar_produto(
        nome_entry.get(), qtd_entry.get(), preco_entry.get()
    )).pack(pady=10)

# Tela de Consulta
def tela_consulta():
    consulta = tk.Toplevel(root)
    consulta.title("Consultar Produto")
    consulta.geometry("400x300")

    tk.Label(consulta, text="Consultar por Nome ou Código:").pack()
    pesquisa_entry = tk.Entry(consulta)
    pesquisa_entry.pack()

    resultado = tk.Listbox(consulta, width=50)
    resultado.pack(pady=10)

    def buscar():
        pesquisa = pesquisa_entry.get().lower()
        resultado.delete(0, tk.END)
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            for linha in leitor:
                if pesquisa in linha["Nome"].lower() or pesquisa == linha["Código"]:
                    resultado.insert(tk.END, f"Cód {linha['Código']} - {linha['Nome']} - {linha['Quantidade']} un - R$ {linha['Preço']}")

    tk.Button(consulta, text="Buscar", command=buscar).pack()

# Tela Inicial
root = tk.Tk()
root.title("Lojas Xavier - Cadastro de Mercadorias")
root.geometry("300x200")

tk.Label(root, text="Programa Cadastro de Mercadorias", font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="Cadastrar Produtos", command=tela_cadastro).pack(pady=5)
tk.Button(root, text="Consultar Produtos", command=tela_consulta).pack(pady=5)

root.mainloop()
