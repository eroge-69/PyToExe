import tkinter as tk
from tkinter import messagebox

# Diccionario de productos con su stock
stock_tienda = {
    "spotify": {"cantidad": 116, "precio": 0.78},
    "netflix": {"cantidad": 564, "precio": 0.57},
    "ytpremium": {"cantidad": 54, "precio": 0.83},
    "dazn": {"cantidad": 1001, "precio": 0.35},
    "nordvpn": {"cantidad": 0, "precio": 1.07},
    "hbo": {"cantidad": 236, "precio": 0.44},
    "disney+": {"cantidad": 154, "precio": 0.31},
    "amazon prime": {"cantidad": 0, "precio": 1.18},
    "canva": {"cantidad": 14, "precio": 0.89},
    "pornhub": {"cantidad": 56, "precio": 0.99},
    "onlyfans": {"cantidad": 0, "precio": 1.04},
    "chatgpt": {"cantidad": 7, "precio": 1.17},
    "fivem": {"cantidad": 226, "precio": 0.35},
    "expressvpn": {"cantidad": 184, "precio": 0.49},
    "paramount+": {"cantidad": 10, "precio": 0.34},
    "duolingo": {"cantidad": 482, "precio": 0.28},
    "ufc fight pass": {"cantidad": 0, "precio": 0.39},
    "filmora": {"cantidad": 296, "precio": 0.30},
    "nba league pass": {"cantidad": 123, "precio": 0.34},
    "surfshark": {"cantidad": 8, "precio": 0.77},
    "stake": {"cantidad": 0, "precio": 1.99},
    "capcut": {"cantidad": 9, "precio": 0.76},
    "crunchyroll": {"cantidad": 1015, "precio": 0.35},
    "steam": {"cantidad": 623, "precio": 0.34},
}

# Función para consultar el stock
def consultar_stock():
    producto = entrada_producto.get().lower()
    if producto in stock_tienda:
        cantidad = stock_tienda[producto]["cantidad"]
        precio = stock_tienda[producto]["precio"]
        resultado.set(f"Producto: {producto}\nCantidad en stock: {cantidad}\nPrecio: {precio}€")
    else:
        resultado.set("")
        messagebox.showwarning("Producto no encontrado", f"'{producto}' no está registrado en el inventario.")

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Consulta de Stock")
ventana.geometry("400x300")
ventana.resizable(False, False)

# Etiqueta e entrada
tk.Label(ventana, text="Introduce el nombre del producto:", font=("Arial", 12)).pack(pady=10)
entrada_producto = tk.Entry(ventana, font=("Arial", 12), width=30)
entrada_producto.pack()

# Botón para consultar
tk.Button(ventana, text="Consultar Stock", font=("Arial", 12), command=consultar_stock).pack(pady=10)

# Resultado
resultado = tk.StringVar()
tk.Label(ventana, textvariable=resultado, font=("Arial", 12), justify="left").pack(pady=10)

# Ejecutar ventana
ventana.mainloop()
