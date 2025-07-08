import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(title="Seleccioná el archivo Excel", filetypes=[("Excel files", "*.xlsx")])
    if not archivo:
        return

    try:
        df = pd.read_excel(archivo, skiprows=7)
        df = df.rename(columns={
            'Codigo  ': 'Codigo',
            'Descripción           ': 'Descripcion',
            'Stock           ': 'Stock'
        })

        df = df[['Codigo', 'Descripcion', 'Stock']]
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce')
        df = df.dropna(subset=['Codigo', 'Stock'])

        codigos = simpledialog.askstring("Códigos a controlar", "Ingresá los códigos separados por coma (,):\nEj: Nmsl6, Tpe4-3, Blow2")
        if not codigos:
            return

        codigos_lista = [c.strip() for c in codigos.split(",")]

        umbral = simpledialog.askinteger("Umbral", "¿Cuál es el mínimo de stock que querés controlar?\nEj: 2", minvalue=0)
        if umbral is None:
            return

        alertas = df[df['Codigo'].isin(codigos_lista) & (df['Stock'] < umbral)]

        if alertas.empty:
            messagebox.showinfo("Todo bien", "✅ Todos los productos seleccionados tienen stock suficiente.")
        else:
            resultado = "⚠️ Productos con bajo stock:\n\n"
            for _, row in alertas.iterrows():
                resultado += f"{row['Codigo']}: {row['Descripcion']} (Stock: {int(row['Stock'])})\n"

            messagebox.showwarning("Alerta de stock", resultado)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Alerta de Stock")
ventana.geometry("300x150")

tk.Label(ventana, text="Control de Stock Aiken", font=("Helvetica", 14)).pack(pady=10)
tk.Button(ventana, text="Seleccionar archivo Excel", command=seleccionar_archivo).pack(pady=10)
tk.Label(ventana, text="v1.0").pack(side="bottom")

ventana.mainloop()
