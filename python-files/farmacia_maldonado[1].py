# -*- coding: utf-8 -*-
"""
Farmacia Maldonado - Sistema POS 5.0 (Prototipo)
- Tkinter GUI
- Preventa + Caja con Vendedor y Tipo de Documento (Contado, Crédito, Regalías)
- Clientes (Dirección obligatoria, RUC opcional)
- Compras con categorías, costo, margen y precio de venta
- Inventario avanzado (categorías, auditoría, cambio múltiple, productos regalía)
- Factura PDF con opción de incluir dirección (por defecto NO se imprime)
- Pagos en Caja: Efectivo, Tarjeta, Dólares, Transferencia
- Regalías: muestra precio pero totaliza 0 y no afecta caja
Nota: almacenamiento en memoria (para .exe simple); idealmente persistir a DB en producción.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
import os

# -------------------- Datos iniciales --------------------
usuarios = {
    "admin": {"password": "1234", "rol": "admin"},
    "preventa": {"password": "1234", "rol": "preventa"}
}

# clientes[doc] = {...}
clientes = {
    "CF": {"nombre": "Consumidor Final", "direccion": "", "ruc": "", "telefono": "", "correo": "", "limite_credito": 0.0, "credito_usado": 0.0}
}

proveedores = {}
categorias = ["Analgésicos", "Antibióticos", "Vitaminas", "Cuidado personal", "Sin categoría"]

# productos[codigo]
productos = {
    "001": {"nombre": "Paracetamol 500mg", "precio": 30.0, "stock": 30, "vencimiento": "2025-12-31", "categoria": "Analgésicos", "sustitutos": ["002"], "regalia_ok": False},
    "002": {"nombre": "Ibuprofeno 400mg", "precio": 45.0, "stock": 25, "vencimiento": "2025-11-30", "categoria": "Analgésicos", "sustitutos": ["001"], "regalia_ok": True}
}

# preventas en cola para Caja
preventas = []  # cada preventa es un dict con items, cliente, vendedor, doc_type, incluir_direccion, totals, etc.
ventas = []     # ventas finalizadas en caja
cortes = []     # cierres de caja

nombre_farmacia = "Farmacia Maldonado"
logo_text = "FM"  # placeholder

# -------------------- Utilidades --------------------
def login(usuario, clave):
    if usuario in usuarios and usuarios[usuario]["password"] == clave:
        return usuarios[usuario]["rol"]
    return None

def pedir_float(titulo, prompt, default=None):
    while True:
        s = simpledialog.askstring(titulo, prompt if default is None else f"{prompt} (Enter={default})")
        if s in (None, ""):
            if default is not None:
                return float(default)
            return None
        try:
            return float(s.replace(",", "."))
        except:
            messagebox.showerror(titulo, "Ingrese un número válido.")

def pedir_int(titulo, prompt, default=None):
    while True:
        s = simpledialog.askstring(titulo, prompt if default is None else f"{prompt} (Enter={default})")
        if s in (None, ""):
            if default is not None:
                return int(default)
            return None
        try:
            return int(s)
        except:
            messagebox.showerror(titulo, "Ingrese un entero válido.")

# -------------------- Clientes --------------------
def crear_o_elegir_cliente():
    # Buscar por documento/ID (si no existe, crear)
    doc = simpledialog.askstring("Cliente", "Identificación del cliente (o CF):")
    if doc is None:
        return None
    if doc in clientes:
        return doc
    # Crear nuevo cliente
    nombre = simpledialog.askstring("Cliente nuevo", "Nombre del cliente:")
    if not nombre:
        messagebox.showerror("Cliente", "Nombre es obligatorio.")
        return None
    direccion = simpledialog.askstring("Cliente nuevo", "Dirección (obligatoria):")
    if not direccion:
        messagebox.showerror("Cliente", "Dirección es obligatoria.")
        return None
    ruc = simpledialog.askstring("Cliente nuevo", "RUC (opcional):") or ""
    tel = simpledialog.askstring("Cliente nuevo", "Teléfono (opcional):") or ""
    correo = simpledialog.askstring("Cliente nuevo", "Correo (opcional):") or ""
    limite = pedir_float("Cliente nuevo", "Límite de crédito (0 si no aplica):", default=0)
    if limite is None:
        limite = 0.0
    clientes[doc] = {
        "nombre": nombre, "direccion": direccion, "ruc": ruc,
        "telefono": tel, "correo": correo, "limite_credito": float(limite), "credito_usado": 0.0
    }
    messagebox.showinfo("Cliente", f"Cliente {nombre} creado.")
    return doc

# -------------------- Inventario --------------------
def registrar_compra():
    proveedor = simpledialog.askstring("Compras", "Proveedor:")
    if not proveedor:
        return
    if proveedor not in proveedores:
        proveedores[proveedor] = {"contacto": "", "compras": []}
    codigo = simpledialog.askstring("Compras", "Código del producto:")
    if not codigo:
        return
    if codigo in productos:
        # producto existente
        cantidad = pedir_int("Compras", "Cantidad comprada:", default=0)
        if cantidad is None:
            return
        costo = pedir_float("Compras", "Precio costo:", default=0)
        margen = pedir_float("Compras", "Margen % (sobre costo):", default=20)
        precio_venta = round(costo * (1 + (margen or 0)/100.0), 2)
        productos[codigo]["stock"] += cantidad
        productos[codigo]["precio"] = precio_venta
        compra = {"producto": codigo, "cantidad": cantidad, "precio_costo": costo, "precio_venta": precio_venta, "fecha": datetime.now().strftime("%Y-%m-%d")}
        proveedores[proveedor]["compras"].append(compra)
        messagebox.showinfo("Compras", f"Compra registrada. Stock {codigo}: {productos[codigo]['stock']}  Precio venta: {precio_venta}")
    else:
        # producto nuevo
        nombre = simpledialog.askstring("Compras", "Nombre del producto:")
        cantidad = pedir_int("Compras", "Cantidad comprada:", default=0)
        costo = pedir_float("Compras", "Precio costo:", default=0)
        margen = pedir_float("Compras", "Margen % (sobre costo):", default=20)
        precio_venta = round(costo * (1 + (margen or 0)/100.0), 2)
        # categoría (seleccionar o crear)
        cat = simpledialog.askstring("Compras", f"Categoría ({', '.join(categorias)}). Si no existe, se crea:") or "Sin categoría"
        if cat not in categorias:
            categorias.append(cat)
        productos[codigo] = {"nombre": nombre, "precio": precio_venta, "stock": cantidad, "vencimiento": "N/A", "categoria": cat, "sustitutos": [], "regalia_ok": False}
        compra = {"producto": codigo, "cantidad": cantidad, "precio_costo": costo, "precio_venta": precio_venta, "fecha": datetime.now().strftime("%Y-%m-%d")}
        proveedores[proveedor]["compras"].append(compra)
        messagebox.showinfo("Compras", f"Producto {nombre} creado y compra registrada.")

def inventario_menu():
    while True:
        accion = simpledialog.askstring("Inventario", "Acciones: ver / ajustar / auditoria / cambiar_categoria / regalias / salir")
        if not accion:
            return
        if accion == "salir":
            break
        elif accion == "ver":
            texto = ""
            for cod,p in productos.items():
                texto += f"{cod}: {p['nombre']}  Cat:{p['categoria']}  Stock:{p['stock']}  RegaliaOK:{p['regalia_ok']}\n"
            messagebox.showinfo("Inventario", texto or "Sin productos.")
        elif accion == "ajustar":
            cod = simpledialog.askstring("Ajustar", "Código:")
            if cod in productos:
                cant = pedir_int("Ajustar", "Cantidad (+ agrega / - descuenta):", default=0)
                if cant is not None:
                    productos[cod]["stock"] += cant
            else:
                messagebox.showerror("Ajustar", "Producto no existe.")
        elif accion == "auditoria":
            texto = ""
            for cod,p in productos.items():
                alerta = " ⚠️ Bajo" if p["stock"] <= 5 else ""
                texto += f"{cod}: {p['nombre']}  Stock:{p['stock']}{alerta}  Vence:{p['vencimiento']}\n"
            messagebox.showinfo("Auditoría", texto or "Sin datos.")
        elif accion == "cambiar_categoria":
            lista = simpledialog.askstring("Categoría", "Códigos separados por coma:")
            if not lista:
                continue
            nueva = simpledialog.askstring("Categoría", f"Nueva categoría ({', '.join(categorias)}). Si no existe se crea:")
            if not nueva:
                continue
            if nueva not in categorias:
                categorias.append(nueva)
            for c in [x.strip() for x in lista.split(",")]:
                if c in productos:
                    productos[c]["categoria"] = nueva
            messagebox.showinfo("Categoría", "Actualizada.")
        elif accion == "regalias":
            # marcar productos permitidos para regalías
            lista = simpledialog.askstring("Regalías", "Códigos a habilitar/deshabilitar (coma):")
            if not lista:
                continue
            valor = simpledialog.askstring("Regalías", "Escribir 'on' para habilitar, 'off' para deshabilitar:")
            if valor not in ("on","off"):
                messagebox.showerror("Regalías","Valor inválido.")
                continue
            flag = (valor == "on")
            for c in [x.strip() for x in lista.split(",")]:
                if c in productos:
                    productos[c]["regalia_ok"] = flag
            messagebox.showinfo("Regalías","Actualizado.")

# -------------------- Preventa --------------------
def seleccionar_vendedor():
    # permite escribir a mano (como el + de la imagen)
    vendedor = simpledialog.askstring("Vendedor", "Nombre del vendedor que atiende:")
    return vendedor

def seleccionar_tipo_documento(cliente_doc):
    # 1 Contado (default), 2 Crédito, 3 Regalías
    opciones = ["Factura de contado","Factura de crédito","Regalías"]
    root = tk.Toplevel()
    root.title("Tipo de documento")
    tk.Label(root, text="Selecciona tipo de documento:").pack(padx=10, pady=10)
    cb = ttk.Combobox(root, values=opciones, state="readonly")
    cb.current(0)
    cb.pack(padx=10, pady=5)
    info_lbl = tk.Label(root, text="", fg="blue")
    info_lbl.pack(pady=4)

    def on_change(event=None):
        sel = cb.get()
        if sel == "Factura de crédito":
            c = clientes.get(cliente_doc, {})
            lim = c.get("limite_credito", 0.0)
            usado = c.get("credito_usado", 0.0)
            disp = lim - usado
            info_lbl.config(text=f"Límite: {lim:.2f}   Usado: {usado:.2f}   Disponible: {disp:.2f}")
        else:
            info_lbl.config(text="")

    cb.bind("<<ComboboxSelected>>", on_change)

    elegido = {"val": None}
    def aceptar():
        elegido["val"] = cb.get()
        root.destroy()
    tk.Button(root, text="Aceptar", command=aceptar).pack(pady=8)
    on_change()
    root.grab_set()
    root.wait_window()
    return elegido["val"] or "Factura de contado"

def agregar_item_a_orden(orden):
    codigo = simpledialog.askstring("Artículo", "Código del producto (Enter para terminar):")
    if not codigo:
        return False
    if codigo not in productos:
        messagebox.showerror("Artículo", "No existe ese código.")
        return True
    p = productos[codigo]
    # validar regalías
    if orden["doc_type"] == "Regalías" and not p.get("regalia_ok", False):
        messagebox.showerror("Regalías", f"{p['nombre']} no está habilitado para regalías.")
        return True
    cantidad = pedir_int("Artículo", f"Cantidad de {p['nombre']}:", default=1)
    if cantidad is None:
        return True
    precio_unit = p["precio"]
    subtotal = round(cantidad * precio_unit, 2)
    orden["items"].append({"codigo": codigo, "nombre": p["nombre"], "cantidad": cantidad, "precio": precio_unit, "subtotal": subtotal})
    # stock se descuenta en preventa para reservar (puede quedar negativo)
    p["stock"] -= cantidad
    return True

def iniciar_preventa(usuario):
    cliente_doc = crear_o_elegir_cliente()
    if not cliente_doc:
        return
    # Si documento es regalías: cliente obligatorio (no CF)
    vendedor = seleccionar_vendedor()
    if not vendedor:
        messagebox.showerror("Vendedor", "Debe indicar quién atendió.")
        return
    doc_type = seleccionar_tipo_documento(cliente_doc)
    if doc_type == "Regalías" and client es_cf(cliente_doc):
        messagebox.showerror("Regalías", "Para regalías debe seleccionar un cliente identificado (no CF).")
        return
    # Construir orden
    orden = {
        "cliente_doc": cliente_doc,
        "cliente_nombre": clientes[cliente_doc]["nombre"],
        "vendedor": vendedor,
        "doc_type": doc_type,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": []
    }
    # Agregar artículos
    while True:
        if not agregar_item_a_orden(orden):
            break
    if not orden["items"]:
        messagebox.showinfo("Preventa", "Sin artículos.")
        return
    # Validación crédito
    if doc_type == "Factura de crédito":
        c = clientes[cliente_doc]
        lim = c.get("limite_credito", 0.0)
        usado = c.get("credito_usado", 0.0)
        total = sum(i["subtotal"] for i in orden["items"])
        if usado + total > lim + 1e-6:
            messagebox.showerror("Crédito", f"Excede el disponible. Disponible: {lim - usado:.2f}")
            # revertir stock
            for it in orden["items"]:
                productos[it["codigo"]]["stock"] += it["cantidad"]
            return
    preventas.append(orden)
    messagebox.showinfo("Preventa", f"Preventa creada para {orden['cliente_nombre']}.\nItems: {len(orden['items'])}")

def client es_cf(doc):
    return doc == "CF"

# -------------------- Caja --------------------
METODOS_PAGO = ["Efectivo","Tarjeta","Dólares","Transferencia"]

def listar_preventas():
    if not preventas:
        messagebox.showinfo("Caja","No hay preventas.")
        return None
    texto = ""
    for idx, o in enumerate(preventas, start=1):
        total = sum(i["subtotal"] for i in o["items"])
        texto += f"{idx}) {o['fecha']}  {o['cliente_nombre']}  Doc:{o['doc_type']}  Total:{total:.2f}\n"
    messagebox.showinfo("Preventas", texto)
    pos = pedir_int("Caja","Ingrese número de preventa a procesar:", default=1)
    if pos is None or pos<1 or pos>len(preventas):
        return None
    return preventas.pop(pos-1)

def finalizar_en_caja(usuario):
    orden = listar_preventas()
    if not orden:
        return
    incluir_dir = messagebox.askyesno("Factura","¿Imprimir con dirección del cliente? (por defecto NO)")
    metodo = simpledialog.askstring("Pago", f"Método de pago ({', '.join(METODOS_PAGO)}):")
    if metodo not in METODOS_PAGO:
        messagebox.showerror("Pago","Método inválido.")
        return
    total_lineas = sum(i["subtotal"] for i in orden["items"])
    total_caja = total_lineas
    if orden["doc_type"] == "Regalías":
        total_caja = 0.0  # no afecta caja
    # actualizar crédito si es crédito
    if orden["doc_type"] == "Factura de crédito":
        c = clientes[orden["cliente_doc"]]
        c["credito_usado"] += total_lineas
    # registrar venta
    venta = {
        "usuario_cajero": usuario,
        "vendedor": orden["vendedor"],
        "cliente_doc": orden["cliente_doc"],
        "cliente_nombre": orden["cliente_nombre"],
        "doc_type": orden["doc_type"],
        "pago": metodo,
        "total": total_lineas,
        "total_caja": total_caja,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": orden["items"],
        "incluir_dir": incluir_dir
    }
    ventas.append(venta)
    generar_factura_pdf(venta)
    messagebox.showinfo("Caja", f"Factura generada. Total mostrado: {total_lineas:.2f}. Total para caja: {total_caja:.2f}")

# -------------------- Factura PDF --------------------
def generar_factura_pdf(venta):
    carpeta = os.path.join(os.getcwd(), "facturas")
    os.makedirs(carpeta, exist_ok=True)
    nombre_arch = f"Factura_{venta['fecha'].replace(':','').replace(' ','_')}_{venta['cliente_doc']}.pdf"
    ruta = os.path.join(carpeta, nombre_arch)

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    c = canvas.Canvas(ruta, pagesize=letter)
    w, h = letter

    y = h - 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, nombre_farmacia); y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(30, y, f"Fecha: {venta['fecha']}"); y -= 12
    c.drawString(30, y, f"Cliente: {venta['cliente_nombre']}  (ID: {venta['cliente_doc']})"); y -= 12
    if venta["incluir_dir"]:
        dirc = clientes.get(venta["cliente_doc"],{}).get("direccion","")
        if dirc:
            c.drawString(30, y, f"Dirección: {dirc}"); y -= 12
    c.drawString(30, y, f"Vendedor: {venta['vendedor']}   Cajero: {venta['usuario_cajero']}"); y -= 12
    c.drawString(30, y, f"Tipo de documento: {venta['doc_type']}"); y -= 16

    c.setFont("Helvetica-Bold", 9)
    c.drawString(30, y, "Código"); c.drawString(100, y, "Descripción"); c.drawString(320, y, "Cant"); c.drawString(360, y, "P.Unit"); c.drawString(430, y, "Subtotal"); y -= 12
    c.setFont("Helvetica", 9)

    for it in venta["items"]:
        c.drawString(30, y, it["codigo"])
        c.drawString(100, y, it["nombre"][:35])
        c.drawRightString(350, y, str(it["cantidad"]))
        c.drawRightString(420, y, f"{it['precio']:.2f}")
        c.drawRightString(500, y, f"{it['subtotal']:.2f}")
        y -= 12
        if y < 80:
            c.showPage(); y = h - 40

    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(500, y-10, f"Total mostrado: {venta['total']:.2f}")
    c.drawRightString(500, y-25, f"Total caja: {venta['total_caja']:.2f}")
    c.setFont("Helvetica", 9)
    c.drawString(30, 40, "*** Gracias por su preferencia ***")
    c.save()
    # informar ubicación
    messagebox.showinfo("PDF", f"Factura guardada en:\n{ruta}")

# -------------------- Reportes simples --------------------
def reporte_ventas():
    if not ventas:
        messagebox.showinfo("Reporte", "Sin ventas.")
        return
    texto = ""
    suma_caja = 0.0
    for i,v in enumerate(ventas, start=1):
        texto += f"{i}) {v['fecha']} Doc:{v['doc_type']} Cliente:{v['cliente_nombre']} Pago:{v['pago']} Total:{v['total']:.2f} Caja:{v['total_caja']:.2f}\n"
        suma_caja += v["total_caja"]
    texto += f"\nTotal para caja (acumulado): {suma_caja:.2f}"
    messagebox.showinfo("Reporte de ventas", texto)

# -------------------- GUI principal --------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title(nombre_farmacia)
        self.usuario = None
        self.rol = None
        self._login()

    def _login(self):
        for w in self.root.winfo_children():
            w.destroy()
        frm = tk.Frame(self.root, bg="#e8f2ff", padx=16, pady=16)
        frm.pack(fill="both", expand=True)
        tk.Label(frm, text="Usuario").grid(row=0, column=0, sticky="w")
        self.e_user = tk.Entry(frm); self.e_user.grid(row=0, column=1, sticky="ew")
        tk.Label(frm, text="Contraseña").grid(row=1, column=0, sticky="w")
        self.e_pass = tk.Entry(frm, show="*"); self.e_pass.grid(row=1, column=1, sticky="ew")
        tk.Button(frm, text="Ingresar", command=self._do_login).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        frm.columnconfigure(1, weight=1)

    def _do_login(self):
        u = self.e_user.get().strip()
        p = self.e_pass.get().strip()
        rol = login(u,p)
        if not rol:
            messagebox.showerror("Login","Usuario/clave inválidos.")
            return
        self.usuario, self.rol = u, rol
        self._menu()

    def _menu(self):
        for w in self.root.winfo_children():
            w.destroy()
        hdr = tk.Label(self.root, text=f"{nombre_farmacia}  |  Sesión: {self.usuario} ({self.rol})", bg="#cfe8ff", fg="#002b55", font=("Segoe UI", 12, "bold"))
        hdr.pack(fill="x")
        cont = tk.Frame(self.root, padx=12, pady=12); cont.pack(fill="both", expand=True)

        tk.Button(cont, text="Preventa", command=lambda: iniciar_preventa(self.usuario), width=30).grid(row=0, column=0, pady=4, sticky="w")
        tk.Button(cont, text="Caja (finalizar facturas)", command=lambda: finalizar_en_caja(self.usuario), width=30).grid(row=1, column=0, pady=4, sticky="w")
        tk.Button(cont, text="Compras / Ingreso de productos", command=registrar_compra, width=30).grid(row=2, column=0, pady=4, sticky="w")
        tk.Button(cont, text="Inventario / Auditoría", command=inventario_menu, width=30).grid(row=3, column=0, pady=4, sticky="w")
        tk.Button(cont, text="Reporte de ventas", command=reporte_ventas, width=30).grid(row=4, column=0, pady=4, sticky="w")

        if self.rol == "admin":
            tk.Button(cont, text="Crear usuario", command=self._crear_usuario, width=30).grid(row=5, column=0, pady=4, sticky="w")
            tk.Button(cont, text="Cambiar nombre de la farmacia", command=self._cambiar_nombre, width=30).grid(row=6, column=0, pady=4, sticky="w")

        tk.Button(cont, text="Salir", command=self.root.destroy, width=30, bg="#ff4d4d", fg="white").grid(row=7, column=0, pady=12, sticky="w")

    def _crear_usuario(self):
        nombre = simpledialog.askstring("Usuario", "Nombre de usuario:")
        if not nombre:
            return
        if nombre in usuarios:
            messagebox.showerror("Usuario","Ya existe.")
            return
        clave = simpledialog.askstring("Usuario", "Contraseña:")
        rol = simpledialog.askstring("Usuario", "Rol (admin/preventa):", initialvalue="preventa")
        if rol not in ("admin","preventa"):
            messagebox.showerror("Usuario","Rol inválido.")
            return
        usuarios[nombre] = {"password": clave or "1234", "rol": rol}
        messagebox.showinfo("Usuario","Creado.")

    def _cambiar_nombre(self):
        global nombre_farmacia
        nv = simpledialog.askstring("Farmacia","Nombre visible de la farmacia:", initialvalue=nombre_farmacia)
        if nv:
            nombre_farmacia = nv
            self.root.title(nombre_farmacia)
            messagebox.showinfo("Farmacia","Actualizado.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("520x420")
    App(root)
    root.mainloop()
