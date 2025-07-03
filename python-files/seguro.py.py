import tkinter as tk
from tkinter import messagebox
import datetime

# --- Crear ventana principal ---
ventana = tk.Tk()
ventana.title("Sistema de Ventas")
ventana.geometry("700x600")

# --- Fuente para botones (puedes ajustar si no existe la variable) ---
fuente_boton = ("Arial", 14)

# --- Datos de productos ---
precios = {
    "CORRIENTAZO LOCAL": 10000,
    "CORRIENTAZO LLEVAR": 11000,
    "SOPA LOCAL": 5000,
    "SOPA LLEVAR": 6000,
    "CENA LOCAL": 12000,
    "CENA LLEVAR": 13000,
    "CALDO LOCAL": 10000,
    "CALDO LLEVAR": 11000,
    "AGUA 600ML": 3000,
    "CRISTALITE 600ML": 3500,
    "GATORADE 500ML": 5000,
    "POSTOBON PERSONAL 500ML": 3000,
    "JUGO HIT PERSONAL 500ML": 3500,
    "MR TEA 500ML": 3500,
    "HATSU 400ML": 5000,
    "POSTOBON 1500ML": 6000,
    "PEPSI 1000ML": 4500,
    "SPEED MAX 269ML": 2500,
    "BAÑOS": 1000
}

bebidas = {
    "AGUA 600ML", "CRISTALITE 600ML", "GATORADE 500ML",
    "POSTOBON PERSONAL 500ML", "JUGO HIT PERSONAL 500ML",
    "MR TEA 500ML", "HATSU 400ML", "POSTOBON 1500ML",
    "PEPSI 1000ML", "SPEED MAX 269ML"
}

servicios = {"BAÑOS"}
comidas = set(precios.keys()) - bebidas - servicios

ventas = {item: 0 for item in precios}

# --- Función para mostrar productos por categoría ---
def abrir_ventana_categoria(categoria):
    ventana_cat = tk.Toplevel(ventana)
    ventana_cat.title(f"Seleccionar productos - {categoria}")
    ventana_cat.geometry("600x500")

    tk.Label(ventana_cat, text="Empleado:", font=fuente_boton).pack(pady=10)
    entry_local = tk.Entry(ventana_cat, font=fuente_boton)
    entry_local.pack(pady=5)

    if categoria == "COMIDAS":
        productos = comidas
    elif categoria == "BEBIDAS":
        productos = bebidas
    elif categoria == "SERVICIOS":
        productos = servicios
    else:
        productos = []

    for item in productos:
        tk.Button(
            ventana_cat,
            text=item,
            font=fuente_boton,
            command=lambda i=item: abrir_ventana_cantidad(i, entry_local.get(), ventana_cat)
        ).pack(pady=5, fill="x", padx=20)

# --- Ventana emergente para registrar cantidad ---
def abrir_ventana_cantidad(item, empleado, contenedor):
    if not empleado.strip():
        messagebox.showwarning("Falta empleado", "Debe ingresar el nombre del empleado.")
        return

    ventana_cantidad = tk.Toplevel(contenedor)
    ventana_cantidad.title(f"🧾 {item}")
    ventana_cantidad.geometry("300x200")

    cantidad_var = tk.IntVar(value=1)

    def aumentar():
        cantidad_var.set(cantidad_var.get() + 1)

    def disminuir():
        if cantidad_var.get() > 1:
            cantidad_var.set(cantidad_var.get() - 1)

    tk.Label(ventana_cantidad, text=f"{item}", font=fuente_boton).pack(pady=10)
    tk.Button(ventana_cantidad, text="➖", font=fuente_boton, command=disminuir).pack(side="left", padx=10)
    tk.Label(ventana_cantidad, textvariable=cantidad_var, font=fuente_boton).pack(side="left")
    tk.Button(ventana_cantidad, text="➕", font=fuente_boton, command=aumentar).pack(side="left", padx=10)

    def registrar():
        cantidad = cantidad_var.get()
        subtotal = precios[item] * cantidad
        ventas[item] += cantidad
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("registro_ventas.txt", "a", encoding="utf-8") as f:
            f.write(f"{fecha} | Empleado: {empleado.strip()} | {item} x{cantidad} = ${subtotal}\n")
        messagebox.showinfo("Venta registrada", f"✅ {item} x{cantidad} registrado.")
        ventana_cantidad.destroy()

    tk.Button(ventana_cantidad, text="Registrar venta", font=fuente_boton, bg="#d9ead3", command=registrar).pack(pady=20)

# --- Generar resumen completo por empleado y categorías ---
def generar_resumen_completo():
    try:
        with open("registro_ventas.txt", "r", encoding="utf-8") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        messagebox.showwarning("Sin datos", "No hay registros de ventas.")
        return

    resumen = {}
    totales = {}

    for linea in lineas:
        try:
            fecha_hora, resto = linea.strip().split(" | ", 1)
            empleado = resto.split("Empleado:")[1].split(" |")[0].strip()
            item = resto.split("|")[1].split(" x")[0].strip()
            monto = int(linea.strip().split("$")[-1])
            if empleado not in resumen:
                resumen[empleado] = {"COMIDAS": [], "BEBIDAS": [], "SERVICIOS": []}
                totales[empleado] = 0
            if item in comidas:
                resumen[empleado]["COMIDAS"].append(f"{fecha_hora} | {resto}")
            elif item in bebidas:
                resumen[empleado]["BEBIDAS"].append(f"{fecha_hora} | {resto}")
            elif item in servicios:
                resumen[empleado]["SERVICIOS"].append(f"{fecha_hora} | {resto}")
            totales[empleado] += monto
        except:
            continue

    resumen_txt = "RESUMEN DE VENTAS POR EMPLEADO:\n\n"
    for emp, grupos in resumen.items():
        resumen_txt += f"🧑 Empleado: {emp}\n"
        for cat in ["COMIDAS", "BEBIDAS", "SERVICIOS"]:
            if grupos[cat]:
                etiqueta = "🍛 COMIDAS" if cat == "COMIDAS" else "🥤 BEBIDAS" if cat == "BEBIDAS" else "🚻 SERVICIOS"
                resumen_txt += f"  {etiqueta}:\n"
                for venta in grupos[cat]:
                    resumen_txt += f"   📅 {venta}\n"
        resumen_txt += f"  💰 Total vendido: ${totales[emp]}\n\n"

    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"resumen_total_{fecha_actual}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(resumen_txt)

    messagebox.showinfo("Archivo generado", f"✅ Guardado como:\n{nombre_archivo}")
    messagebox.showinfo("Resumen por empleado", resumen_txt[:3000] if len(resumen_txt) > 3000 else resumen_txt)

def abrir_editor_productos():
    editor = tk.Toplevel()
    editor.title("🔧 Editar Productos")
    editor.geometry("500x550")

    tk.Label(editor, text="Producto existente:", font=fuente_boton).pack(pady=5)
    producto_var = tk.StringVar(editor)
    producto_var.set(list(precios)[0])
    menu = tk.OptionMenu(editor, producto_var, *precios.keys())
    menu.config(font=fuente_boton)
    menu.pack(pady=5)

    tk.Label(editor, text="Nuevo nombre:", font=fuente_boton).pack(pady=5)
    nombre_entry = tk.Entry(editor, font=fuente_boton)
    nombre_entry.pack(pady=5)

    tk.Label(editor, text="Nuevo precio:", font=fuente_boton).pack(pady=5)
    precio_entry = tk.Entry(editor, font=fuente_boton)
    precio_entry.pack(pady=5)

    def actualizar_producto():
        original = producto_var.get()
        nuevo_nombre = nombre_entry.get().strip() or original
        try:
            nuevo_precio = int(precio_entry.get())
        except ValueError:
            messagebox.showwarning("Error", "El precio debe ser un número entero.")
            return

        if nuevo_nombre != original:
            precios[nuevo_nombre] = nuevo_precio
            if original in precios:
                del precios[original]
            if original in bebidas:
                bebidas.remove(original)
                bebidas.add(nuevo_nombre)
            elif original in servicios:
                servicios.remove(original)
                servicios.add(nuevo_nombre)
            elif original in comidas:
                comidas.remove(original)
                comidas.add(nuevo_nombre)
        else:
            precios[original] = nuevo_precio

        messagebox.showinfo("Actualizado", f"✅ Producto '{original}' actualizado como '{nuevo_nombre}' con precio ${nuevo_precio}")
        editor.destroy()

    def eliminar_producto():
        prod = producto_var.get()
        if messagebox.askyesno("Eliminar", f"¿Seguro que deseas eliminar '{prod}'?"):
            precios.pop(prod, None)
            bebidas.discard(prod)
            comidas.discard(prod)
            servicios.discard(prod)
            messagebox.showinfo("Eliminado", f"❌ '{prod}' fue eliminado.")
            editor.destroy()

    def agregar_producto():
        nuevo = nombre_entry.get().strip()
        try:
            valor = int(precio_entry.get())
        except:
            messagebox.showwarning("Error", "Precio inválido.")
            return
        if nuevo in precios:
            messagebox.showwarning("Existe", "Ya existe un producto con ese nombre.")
            return
        precios[nuevo] = valor
        comidas.add(nuevo)
        messagebox.showinfo("Agregado", f"✅ '{nuevo}' agregado con precio ${valor}")
        editor.destroy()

    tk.Button(editor, text="💾 Actualizar", font=fuente_boton, bg="#cfe2f3", command=actualizar_producto).pack(pady=10, fill="x", padx=40)
    tk.Button(editor, text="🗑️ Eliminar", font=fuente_boton, bg="#f4cccc", command=eliminar_producto).pack(pady=5, fill="x", padx=40)
    tk.Button(editor, text="➕ Agregar como nuevo", font=fuente_boton, bg="#d9ead3", command=agregar_producto).pack(pady=10, fill="x", padx=40)
    
# --- Variables para almacenar el pedido temporal ---
pedido_actual = {
    "empleado": "",
    "COMIDAS": {},
    "BEBIDAS": {},
    "SERVICIOS": {}
}

# --- Función para iniciar el flujo de pedido ---
def iniciar_pedido():
    pedido_actual["empleado"] = ""
    pedido_actual["COMIDAS"].clear()
    pedido_actual["BEBIDAS"].clear()
    pedido_actual["SERVICIOS"].clear()
    abrir_ventana_empleado()

def abrir_ventana_empleado():
    for w in ventana.winfo_children():
        w.destroy()
    tk.Label(ventana, text="Empleado:", font=fuente_boton).pack(pady=20)
    entry_emp = tk.Entry(ventana, font=fuente_boton)
    entry_emp.pack(pady=10)
    def siguiente():
        nombre = entry_emp.get().strip()
        if not nombre:
            messagebox.showwarning("Falta empleado", "Debe ingresar el nombre del empleado.")
            return
        pedido_actual["empleado"] = nombre
        abrir_ventana_categoria_flujo("COMIDAS")
    tk.Button(ventana, text="Siguiente ➡️", font=fuente_boton, command=siguiente).pack(pady=20)
    tk.Button(ventana, text="⬅️ Volver al menú principal", font=fuente_boton, command=mostrar_menu_principal).pack(pady=10)

def abrir_ventana_categoria_flujo(categoria):
    for w in ventana.winfo_children():
        w.destroy()
    tk.Label(ventana, text=f"Seleccionar {categoria}", font=fuente_boton).pack(pady=10)
    productos = comidas if categoria == "COMIDAS" else bebidas if categoria == "BEBIDAS" else servicios
    seleccionados = pedido_actual[categoria]
    for item in productos:
        def seleccionar(i=item):
            abrir_ventana_cantidad_flujo(categoria, i)
        cantidad = seleccionados.get(item, 0)
        texto = f"{item} ({cantidad})" if cantidad else item
        tk.Button(ventana, text=texto, font=fuente_boton, command=seleccionar).pack(pady=3, fill="x", padx=30)
    def siguiente():
        # Solo es obligatorio seleccionar una comida, no bebida ni servicio
        if categoria == "COMIDAS" and not pedido_actual[categoria]:
            messagebox.showwarning("Falta selección", f"Debe seleccionar al menos un producto de {categoria}.")
            return
        if categoria == "COMIDAS":
            abrir_ventana_categoria_flujo("BEBIDAS")
        elif categoria == "BEBIDAS":
            abrir_ventana_categoria_flujo("SERVICIOS")
        else:
            mostrar_resumen_pedido()
    tk.Button(ventana, text="Siguiente ➡️", font=fuente_boton, command=siguiente).pack(pady=10)
    tk.Button(ventana, text="⬅️ Volver atrás", font=fuente_boton, command=lambda: volver_categoria(categoria)).pack(pady=5)
    tk.Button(ventana, text="🏠 Menú principal", font=fuente_boton, command=mostrar_menu_principal).pack(pady=5)

def volver_categoria(categoria):
    if categoria == "COMIDAS":
        abrir_ventana_empleado()
    elif categoria == "BEBIDAS":
        abrir_ventana_categoria_flujo("COMIDAS")
    elif categoria == "SERVICIOS":
        abrir_ventana_categoria_flujo("BEBIDAS")

def abrir_ventana_cantidad_flujo(categoria, item):
    top = tk.Toplevel(ventana)
    top.title(f"{item}")
    top.geometry("300x200")
    cantidad_var = tk.IntVar(value=pedido_actual[categoria].get(item, 1))
    def aumentar():
        cantidad_var.set(cantidad_var.get() + 1)
    def disminuir():
        if cantidad_var.get() > 1:
            cantidad_var.set(cantidad_var.get() - 1)
    tk.Label(top, text=f"{item}", font=fuente_boton).pack(pady=10)
    tk.Button(top, text="➖", font=fuente_boton, command=disminuir).pack(side="left", padx=10)
    tk.Label(top, textvariable=cantidad_var, font=fuente_boton).pack(side="left")
    tk.Button(top, text="➕", font=fuente_boton, command=aumentar).pack(side="left", padx=10)
    def guardar():
        pedido_actual[categoria][item] = cantidad_var.get()
        top.destroy()
        abrir_ventana_categoria_flujo(categoria)
    tk.Button(top, text="Guardar", font=fuente_boton, bg="#d9ead3", command=guardar).pack(pady=20)
    tk.Button(top, text="Cancelar", font=fuente_boton, command=top.destroy).pack()

def mostrar_resumen_pedido():
    for w in ventana.winfo_children():
        w.destroy()
    resumen = f"Empleado: {pedido_actual['empleado']}\n\n"
    total = 0
    for cat in ["COMIDAS", "BEBIDAS", "SERVICIOS"]:
        if pedido_actual[cat]:
            resumen += f"{cat}:\n"
            for prod, cant in pedido_actual[cat].items():
                subtotal = precios[prod] * cant
                resumen += f"  {prod} x{cant} = ${subtotal}\n"
                total += subtotal
    resumen += f"\nTOTAL: ${total}"
    tk.Label(ventana, text="Resumen del Pedido", font=fuente_boton).pack(pady=10)
    tk.Label(ventana, text=resumen, font=("Arial", 12), justify="left").pack(pady=10)
    def registrar():
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("registro_ventas.txt", "a", encoding="utf-8") as f:
            for cat in ["COMIDAS", "BEBIDAS", "SERVICIOS"]:
                for prod, cant in pedido_actual[cat].items():
                    subtotal = precios[prod] * cant
                    f.write(f"{fecha} | Empleado: {pedido_actual['empleado']} | {prod} x{cant} = ${subtotal}\n")
        messagebox.showinfo("Pedido registrado", "✅ Pedido registrado correctamente.")
        mostrar_menu_principal()
    tk.Button(ventana, text="Registrar pedido", font=fuente_boton, bg="#d9ead3", command=registrar).pack(pady=10)
    tk.Button(ventana, text="⬅️ Volver atrás", font=fuente_boton, command=lambda: abrir_ventana_categoria_flujo("SERVICIOS")).pack(pady=5)
    tk.Button(ventana, text="🏠 Menú principal", font=fuente_boton, command=mostrar_menu_principal).pack(pady=5)

def mostrar_menu_principal():
    for w in ventana.winfo_children():
        w.destroy()
    frame_inicio = tk.Frame(ventana)
    frame_inicio.pack(expand=True, fill="both", pady=30)
    tk.Label(frame_inicio, text="¿Qué desea registrar hoy?", font=fuente_boton).pack(pady=10)
    tk.Button(
        frame_inicio,
        text="📝 Nuevo Pedido Guiado",
        font=fuente_boton,
        bg="#d0f0c0",
        command=iniciar_pedido
    ).pack(pady=10, fill="x", padx=40)
    tk.Button(
        frame_inicio,
        text="🗂️ Generar Resumen por Empleado",
        font=fuente_boton,
        bg="#fde9d9",
        command=generar_resumen_completo
    ).pack(pady=10, fill="x", padx=40)
    tk.Button(
        frame_inicio,
        text="⚙️ Administrar Productos",
        font=fuente_boton,
        bg="#d9d2e9",
        command=abrir_editor_productos
    ).pack(pady=10, fill="x", padx=40)

# --- Al iniciar, mostrar menú principal ---
mostrar_menu_principal()
ventana.mainloop()


