import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime, timedelta
import os

ARQUIVO_DADOS = "registros.csv"

# Função para salvar os dados
def salvar_dados():
    empresa = entry_empresa.get().strip()
    servico = entry_servico.get().strip()
    quantidade = entry_quantidade.get().strip()
    data = entry_data.get().strip()
    hora = entry_hora.get().strip()

    if not all([empresa, servico, quantidade, data, hora]):
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return

    with open(ARQUIVO_DADOS, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([empresa, servico, quantidade, data, hora])

    messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
    entry_empresa.delete(0, tk.END)
    entry_servico.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    now = datetime.now()
    entry_data.delete(0, tk.END)
    entry_data.insert(0, now.strftime("%Y-%m-%d"))
    entry_hora.delete(0, tk.END)
    entry_hora.insert(0, now.strftime("%H:%M:%S"))

# Função para mostrar o relatório
def mostrar_relatorio():
    if not os.path.exists(ARQUIVO_DADOS):
        messagebox.showinfo("Informação", "Nenhum dado foi salvo ainda.")
        return

    relatorio_window = tk.Toplevel(root)
    relatorio_window.title("Relatório de Serviços")

    # Criação de menu suspenso para selecionar o filtro de visualização
    filtro_label = tk.Label(relatorio_window, text="Filtrar por:")
    filtro_label.grid(row=0, column=0, padx=10, pady=10)

    filtro_var = tk.StringVar()
    filtro_menu = ttk.Combobox(relatorio_window, textvariable=filtro_var, values=["Dia", "Semana", "Mês"], state="readonly", width=15)
    filtro_menu.grid(row=0, column=1, padx=10, pady=10)
    filtro_menu.set("Dia")

    # Função para aplicar o filtro e mostrar os dados
    def aplicar_filtro():
        periodo = filtro_var.get()
        tree.delete(*tree.get_children())  # Limpar a árvore antes de adicionar os novos dados

        with open(ARQUIVO_DADOS, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            dados = list(reader)
        
        if periodo == "Dia":
            dados = [row for row in dados if row[3] == datetime.now().strftime("%Y-%m-%d")]
        elif periodo == "Semana":
            data_inicio = datetime.now() - timedelta(days=datetime.now().weekday())  # Início da semana
            data_fim = data_inicio + timedelta(days=7)  # Fim da semana
            dados = [row for row in dados if data_inicio <= datetime.strptime(row[3], "%Y-%m-%d") <= data_fim]
        elif periodo == "Mês":
            mes_atual = datetime.now().month
            dados = [row for row in dados if datetime.strptime(row[3], "%Y-%m-%d").month == mes_atual]

        for row in dados:
            tree.insert("", tk.END, values=row)

    # Tabela de relatório
    tree = ttk.Treeview(relatorio_window, columns=("Empresa", "Serviço", "Quantidade", "Data", "Hora"), show="headings")
    for col in ("Empresa", "Serviço", "Quantidade", "Data", "Hora"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    btn_aplicar_filtro = tk.Button(relatorio_window, text="Aplicar Filtro", command=aplicar_filtro, bg="blue", fg="white")
    btn_aplicar_filtro.grid(row=2, column=0, columnspan=2, pady=10)

# Interface Gráfica
root = tk.Tk()
root.title("Cadastro de Serviços")

# Ajuste da aparência
root.configure(bg="#f0f0f0")
root.geometry("500x400")
root.resizable(False, False)

# Labels e campos de entrada
tk.Label(root, text="Empresa:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", padx=10, pady=5)
entry_empresa = tk.Entry(root, width=40)
entry_empresa.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Serviço:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=10, pady=5)
entry_servico = tk.Entry(root, width=40)
entry_servico.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Quantidade:", bg="#f0f0f0").grid(row=2, column=0, sticky="e", padx=10, pady=5)
entry_quantidade = tk.Entry(root, width=40)
entry_quantidade.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Data (AAAA-MM-DD):", bg="#f0f0f0").grid(row=3, column=0, sticky="e", padx=10, pady=5)
entry_data = tk.Entry(root, width=40)
entry_data.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Hora (HH:MM:SS):", bg="#f0f0f0").grid(row=4, column=0, sticky="e", padx=10, pady=5)
entry_hora = tk.Entry(root, width=40)
entry_hora.grid(row=4, column=1, padx=10, pady=5)

# Preencher data e hora atuais
now = datetime.now()
entry_data.insert(0, now.strftime("%Y-%m-%d"))
entry_hora.insert(0, now.strftime("%H:%M:%S"))

# Botões
btn_salvar = tk.Button(root, text="Salvar Cadastro", command=salvar_dados, bg="green", fg="white")
btn_salvar.grid(row=5, column=0, columnspan=2, pady=15)

btn_relatorio = tk.Button(root, text="Mostrar Relatório", command=mostrar_relatorio, bg="blue", fg="white")
btn_relatorio.grid(row=6, column=0, columnspan=2, pady=5)

root.mainloop()
