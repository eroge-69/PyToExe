import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

# Configura a aparência da interface (tema escuro, azul, etc.)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Dados da tabela
dados_tabela = [
    {'Cor': 'Verde', 'ID (pol)': 0.03, 'ID (cm)': 0.0762},
    {'Cor': 'Laranja', 'ID (pol)': 0.02, 'ID (cm)': 0.0508},
    {'Cor': 'Azul', 'ID (pol)': 0.013, 'ID (cm)': 0.03302},
    {'Cor': 'Preto', 'ID (pol)': 0.01, 'ID (cm)': 0.0254},
    {'Cor': 'Vermelho', 'ID (pol)': 0.005, 'ID (cm)': 0.0127},
    {'Cor': 'Mostarda', 'ID (pol)': 0.003, 'ID (cm)': 0.00762}
]

def calcular_e_mostrar_resultados():
    """Função para realizar os cálculos e exibir os resultados em uma nova janela."""
    valor_entrada_str = entrada_valor.get()
    if not valor_entrada_str:
        messagebox.showerror("Erro de entrada", "O campo de Volume (uL) não pode estar vazio.")
        return
    
    try:
        volume_ul = float(valor_entrada_str)

        janela_resultados = ctk.CTkToplevel(janela)
        janela_resultados.title("Resultados do Cálculo")
        janela_resultados.geometry("300x250")

        titulo_resultados = ctk.CTkLabel(janela_resultados, text="Resultados (cm)", font=ctk.CTkFont(size=16, weight="bold"))
        titulo_resultados.pack(pady=10)

        for linha in dados_tabela:
            id_cm = linha['ID (cm)']
            resultado = (volume_ul / 1000) / (3.14 * (id_cm / 2)**2)
            
            texto_resultado = f"Cor {linha['Cor']}: {resultado:.2f}"
            
            label_resultado = ctk.CTkLabel(janela_resultados, text=texto_resultado)
            label_resultado.pack(anchor="w", padx=10, pady=2)
            
    except ValueError:
        messagebox.showerror("Erro de entrada", "Por favor, insira um valor numérico válido.")

# --- Interface Gráfica ---
janela = ctk.CTk()
janela.title("Cálculo de Loops")
janela.geometry("400x400")

titulo = ctk.CTkLabel(janela, text="Cálculo de Loops", font=ctk.CTkFont(size=20, weight="bold"))
titulo.pack(pady=10)

tabela_frame = ctk.CTkFrame(janela)
tabela_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Tabela (ainda usa ttk.Treeview)
tabela_cores = ttk.Treeview(tabela_frame, columns=("Cor", "ID (pol)", "ID (cm)"), show='headings')
tabela_cores.heading("Cor", text="Cor")
tabela_cores.heading("ID (pol)", text="ID (pol)")
tabela_cores.heading("ID (cm)", text="ID (cm)")
tabela_cores.column("Cor", width=100, anchor=tk.CENTER)
tabela_cores.column("ID (pol)", width=100, anchor=tk.CENTER)
tabela_cores.column("ID (cm)", width=100, anchor=tk.CENTER)

for linha in dados_tabela:
    tabela_cores.insert("", "end", values=(linha['Cor'], linha['ID (pol)'], linha['ID (cm)']))
tabela_cores.pack(pady=10, padx=10, fill="both", expand=True)

label_entrada = ctk.CTkLabel(janela, text="Volume (uL):")
label_entrada.pack(pady=(0, 5))

entrada_valor = ctk.CTkEntry(janela, placeholder_text="Digite o volume aqui")
entrada_valor.pack(pady=5)

botao_calcular = ctk.CTkButton(janela, text="Calcular", command=calcular_e_mostrar_resultados)
botao_calcular.pack(pady=10)

janela.mainloop()