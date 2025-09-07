import tkinter as tk

def click(boton):
    if boton == "=":
        try:
            resultado = str(eval(entrada.get()))
            entrada.delete(0, tk.END)
            entrada.insert(tk.END, resultado)
        except:
            entrada.delete(0, tk.END)
            entrada.insert(tk.END, "Error")
    elif boton == "C":
        entrada.delete(0, tk.END)
    else:
        entrada.insert(tk.END, boton)

# Ventana principal
ventana = tk.Tk()
ventana.title("Calculadora")

entrada = tk.Entry(ventana, width=20, font=("Arial", 18), borderwidth=5, relief="ridge", justify="right")
entrada.grid(row=0, column=0, columnspan=4)

# Botones
botones = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "0", ".", "=", "+"
]

fila, col = 1, 0
for boton in botones:
    b = tk.Button(ventana, text=boton, width=5, height=2, font=("Arial", 14),
                  command=lambda x=boton: click(x))
    b.grid(row=fila, column=col, padx=5, pady=5)
    col += 1
    if col > 3:
        col = 0
        fila += 1

# Botón de limpiar
b_clear = tk.Button(ventana, text="C", width=22, height=2, font=("Arial", 14),
                    command=lambda: click("C"))
b_clear.grid(row=fila, column=0, columnspan=4, padx=5, pady=5)

ventana.mainloop()
