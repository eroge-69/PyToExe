
import tkinter as tk
from tkinter import messagebox
import os

ARQUIVO_DADOS = "registros.txt"

def salvar():
    cnpj = entry_cnpj.get()
    nome = entry_nome.get()
    acesso = entry_acesso.get()
    campanha = entry_campanha.get()
    motivo = entry_motivo.get()

    if not cnpj or not nome:
        messagebox.showwarning("Atenção", "CNPJ e Nome do Cliente são obrigatórios.")
        return

    with open(ARQUIVO_DADOS, "a", encoding="utf-8") as f:
        f.write(f"CNPJ: {cnpj} | Cliente: {nome} | Acesso: {acesso} | Campanha: {campanha} | Motivo: {motivo}\n")

    messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
    limpar_campos()

def limpar_campos():
    entry_cnpj.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_acesso.delete(0, tk.END)
    entry_campanha.delete(0, tk.END)
    entry_motivo.delete(0, tk.END)

def ver_registros():
    if not os.path.exists(ARQUIVO_DADOS):
        messagebox.showinfo("Aviso", "Nenhum registro encontrado.")
        return

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        conteudo = f.read()

    janela_registros = tk.Toplevel(root)
    janela_registros.title("Registros Salvos")
    text = tk.Text(janela_registros, wrap="word")
    text.insert("1.0", conteudo)
    text.pack(expand=True, fill="both")

def excluir_registros():
    if os.path.exists(ARQUIVO_DADOS):
        os.remove(ARQUIVO_DADOS)
        messagebox.showinfo("Sucesso", "Todos os registros foram apagados.")
    else:
        messagebox.showinfo("Aviso", "Nenhum arquivo para excluir.")

root = tk.Tk()
root.title("Registro de Chamadas")
root.geometry("400x300")

tk.Label(root, text="CNPJ:").pack()
entry_cnpj = tk.Entry(root)
entry_cnpj.pack()

tk.Label(root, text="Nome do Cliente:").pack()
entry_nome = tk.Entry(root)
entry_nome.pack()

tk.Label(root, text="Acesso Remoto:").pack()
entry_acesso = tk.Entry(root)
entry_acesso.pack()

tk.Label(root, text="Campanha:").pack()
entry_campanha = tk.Entry(root)
entry_campanha.pack()

tk.Label(root, text="Motivo da Ligação:").pack()
entry_motivo = tk.Entry(root)
entry_motivo.pack()

tk.Button(root, text="Salvar", command=salvar).pack(pady=5)
tk.Button(root, text="Ver Registros", command=ver_registros).pack(pady=5)
tk.Button(root, text="Excluir Todos", command=excluir_registros).pack(pady=5)

root.mainloop()
