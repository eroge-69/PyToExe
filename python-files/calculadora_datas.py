
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def calcular_data():
    data_inicial = entrada_data.get()
    dias_str = entrada_dias.get()

    try:
        data_obj = datetime.strptime(data_inicial, "%d/%m/%Y")
        dias = int(dias_str)
        data_final = data_obj + timedelta(days=dias)
        resultado_label.config(text=f"Data final: {data_final.strftime('%d/%m/%Y')}")
    except Exception as e:
        messagebox.showerror("Erro", f"Entrada inválida.\nDetalhes: {e}")

janela = tk.Tk()
janela.title("Calculadora de Datas")
janela.geometry("300x180")

tk.Label(janela, text="Data inicial (dd/mm/yyyy):").pack(pady=5)
entrada_data = tk.Entry(janela)
entrada_data.pack()

tk.Label(janela, text="Quantidade de dias:").pack(pady=5)
entrada_dias = tk.Entry(janela)
entrada_dias.pack()

tk.Button(janela, text="Calcular data final", command=calcular_data).pack(pady=10)

resultado_label = tk.Label(janela, text="")
resultado_label.pack()

janela.mainloop()
