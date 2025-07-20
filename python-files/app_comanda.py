import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import os
import sqlite3
import json

# Menú de la cafetería
MENU = {
    "Café Americano": 25.00,
    "Cappuccino": 35.00,
    "Latte": 30.00,
    "Té": 20.00,
    "Croissant": 15.00,
    "Muffin": 18.00,
    "Sándwich": 40.00,
    "Pastel": 25.00
}

# Lista para almacenar el pedido actual
pedido = []

class ComandaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Comanda - Cafetería")
        self.root.geometry("800x700")
        self.ultimo_recibo = None
        self.botones_productos = {}
        self.item_seleccionado = None
        
        # Conexión a la base de datos SQLite
        self.conexion = sqlite3.connect("ordenes_cafeteria.db")
        self.crear_tabla()
        
        # Estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5, font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        # Título
        ttk.Label(root, text="Sistema de Comanda - Cafetería", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para el menú
        frame_menu = ttk.Frame(root)
        frame_menu.pack(pady=10, padx=10, fill="x")
        ttk.Label(frame_menu, text="Menú", font=("Arial", 12, "bold")).pack()
        
        # Botones estilizados para productos
        frame_botones = ttk.Frame(frame_menu)
        frame_botones.pack(fill="x")
        for i, (item, precio) in enumerate(MENU.items()):
            btn = tk.Button(frame_botones, text=f"{item}\n${precio:.2f}", font=("Arial", 12), 
                           command=lambda x=item: self.seleccionar_item(x), relief="flat", 
                           bg="#FFFFFF", activebackground="#90EE90", width=15, height=3)
            btn.grid(row=i//4, column=i%4, padx=10, pady=10)
            self.botones_productos[item] = btn
        
        # Frame para agregar cantidad
        frame_agregar = ttk.Frame(root)
        frame_agregar.pack(pady=10, padx=10, fill="x")
        ttk.Label(frame_agregar, text="Cantidad:").pack(side="left")
        self.entry_cantidad = ttk.Entry(frame_agregar, width=5)
        self.entry_cantidad.pack(side="left", padx=5)
        self.entry_cantidad.insert(0, "1")
        self.boton_agregar = ttk.Button(frame_agregar, text="Agregar al Pedido", command=self.agregar_item)
        self.boton_agregar.pack(side="left", padx=5)
        
        # Frame para el pedido actual
        frame_pedido = ttk.Frame(root)
        frame_pedido.pack(pady=10, padx=10, fill="both", expand=True)
        ttk.Label(frame_pedido, text="Pedido Actual", font=("Arial", 12, "bold")).pack()
        
        self.tree_pedido = ttk.Treeview(frame_pedido, columns=("Producto", "Cantidad", "Subtotal"), show="headings")
        self.tree_pedido.heading("Producto", text="Producto")
        self.tree_pedido.heading("Cantidad", text="Cantidad")
        self.tree_pedido.heading("Subtotal", text="Subtotal")
        self.tree_pedido.column("Producto", width=200)
        self.tree_pedido.column("Cantidad", width=100)
        self.tree_pedido.column("Subtotal", width=100)
        self.tree_pedido.pack(fill="both", expand=True)
        
        # Total
        self.label_total = ttk.Label(frame_pedido, text="Total: $0.00")
        self.label_total.pack(pady=5)
        
        # Frame para el historial
        frame_historial = ttk.Frame(root)
        frame_historial.pack(pady=10, padx=10, fill="both", expand=True)
        ttk.Label(frame_historial, text="Historial de Recibos", font=("Arial", 12, "bold")).pack()
        
        self.tree_historial = ttk.Treeview(frame_historial, columns=("ID", "Fecha", "Total", "Estado"), show="headings")
        self.tree_historial.heading("ID", text="ID")
        self.tree_historial.heading("Fecha", text="Fecha")
        self.tree_historial.heading("Total", text="Total")
        self.tree_historial.heading("Estado", text="Estado")
        self.tree_historial.column("ID", width=50)
        self.tree_historial.column("Fecha", width=150)
        self.tree_historial.column("Total", width=100)
        self.tree_historial.column("Estado", width=100)
        self.tree_historial.pack(fill="both", expand=True)
        
        # Actualizar historial inicialmente
        self.actualizar_historial()
        
        # Botones
        frame_botones = ttk.Frame(root)
        frame_botones.pack(pady=10)
        ttk.Button(frame_botones, text="Eliminar Seleccionado", command=self.eliminar_item).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Generar Recibo", command=self.generar_recibo).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Ver Último Recibo", command=self.ver_ultimo_recibo).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Cambiar Estado", command=self.cambiar_estado).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Ver Detalles", command=self.ver_detalles).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Cerrar Día", command=self.cerrar_dia).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Salir", command=root.quit).pack(side="left", padx=5)
    
    def crear_tabla(self):
        cursor = self.conexion.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS recibos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            productos TEXT,
            total REAL,
            estado TEXT
        )''')
        self.conexion.commit()
    
    def seleccionar_item(self, item):
        for btn_item, btn in self.botones_productos.items():
            btn.config(bg="#FFFFFF")
        self.botones_productos[item].config(bg="#90EE90")
        self.item_seleccionado = item
        self.boton_agregar.config(text=f"Agregar {item} al Pedido")
    
    def agregar_item(self):
        if not self.item_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto primero.")
            return
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
                return
            item = self.item_seleccionado
            pedido.append({"item": item, "cantidad": cantidad, "precio_unitario": MENU[item]})
            self.actualizar_pedido()
            self.entry_cantidad.delete(0, tk.END)
            self.entry_cantidad.insert(0, "1")
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida.")
    
    def eliminar_item(self):
        seleccion = self.tree_pedido.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un ítem para eliminar.")
            return
        indice = self.tree_pedido.index(seleccion[0])
        pedido.pop(indice)
        self.actualizar_pedido()
    
    def actualizar_pedido(self):
        for item in self.tree_pedido.get_children():
            self.tree_pedido.delete(item)
        total = 0
        for i, item in enumerate(pedido):
            subtotal = item["cantidad"] * item["precio_unitario"]
            total += subtotal
            self.tree_pedido.insert("", tk.END, values=(item["item"], item["cantidad"], f"${subtotal:.2f}"))
        self.label_total.config(text=f"Total: ${total:.2f}")
    
    def generar_recibo(self):
        if not pedido:
            messagebox.showwarning("Advertencia", "El pedido está vacío.")
            return
        total = sum(item["cantidad"] * item["precio_unitario"] for item in pedido)
        fecha = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs("Recibos", exist_ok=True)
        contador = len(os.listdir("Recibos")) + 1
        nombre_archivo = f"Recibos/recibo_{fecha}_orden{contador}.txt"
        
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write("=== Recibo de la Cafetería ===\n")
            archivo.write(f"Fecha: {fecha.replace('_', ' ')}\n")
            archivo.write("Estado: Pendiente\n\n")
            archivo.write("Productos:\n")
            for item in pedido:
                subtotal = item["cantidad"] * item["precio_unitario"]
                archivo.write(f"{item['item']} x{item['cantidad']} - ${subtotal:.2f}\n")
            archivo.write(f"\nTotal: ${total:.2f}\n")
            archivo.write("============================\n")
        
        productos_json = json.dumps(pedido)
        cursor = self.conexion.cursor()
        cursor.execute("INSERT INTO recibos (fecha, productos, total, estado) VALUES (?, ?, ?, ?)",
                      (fecha, productos_json, total, "Pendiente"))
        self.conexion.commit()
        
        self.ultimo_recibo = nombre_archivo
        messagebox.showinfo("Éxito", f"Recibo generado: {nombre_archivo}")
        pedido.clear()
        self.actualizar_pedido()
        self.actualizar_historial()
    
    def ver_ultimo_recibo(self):
        if not self.ultimo_recibo:
            messagebox.showwarning("Advertencia", "No se ha generado ningún recibo.")
            return
        try:
            with open(self.ultimo_recibo, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            ventana_recibo = tk.Toplevel(self.root)
            ventana_recibo.title("Último Recibo")
            ventana_recibo.geometry("300x400")
            texto = tk.Text(ventana_recibo, font=("Arial", 12))
            texto.insert(tk.END, contenido)
            texto.config(state="disabled")
            texto.pack(pady=10, padx=10)
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el recibo.")
    
    def actualizar_historial(self, filtro_estado="Todos"):
        try:
            for item in self.tree_historial.get_children():
                self.tree_historial.delete(item)
            cursor = self.conexion.cursor()
            query = "SELECT id, fecha, productos, total, estado FROM recibos"
            if filtro_estado != "Todos":
                query += " WHERE estado = ?"
                cursor.execute(query, (filtro_estado,))
            else:
                cursor.execute(query)
            recibos = cursor.fetchall()
            for recibo in recibos:
                id_recibo, fecha, productos, total, estado = recibo
                self.tree_historial.insert("", tk.END, values=(id_recibo, fecha.replace('_', ' '), f"${total:.2f}", estado))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial: {str(e)}")
    
    def cambiar_estado(self):
        seleccion = self.tree_historial.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un recibo.")
            return
        id_recibo = self.tree_historial.item(seleccion[0])["values"][0]
        cursor = self.conexion.cursor()
        cursor.execute("SELECT fecha, estado FROM recibos WHERE id = ?", (id_recibo,))
        fecha, estado_actual = cursor.fetchone()
        nuevo_estado = "Despachado" if estado_actual == "Pendiente" else "Pendiente"
        cursor.execute("UPDATE recibos SET estado = ? WHERE id = ?", (nuevo_estado, id_recibo))
        self.conexion.commit()
        
        for archivo in os.listdir("Recibos"):
            if f"recibo_{fecha}_orden" in archivo:
                try:
                    with open(f"Recibos/{archivo}", "r", encoding="utf-8") as f:
                        lineas = f.readlines()
                    with open(f"Recibos/{archivo}", "w", encoding="utf-8") as f:
                        for linea in lineas:
                            if linea.startswith("Estado:"):
                                f.write(f"Estado: {nuevo_estado}\n")
                            else:
                                f.write(linea)
                except FileNotFoundError:
                    pass
        
        self.actualizar_historial()
    
    def ver_detalles(self):
        seleccion = self.tree_historial.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un recibo.")
            return
        id_recibo = self.tree_historial.item(seleccion[0])["values"][0]
        cursor = self.conexion.cursor()
        cursor.execute("SELECT fecha, productos, total, estado FROM recibos WHERE id = ?", (id_recibo,))
        fecha, productos_json, total, estado = cursor.fetchone()
        productos = json.loads(productos_json)
        
        contenido = f"=== Recibo de la Cafetería ===\n"
        contenido += f"Fecha: {fecha.replace('_', ' ')}\n"
        contenido += f"Estado: {estado}\n\n"
        contenido += "Productos:\n"
        for item in productos:
            subtotal = item["cantidad"] * item["precio_unitario"]
            contenido += f"{item['item']} x{item['cantidad']} - ${subtotal:.2f}\n"
        contenido += f"\nTotal: ${total:.2f}\n"
        contenido += "============================\n"
        
        ventana_detalles = tk.Toplevel(self.root)
        ventana_detalles.title(f"Recibo ID {id_recibo}")
        ventana_detalles.geometry("300x400")
        texto = tk.Text(ventana_detalles, font=("Arial", 12))
        texto.insert(tk.END, contenido)
        texto.config(state="disabled")
        texto.pack(pady=10, padx=10)
    
    def cerrar_dia(self):
        # Confirmar acción
        if not messagebox.askyesno("Confirmar", "¿Estás seguro de cerrar el día? Esto generará un reporte CSV y borrará el historial de recibos."):
            return
        
        # Obtener la fecha actual
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Consultar recibos del día actual
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id, fecha, productos, total, estado FROM recibos WHERE fecha LIKE ?", (f"{fecha_hoy}%",))
        recibos = cursor.fetchall()
        
        if not recibos:
            messagebox.showinfo("Información", f"No hay recibos para el día {fecha_hoy}.")
            return
        
        # Generar archivo CSV
        os.makedirs("Recibos", exist_ok=True)
        nombre_archivo = f"Recibos/reporte_diario_{fecha_hoy}.csv"
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write("ID,Fecha,Productos,Total,Estado\n")
                for recibo in recibos:
                    id_recibo, fecha, productos_json, total, estado = recibo
                    productos = json.loads(productos_json)
                    productos_str = ", ".join(f"{item['item']} x{item['cantidad']}" for item in productos)
                    f.write(f"{id_recibo},{fecha},\"{productos_str}\",{total:.2f},{estado}\n")
            
            # Borrar todos los recibos de la base de datos
            cursor.execute("DELETE FROM recibos")
            self.conexion.commit()
            
            # Actualizar historial (quedará vacío)
            self.actualizar_historial()
            
            messagebox.showinfo("Éxito", f"Reporte diario generado: {nombre_archivo}\nHistorial de recibos borrado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cerrar el día: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComandaApp(root)
    root.mainloop()