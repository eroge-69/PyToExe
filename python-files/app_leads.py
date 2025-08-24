import tkinter as tk
from tkinter import messagebox

def buscar_leads():
    # Aqui você coloca seu código real de captura de leads
    # Exemplo fictício de leads
    resultado = "Lead 1: João, 99999-9999\nLead 2: Maria, 88888-8888\nLead 3: Carlos, 77777-7777"
    messagebox.showinfo("Leads encontrados", resultado)

# Criando a janela principal
janela = tk.Tk()
janela.title("App de Leads")
janela.geometry("400x250")

# Label de instrução
label = tk.Label(janela, text="Clique no botão para buscar leads", font=("Arial", 12))
label.pack(pady=20)

# Botão para buscar leads
botao = tk.Button(janela, text="Buscar Leads", font=("Arial", 12), width=20, command=buscar_leads)
botao.pack(pady=30)

# Rodando a interface
janela.mainloop()
