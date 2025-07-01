import os
from tkinter import Tk, Label, Entry, Button, messagebox

productos = [
    "sorgo", "aflechillo de trigo", "preparada", "maiz entero", "maiz quebrado", "baguetti", "bague",
    "avena", "alfalfa", "procaballo nucleo", "farelón", "birbo adulto", "birbo filhote", "bravo", "mandela"
]

entradas_stock = {}
entradas_ventas = {}

def calcular_stock():
    resultado = ""
    for producto in productos:
        try:
            stock = int(entradas_stock[producto].get())
            vendido = int(entradas_ventas[producto].get())
            restante = stock - vendido
            resultado += f"{producto}: {restante} unidades restantes\n"
        except ValueError:
            resultado += f"{producto}: entrada inválida\n"
    messagebox.showinfo("Stock restante", resultado)

ventana = Tk()
ventana.title("Gestión de Stock de Productos")
ventana.geometry("600x700")

Label(ventana, text="Producto", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=5, pady=5)
Label(ventana, text="Cantidad en stock", font=('Arial', 12, 'bold')).grid(row=0, column=1, padx=5, pady=5)
Label(ventana, text="Cantidad vendida", font=('Arial', 12, 'bold')).grid(row=0, column=2, padx=5, pady=5)

for idx, producto in enumerate(productos, start=1):
    Label(ventana, text=producto).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
    entrada_stock = Entry(ventana)
    entrada_stock.grid(row=idx, column=1, padx=5, pady=2)
    entrada_vendido = Entry(ventana)
    entrada_vendido.grid(row=idx, column=2, padx=5, pady=2)
    entradas_stock[producto] = entrada_stock
    entradas_ventas[producto] = entrada_vendido

boton = Button(ventana, text="Calcular stock restante", command=calcular_stock, bg="lightblue", font=('Arial', 12))
boton.grid(row=len(productos)+1, column=0, columnspan=3, pady=20)

ventana.mainloop()
