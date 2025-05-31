import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        monto = float(entry_monto.get())
        precio = float(entry_precio.get())
        lectura = float(entry_lectura.get())

        galones = monto / precio
        nueva_lectura = lectura + galones

        resultado.set(f"Galones agregados: {galones:.3f}\nNueva lectura: {nueva_lectura:.3f}")
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresá solo números válidos.")

app = tk.Tk()
app.title("Calculadora de Giro - Bomba de Gasolina")
app.geometry("350x250")
app.resizable(False, False)

tk.Label(app, text="Monto girado ($):").pack(pady=5)
entry_monto = tk.Entry(app)
entry_monto.pack()

tk.Label(app, text="Precio por galón ($):").pack(pady=5)
entry_precio = tk.Entry(app)
entry_precio.pack()

tk.Label(app, text="Lectura anterior (galones):").pack(pady=5)
entry_lectura = tk.Entry(app)
entry_lectura.pack()

tk.Button(app, text="Calcular", command=calcular).pack(pady=10)

resultado = tk.StringVar()
tk.Label(app, textvariable=resultado, fg="blue").pack(pady=10)

app.mainloop()
