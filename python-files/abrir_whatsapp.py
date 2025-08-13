import tkinter as tk
from tkinter import messagebox
import webbrowser

def abrir_whatsapp():
    numero = entry_numero.get().strip()
    numero = ''.join(filter(str.isdigit, numero))  # Remove caracteres não numéricos

    if len(numero) < 10:
        messagebox.showerror("Erro", "Digite um número válido com DDD.")
        return

    link = f"https://wa.me/{numero}"
    webbrowser.open(link)

# Criar janela
janela = tk.Tk()
janela.title("Abrir WhatsApp")
janela.geometry("300x150")
janela.resizable(False, False)

# Label
label = tk.Label(janela, text="Digite o número com DDD:")
label.pack(pady=10)

# Campo de entrada
entry_numero = tk.Entry(janela, width=25, font=("Arial", 12))
entry_numero.pack()

# Botão
btn_abrir = tk.Button(janela, text="Abrir no WhatsApp", command=abrir_whatsapp, bg="green", fg="white")
btn_abrir.pack(pady=20)

# Iniciar loop
janela.mainloop()
