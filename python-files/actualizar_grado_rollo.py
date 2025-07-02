
import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc

# Cadena de conexión (idéntica a la del ejecutable original)
CONNECTION_STRING = (
    "Driver={{SQL Server}};"
    "Server=10.160.48.8;"
    "Database=AXSTD;"
    "UID=yeebran.aguirre;"
    "PWD=Newuser03;"
)

# Función para actualizar el grado en la base de datos
def actualizar_grado():
    rollo = entry_rollo.get().strip()
    nuevo_grado = combo_grado.get()

    if not rollo:
        messagebox.showerror("Error", "Debes ingresar el número de rollo.")
        return
    if not nuevo_grado:
        messagebox.showerror("Error", "Debes seleccionar un grado.")
        return

    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()

        sql = """
        UPDATE TB_T_PRODUCT_ROLL
        SET INSP_GRADE = ?
        WHERE PRODUCT_ROLL_NO = ?
        """
        cursor.execute(sql, (nuevo_grado, rollo))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", f"El grado del rollo {rollo} fue actualizado a '{nuevo_grado}'.")
        entry_rollo.delete(0, tk.END)
        combo_grado.set("")

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo actualizar el grado.\n{e}")

# Crear ventana
root = tk.Tk()
root.title("Actualizar Grado de Rollo")
root.geometry("400x200")

tk.Label(root, text="Número de Rollo:").pack(pady=5)
entry_rollo = tk.Entry(root, width=40)
entry_rollo.pack()

tk.Label(root, text="Nuevo Grado:").pack(pady=5)
combo_grado = ttk.Combobox(root, values=["A", "B", "B2", "C"], state="readonly")
combo_grado.pack()

tk.Button(root, text="Actualizar Grado", command=actualizar_grado).pack(pady=20)

root.mainloop()
