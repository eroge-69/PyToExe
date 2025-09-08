import os
import csv
import tkinter as tk
from tkinter import ttk

# Caminho da planilha (convertida para .csv)
CAMINHO_PLANILHA = os.path.join("dados", "planilha.csv")

# Carrega os dados da planilha
def carregar_dados():
    dados = []
    with open(CAMINHO_PLANILHA, newline='', encoding='utf-8') as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for linha in leitor:
            dados.append(linha)
    return dados

# Atualiza os campos com base no item selecionado
def atualizar_info(event):
    nome = combo.get()
    for item in dados:
        if item["Nome"] == nome:
            info_var.set(f"Data Nasc: {item['DataNascimento']} | RA: {item['RA']} | Sala: {item['Sala']}")
            break

# Carrega os dados
dados = carregar_dados()
nomes = [item["Nome"] for item in dados]

# Cria��o da janela
janela = tk.Tk()
janela.title("Localizar Crian�a")

# Lista suspensa (ComboBox)
combo = ttk.Combobox(janela, values=nomes)
combo.bind("<<ComboboxSelected>>", atualizar_info)
combo.pack(pady=10)

# Label para mostrar dados
info_var = tk.StringVar()
info_label = tk.Label(janela, textvariable=info_var)
info_label.pack(pady=10)

# Executa a janela
janela.mainloop()
