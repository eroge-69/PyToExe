import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        contado = float(entry_contado.get())
        total_cuotas = float(entry_cuotas.get())
        n_cuotas = int(entry_num_cuotas.get())
        inflacion_mensual = float(entry_inflacion.get()) / 100

        valor_cuota = total_cuotas / n_cuotas
        valor_presente = 0
        for i in range(1, n_cuotas + 1):
            valor_presente += valor_cuota / ((1 + inflacion_mensual) ** i)

        if valor_presente < contado:
            resultado = "Conviene pagar en CUOTAS."
        elif valor_presente > contado:
            resultado = "Conviene pagar al CONTADO."
        else:
            resultado = "Ambas opciones son equivalentes."

        messagebox.showinfo("Resultado", 
            f"Precio contado: {contado:.2f}\n"
            f"Valor presente de las cuotas: {valor_presente:.2f}\n\n"
            f"👉 {resultado}"
        )
    except Exception:
        messagebox.showerror("Error", "Por favor ingrese valores válidos.")

# Crear ventana
root = tk.Tk()
root.title("Comparador de Precios")
root.geometry("400x300")

tk.Label(root, text="Precio contado:").pack(pady=5)
entry_contado = tk.Entry(root)
entry_contado.pack()

tk.Label(root, text="Precio total en cuotas:").pack(pady=5)
entry_cuotas = tk.Entry(root)
entry_cuotas.pack()

tk.Label(root, text="Cantidad de cuotas:").pack(pady=5)
entry_num_cuotas = tk.Entry(root)
entry_num_cuotas.pack()

tk.Label(root, text="Inflación mensual estimada (%):").pack(pady=5)
entry_inflacion = tk.Entry(root)
entry_inflacion.pack()

tk.Button(root, text="Calcular", command=calcular).pack(pady=20)

root.mainloop()
