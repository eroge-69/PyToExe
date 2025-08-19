import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
import os, sys

# ========================= BASE DE DATOS =========================

DB_NAME = "ordenes.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Tabla frecuencias con nombre de cliente y frecuencias preventa y entrega
c.execute("""
CREATE TABLE IF NOT EXISTS frecuencias (
    numero_cliente TEXT PRIMARY KEY,
    nombre_cliente TEXT,
    direccion TEXT,
    ruta TEXT,
    frecuencia_preventa TEXT,
    frecuencia_entrega TEXT,
    supervisor TEXT
)
""")

# Tabla órdenes de servicio
c.execute("""
CREATE TABLE IF NOT EXISTS ordenes (
    numero_orden TEXT PRIMARY KEY,
    numero_cliente TEXT,
    nombre_cliente TEXT,
    direccion TEXT,
    ruta TEXT,
    frecuencia_preventa TEXT,
    frecuencia_entrega TEXT,
    supervisor TEXT,
    motivo TEXT,
    telefono TEXT,
    quien_reporta TEXT,
    comentarios TEXT
)
""")

conn.commit()

# ========================= FUNCIONES =========================

def cargar_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if archivo:
        try:
            df = pd.read_excel(archivo)
            # Se espera que el Excel tenga las columnas: ruta, numero_cliente, nombre_cliente, direccion, frecuencia_preventa, frecuencia_entrega, supervisor
            for _, row in df.iterrows():
                c.execute("""
                    INSERT OR REPLACE INTO frecuencias (numero_cliente, nombre_cliente, direccion, ruta, frecuencia_preventa, frecuencia_entrega, supervisor)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row["numero_cliente"]),
                    row.get("nombre_cliente", ""),
                    row.get("direccion", ""),
                    row.get("ruta", ""),
                    row.get("frecuencia_preventa", ""),
                    row.get("frecuencia_entrega", ""),
                    row.get("supervisor", "")
                ))
            conn.commit()
            messagebox.showinfo("Éxito", "Archivo cargado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")


def buscar_cliente(numero_cliente, entry_nombre, entry_direccion, entry_ruta, entry_preventa, entry_entrega, entry_supervisor):
    c.execute("SELECT nombre_cliente, direccion, ruta, frecuencia_preventa, frecuencia_entrega, supervisor FROM frecuencias WHERE numero_cliente=?", (numero_cliente,))
    row = c.fetchone()
    if row:
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, row[0])
        entry_direccion.delete(0, tk.END)
        entry_direccion.insert(0, row[1])
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, row[2])
        entry_preventa.delete(0, tk.END)
        entry_preventa.insert(0, row[3])
        entry_entrega.delete(0, tk.END)
        entry_entrega.insert(0, row[4])
        entry_supervisor.delete(0, tk.END)
        entry_supervisor.insert(0, row[5])


def guardar_orden(datos):
    try:
        c.execute("""
            INSERT INTO ordenes (numero_orden, numero_cliente, nombre_cliente, direccion, ruta, frecuencia_preventa, frecuencia_entrega, supervisor, motivo, telefono, quien_reporta, comentarios)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        conn.commit()
        messagebox.showinfo("Éxito", "Orden guardada correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la orden: {e}")


# ========================= INTERFAZ =========================

class App(tb.Window):
    def __init__(self):
        super().__init__(title="Gestor de Órdenes de Servicio", themename="cosmo")
        self.geometry("1000x600")

        self.sidebar = tk.Frame(self, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")

        tk.Button(self.sidebar, text="Alta", command=self.mostrar_alta, bg="#34495e", fg="white").pack(fill="x", pady=5)
        tk.Button(self.sidebar, text="Consulta", command=self.mostrar_consulta, bg="#34495e", fg="white").pack(fill="x", pady=5)
        tk.Button(self.sidebar, text="Configuración", command=self.mostrar_configuracion, bg="#34495e", fg="white").pack(fill="x", pady=5)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

    def limpiar_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_configuracion(self):
        self.limpiar_main()
        tk.Label(self.main_frame, text="Configuración", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.main_frame, text="Cargar Excel", command=cargar_excel).pack(pady=10)

    def mostrar_alta(self):
        self.limpiar_main()
        tk.Label(self.main_frame, text="Alta de Orden", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        labels = [
            "Número de Orden", "Número de Cliente", "Nombre Cliente", "Dirección", "Ruta",
            "Frecuencia Preventa", "Frecuencia Entrega", "Supervisor", "Motivo", "Teléfono", "Quién Reporta", "Comentarios"
        ]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(self.main_frame, text=label).grid(row=i+1, column=0, sticky="e", padx=5, pady=5)
            e = tk.Entry(self.main_frame, width=50)
            e.grid(row=i+1, column=1, padx=5, pady=5)
            entries[label] = e

        # Búsqueda automática al escribir número de cliente
        entries["Número de Cliente"].bind("<FocusOut>", lambda e: buscar_cliente(
            entries["Número de Cliente"].get(),
            entries["Nombre Cliente"],
            entries["Dirección"],
            entries["Ruta"],
            entries["Frecuencia Preventa"],
            entries["Frecuencia Entrega"],
            entries["Supervisor"]
        ))

        tk.Button(self.main_frame, text="Guardar", command=lambda: guardar_orden(
            (
                entries["Número de Orden"].get(),
                entries["Número de Cliente"].get(),
                entries["Nombre Cliente"].get(),
                entries["Dirección"].get(),
                entries["Ruta"].get(),
                entries["Frecuencia Preventa"].get(),
                entries["Frecuencia Entrega"].get(),
                entries["Supervisor"].get(),
                entries["Motivo"].get(),
                entries["Teléfono"].get(),
                entries["Quién Reporta"].get(),
                entries["Comentarios"].get()
            )
        )).grid(row=len(labels)+2, column=0, columnspan=2, pady=20)

    def mostrar_consulta(self):
        self.limpiar_main()
        tk.Label(self.main_frame, text="Consulta de Órdenes", font=("Arial", 16)).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
