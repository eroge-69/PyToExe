import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import csv
from fpdf import FPDF
import os
import pandas as pd
from PIL import Image, ImageTk

# === Configuración de la Asociación ===
NOMBRE_ASOCIACION = "Team Kraken Robótica"
DIRECCION = "Plaza Mayor de Llaranes nº11 planta bajo puerta 12, 33450 Avilés, Asturias"
CIF = "G22734043"
LOGO_PATH = "logo.png"

# === Base de datos ===
conn = sqlite3.connect("datos.db")
c = conn.cursor()

# Tabla de socios
c.execute('''CREATE TABLE IF NOT EXISTS socios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    apellido TEXT,
    dni TEXT,
    direccion TEXT,
    tipo TEXT,
    consentimiento_imagen TEXT,
    nombre_padre TEXT,
    nombre_madre TEXT,
    telefono TEXT
)''')

# Tabla de movimientos
c.execute('''CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    descripcion TEXT,
    cantidad REAL,
    con_iva INTEGER,
    fecha TEXT
)''')

# Tabla de stock
c.execute('''CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT,
    descripcion TEXT,
    cantidad INTEGER,
    precio_unitario REAL
)''')

# Tabla para facturas/tickets personalizados
c.execute('''CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    fecha TEXT,
    nombre TEXT,
    apellidos TEXT,
    concepto TEXT,
    cantidad REAL
)''')

conn.commit()

# === Funciones de Socios ===
def agregar_socio():
    datos = (
        entry_nombre.get(), entry_apellido.get(), entry_dni.get(), entry_direccion.get(),
        combo_tipo_socio.get(), var_consentimiento.get(), entry_padre.get(), entry_madre.get(), entry_telefono.get()
    )
    c.execute("INSERT INTO socios (nombre, apellido, dni, direccion, tipo, consentimiento_imagen, nombre_padre, nombre_madre, telefono) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", datos)
    conn.commit()
    actualizar_lista_socios()
    # Limpiar campos
    entry_nombre.delete(0, tk.END)
    entry_apellido.delete(0, tk.END)
    entry_dni.delete(0, tk.END)
    entry_direccion.delete(0, tk.END)
    entry_padre.delete(0, tk.END)
    entry_madre.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)

def actualizar_lista_socios():
    lista_socios.delete(*lista_socios.get_children())
    for row in c.execute("SELECT * FROM socios"):
        lista_socios.insert("", "end", values=row)

def exportar_socios():
    try:
        data = c.execute("SELECT * FROM socios").fetchall()
        df = pd.DataFrame(data, columns=["ID", "Nombre", "Apellido", "DNI", "Dirección", "Tipo", "Consentimiento", "Padre", "Madre", "Teléfono"])
        df.to_excel("socios.xlsx", index=False)
        messagebox.showinfo("Exportado", "Lista de socios exportada como 'socios.xlsx'")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar socios: {str(e)}")

def eliminar_socio():
    seleccion = lista_socios.selection()
    if seleccion:
        item = lista_socios.item(seleccion)
        id_socio = item['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este socio?"):
            c.execute("DELETE FROM socios WHERE id=?", (id_socio,))
            conn.commit()
            actualizar_lista_socios()
    else:
        messagebox.showwarning("Advertencia", "Seleccione un socio para eliminar")

def modificar_socio():
    seleccion = lista_socios.selection()
    if seleccion:
        item = lista_socios.item(seleccion)
        valores = item['values']
        
        # Rellenar campos con datos actuales
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, valores[1])
        entry_apellido.delete(0, tk.END)
        entry_apellido.insert(0, valores[2])
        entry_dni.delete(0, tk.END)
        entry_dni.insert(0, valores[3])
        entry_direccion.delete(0, tk.END)
        entry_direccion.insert(0, valores[4])
        combo_tipo_socio.set(valores[5])
        var_consentimiento.set(valores[6])
        entry_padre.delete(0, tk.END)
        entry_padre.insert(0, valores[7])
        entry_madre.delete(0, tk.END)
        entry_madre.insert(0, valores[8])
        entry_telefono.delete(0, tk.END)
        entry_telefono.insert(0, valores[9])
        
        # Eliminar el registro actual para que se pueda "modificar" agregando de nuevo
        c.execute("DELETE FROM socios WHERE id=?", (valores[0],))
        conn.commit()
        actualizar_lista_socios()
        messagebox.showinfo("Modificar", "Datos cargados. Modifique los campos necesarios y haga clic en 'Agregar Socio'")
    else:
        messagebox.showwarning("Advertencia", "Seleccione un socio para modificar")

# === Funciones de Movimientos ===
def agregar_movimiento():
    try:
        tipo = combo_tipo_mov.get()
        descripcion = entry_desc.get()
        cantidad = float(entry_cant.get())
        con_iva = var_iva.get()
        fecha = datetime.date.today().isoformat()
        if con_iva:
            cantidad *= 1.21
        c.execute("INSERT INTO movimientos (tipo, descripcion, cantidad, con_iva, fecha) VALUES (?, ?, ?, ?, ?)",
                  (tipo, descripcion, cantidad, con_iva, fecha))
        conn.commit()
        actualizar_libro()
        actualizar_balance()
        # Limpiar campos
        entry_desc.delete(0, tk.END)
        entry_cant.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese una cantidad válida")

def actualizar_libro():
    libro_diario.delete(*libro_diario.get_children())
    for row in c.execute("SELECT id, tipo, descripcion, cantidad, con_iva, fecha FROM movimientos"):
        libro_diario.insert("", "end", values=row)

def actualizar_balance():
    c.execute("SELECT SUM(cantidad) FROM movimientos WHERE tipo='Ingreso'")
    ingresos = c.fetchone()[0] or 0
    c.execute("SELECT SUM(cantidad) FROM movimientos WHERE tipo='Gasto'")
    gastos = c.fetchone()[0] or 0
    balance = ingresos - gastos
    label_balance.config(text=f"Balance: {balance:.2f} €")

def eliminar_movimiento():
    seleccion = libro_diario.selection()
    if seleccion:
        item = libro_diario.item(seleccion)
        id_mov = item['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este movimiento?"):
            c.execute("DELETE FROM movimientos WHERE id=?", (id_mov,))
            conn.commit()
            actualizar_libro()
            actualizar_balance()
    else:
        messagebox.showwarning("Advertencia", "Seleccione un movimiento para eliminar")

def modificar_movimiento():
    seleccion = libro_diario.selection()
    if seleccion:
        item = libro_diario.item(seleccion)
        valores = item['values']
        
        combo_tipo_mov.set(valores[1])
        entry_desc.delete(0, tk.END)
        entry_desc.insert(0, valores[2])
        entry_cant.delete(0, tk.END)
        # Si tenía IVA, mostrar cantidad sin IVA
        cantidad = float(valores[3])
        if valores[4] == 1:  # Con IVA
            cantidad = cantidad / 1.21
            var_iva.set(True)
        else:
            var_iva.set(False)
        entry_cant.insert(0, str(round(cantidad, 2)))
        
        c.execute("DELETE FROM movimientos WHERE id=?", (valores[0],))
        conn.commit()
        actualizar_libro()
        actualizar_balance()
        messagebox.showinfo("Modificar", "Datos cargados. Modifique los campos necesarios y haga clic en 'Agregar Movimiento'")
    else:
        messagebox.showwarning("Advertencia", "Seleccione un movimiento para modificar")

def exportar_excel():
    try:
        data = c.execute("SELECT * FROM movimientos").fetchall()
        df = pd.DataFrame(data, columns=["ID", "Tipo", "Descripción", "Cantidad", "Con IVA", "Fecha"])
        df.to_excel("movimientos.xlsx", index=False)
        messagebox.showinfo("Exportado", "Datos exportados a 'movimientos.xlsx'")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar: {str(e)}")

# === Funciones de Stock ===
def agregar_stock():
    try:
        datos = (entry_producto.get(), entry_desc_stock.get(), int(entry_cant_stock.get()), float(entry_precio_unit.get()))
        c.execute("INSERT INTO stock (producto, descripcion, cantidad, precio_unitario) VALUES (?, ?, ?, ?)", datos)
        conn.commit()
        actualizar_stock()
        # Limpiar campos
        entry_producto.delete(0, tk.END)
        entry_desc_stock.delete(0, tk.END)
        entry_cant_stock.delete(0, tk.END)
        entry_precio_unit.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores válidos para cantidad y precio")

def actualizar_stock():
    lista_stock.delete(*lista_stock.get_children())
    for row in c.execute("SELECT * FROM stock"):
        lista_stock.insert("", "end", values=row)

def eliminar_stock():
    seleccion = lista_stock.selection()
    if seleccion:
        item = lista_stock.item(seleccion)
        id_stock = item['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            c.execute("DELETE FROM stock WHERE id=?", (id_stock,))
            conn.commit()
            actualizar_stock()
    else:
        messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")

def modificar_stock():
    seleccion = lista_stock.selection()
    if seleccion:
        item = lista_stock.item(seleccion)
        valores = item['values']
        
        entry_producto.delete(0, tk.END)
        entry_producto.insert(0, valores[1])
        entry_desc_stock.delete(0, tk.END)
        entry_desc_stock.insert(0, valores[2])
        entry_cant_stock.delete(0, tk.END)
        entry_cant_stock.insert(0, valores[3])
        entry_precio_unit.delete(0, tk.END)
        entry_precio_unit.insert(0, valores[4])
        
        c.execute("DELETE FROM stock WHERE id=?", (valores[0],))
        conn.commit()
        actualizar_stock()
        messagebox.showinfo("Modificar", "Datos cargados. Modifique los campos necesarios y haga clic en 'Agregar Producto'")
    else:
        messagebox.showwarning("Advertencia", "Seleccione un producto para modificar")

def exportar_stock():
    try:
        data = c.execute("SELECT * FROM stock").fetchall()
        df = pd.DataFrame(data, columns=["ID", "Producto", "Descripción", "Cantidad", "Precio Unitario"])
        df.to_excel("stock.xlsx", index=False)
        messagebox.showinfo("Exportado", "Stock exportado como 'stock.xlsx'")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar stock: {str(e)}")

# === Funciones de Documentos ===
def actualizar_lista_documentos():
    lista_documentos.delete(*lista_documentos.get_children())
    for row in c.execute("SELECT * FROM documentos"):
        lista_documentos.insert("", "end", values=row)

def exportar_documentos():
    try:
        data = c.execute("SELECT * FROM documentos").fetchall()
        df = pd.DataFrame(data, columns=["ID", "Tipo", "Fecha", "Nombre", "Apellidos", "Concepto", "Cantidad"])
        df.to_excel("documentos.xlsx", index=False)
        messagebox.showinfo("Exportado", "Documentos exportados como 'documentos.xlsx'")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar documentos: {str(e)}")

def generar_documento_personalizado(tipo_doc):
    try:
        fecha = entry_fecha_doc.get() or datetime.date.today().isoformat()
        nombre = entry_nombre_doc.get()
        apellidos = entry_apellidos_doc.get()
        concepto = entry_concepto_doc.get()
        cantidad = float(entry_cantidad_doc.get()) if entry_cantidad_doc.get() else 0.0
        
        # Guardar en base de datos
        c.execute("INSERT INTO documentos (tipo, fecha, nombre, apellidos, concepto, cantidad) VALUES (?, ?, ?, ?, ?, ?)",
                  (tipo_doc, fecha, nombre, apellidos, concepto, cantidad))
        conn.commit()
        
        # Generar PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Logo si existe
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, 10, 8, 30)
        
        # Datos de la asociación
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, NOMBRE_ASOCIACION, ln=True, align="R")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, DIRECCION, ln=True, align="R")
        pdf.cell(0, 5, f"CIF: {CIF}", ln=True, align="R")
        
        pdf.ln(15)
        
        # Título del documento
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{tipo_doc.upper()}", ln=True, align="C")
        pdf.ln(10)
        
        # Datos del documento
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Fecha: {fecha}", ln=True)
        if nombre or apellidos:
            pdf.cell(0, 8, f"Cliente: {nombre} {apellidos}", ln=True)
        if concepto:
            pdf.cell(0, 8, f"Concepto: {concepto}", ln=True)
        if cantidad > 0:
            pdf.cell(0, 8, f"Importe: {cantidad:.2f} €", ln=True)
        
        pdf.ln(10)
        
        # Firma
        pdf.cell(0, 8, "Firma:", ln=True)
        pdf.ln(20)
        pdf.cell(0, 8, "_" * 30, ln=True)
        
        filename = f"{tipo_doc}_{fecha}_{nombre}_{apellidos}.pdf".replace(" ", "_")
        pdf.output(filename)
        
        messagebox.showinfo("Generado", f"{tipo_doc.capitalize()} generado: {filename}")
        actualizar_lista_documentos()
        
        # Limpiar campos
        entry_fecha_doc.delete(0, tk.END)
        entry_nombre_doc.delete(0, tk.END)
        entry_apellidos_doc.delete(0, tk.END)
        entry_concepto_doc.delete(0, tk.END)
        entry_cantidad_doc.delete(0, tk.END)
        
    except ValueError:
        messagebox.showerror("Error", "Por favor verifique que la cantidad sea un número válido")
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar documento: {str(e)}")

def generar_informe_anual():
    try:
        año = entry_año_informe.get() or str(datetime.date.today().year)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Logo
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, 10, 8, 30)
        
        # Encabezado
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, NOMBRE_ASOCIACION, ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, DIRECCION, ln=True, align="C")
        pdf.cell(0, 5, f"CIF: {CIF}", ln=True, align="C")
        
        pdf.ln(15)
        
        # Título
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"INFORME DE BALANCE ANUAL - {año}", ln=True, align="C")
        pdf.ln(10)
        
        # Consultas a la base de datos
        c.execute("SELECT SUM(cantidad) FROM movimientos WHERE tipo='Ingreso' AND strftime('%Y', fecha) = ?", (año,))
        ingresos_anuales = c.fetchone()[0] or 0
        
        c.execute("SELECT SUM(cantidad) FROM movimientos WHERE tipo='Gasto' AND strftime('%Y', fecha) = ?", (año,))
        gastos_anuales = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM socios")
        total_socios = c.fetchone()[0] or 0
        
        balance_anual = ingresos_anuales - gastos_anuales
        
        # Contenido del informe
        pdf.set_font("Arial", size=12)
        
        # 1. Información general
        pdf.cell(0, 8, "1. INFORMACIÓN GENERAL DE LA ASOCIACIÓN", ln=True)
        pdf.ln(3)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"Denominación: {NOMBRE_ASOCIACION}", ln=True)
        pdf.cell(0, 6, f"Domicilio: {DIRECCION}", ln=True)
        pdf.cell(0, 6, f"CIF: {CIF}", ln=True)
        pdf.cell(0, 6, f"Número de socios: {total_socios}", ln=True)
        pdf.ln(5)
        
        # 2. Balance económico
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "2. BALANCE ECONÓMICO", ln=True)
        pdf.ln(3)
        pdf.set_font("Arial", size=10)
        
        pdf.cell(60, 8, "INGRESOS:", border=1)
        pdf.cell(40, 8, f"{ingresos_anuales:.2f} €", border=1, align="R")
        pdf.ln()
        
        pdf.cell(60, 8, "GASTOS:", border=1)
        pdf.cell(40, 8, f"{gastos_anuales:.2f} €", border=1, align="R")
        pdf.ln()
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, "RESULTADO:", border=1)
        pdf.cell(40, 8, f"{balance_anual:.2f} €", border=1, align="R")
        pdf.ln(10)
        
        # 3. Desglose de movimientos
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "3. DESGLOSE DE MOVIMIENTOS", ln=True)
        pdf.ln(3)
        
        # Ingresos detallados
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "INGRESOS:", ln=True)
        pdf.set_font("Arial", size=9)
        
        for row in c.execute("SELECT descripcion, cantidad, fecha FROM movimientos WHERE tipo='Ingreso' AND strftime('%Y', fecha) = ? ORDER BY fecha", (año,)):
            pdf.cell(0, 5, f"• {row[2]} - {row[0]}: {row[1]:.2f} €", ln=True)
        
        pdf.ln(3)
        
        # Gastos detallados
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "GASTOS:", ln=True)
        pdf.set_font("Arial", size=9)
        
        for row in c.execute("SELECT descripcion, cantidad, fecha FROM movimientos WHERE tipo='Gasto' AND strftime('%Y', fecha) = ? ORDER BY fecha", (año,)):
            pdf.cell(0, 5, f"• {row[2]} - {row[0]}: {row[1]:.2f} €", ln=True)
        
        pdf.ln(10)
        
        # 4. Cumplimiento normativo
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "4. CUMPLIMIENTO NORMATIVO", ln=True)
        pdf.ln(3)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, "Este informe se presenta en cumplimiento de:", ln=True)
        pdf.cell(0, 6, "• Ley Orgánica 1/2002, de 22 de marzo, reguladora del Derecho de Asociación", ln=True)
        pdf.cell(0, 6, "• Ley del Principado de Asturias 4/2010, de 29 de junio, de Asociaciones", ln=True)
        pdf.cell(0, 6, "• Real Decreto 949/2015 sobre registro de asociaciones de ámbito estatal", ln=True)
        
        pdf.ln(10)
        
        # Fecha y firma
        pdf.cell(0, 8, f"En Avilés, a {datetime.date.today().strftime('%d de %B de %Y')}", ln=True, align="R")
        pdf.ln(10)
        pdf.cell(0, 8, "El Presidente de la Asociación", ln=True, align="R")
        pdf.ln(15)
        pdf.cell(0, 8, "_" * 30, ln=True, align="R")
        
        filename = f"Informe_Anual_{año}_TeamKraken.pdf"
        pdf.output(filename)
        
        messagebox.showinfo("Informe Generado", f"Informe anual generado: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar informe: {str(e)}")

# === Interfaz gráfica ===
root = tk.Tk()
root.title("Contabilidad - TEAM KRAKEN ROBÓTICA")
root.configure(bg="#B19CD9")

# Cargar y mostrar logo en la ventana principal
try:
    if os.path.exists(LOGO_PATH):
        logo_img = Image.open(LOGO_PATH)
        logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        
        logo_frame = tk.Frame(root, bg="#B19CD9")
        logo_frame.pack(pady=5)
        
        logo_label = tk.Label(logo_frame, image=logo_photo, bg="#B19CD9")
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(logo_frame, text="TEAM KRAKEN ROBÓTICA\nSistema de Gestión", 
                             font=("Arial", 14, "bold"), bg="#B19CD9", fg="white")
        title_label.pack(side=tk.LEFT, padx=10)
except:
    pass  # Si no se puede cargar el logo, continuar sin él

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, expand=True, fill="both")

# === Pestaña: Registro de Socios ===
tab_socios = ttk.Frame(notebook)
notebook.add(tab_socios, text="Registro de Socios")

# Campos de entrada para socios
ttk.Label(tab_socios, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_nombre = ttk.Entry(tab_socios)
entry_nombre.grid(row=0, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Apellidos:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_apellido = ttk.Entry(tab_socios)
entry_apellido.grid(row=1, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="DNI:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_dni = ttk.Entry(tab_socios)
entry_dni.grid(row=2, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Dirección:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
entry_direccion = ttk.Entry(tab_socios)
entry_direccion.grid(row=3, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Tipo de Socio:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
combo_tipo_socio = ttk.Combobox(tab_socios, values=["Socio Fundador", "Socio"])
combo_tipo_socio.grid(row=4, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Consentimiento Imagen:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
var_consentimiento = tk.StringVar()
ttk.Checkbutton(tab_socios, text="Sí", variable=var_consentimiento, onvalue="Sí", offvalue="No").grid(row=5, column=1, sticky="w", padx=5, pady=2)

ttk.Label(tab_socios, text="Nombre del Padre:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
entry_padre = ttk.Entry(tab_socios)
entry_padre.grid(row=6, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Nombre de la Madre:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
entry_madre = ttk.Entry(tab_socios)
entry_madre.grid(row=7, column=1, padx=5, pady=2)

ttk.Label(tab_socios, text="Teléfono:").grid(row=8, column=0, sticky="w", padx=5, pady=2)
entry_telefono = ttk.Entry(tab_socios)
entry_telefono.grid(row=8, column=1, padx=5, pady=2)

ttk.Button(tab_socios, text="Agregar Socio", command=agregar_socio).grid(row=9, column=0, columnspan=2, pady=10)

# Botones de acciones para socios
frame_botones_socios = ttk.Frame(tab_socios)
frame_botones_socios.grid(row=10, column=0, columnspan=2, pady=5)
ttk.Button(frame_botones_socios, text="Eliminar Socio", command=eliminar_socio).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botones_socios, text="Modificar Socio", command=modificar_socio).pack(side=tk.LEFT, padx=5)

# Lista de socios
lista_socios = ttk.Treeview(tab_socios, columns=["ID", "Nombre", "Apellidos", "DNI", "Dirección", "Tipo", "Consentimiento", "Padre", "Madre", "Teléfono"], show="headings")
for col in lista_socios["columns"]:
    lista_socios.heading(col, text=col)
    lista_socios.column(col, width=100)
lista_socios.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Botón para exportar socios
ttk.Button(tab_socios, text="Exportar Socios a Excel", command=exportar_socios).grid(row=12, column=0, columnspan=2, pady=5)

# === Pestaña: Caja ===
tab_caja = ttk.Frame(notebook)
notebook.add(tab_caja, text="Caja")

# Campos para movimientos
ttk.Label(tab_caja, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
combo_tipo_mov = ttk.Combobox(tab_caja, values=["Ingreso", "Gasto"])
combo_tipo_mov.grid(row=0, column=1, padx=5, pady=2)

ttk.Label(tab_caja, text="Descripción:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_desc = ttk.Entry(tab_caja)
entry_desc.grid(row=1, column=1, padx=5, pady=2)

ttk.Label(tab_caja, text="Cantidad:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_cant = ttk.Entry(tab_caja)
entry_cant.grid(row=2, column=1, padx=5, pady=2)

var_iva = tk.BooleanVar()
ttk.Checkbutton(tab_caja, text="Con IVA (21%)", variable=var_iva).grid(row=3, column=0, columnspan=2, padx=5, pady=2)

ttk.Button(tab_caja, text="Agregar Movimiento", command=agregar_movimiento).grid(row=4, column=0, columnspan=2, pady=10)

# Botones de acciones para movimientos
frame_botones_mov = ttk.Frame(tab_caja)
frame_botones_mov.grid(row=5, column=0, columnspan=2, pady=5)
ttk.Button(frame_botones_mov, text="Eliminar Movimiento", command=eliminar_movimiento).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botones_mov, text="Modificar Movimiento", command=modificar_movimiento).pack(side=tk.LEFT, padx=5)

# Libro diario
libro_diario = ttk.Treeview(tab_caja, columns=["ID", "Tipo", "Descripción", "Cantidad", "Con IVA", "Fecha"], show="headings")
for col in libro_diario["columns"]:
    libro_diario.heading(col, text=col)
    libro_diario.column(col, width=100)
libro_diario.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Balance
label_balance = ttk.Label(tab_caja, text="Balance: 0.00 €", font=("Arial", 12, "bold"))
label_balance.grid(row=7, column=0, columnspan=2, pady=10)

# Botón exportar movimientos
ttk.Button(tab_caja, text="Exportar a Excel", command=exportar_excel).grid(row=8, column=0, columnspan=2, pady=5)

# === Pestaña: Stock ===
tab_stock = ttk.Frame(notebook)
notebook.add(tab_stock, text="Stock")

# Campos para stock
ttk.Label(tab_stock, text="Producto:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_producto = ttk.Entry(tab_stock)
entry_producto.grid(row=0, column=1, padx=5, pady=2)

ttk.Label(tab_stock, text="Descripción:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_desc_stock = ttk.Entry(tab_stock)
entry_desc_stock.grid(row=1, column=1, padx=5, pady=2)

ttk.Label(tab_stock, text="Cantidad:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_cant_stock = ttk.Entry(tab_stock)
entry_cant_stock.grid(row=2, column=1, padx=5, pady=2)

ttk.Label(tab_stock, text="Precio Unitario:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
entry_precio_unit = ttk.Entry(tab_stock)
entry_precio_unit.grid(row=3, column=1, padx=5, pady=2)

ttk.Button(tab_stock, text="Agregar Producto", command=agregar_stock).grid(row=4, column=0, columnspan=2, pady=10)

# Botones de acciones para stock
frame_botones_stock = ttk.Frame(tab_stock)
frame_botones_stock.grid(row=5, column=0, columnspan=2, pady=5)
ttk.Button(frame_botones_stock, text="Eliminar Producto", command=eliminar_stock).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botones_stock, text="Modificar Producto", command=modificar_stock).pack(side=tk.LEFT, padx=5)

# Lista de stock
lista_stock = ttk.Treeview(tab_stock, columns=["ID", "Producto", "Descripción", "Cantidad", "Precio Unitario"], show="headings")
for col in lista_stock["columns"]:
    lista_stock.heading(col, text=col)
    lista_stock.column(col, width=120)
lista_stock.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Botón exportar stock
ttk.Button(tab_stock, text="Exportar Stock a Excel", command=exportar_stock).grid(row=7, column=0, columnspan=2, pady=5)

# === Pestaña: Documentos ===
tab_documentos = ttk.Frame(notebook)
notebook.add(tab_documentos, text="Documentos")

# Campos para documentos personalizados
ttk.Label(tab_documentos, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_fecha_doc = ttk.Entry(tab_documentos)
entry_fecha_doc.grid(row=0, column=1, padx=5, pady=2)

ttk.Label(tab_documentos, text="Nombre:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_nombre_doc = ttk.Entry(tab_documentos)
entry_nombre_doc.grid(row=1, column=1, padx=5, pady=2)

ttk.Label(tab_documentos, text="Apellidos:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
entry_apellidos_doc = ttk.Entry(tab_documentos)
entry_apellidos_doc.grid(row=2, column=1, padx=5, pady=2)

ttk.Label(tab_documentos, text="Concepto:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
entry_concepto_doc = ttk.Entry(tab_documentos)
entry_concepto_doc.grid(row=3, column=1, padx=5, pady=2)

ttk.Label(tab_documentos, text="Cantidad:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
entry_cantidad_doc = ttk.Entry(tab_documentos)
entry_cantidad_doc.grid(row=4, column=1, padx=5, pady=2)

# Botones para generar documentos
frame_botones_doc = ttk.Frame(tab_documentos)
frame_botones_doc.grid(row=5, column=0, columnspan=2, pady=10)
ttk.Button(frame_botones_doc, text="Generar Factura", command=lambda: generar_documento_personalizado("factura")).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botones_doc, text="Generar Ticket", command=lambda: generar_documento_personalizado("ticket")).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_botones_doc, text="Generar Recibo", command=lambda: generar_documento_personalizado("recibo")).pack(side=tk.LEFT, padx=5)

# Lista de documentos generados
lista_documentos = ttk.Treeview(tab_documentos, columns=["ID", "Tipo", "Fecha", "Nombre", "Apellidos", "Concepto", "Cantidad"], show="headings")
for col in lista_documentos["columns"]:
    lista_documentos.heading(col, text=col)
    lista_documentos.column(col, width=100)
lista_documentos.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Botón exportar documentos
ttk.Button(tab_documentos, text="Exportar Documentos a Excel", command=exportar_documentos).grid(row=7, column=0, columnspan=2, pady=5)

# === Pestaña: Informes ===
tab_informes = ttk.Frame(notebook)
notebook.add(tab_informes, text="Informes")

ttk.Label(tab_informes, text="Año para informe anual:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_año_informe = ttk.Entry(tab_informes)
entry_año_informe.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(tab_informes, text="Generar Informe Anual", command=generar_informe_anual).grid(row=1, column=0, columnspan=2, pady=20)

# Información del informe
info_frame = ttk.LabelFrame(tab_informes, text="Información del Informe")
info_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

info_text = """
El informe anual incluye:
• Balance económico completo
• Desglose detallado de ingresos y gastos
• Número total de socios
• Cumplimiento normativo
• Formato oficial para presentación ante organismos oficiales
"""

ttk.Label(info_frame, text=info_text, justify="left").pack(padx=10, pady=10)

# Configurar la expansión de las columnas y filas
for tab in [tab_socios, tab_caja, tab_stock, tab_documentos]:
    tab.columnconfigure(1, weight=1)
    tab.rowconfigure(6, weight=1)  # Para que las listas se expandan

# Inicializar las listas
actualizar_lista_socios()
actualizar_libro()
actualizar_balance()
actualizar_stock()
actualizar_lista_documentos()

# Ejecutar la aplicación
root.mainloop()

# Cerrar conexión a la base de datos al salir
conn.close()