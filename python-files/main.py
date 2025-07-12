import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AppCitas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Citas Telefónicas")
        self.root.geometry("800x600")
        
        # Conexión a la base de datos
        self.conn = sqlite3.connect('citas.db')
        self.crear_tabla()
        
        # Crear pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")
        
        # Pestaña de programación
        self.frame_programar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_programar, text="Programar Cita")
        self.crear_formulario_programar()
        
        # Pestaña de visualización
        self.frame_visualizar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_visualizar, text="Ver Citas")
        self.crear_interfaz_visualizar()
        
        # Pestaña de búsqueda
        self.frame_buscar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_buscar, text="Buscar Citas")
        self.crear_interfaz_busqueda()
    
    def crear_tabla(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS citas
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         nombre TEXT NOT NULL,
                         telefono TEXT NOT NULL,
                         servicio TEXT NOT NULL,
                         fecha TEXT NOT NULL,
                         confirmada INTEGER DEFAULT 0)''')
        self.conn.commit()
    
    def crear_formulario_programar(self):
        # Etiquetas y campos de entrada
        ttk.Label(self.frame_programar, text="Nombre:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_nombre = ttk.Entry(self.frame_programar, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.frame_programar, text="Teléfono:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_telefono = ttk.Entry(self.frame_programar, width=30)
        self.entry_telefono.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.frame_programar, text="Servicio:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_servicio = ttk.Entry(self.frame_programar, width=30)
        self.entry_servicio.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.frame_programar, text="Fecha (DD/MM/AAAA):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_fecha = ttk.Entry(self.frame_programar, width=30)
        self.entry_fecha.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self.frame_programar, text="Hora (HH:MM):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry_hora = ttk.Entry(self.frame_programar, width=30)
        self.entry_hora.grid(row=4, column=1, padx=10, pady=5)
        
        # Botón de programar
        btn_programar = ttk.Button(self.frame_programar, text="Programar Cita", command=self.programar_cita)
        btn_programar.grid(row=5, column=0, columnspan=2, pady=20)
    
    def crear_interfaz_visualizar(self):
        # Treeview para mostrar las citas
        self.tree = ttk.Treeview(self.frame_visualizar, columns=("Nombre", "Teléfono", "Servicio", "Fecha", "Estado"), show="headings")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Fecha", text="Fecha y Hora")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("Nombre", width=150)
        self.tree.column("Teléfono", width=100)
        self.tree.column("Servicio", width=150)
        self.tree.column("Fecha", width=150)
        self.tree.column("Estado", width=100)
        
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Botones de acción
        frame_botones = ttk.Frame(self.frame_visualizar)
        frame_botones.pack(pady=10)
        
        btn_actualizar = ttk.Button(frame_botones, text="Actualizar Lista", command=self.actualizar_lista)
        btn_actualizar.grid(row=0, column=0, padx=5)
        
        btn_confirmar = ttk.Button(frame_botones, text="Confirmar Cita", command=self.confirmar_cita)
        btn_confirmar.grid(row=0, column=1, padx=5)
        
        btn_cancelar = ttk.Button(frame_botones, text="Cancelar Cita", command=self.cancelar_cita)
        btn_cancelar.grid(row=0, column=2, padx=5)
        
        # Actualizar lista al iniciar
        self.actualizar_lista()
    
    def crear_interfaz_busqueda(self):
        # Frame de búsqueda
        frame_busqueda = ttk.Frame(self.frame_buscar)
        frame_busqueda.pack(pady=10)
        
        ttk.Label(frame_busqueda, text="Buscar por:").grid(row=0, column=0, padx=5)
        self.busqueda_opcion = tk.StringVar(value="nombre")
        ttk.Radiobutton(frame_busqueda, text="Nombre", variable=self.busqueda_opcion, value="nombre").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(frame_busqueda, text="Fecha", variable=self.busqueda_opcion, value="fecha").grid(row=0, column=2, padx=5)
        
        self.entry_busqueda = ttk.Entry(frame_busqueda, width=30)
        self.entry_busqueda.grid(row=1, column=0, columnspan=3, pady=5)
        
        btn_buscar = ttk.Button(frame_busqueda, text="Buscar", command=self.buscar_citas)
        btn_buscar.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Treeview para resultados
        self.tree_busqueda = ttk.Treeview(self.frame_buscar, columns=("Nombre", "Teléfono", "Servicio", "Fecha", "Estado"), show="headings")
        self.tree_busqueda.heading("Nombre", text="Nombre")
        self.tree_busqueda.heading("Teléfono", text="Teléfono")
        self.tree_busqueda.heading("Servicio", text="Servicio")
        self.tree_busqueda.heading("Fecha", text="Fecha y Hora")
        self.tree_busqueda.heading("Estado", text="Estado")
        
        self.tree_busqueda.pack(pady=10, padx=10, fill="both", expand=True)
    
    def programar_cita(self):
        # Obtener datos del formulario
        nombre = self.entry_nombre.get()
        telefono = self.entry_telefono.get()
        servicio = self.entry_servicio.get()
        fecha_str = self.entry_fecha.get()
        hora_str = self.entry_hora.get()
        
        # Validación básica
        if not all([nombre, telefono, servicio, fecha_str, hora_str]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            # Convertir a formato datetime
            fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
            fecha_hora_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha u hora incorrecto")
            return
        
        # Verificar disponibilidad
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM citas WHERE fecha = ?", (fecha_hora_str,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Ese horario ya está ocupado")
            return
        
        # Insertar en la base de datos
        cursor.execute("INSERT INTO citas (nombre, telefono, servicio, fecha) VALUES (?, ?, ?, ?)",
                      (nombre, telefono, servicio, fecha_hora_str))
        self.conn.commit()
        
        messagebox.showinfo("Éxito", "Cita programada correctamente")
        self.limpiar_formulario()
    
    def limpiar_formulario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_servicio.delete(0, tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
    
    def actualizar_lista(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener citas de la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM citas ORDER BY fecha")
        citas = cursor.fetchall()
        
        # Agregar citas al treeview
        for cita in citas:
            id, nombre, telefono, servicio, fecha_str, confirmada = cita
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            estado = "Confirmada" if confirmada else "Pendiente"
            self.tree.insert("", tk.END, values=(nombre, telefono, servicio, fecha.strftime("%d/%m/%Y %H:%M"), estado), iid=id)
    
    def confirmar_cita(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una cita para confirmar")
            return
        
        id_cita = selected[0]
        cursor = self.conn.cursor()
        cursor.execute("UPDATE citas SET confirmada = 1 WHERE id = ?", (id_cita,))
        self.conn.commit()
        
        messagebox.showinfo("Éxito", "Cita confirmada correctamente")
        self.actualizar_lista()
    
    def cancelar_cita(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una cita para cancelar")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Está seguro de cancelar esta cita?"):
            return
        
        id_cita = selected[0]
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM citas WHERE id = ?", (id_cita,))
        self.conn.commit()
        
        messagebox.showinfo("Éxito", "Cita cancelada correctamente")
        self.actualizar_lista()
    
    def buscar_citas(self):
        # Limpiar resultados anteriores
        for item in self.tree_busqueda.get_children():
            self.tree_busqueda.delete(item)
        
        criterio = self.entry_busqueda.get()
        if not criterio:
            messagebox.showwarning("Advertencia", "Ingrese un criterio de búsqueda")
            return
        
        opcion = self.busqueda_opcion.get()
        cursor = self.conn.cursor()
        
        if opcion == "nombre":
            cursor.execute("SELECT * FROM citas WHERE nombre LIKE ? ORDER BY fecha", (f"%{criterio}%",))
        else:  # fecha
            try:
                fecha = datetime.strptime(criterio, "%d/%m/%Y").date()
                fecha_str = fecha.strftime("%Y-%m-%d")
                cursor.execute("SELECT * FROM citas WHERE date(fecha) = ? ORDER BY fecha", (fecha_str,))
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD/MM/AAAA")
                return
        
        citas = cursor.fetchall()
        
        if not citas:
            messagebox.showinfo("Información", "No se encontraron citas con ese criterio")
            return
        
        for cita in citas:
            id, nombre, telefono, servicio, fecha_str, confirmada = cita
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            estado = "Confirmada" if confirmada else "Pendiente"
            self.tree_busqueda.insert("", tk.END, values=(nombre, telefono, servicio, fecha.strftime("%d/%m/%Y %H:%M"), estado))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCitas(root)
    root.mainloop()