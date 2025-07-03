import tkinter as tk
from tkinter import messagebox, PhotoImage
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
import uuid

# ===== CONFIGURACIÓN GENERAL =====
COLOR_TEXTO = "#000000"
COLOR_BOTON_PRINCIPAL = "#D10000"
COLOR_BOTON_SECUNDARIO = "#333333"
FUENTE_TITULO = ("Arial", 18, "bold")
FUENTE_NORMAL = ("Arial", 12)
LOGO_PATH = "logo.png"
FONDO_PATH = "fondo_degradado.png"

# ===== DATOS USUARIO =====
datos_usuario = {
    "usuario": "usuario1",
    "contraseña": "contra123",
    "saldo": 100000,
    "saldo_dolar": 500
}
intentos_fallidos = 0

def autenticar():
    global intentos_fallidos
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    if usuario == datos_usuario["usuario"] and contraseña == datos_usuario["contraseña"]:
        messagebox.showinfo("Acceso", "Acceso concedido.")
        mostrar_menu()
    else:
        intentos_fallidos += 1
        if intentos_fallidos >= 3:
            messagebox.showerror("Bloqueado", "Su usuario ha sido bloqueado.")
            root.destroy()
        else:
            messagebox.showerror("Error", f"Intento {intentos_fallidos} de 3.")

def mostrar_menu():
    for widget in root.winfo_children():
        widget.destroy()
    fondo_label = tk.Label(root, image=fondo_img)
    fondo_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(root, image=logo_img, bg=None).pack(pady=10)
    tk.Label(root, text="Menú de Operaciones", font=FUENTE_TITULO, bg=None, fg=COLOR_TEXTO).pack(pady=10)
    tk.Label(root, text=f"Saldo actual: ${datos_usuario['saldo']}", font=FUENTE_NORMAL, bg=None, fg=COLOR_TEXTO).pack(pady=5)
    tk.Label(root, text=f"Saldo dólar actual: ${datos_usuario['saldo_dolar']}", font=FUENTE_NORMAL, bg=None, fg=COLOR_TEXTO).pack(pady=5)

    tk.Button(root, text="Depositar Dinero", width=25, command=depositar, bg=COLOR_BOTON_PRINCIPAL, fg="white", font=FUENTE_NORMAL).pack(pady=10)
    tk.Button(root, text="Transferencia", width=25, command=transferir, bg=COLOR_BOTON_PRINCIPAL, fg="white", font=FUENTE_NORMAL).pack(pady=10)
    tk.Button(root, text="Comprar Dólares", width=25, command=comprar_dolares, bg=COLOR_BOTON_PRINCIPAL, fg="white", font=FUENTE_NORMAL).pack(pady=10)
    tk.Button(root, text="Vender Dólares", width=25, command=vender_dolar, bg=COLOR_BOTON_PRINCIPAL, fg="white", font=FUENTE_NORMAL).pack(pady=10)
    tk.Button(root, text="Salir", width=25, command=root.destroy, bg=COLOR_BOTON_SECUNDARIO, fg="white", font=FUENTE_NORMAL).pack(pady=10)

def agregar_logo_ventana(ventana):
    logo_pequeño = tk.Label(ventana, image=logo_img, bg="white")
    logo_pequeño.image = logo_img
    logo_pequeño.place(x=230, y=5)

def depositar():
    def realizar_deposito():
        try:
            monto = float(entry_monto.get())
            if monto > 0:
                datos_usuario["saldo"] += monto
                messagebox.showinfo("Éxito", f"Depósito exitoso. Nuevo saldo: ${datos_usuario['saldo']}")
                ventana.destroy()
                mostrar_menu()
            else:
                messagebox.showerror("Error", "Ingrese un monto válido.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido.")

    ventana = tk.Toplevel(root)
    ventana.title("Depositar Dinero")
    ventana.geometry("300x150")
    ventana.configure(bg="white")
    agregar_logo_ventana(ventana)
    tk.Label(ventana, text="Monto a depositar:", bg="white", fg=COLOR_TEXTO).pack(pady=5)
    entry_monto = tk.Entry(ventana)
    entry_monto.pack(pady=5)
    tk.Button(ventana, text="Depositar", command=realizar_deposito, bg=COLOR_BOTON_PRINCIPAL, fg="white").pack(pady=10)

def transferir():
    def realizar_transferencia():
        try:
            monto = float(entry_monto.get())
            cuenta = entry_cuenta.get()
            if not cuenta:
                messagebox.showerror("Error", "Ingrese una cuenta de destino.")
                return
            if monto > 0 and monto <= datos_usuario["saldo"]:
                datos_usuario["saldo"] -= monto
                now = datetime.now()
                fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
                respuesta = messagebox.askyesno("Guardar comprobante", "¿Desea guardar un comprobante en PDF?")
                if respuesta:
                    guardar_comprobante_pdf(cuenta, monto, fecha_hora)
                messagebox.showinfo("Éxito", f"Transferencia de ${monto} a {cuenta} realizada.")
                ventana.destroy()
                mostrar_menu()
            else:
                messagebox.showerror("Error", "Monto inválido o fondos insuficientes.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese datos válidos.")

    ventana = tk.Toplevel(root)
    ventana.title("Transferencia")
    ventana.geometry("300x200")
    ventana.configure(bg="white")
    agregar_logo_ventana(ventana)
    tk.Label(ventana, text="Cuenta de destino (alias):", bg="white", fg=COLOR_TEXTO).pack(pady=5)
    entry_cuenta = tk.Entry(ventana)
    entry_cuenta.pack(pady=5)
    tk.Label(ventana, text="Monto a transferir:", bg="white", fg=COLOR_TEXTO).pack(pady=5)
    entry_monto = tk.Entry(ventana)
    entry_monto.pack(pady=5)
    tk.Button(ventana, text="Transferir", command=realizar_transferencia, bg=COLOR_BOTON_PRINCIPAL, fg="white").pack(pady=10)

def guardar_comprobante_pdf(alias_destino, monto, fecha_hora):
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    nombre_archivo = f"comprobante_transferencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta_pdf = os.path.join(escritorio, nombre_archivo)
    id_comprobante = str(uuid.uuid4())[:8].upper()

    c = canvas.Canvas(ruta_pdf)
    try:
        c.drawImage(ImageReader(LOGO_PATH), 400, 750, width=150, preserveAspectRatio=True, mask='auto')
    except:
        pass
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 780, "Comprobante de Transferencia")
    c.setFont("Helvetica", 12)
    c.drawString(50, 740, f"Alias/Cuenta de destino: {alias_destino}")
    c.drawString(50, 720, f"Monto transferido: ${monto:.2f}")
    c.drawString(50, 700, f"Fecha y hora: {fecha_hora}")
    c.drawString(50, 680, f"ID del comprobante: {id_comprobante}")
    c.save()

def comprar_dolares():
    def realizar_compra():
        try:
            tasa_dolar = 1000
            cantidad_usd = float(entry_dolares.get())
            costo_total = cantidad_usd * tasa_dolar
            if cantidad_usd <= 0:
                messagebox.showerror("Error", "Ingrese una cantidad válida.")
                return
            if datos_usuario["saldo"] >= costo_total:
                datos_usuario["saldo"] -= costo_total
                datos_usuario["saldo_dolar"] += cantidad_usd
                messagebox.showinfo("Éxito", f"Compra exitosa. Compraste {cantidad_usd} USD por ${costo_total}.")
                ventana.destroy()
                mostrar_menu()
            else:
                messagebox.showerror("Error", "Fondos insuficientes.")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido.")

    ventana = tk.Toplevel(root)
    ventana.title("Comprar dólares")
    ventana.geometry("300x150")
    ventana.configure(bg="white")
    agregar_logo_ventana(ventana)
    tk.Label(ventana, text="Cantidad de USD a comprar:", bg="white", fg=COLOR_TEXTO).pack(pady=5)
    entry_dolares = tk.Entry(ventana)
    entry_dolares.pack(pady=5)
    tk.Button(ventana, text="Comprar", command=realizar_compra, bg=COLOR_BOTON_PRINCIPAL, fg="white").pack(pady=10)

def vender_dolar():
    def venta():
        try:
            tasa_dolar = 1000
            cant_dolar = float(entry_dolares.get())
            costo_total = cant_dolar * tasa_dolar
            if cant_dolar <= 0:
                messagebox.showerror("Error", "Ingrese un monto válido.")
                return
            if datos_usuario["saldo_dolar"] >= cant_dolar:
                datos_usuario["saldo_dolar"] -= cant_dolar
                datos_usuario["saldo"] += costo_total
                messagebox.showinfo("Éxito", f"Venta exitosa. Vendiste {cant_dolar} USD por ${costo_total}.")
                ventana.destroy()
                mostrar_menu()
            else:
                messagebox.showerror("Error", "Montos insuficientes")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")

    ventana = tk.Toplevel(root)
    ventana.title("Vender dólares")
    ventana.geometry("300x150")
    ventana.configure(bg="white")
    agregar_logo_ventana(ventana)
    tk.Label(ventana, text="Cantidad de USD a vender:", bg="white", fg=COLOR_TEXTO).pack(pady=5)
    entry_dolares = tk.Entry(ventana)
    entry_dolares.pack(pady=5)
    tk.Button(ventana, text="Vender", command=venta, bg=COLOR_BOTON_PRINCIPAL, fg="white").pack(pady=10)

# ===== VENTANA INICIO =====
root = tk.Tk()
root.title("Sistema de Operaciones Bancarias")
root.geometry("1200x600")
root.resizable(False, False)

# Fondo degradado
fondo_img_raw = Image.open(FONDO_PATH)
fondo_img = ImageTk.PhotoImage(fondo_img_raw)

# Logo
logo_img = PhotoImage(file=LOGO_PATH)

fondo_label = tk.Label(root, image=fondo_img)
fondo_label.place(relx=0, rely=0, relwidth=1, relheight=1)

tk.Label(root, text="¡Bienvenido!", font=FUENTE_TITULO, bg=None, fg=COLOR_TEXTO).pack(pady=20)
tk.Label(root, text="Usuario:", bg=None, fg=COLOR_TEXTO, font=FUENTE_NORMAL).pack()
entry_usuario = tk.Entry(root)
entry_usuario.pack(pady=5)

tk.Label(root, text="Contraseña:", bg=None, fg=COLOR_TEXTO, font=FUENTE_NORMAL).pack()
entry_contraseña = tk.Entry(root, show="*")
entry_contraseña.pack(pady=5)

tk.Button(root, text="Iniciar sesión", command=autenticar, bg=COLOR_BOTON_PRINCIPAL, fg="white", font=FUENTE_NORMAL).pack(pady=20)

root.mainloop()
