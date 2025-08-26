import tkinter as tk

def calcular():
    try:
        resultado = eval(entrada.get())
        label_resultado.config(text=f"Resultado: {resultado}")
    except:
        label_resultado.config(text="Erro!")

# Janela principal
root = tk.Tk()
root.title("Calculadora do Davi")

entrada = tk.Entry(root, width=20)
entrada.pack(padx=10, pady=10)

botao = tk.Button(root, text="Calcular", command=calcular)
botao.pack(padx=10, pady=10)

label_resultado = tk.Label(root, text="Resultado: ")
label_resultado.pack(padx=10, pady=10)

root.mainloop()