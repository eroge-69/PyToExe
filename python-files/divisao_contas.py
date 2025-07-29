
import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        agua = float(entry_agua.get())
        luz = float(entry_luz.get())

        total = agua + luz
        por_pessoa = total / 2
        restante = 500 - por_pessoa

        resultado_total.config(text=f"Total das contas: R$ {total:.2f}")
        resultado_pessoa.config(text=f"Para cada pessoa: R$ {por_pessoa:.2f}")
        resultado_final.config(text=f"R$500,00 - metade: R$ {restante:.2f}")

    except ValueError:
        messagebox.showerror("Erro", "Digite apenas números válidos.")

# Janela principal
janela = tk.Tk()
janela.title("Divisão de Contas")

# Layout
tk.Label(janela, text="Valor da conta de água (R$):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_agua = tk.Entry(janela)
entry_agua.grid(row=0, column=1, padx=10, pady=5)

tk.Label(janela, text="Valor da conta de luz (R$):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_luz = tk.Entry(janela)
entry_luz.grid(row=1, column=1, padx=10, pady=5)

btn_calcular = tk.Button(janela, text="Calcular", command=calcular)
btn_calcular.grid(row=2, column=0, columnspan=2, pady=10)

resultado_total = tk.Label(janela, text="")
resultado_total.grid(row=3, column=0, columnspan=2)

resultado_pessoa = tk.Label(janela, text="")
resultado_pessoa.grid(row=4, column=0, columnspan=2)

resultado_final = tk.Label(janela, text="")
resultado_final.grid(row=5, column=0, columnspan=2)

# Iniciar a interface
janela.mainloop()
