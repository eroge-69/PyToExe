import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
import time
import datetime
from PIL import Image, ImageTk
from tkinter import filedialog
import tkinter.messagebox as messagebox
import caja
import qrcode
import serial
import uuid


conn = sqlite3.connect('almacen.db')
cursor = conn.cursor()
cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        hora TEXT,
        codigo_qr TEXT,
        tipo_documento TEXT,
        precio REAL
    )
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        precio REAL,
        descripcion TEXT,
        imagen TEXT
    )
""")

cursor.execute(""" CREATE TABLE IF NOT EXISTS configuracion (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    valor TEXT
) """)

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS caja (
        id INTEGER PRIMARY KEY,
        fecha DATE,
        estado TEXT
    ) 
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS familias (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS familia_producto (
    familia_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    FOREIGN KEY (familia_id) REFERENCES familias (id),
    FOREIGN KEY (producto_id) REFERENCES productos (id)
)
""")

conn.commit()
conn.close()



class TpvBar:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("TpvBar                                                KINGDOMBEAR(R)")
        self.ventana.geometry("1920x1080")
        self.label_importe = None
        self.ticket_text = ""
        self.total = 0
        self.total_varios = 0
        self.nombre_empresa = ""
        self.nif_empresa = ""
        self.direccion_empresa = ""
        self.telefono_empresa = ""
        self.correo_empresa = ""
        self.conn = sqlite3.connect("almacen.db")
        self.cursor = self.conn.cursor()
        self.crear_tablas()
        self.lista_familias = tk.Listbox(self.ventana)
        self.lista_familias.pack()
        self.actualizar_lista_familias()
        
        
        
        

        # IMÁGENES DE BUTTONS #

        imagen_salir = Image.open("Imágenes de diseño/Buttons/Buttons/Salir.png")
        imagen_salir = imagen_salir.resize((90, 90))
        imagen_salir_tk = ImageTk.PhotoImage(imagen_salir)
        imagen_inventario = Image.open("Imágenes de diseño/Buttons/Buttons/Inventario.png")
        imagen_inventario = imagen_inventario.resize((90, 90))
        imagen_inventario_tk = ImageTk.PhotoImage(imagen_inventario)
        imagen_personal = Image.open("Imágenes de diseño/Buttons/Buttons/Personal.png")
        imagen_personal = imagen_personal.resize((90,90))
        imagen_personal_tk = ImageTk.PhotoImage(imagen_personal)
        imagen_caja = Image.open("Imágenes de diseño/Buttons/Buttons/Caja.png")
        imagen_caja = imagen_caja.resize((90,90))
        imagen_caja_tk = ImageTk.PhotoImage(imagen_caja)
        imagen_venta = Image.open("Imágenes de diseño/Buttons/Buttons/Venta.png")
        imagen_venta = imagen_venta.resize((90,90))
        imagen_venta_tk = ImageTk.PhotoImage(imagen_venta)
        imagen_familias = Image.open("Imágenes de diseño/Buttons/Buttons/Familias.png")
        imagen_familias = imagen_familias.resize((90,90))
        imagen_familias_tk = ImageTk.PhotoImage(imagen_familias)
        imagen_config = Image.open("Imágenes de diseño/Buttons/Buttons/Config.png")
        imagen_config = imagen_config.resize((90,90))
        imagen_config_tk = ImageTk.PhotoImage(imagen_config)
        imagen_pagado = Image.open("Imágenes de diseño/Buttons/Buttons/Pagado.png")
        imagen_pagado = imagen_pagado.resize((65, 65))
        imagen_pagado_tk = ImageTk.PhotoImage(imagen_pagado)
        imagen_terraza = Image.open("Imágenes de diseño/Buttons/Buttons/Terraza.png")
        imagen_terraza = imagen_terraza.resize((90, 90))
        imagen_terraza_tk = ImageTk.PhotoImage(imagen_terraza)
        imagen_barra = Image.open("Imágenes de diseño/Buttons/Buttons/Barra.png")
        imagen_barra = imagen_barra.resize((90, 90))
        imagen_barra_tk = ImageTk.PhotoImage(imagen_barra)
        imagen_ON = Image.open("Imágenes de diseño/Buttons/Buttons/ON.png")
        imagen_ON = imagen_ON.resize((90, 90))
        imagen_ON_tk = ImageTk.PhotoImage(imagen_ON)
        imagen_logo = Image.open("Imágenes de diseño/Koffeeapp_Logo.jpg")
        imagen_logo = imagen_logo.resize((400, 400))
        imagen_logo_tk = ImageTk.PhotoImage(imagen_logo)

        # CAMBIO DE IMÁGENES #

        imagen_verde = Image.open("Imágenes de diseño/semáforo/Semáforo/luz_verde_!.png")
        imagen_verde = imagen_verde.resize((50, 70))
        imagen_rojo = Image.open("Imágenes de diseño/semáforo/Semáforo/luz_roja_1.png")
        imagen_rojo = imagen_rojo.resize((50, 70))

        self.imagen_verde = ImageTk.PhotoImage(imagen_verde)
        self.imagen_rojo = ImageTk.PhotoImage(imagen_rojo)
        self.estado_label = tk.Label(self.ventana, image=self.imagen_verde)

        # DIVIDIMOS LA INTERFAZ EN 2
        self.frame_izquierdo_superior = tk.Frame(self.ventana, bg="black")
        self.frame_izquierdo_inferior = tk.Frame(self.ventana, bg="darkblue")
        self.frame_izquierdo_inferior.pack()
        for i in range(7):
            self.frame_izquierdo_inferior.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.frame_izquierdo_inferior.grid_columnconfigure(i, weight=1)

        self.frame_derecho_superior = tk.Frame(self.ventana, bg="white")
        self.frame_derecho_inferior = tk.Frame(self.ventana, bg="black")

        # COLOCAR LOS FRAMES
        self.frame_izquierdo_superior.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)
        self.frame_izquierdo_inferior.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)
        self.frame_derecho_superior.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.5)
        self.frame_derecho_inferior.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)

        # COLOCAR TICKET #

        self.ticket_label = tk.Label(self.frame_derecho_superior, bg="white")
        self.label_ventas = tk.Label(self.frame_derecho_superior, bg="white", font=(None, 16))
        self.label_ventas.place(relx=0.01, rely=0.1)
        self.ticket_label.place(relx=0.5, rely=0.1)
       
        
        
        
        

        # COLOCAR LOS BUTTONS  PANEL IZQUIERDO SUPERIOR#

        self.btn_salir = tk.Button(self.frame_izquierdo_superior, image= imagen_salir_tk, command=self.salir_app, bd=5, relief="raised")
        self.btn_salir.image = imagen_salir_tk
        self.btn_salir.place(relx=0, rely=0, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_inventario = tk.Button(self.frame_izquierdo_superior, image= imagen_inventario_tk, command=self.ventana_inventario, bd=5, relief="raised")
        self.btn_inventario.image = imagen_inventario_tk
        self.btn_inventario.place(relx=0, rely=0.2, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_personal = tk.Button(self.frame_izquierdo_superior, image= imagen_personal_tk, command=self.mostrar_personal,bd=5, relief="raised")
        self.btn_personal.image = imagen_personal_tk
        self.btn_personal.place(relx=0, rely=0.4, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_caja = tk.Button(self.frame_izquierdo_superior, image= imagen_caja_tk, command=self.mostrar_caja, bd=5, relief="raised")
        self.btn_caja.image = imagen_caja_tk
        self.btn_caja.place(relx=0, rely=0.6, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_venta = tk.Button(self.frame_izquierdo_superior, image= imagen_venta_tk, command=self.resumen_ventas, bd=5, relief="raised")
        self.btn_venta.image = imagen_venta_tk
        self.btn_venta.place(relx=0, rely=0.8, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_familias = tk.Button(self.frame_izquierdo_superior, image= imagen_familias_tk, command=self.mostrar_familias, bd=5, relief="raised")
        self.btn_familias.image = imagen_familias_tk
        self.btn_familias.place(relx=0.1, rely=0, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_config = tk.Button(self.frame_izquierdo_superior, image= imagen_config_tk, command=self.mostrar_config, bd=5, relief="raised")
        self.btn_config.image = imagen_config_tk
        self.btn_config.place(relx=0.1, rely=0.2, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_terraza = tk.Button(self.frame_izquierdo_superior, image= imagen_terraza_tk, bd=5, relief="raised",command=self.mostrar_terraza)
        self.btn_terraza.image = imagen_terraza_tk
        self.btn_terraza.place(relx=0.1, rely=0.4, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_barra = tk.Button(self.frame_izquierdo_superior, image= imagen_barra_tk, command=self.mostrar_barra, bd=5, relief="raised")
        self.btn_barra.image = imagen_barra_tk
        self.btn_barra.place(relx=0.1, rely=0.6, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_abrir_caja = tk.Button(self.frame_izquierdo_superior, image= imagen_ON_tk, command=self.abrir_caja, bd=5, relief="raised")
        self.btn_abrir_caja.image = imagen_ON_tk
        self.btn_abrir_caja.place(relx=0.1, rely=0.8, relwidth=0.1, relheight=0.2, anchor=tk.NW)

        self.btn_logo = tk.Button(self.frame_izquierdo_superior, image= imagen_logo_tk, command=self.mostrar_logo, bg="white", bd=2, relief="raised")
        self.btn_logo.image = imagen_logo_tk
        self.btn_logo.place(relx=0.35, rely=0.2, relwidth=0.4, relheight=0.6, anchor=tk.NW)

 

        # COLOCAR LOS BUTTONS  PANEL DERECHO #

        self.btn_pagado = tk.Button(self.frame_derecho_superior, image= imagen_pagado_tk, bd=3, relief="raised", command=self.mostrar_pagado)
        self.btn_pagado.image = imagen_pagado_tk
        self.btn_pagado.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        self.label_codigo_qr = tk.Label(self.frame_derecho_superior, image=None)
        self.label_codigo_qr.pack()
        

        # CAJA REGISTRADORA #

        self.txt_resultado = tk.Text(self.frame_derecho_superior)
        self.txt_resultado.place(relx=0, rely=0, width=1, height=1)


        # BOTONES PANEL DERECHO INFERIOR #

        imagen_aper_caja = Image.open("Imágenes de diseño/Buttons/Buttons/Apertura_caja.png")
        imagen_aper_caja = imagen_aper_caja.resize((270, 270))
        imagen_aper_caja_tk = ImageTk.PhotoImage(imagen_aper_caja)

        self.btn_aper_caja = tk.Button(self.frame_derecho_inferior, image= imagen_aper_caja_tk, command=self.apertura_caja, bd=5, relief="raised")
        self.btn_aper_caja.image = imagen_aper_caja_tk
        self.btn_aper_caja.place(relx=0.02, rely=0, relwidth=0.3, relheight=0.5, anchor=tk.NW)

        imagen_tarjeta = Image.open("Imágenes de diseño/Buttons/Buttons/Pago_Tarjeta.png")
        imagen_tarjeta = imagen_tarjeta.resize((270, 270))
        imagen_tarjeta_tk = ImageTk.PhotoImage(imagen_tarjeta)

        self.btn_tarjeta= tk.Button(self.frame_derecho_inferior, image= imagen_tarjeta_tk, command=self.apertura_caja, bd=5, relief="raised")
        self.btn_tarjeta.image = imagen_tarjeta_tk
        self.btn_tarjeta.place(relx=0.35, rely=0, relwidth=0.3, relheight=0.5, anchor=tk.NW)

        imagen_bizzum = Image.open("Imágenes de diseño/Buttons/Buttons/Pago_Bizum.png")
        imagen_bizzum = imagen_bizzum.resize((270, 270))
        imagen_bizzum_tk = ImageTk.PhotoImage(imagen_bizzum)

        self.btn_bizzum= tk.Button(self.frame_derecho_inferior, image= imagen_bizzum_tk, command=self.apertura_caja, bd=5, relief="raised")
        self.btn_bizzum.image = imagen_bizzum_tk
        self.btn_bizzum.place(relx=0.68, rely=0, relwidth=0.3, relheight=0.5, anchor=tk.NW)

      

        # INDICADOR DE CONEXIÓN A BASE DE DATOS #

        self.estado_label = tk.Label(self.frame_derecho_superior, image=self.imagen_verde)
        self.estado_label.image = self.imagen_verde  # Esto es importante para evitar que la imagen se borre
        self.estado_label.place(relx=1, rely=0, anchor=tk.NE)
        self.label_codigo_qr = tk.Label(self.frame_derecho_superior)
        self.label_codigo_qr.place(relx=0.8, rely=0.9, anchor=tk.SE)

        # RELOJ #

        self.reloj_label = tk.Label(self.frame_derecho_superior, font=(None, 80), bg="white", fg="black")
        self.reloj_label.place(relx=0.68, rely=0.05, relwidth=0.25, relheight=0.15, anchor=tk.NW)
        self.actualizar_reloj()

    
    def crear_tablas(self):
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS familias (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL
            )""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS familia_producto (
                familia_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                FOREIGN KEY (familia_id) REFERENCES familias (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )""")
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror(f"Error al crear la tabla: {e}")

    def abrir_caja(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM caja WHERE fecha = ?", (fecha_actual,))
        caja = cursor.fetchone()
        if caja is None:
            cursor.execute("INSERT INTO caja (fecha, estado) VALUES (?, 'abierta')", (fecha_actual,))
            conn.commit()
            messagebox.showinfo("Caja abierta", "La caja ha sido abierta correctamente")
        elif caja[2] == "abierta":
            messagebox.showerror("Caja ya abierta", "La caja ya está abierta")
        else:
            cursor.execute("UPDATE caja SET estado = 'abierta' WHERE fecha = ?", (fecha_actual,))
            conn.commit()
            messagebox.showinfo("Caja abierta", "La caja ha sido abierta correctamente")
        conn.close()

    def mostrar_logo(self):
        pass
        
    def apertura_caja(self):
        try:
            ser = serial.Serial('COM1', 9600, timeout=1) #ajusta el puerto y la velocidad de baudios
            comando = b'\x1B\x70\x00\x1E\x00' # comando específico del periférico de la caja
            ser.write(comando)
            ser.close
        except serial.SerialException as e:
            messagebox.showerror(f"Error al abrir la caja: {e}")
        

    def actualizar_reloj(self):
        fecha_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        self.reloj_label.config(text=fecha_hora, font=(None, 12))
        self.frame_derecho_superior.after(1000, self.actualizar_reloj)


        imagen_verde = Image.open("Imágenes de diseño/semáforo/Semáforo/luz_verde_!.png")
        imagen_verde = imagen_verde.resize((50, 70))
        imagen_rojo = Image.open("Imágenes de diseño/semáforo/Semáforo/luz_roja_1.png")
        imagen_rojo = imagen_rojo.resize((50, 70))

        self.imagen_verde = ImageTk.PhotoImage(imagen_verde)
        self.imagen_rojo = ImageTk.PhotoImage(imagen_rojo)
        self.estado_label = tk.Label(self.ventana, image=self.imagen_verde)

    def ventana_inventario(self):
        ventana_inventario = tk.Toplevel(self.ventana)
        ventana_inventario.title("Inventario")
        ventana_inventario.geometry("800x600")
        self.conn = sqlite3.connect('almacen.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT nombre, precio, imagen FROM productos")
        self.productos = self.cursor.fetchall()
        self.frame_botones = tk.Frame(ventana_inventario)
        self.frame_botones.pack(side=tk.LEFT, padx=10, pady=0)
        self.btn_agregar = tk.Button(self.frame_botones, text="Agregar producto", command=self.agregar_producto)
        self.btn_agregar.pack(fill=tk.X, pady=5)
        self.btn_buscar = tk.Button(self.frame_botones, text="Buscar producto", command=self.buscar_producto)
        self.btn_buscar.pack(fill=tk.X, pady=5)
        self.frame_productos = tk.Frame(ventana_inventario)
        self.frame_productos.pack(padx=10, pady=10, fill="both", expand=True)
        self.mostrar_inventario()

    def leer_base_de_datos(self):
        conn = sqlite3.connect('almacen.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        rows = cursor.fetchall()
        texto = ''
        for row in rows:
            texto += f"ID: {row[0]}, Nombre: {row[1]}, Precio: {row[2]}, Imagen: {row[3]}\n"
        self.txt_resultado.delete('1.0', tk.END)
        self.txt_resultado.insert(tk.END, texto)
        conn.close()

    def agregar_producto_al_ticket(self, producto):
        if not hasattr(self, 'ticket_text'):
            self.ticket_text = ""
        self.ticket_text += f"{producto[1]} - €{producto[2]:.2f}\n"
        self.total += float(producto[2])
        texto = self.ticket_text
        if hasattr(self, 'total_varios') and self.total_varios > 0:
            texto += f"Varios: {self.total_varios:.2f} €\n"
        total = self.total + getattr(self, 'total_varios', 0)
        importe_sin_iva, importe_iva = self.calcular_importes(total)
        texto += f"Base imponible: {importe_sin_iva:.2f} €\n"
        texto += f"IVA ({self.obtener_iva()}%): {importe_iva:.2f} €\n"
        texto += f"Total: {total:.2f} €"
        self.label_ventas.config(text=texto)
        texto_qr = f"Ticket {self.ticket_text} - Total: {total:.2f} €"
        self.generar_codigo_qr(texto_qr)
        img = Image.open("codigo_qr.png")
        img_tk = ImageTk.PhotoImage(img)
        self.label_codigo_qr.config(image=img_tk)
        self.label_codigo_qr.image = img_tk

    def resetear_ticket(self):
        self.ticket_text = ""
        self.total = 0
        self.total_varios = 0
        self.label_ventas.config(text="")
        self.label_codigo_qr.config(image="")
        
        
        

    def generar_codigo_qr(self, texto_qr):
        # Generar el código QR solo una vez
        if not hasattr(self, 'codigo_qr_generado'):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(texto_qr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((75, 75))  # Cambia el tamaño a 200x200 píxeles
            img.save("codigo_qr.png")
            self.codigo_qr_generado = True
        else:
            # Actualizar el código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=4,
            )
            qr.add_data(texto_qr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((75, 75))  # Cambia el tamaño a 200x200 píxeles
            img.save("codigo_qr.png")


    def imprimir_ventas(self, mensaje=None):
        if mensaje:
            if not hasattr(self, 'total_varios'):
                self.total_varios = 0
            self.total_varios += float(mensaje)
        texto = ""
        if hasattr(self, 'ticket_text'):
            texto += self.ticket_text
        total = getattr(self, 'total', 0)
        if hasattr(self, 'total_varios') and self.total_varios > 0:
            texto += f"Varios: {self.total_varios:.2f} €\n"
            total += self.total_varios
        importe_sin_iva, importe_iva = self.calcular_importes(total)
        texto += f"Base imponible: {importe_sin_iva:.2f} €\n"
        texto += f"IVA ({self.obtener_iva()}%): {importe_iva:.2f} €\n"
        texto += f"Total: {total:.2f} €"
        self.label_ventas.config(text=texto)
        ticket_text = getattr(self, 'ticket_text', '')
        if ticket_text:
            texto_qr = f"Ticket {ticket_text.splitlines()[0]} - Total: {total:.2f} €"
        else:
            texto_qr = f"Ticket - Total: {total:.2f} €"
        self.generar_codigo_qr(texto_qr)
        img = Image.open("codigo_qr.png")
        img_tk = ImageTk.PhotoImage(img)
        self.label_codigo_qr.config(image=img_tk)
        self.label_codigo_qr.image = img_tk
        self.mostrar_datos_empresa()
        self.cargar_datos_empresa()

    
    def calcular_importes(self, total):
        iva = self.obtener_iva()
        if iva is None:
            messagebox.showerror("Error", "El IVA no está configurado. Por favor, configure el IVA antes de continuar.")
            return None
        iva = float(iva)
        importe_sin_iva = total / (1 + iva/100)
        importe_iva = total - importe_sin_iva
        return importe_sin_iva, importe_iva

    def cargar_productos(self):
        # Destruye cualquier widget existente en el frame de productos
        for widget in self.frame_productos.winfo_children():
            widget.destroy()

        # Conecta a la base de datos y carga los productos
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conn.close()

        # Crea una lista de productos en la interfaz gráfica
        for producto in productos:
            label = tk.Label(self.frame_productos, text=f"{producto[1]} - {producto[2]}")
            label.pack()
    
    

    def actualizar(self):
        try:
            self.estado_label.config(image=self.imagen_verde)
            self.leer_base_de_datos()
        except Exception as e:
            messagebox.showerror(f"Error: {e}")
            self.estado_label.config(image=self.imagen_rojo)
            self.estado_label.image = self.imagen_rojo
            messagebox.showerror("Error", "Error al leer la base de datos")

        finally:
            self.ventana.after(1000, lambda: self.actualizar())

    
    def mostrar_inventario(self):
        for widget in self.frame_productos.winfo_children():
            widget.destroy()
        frame_scroll = tk.Frame(self.frame_productos)
        frame_scroll.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame_scroll)
        scrollbar.pack(side="right", fill="y")
        canvas = tk.Canvas(frame_scroll, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)
        frame_productos_interno = tk.Frame(canvas)
        canvas.create_window((0,0), window=frame_productos_interno, anchor="nw")
        self.cursor.execute("SELECT id, nombre, precio, imagen FROM productos")
        productos = self.cursor.fetchall()
        self.productos_seleccionados = []
        for producto in productos:
            frame_producto = tk.Frame(frame_productos_interno)
            frame_producto.pack(fill=tk.X)
            tk.Label(frame_producto, text=f"{producto[1]}: € {producto[2]:.2f}").pack(side=tk.LEFT)
            if producto[3] and isinstance(producto[3], str):
                try:
                    imagen = Image.open(producto[3])
                    imagen = imagen.resize((50, 50))
                    imagen = ImageTk.PhotoImage(imagen)
                    label_imagen = tk.Label(frame_producto, image=imagen)
                    label_imagen.image = imagen
                    label_imagen.pack(side=tk.LEFT)
                except Exception as e:
                    messagebox.showerror(f"Error al cargar la imagen: {e}")
            boton_seleccionar = tk.Button(frame_producto, text="Seleccionar", bg="blue", fg="white", command=lambda producto=producto: self.seleccionar_producto(producto))
            boton_seleccionar.pack(side=tk.LEFT)
            boton_a_bandeja = tk.Button(frame_producto, text='A la bandeja',bg="green", fg="white", command=lambda producto=producto: self.agregar_producto_a_bandeja(producto))
            boton_a_bandeja.pack(side=tk.LEFT)
            boton_eliminar = tk.Button(frame_producto, text='Eliminar', bg="red", fg="white", command=lambda producto=producto: self.eliminar_producto(producto))
            boton_eliminar.pack(side=tk.LEFT)
        frame_productos_interno.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def seleccionar_producto(self, producto):
        if producto in self.productos_seleccionados:
            self.productos_seleccionados.remove(producto)

        else:
            self.productos_seleccionados.append(producto)
            self.mostrar_productos_seleccionados()
        


    
    def eliminar_producto(self, producto):
        try:
            conn = sqlite3.connect("almacen.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto[0],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        

    def agregar_producto(self):

    
        def guardar_inventario():
            nombre = entry_nombre.get()
            precio = entry_precio.get()
            imagen = entry_imagen.get()
            conn = sqlite3.connect('almacen.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, precio, imagen) VALUES (?, ?, ?)", (nombre, precio, imagen))
            conn.commit()
            conn.close()
            messagebox.showinfo("Producto guardado", "El producto ha sido guardado correctamente")
            ventana_inventario.destroy()

        

        def seleccionar_imagen(): # AQUÍ ESTÁ EL ERROR DEL INVENTARIO #
    
            ruta_imagen = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Archivos imagen", ".png .jpg .jpeg")])
            entry_imagen.delete(0, tk.END)
            entry_imagen.insert(0, ruta_imagen)

        ventana_inventario = tk.Toplevel(self.ventana)
        ventana_inventario.title("Introducir Inventario")
        ventana_inventario.geometry("200x200")
        ventana_inventario.transient(self.ventana)
        ventana_inventario.grab_set()
        ventana_inventario.lift()

        tk.Label(ventana_inventario, text="Nombre:").pack()
        entry_nombre = tk.Entry(ventana_inventario)
        entry_nombre.pack()

        tk.Label(ventana_inventario, text="Precio:").pack()
        entry_precio = tk.Entry(ventana_inventario)
        entry_precio.pack()

        tk.Label(ventana_inventario, text="Imagen:").pack()
        entry_imagen = tk.Entry(ventana_inventario, width=50)
        entry_imagen.pack()

        tk.Button(ventana_inventario, text="Seleccionar imagen", command=seleccionar_imagen).pack()
        tk.Button(ventana_inventario, text="Guardar", command=guardar_inventario).pack()



    def agregar_producto_a_bandeja(self, producto):
        imagen = tk.PhotoImage(file=producto[3])
        imagen = imagen.subsample(6, 6) # AJUSTA EL TAMAÑO DE LA IMAGEN
        boton_producto = tk.Button(self.frame_izquierdo_inferior, image=imagen, text=f"{producto[1]}\n€{producto[2]:.2f}", compound=tk.TOP, command=lambda producto=producto: self.agregar_producto_al_ticket(producto))        
        boton_producto.image = imagen
        row =len(self.frame_izquierdo_inferior.winfo_children())//7
        column = len(self.frame_izquierdo_inferior.winfo_children())%7
        if row <4:

            boton_producto.grid(row=row, column=column, padx=5, pady=5)
    
    

           
    def mostrar_productos_seleccionados(self):
        ventana_seleccionados = tk.Toplevel(self.ventana)
        ventana_seleccionados.title("Productos seleccionados")
        ventana_seleccionados.geometry("200x200")  # Agrega un tamaño a la ventana
        

        for producto in self.productos_seleccionados:
            frame_producto = tk.Frame(ventana_seleccionados)
            frame_producto.pack(fill=tk.X)
            tk.Label(frame_producto, text=f"{producto[0]}: € {producto[1]:.2f}").pack(side=tk.LEFT)
            if producto[2]:
                try:
                    imagen = Image.open(producto[2])
                    imagen = imagen.resize((50, 50))
                    imagen = ImageTk.PhotoImage(imagen)
                    label_imagen = tk.Label(frame_producto, image=imagen)
                    label_imagen.image = imagen  # Mantén una referencia a la imagen
                    label_imagen.pack(side=tk.LEFT)
                except Exception as e:
                    messagebox.showerror(f"Error al cargar la imagen: {e}")
        

        ventana_seleccionados.focus_set()

        
            
        
         
    def buscar_producto(self):
            pass
    
    def mostrar_personal(self):
        self.ventana_personal = tk.Toplevel(self.ventana)
        self.ventana_personal.geometry("500x500")
        self.ventana_personal.title("Personal")

        imagen_añadir = Image.open("Imágenes de diseño/Buttons/Buttons/Añdir.png")
        imagen = imagen_añadir.resize((65, 65))
        imagen_tk_añadir = ImageTk.PhotoImage(imagen)

        boton_añadir = tk.Button(self.ventana_personal, image=imagen_tk_añadir, command=lambda: self.añadir_personal())
        boton_añadir.image = imagen_tk_añadir
        boton_añadir.place(relx=0.05, rely=0.01)

        imagen_eliminar = Image.open("Imágenes de diseño/Buttons/Buttons/Eliminar.png")
        imagen_e = imagen_eliminar.resize((65, 65))
        imagen_tk_eliminar = ImageTk.PhotoImage(imagen_e)

        boton_eliminar = tk.Button(self.ventana_personal, image=imagen_tk_eliminar, command=lambda: self.eliminar_personal())
        boton_eliminar.image = imagen_tk_eliminar
        boton_eliminar.place(relx=0.05, rely=0.15)

        imagen_buscar = Image.open("Imágenes de diseño/Buttons/Buttons/Buscar.png")
        imagen = imagen_buscar.resize((65, 65))
        imagen_tk_buscar = ImageTk.PhotoImage(imagen)

        boton_buscar = tk.Button(self.ventana_personal, image=imagen_tk_buscar, command=lambda: self.buscar_personal())
        boton_buscar.image = imagen_tk_buscar
        boton_buscar.place(relx=0.05, rely=0.3)

    def añadir_personal(self):
        self.ventana_agregar_personal = tk.Toplevel(self.ventana_personal)
        self.ventana_agregar_personal.geometry("400x700")
        self.ventana_agregar_personal.title("Agregar Personal")

        # Label para la foto de carnet
        self.label_foto = tk.Label(self.ventana_agregar_personal, text="Foto de carnet", width=20, height=10, borderwidth=1, relief="solid")
        self.label_foto.pack(pady=20)

        # Botón para seleccionar la imagen
        self.btn_seleccionar_imagen = tk.Button(self.ventana_agregar_personal, text="Seleccionar imagen", command=self.seleccionar_imagen)
        self.btn_seleccionar_imagen.pack()
        self.btn_a_barra = tk.Button(self.ventana_agregar_personal, text="A Barra", bg="sienna", fg="white")
        self.btn_a_barra.pack()
        self.btn_a_terraza = tk.Button(self.ventana_agregar_personal, text="A Terraza", bg="green", fg="white")
        self.btn_a_terraza.pack()

        # Entries para el nombre, teléfono y dirección
        tk.Label(self.ventana_agregar_personal, text="Nombre:").pack()
        self.entry_nombre = tk.Entry(self.ventana_agregar_personal, width=30)
        self.entry_nombre.pack()
        tk.Label(self.ventana_agregar_personal, text="Teléfono:").pack()
        self.entry_telefono = tk.Entry(self.ventana_agregar_personal, width=30)
        self.entry_telefono.pack()
        tk.Label(self.ventana_agregar_personal, text="Dirección:").pack()
        self.entry_direccion = tk.Text(self.ventana_agregar_personal, width=30, height=5)
        self.entry_direccion.pack()

        # Botón para guardar los datos
        tk.Button(self.ventana_agregar_personal, text="Guardar", command=self.guardar_personal).pack()

        # Conectar a la base de datos y crear la tabla si no existe
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS personal (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                telefono TEXT,
                direccion TEXT,
                foto BLOB
            )
        """)
        conn.commit()
        conn.close()

    def seleccionar_imagen(self):
        # Abrir la ventana de selección de archivo
        ruta_imagen = filedialog.askopenfilename(filetypes=[("Archivos de imagen", ".jpg .jpeg .png")])

        # Abrir la imagen y mostrarla en el label
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((200, 200))
        imagen_tk = ImageTk.PhotoImage(imagen)
        self.label_foto.config(image=imagen_tk)
        self.label_foto.image = imagen_tk

        # Guardar la ruta de la imagen
        self.ruta_imagen = ruta_imagen

    def guardar_personal(self):
        # Verificar si todos los campos están rellenos
        if not self.entry_nombre.get() or not self.entry_telefono.get() or not self.entry_direccion.get("1.0", tk.END) or not hasattr(self, 'ruta_imagen'):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Conectar a la base de datos
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()

        # Obtener los datos de los entries
        nombre = self.entry_nombre.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get("1.0", tk.END)

        # Abrir la imagen y guardarla en la base de datos
        with open(self.ruta_imagen, "rb") as archivo:
            foto = archivo.read()

        # Insertar los datos en la base de datos
        cursor.execute("INSERT INTO personal (nombre, telefono, direccion, foto) VALUES (?, ?, ?, ?)", (nombre, telefono, direccion, foto))
        conn.commit()
        conn.close()

        # Mostrar un popup de confirmación
        messagebox.showinfo("Datos guardados", "Los datos se han guardado correctamente.")


    def seleccionar_foto(self):
        ruta_foto = filedialog.askopenfilename(filetypes=[("Archivos de imagen", ".jpg .jpeg .png")])
        if ruta_foto:
            imagen = Image.open(ruta_foto)
            imagen = imagen.resize((100, 100))
            imagen_tk = ImageTk.PhotoImage(imagen)
            self.label_foto.config(image=imagen_tk)
            self.label_foto.image = imagen_tk


             
    def click_boton(self, boton):
        if boton == '=':
            try:
                resultado = eval(self.caja_input.cget("text").replace(",", "."))
                self.caja_input.config(text=str(resultado))
            except Exception as e:
                self.caja_input.config(text="Error")
        else:
            current_text = self.caja_input.cget("text")
            if current_text == "0" and boton.isdigit():
                self.caja_input.config(text=boton)
            else:
                self.caja_input.config(text=current_text + str(boton))

    def mostrar_caja(self):
        caj = caja.Caja(self)

    def mostrar_ventas(self):
        self.txt_resultado.pack_forget()  # Oculta el texto de la lectura de la base de datos
        self.frame_ventas.place(relx=0, rely=0, relwidth=1, relheight=1)  # Muestra el frame de ventas
        self.texto_ventas.delete('1.0', tk.END)  # Borra el texto anterior
        self.imprimir_ventas()

    def actualizar_varios(self, resultado):

    
        if resultado == "":
            if hasattr(self, 'label_importe') and self.label_importe is not None:
                self.label_importe.destroy()
                self.label_importe = None
        else:
            if not hasattr(self, 'label_importe') or self.label_importe is None:
                self.label_importe = tk.Label(self.frame_derecho_superior, text=f"Varios: {resultado} €", relief="ridge", bg="white", fg="black", borderwidth=2)
                self.label_importe.pack(side=tk.TOP)
            else:
                self.label_importe.config(text=f"Varios: {resultado} €")



    def mostrar_terraza(self):
        self.ventana_terraza = tk.Toplevel(self.ventana, bg="green")
        self.ventana_terraza.geometry("1300x800")
        self.ventana_terraza.title("TERRAZA")
        self.btn_agregar_ms = tk.Button(self.ventana_terraza, text="Agregar mesa", bg="white", fg="black", relief="raised")
        self.btn_agregar_ms.place(relx=0.05, rely=0.05)
        self.btn_editar_ms = tk.Button(self.ventana_terraza, text="Editar mesa", bg="white", fg="black", relief="raised")
        self.btn_editar_ms.place(relx=0.05, rely=0.1)
        self.btn_cuenta_ms = tk.Button(self.ventana_terraza, text="Cuenta mesa", bg="white", fg="black", relief="raised")
        self.btn_cuenta_ms.place(relx=0.05, rely=0.15)

        imagen = Image.open("Imágenes de diseño/TERRAZA.png")
        imagen = imagen.resize((800,500))  # Redimensionar la imagen
        imagen_tk = ImageTk.PhotoImage(imagen)

        # Crear un Label con la imagen
        label_imagen = tk.Label(self.ventana_terraza, image=imagen_tk)
        label_imagen.image = imagen_tk  # Mantener una referencia a la imagen
        label_imagen.pack()

    def mostrar_barra(self):
        self.ventana_barra = tk.Toplevel(self.ventana, bg="darkblue")
        self.ventana_barra.geometry("1300x800")
        self.ventana_barra.title("BARRA")

        # Cargar la imagen
        imagen = Image.open("Imágenes de diseño/Barra.png")
        imagen = imagen.resize((800,500))  # Redimensionar la imagen
        imagen_tk = ImageTk.PhotoImage(imagen)

        # Crear un Label con la imagen
        label_imagen = tk.Label(self.ventana_barra, image=imagen_tk)
        label_imagen.image = imagen_tk  # Mantener una referencia a la imagen
        label_imagen.pack()

        self.btn_agregar_cn = tk.Button(self.ventana_barra, text="Agregar cuenta", bg="green", fg="white", relief="raised", command=self.mostrar_caja)
        self.btn_agregar_cn.place(relx=0.05, rely=0.05)
        self.btn_CAMARERO = tk.Button(self.ventana_barra, text="CAMARERO", bg="white", fg="black", relief="raised")
        self.btn_CAMARERO.place(relx=0.05, rely=0.1)
        self.btn_cuenta = tk.Button(self.ventana_barra, text="Cuenta", bg="blue", fg="white", relief="raised")
        self.btn_cuenta.place(relx=0.05, rely=0.15)

    def mostrar_caja(self):
        caj = caja.Caja(self)
        
    def elimnar_personal(self):
        pass
    def ver_personal(self):
        pass
    def mostrar_familias(self):
        self.ventana_familias = tk.Toplevel(self.ventana)
        self.ventana_familias.geometry("600x600")
        self.ventana_familias.title("Familias")
        self.frame_botones = tk.Frame(self.ventana_familias)
        self.frame_botones.pack(side=tk.LEFT, padx=10, pady=0)
        self.btn_agregar_F = tk.Button(self.frame_botones, text="Agregar familia", command=self.agregar_familia)
        self.btn_agregar_F.pack(fill=tk.X, pady=5)
        self.btn_agregar_productos = tk.Button(self.frame_botones, text="Agregar productos a familia", command=self.agregar_productos_a_familia)
        self.btn_agregar_productos.pack(fill=tk.X, pady=5)
        self.btn_ver_productos = tk.Button(self.frame_botones, text="Ver productos de familia", command=self.ver_productos_de_familia)
        self.btn_ver_productos.pack(fill=tk.X, pady=5)
        self.btn_buscar_F = tk.Button(self.frame_botones, text="Eliminar familia", command=self.eliminar_familia)
        self.btn_buscar_F.pack(fill=tk.X, pady=5)
        self.lista_familias = tk.Listbox(self.ventana_familias, width=50, height=30)
        self.lista_familias.pack(side=tk.RIGHT, padx=10, pady=10)
        self.actualizar_lista_familias()
    

    def agregar_familia(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS familias (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        )""")
        conn.commit()
        conn.close()


        self.ventana_agregar_familia = tk.Toplevel(self.ventana_familias)
        self.ventana_agregar_familia.title("Agregar Familia")
        self.label_nombre_familia = tk.Label(self.ventana_agregar_familia, text="Nombre de la familia:")
        self.label_nombre_familia.pack()
        self.entry_nombre_familia = tk.Entry(self.ventana_agregar_familia)
        self.entry_nombre_familia.pack()
        self.button_guardar_familia = tk.Button(self.ventana_agregar_familia, text="Guardar", command=self.guardar_familia)
        self.button_guardar_familia.pack()
        

    def eliminar_familia(self):
        pass

    
    def guardar_familia(self):
        nombre_familia = self.entry_nombre_familia.get()
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO familias (nombre) VALUES (?)", (nombre_familia,))
        conn.commit()
        conn.close()
        self.actualizar_lista_familias()
        self.ventana_agregar_familia.destroy()

    def agregar_productos_a_familia(self):
        seleccion = self.lista_familias.curselection()
        if seleccion:
            familia_seleccionada = self.lista_familias.get(seleccion)
            self.ventana_agregar_productos = tk.Toplevel(self.ventana_familias)
            self.ventana_agregar_productos.title("Agregar productos a " + familia_seleccionada)
            self.lista_productos = tk.Listbox(self.ventana_agregar_productos, selectmode=tk.MULTIPLE)
            conn = sqlite3.connect("almacen.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM productos")
            productos = cursor.fetchall()
            conn.close()
            for producto in productos:
                self.lista_productos.insert(tk.END, producto[0])
            self.lista_productos.pack()
            self.button_guardar_productos = tk.Button(self.ventana_agregar_productos, text="Guardar", command=lambda: self.guardar_productos_en_familia(familia_seleccionada))
            self.button_guardar_productos.pack()

    def guardar_productos_en_familia(self, familia_seleccionada):
            seleccion = self.lista_productos.curselection()
            if seleccion:
                productos_seleccionados = [self.lista_productos.get(i) for i in seleccion]
                conn = sqlite3.connect("almacen.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM familias WHERE nombre = ?", (familia_seleccionada,))
                familia_id = cursor.fetchone()[0]
                for producto in productos_seleccionados:
                    cursor.execute("SELECT id FROM productos WHERE nombre = ?", (producto,))
                    producto_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO familia_producto (familia_id, producto_id) VALUES (?, ?)", (familia_id, producto_id))
                conn.commit()
                conn.close()
                self.ventana_agregar_productos.destroy()

    def ver_productos_de_familia(self):
        seleccion = self.lista_familias.curselection()
        if seleccion:
            familia_seleccionada = self.lista_familias.get(seleccion)
            self.ventana_ver_productos = tk.Toplevel(self.ventana_familias)
            self.ventana_ver_productos.title("Productos de " + familia_seleccionada)
            self.lista_productos_familia = tk.Listbox(self.ventana_ver_productos)
            conn = sqlite3.connect("almacen.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM familias WHERE nombre = ?", (familia_seleccionada,))
            familia_id = cursor.fetchone()[0]
            cursor.execute("SELECT p.nombre FROM productos p INNER JOIN familia_producto fp ON p.id = fp.producto_id WHERE fp.familia_id = ?", (familia_id,))
            productos = cursor.fetchall()
            conn.close()
            for producto in productos:
                self.lista_productos_familia.insert(tk.END, producto[0])
            self.lista_productos_familia.pack()

    def actualizar_lista_familias(self):
        self.lista_familias.delete(0, tk.END)
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM familias")
        familias = cursor.fetchall()
        conn.close()
        for familia in familias:
            self.lista_familias.insert(tk.END, familia[0])
            

    def abrir_caja_diaria(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM caja WHERE fecha = ?", (fecha_actual,))
        caja = cursor.fetchone()
        if caja is None:
            cursor.execute("INSERT INTO caja (fecha, estado) VALUES (?, 'abierta')", (fecha_actual,))
            conn.commit()
        elif caja[2] != "abierta":
            cursor.execute("UPDATE caja SET estado = 'abierta' WHERE fecha = ?", (fecha_actual,))
            conn.commit()
        conn.close()

    def resumen_ventas(self):
        self.ventana_ventas = tk.Toplevel(self.ventana, bg="white")
        self.ventana_ventas.geometry("1300x800")
        self.ventana_ventas.title("RESUMEN VENTAS")
        self.btn_cerrar_venta = tk.Button(self.ventana_ventas, text="Cerrar venta diaria", bg="white", fg="black", relief="raised", command=self.cerrar_ventas)
        self.btn_cerrar_venta.place(relx=0.05, rely=0.05)
        self.btn_mostrar_vn_d = tk.Button(self.ventana_ventas, text="Mostrar ventas diarias", bg="white", fg="black", relief="raised", command=self.mostrar_ventas_diarias)
        self.btn_mostrar_vn_d.place(relx=0.05, rely=0.1)
        self.btn_mostrar_vn_men = tk.Button(self.ventana_ventas, text="Imprimir ventas", bg="white", fg="black", relief="raised")
        self.btn_mostrar_vn_men.place(relx=0.05, rely=0.15)
    
    
    
    def mostrar_ventas_diarias(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT estado FROM caja WHERE fecha = ?", (fecha_actual,))
        estado_caja = cursor.fetchone()
        if estado_caja is None or estado_caja[0] != "abierta":
            messagebox.showerror("Error", "La caja diaria está cerrada")
            return
        cursor.execute("SELECT * FROM ventas WHERE fecha = ?", (fecha_actual,))
        ventas_diarias = cursor.fetchall()
        conn.close()
        texto_ventas = ""
        for venta in ventas_diarias:
            texto_ventas += f"ID: {venta[0]}\nFecha: {venta[1]}\nHora: {venta[2]}\nCódigo QR: {venta[3]}\nTipo de documento: {venta[4]}\nPrecio: {venta[5]}\n\n"
        if hasattr(self, 'frame_ventas_diarias'): 
            self.frame_ventas_diarias.destroy()
        if hasattr(self, 'text_ventas_diarias'): 
            self.text_ventas_diarias.destroy()
        if hasattr(self, 'scrollbar_ventas_diarias'): 
            self.scrollbar_ventas_diarias.destroy()
        self.frame_ventas_diarias = tk.Frame(self.ventana_ventas)
        self.frame_ventas_diarias.place(relx=0.7, rely=0.05)
        self.label_ventas_diarias_titulo = tk.Label(self.frame_ventas_diarias, text="Ventas diarias: ", bg="white", fg="black", font=(None, 20))
        self.label_ventas_diarias_titulo.pack(side=tk.LEFT)
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(precio) FROM ventas WHERE fecha = ?", (fecha_actual,))
        self.ventas_diarias = cursor.fetchone()[0]
        if self.ventas_diarias is None:
            self.ventas_diarias = 0
        conn.close()
        self.label_ventas_diarias_valor = tk.Label(self.frame_ventas_diarias, text=f"{self.ventas_diarias:.2f} €", bg="white", fg="black", font=(None,20))
        self.label_ventas_diarias_valor.pack(side=tk.LEFT)
        self.frame_text_ventas_diarias = tk.Frame(self.ventana_ventas)
        self.frame_text_ventas_diarias.place(relx=0.3, rely=0.1)
        self.scrollbar_ventas_diarias = tk.Scrollbar(self.frame_text_ventas_diarias)
        self.scrollbar_ventas_diarias.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_ventas_diarias = tk.Text(self.frame_text_ventas_diarias, width=80, height=20, yscrollcommand=self.scrollbar_ventas_diarias.set)
        self.text_ventas_diarias.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar_ventas_diarias.config(command=self.text_ventas_diarias.yview)
        self.text_ventas_diarias.insert(tk.END, texto_ventas)
        self.text_ventas_diarias.config(state="disabled")
    def cerrar_ventas(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT estado FROM caja WHERE fecha = ?", (fecha_actual,))
        estado_caja = cursor.fetchone()
        if estado_caja is None or estado_caja[0] != "abierta":
            messagebox.showerror("Error", "La caja diaria ya está cerrada")
            return
        confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas cerrar la venta del día?")
        if confirmacion:
            cursor.execute("UPDATE caja SET estado = 'cerrada' WHERE fecha = ?", (fecha_actual,))
            conn.commit()
            conn.close()
            self.ventana_ventas.destroy()

    def mostrar_config(self):

        self.ventana_config = tk.Toplevel(self.ventana, bg="black")
        self.ventana_config.geometry("600x600")
        self.ventana_config.title("Configuración")
        self.btn_datos = tk.Button(self.ventana_config, text="Datos de la empresa", bg="green", fg="white", command=self.configurar_datos_empresa)
        self.btn_datos.pack(padx=0.5, pady=0.5)
        self.btn_estado_em = tk.Button(self.ventana_config, text="Estado de la empresa", bg="blue", fg="white", command=self.buscar_producto)
        self.btn_estado_em.pack(padx=0.5, pady=0.5)
        self.btn_seg_soc = tk.Button(self.ventana_config, text="Seguros Sociales", bg="red", fg="white", command=self.buscar_producto)
        self.btn_seg_soc.pack(padx=0.5, pady=0.5)
        self.btn_ag_trib = tk.Button(self.ventana_config, text="Agencia Tributaria", bg="purple", fg="white", command=self.buscar_producto)
        self.btn_ag_trib.pack(padx=0.5, pady=0.5)
        self.btn_dni_e = tk.Button(self.ventana_config, text="DNI-E", bg="black", fg="white", command=self.cargar_dni_e)
        self.btn_dni_e.pack(padx=0.5, pady=0.5)
        self.btn_fac_dig = tk.Button(self.ventana_config, text="Factura-E", bg="darkblue", fg="white", command=self.buscar_producto)
        self.btn_fac_dig.pack(padx=0.5, pady=0.5)
        self.btn_bizzum = tk.Button(self.ventana_config, text="Bizzum", bg="darkgreen", fg="white", command=self.buscar_producto)
        self.btn_bizzum.pack(padx=0.5, pady=0.5)
        self.btn_whatsapp = tk.Button(self.ventana_config, text="Whatsapp", bg="green", fg="white", command=self.buscar_producto)
        self.btn_whatsapp.pack(padx=0.5, pady=0.5)
        self.btn_telegram= tk.Button(self.ventana_config, text="Telegram", bg="darkgreen", fg="white", command=self.buscar_producto)
        self.btn_telegram.pack(padx=0.5, pady=0.5)
        self.btn_iva= tk.Button(self.ventana_config, text="IVA", bg="black", fg="white", command=self.iva)
        self.btn_iva.pack(padx=0.5, pady=0.5)

    def iva(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                valor TEXT
            )
        """)
        conn.commit()

        # Recuperar el valor del IVA
        cursor.execute("SELECT valor FROM configuracion WHERE nombre = 'iva'")
        iva_configurado = cursor.fetchone()

        ventana_iva = tk.Toplevel(self.ventana)
        ventana_iva.title("Configurar IVA")

        tk.Label(ventana_iva, text="Introduzca IVA:").grid(row=0, column=0)
        entry_porcentaje_iva = tk.Entry(ventana_iva)
        entry_porcentaje_iva.grid(row=0, column=1)

        # Asignar valor al campo de entrada si existe
        if iva_configurado:
            entry_porcentaje_iva.insert(0, iva_configurado[0])

        btn_guardar = tk.Button(ventana_iva, text="Guardar", command=lambda: self.guardar_iva(entry_porcentaje_iva, ventana_iva))
        btn_guardar.grid(row=1, column=0, columnspan=2)
        conn.close()
        
        


    def guardar_iva(self, entry, ventana):
        porcentaje_iva = entry.get()
        # Código para guardar el IVA en la base de datos
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM configuracion WHERE nombre = 'iva'")
        resultado = cursor.fetchone()
        if resultado:
            cursor.execute("UPDATE configuracion SET valor = ? WHERE nombre = 'iva'", (porcentaje_iva,))
        else:
            cursor.execute("INSERT INTO configuracion (nombre, valor) VALUES ('iva', ?)", (porcentaje_iva,))
        conn.commit()
        conn.close()
        ventana.destroy()
        
        
           

    def obtener_iva(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracion WHERE nombre = 'iva'")
        resultado = cursor.fetchone()
        conn.close()
        if resultado and resultado[0]:
            return resultado[0]
        else:
            messagebox.showerror("Error", "El IVA no está configurado. Por favor, configure el IVA antes de continuar.")
            return None



    def cargar_dni_e(self):
        self.ventana_dni_e = tk.Toplevel(self.ventana)
        self.ventana_dni_e.title("Cargar DNI-e")

        tk.Label(self.ventana_dni_e, text="Seleccione el archivo de certificado digital DNI-e:").pack()

        def seleccionar_archivo():
            archivo = filedialog.askopenfilename(title="Seleccione el archivo de certificado digital DNI-e", filetypes=[("Archivos de certificado digital", "*.pfx;*.p12")])
            if archivo:
                self.entry_archivo.delete(0, tk.END)
                self.entry_archivo.insert(0, archivo)

        tk.Button(self.ventana_dni_e, text="Seleccionar archivo", command=seleccionar_archivo).pack()

        self.entry_archivo = tk.Entry(self.ventana_dni_e, width=50)
        self.entry_archivo.pack()

        tk.Button(self.ventana_dni_e, text="Guardar", command=self.guardar_dni_e).pack()

    def guardar_dni_e(self):
        archivo = self.entry_archivo.get()
        messagebox.showinfo(f"Archivo de certificado digital: {archivo}")
        self.ventana_dni_e.destroy()



    def datos_empresa(self):
        frame_datos_empresa = tk.Frame(self.ventana)
        frame_datos_empresa.pack(side=tk.RIGHT)

        tk.Label(frame_datos_empresa, text=f"Nombre de la empresa: {self.nombre_empresa}").pack()
        tk.Label(frame_datos_empresa, text=f"nif: {self.nif_empresa}").pack()
        tk.Label(frame_datos_empresa, text=f"Dirección: {self.direccion_empresa}").pack()
        tk.Label(frame_datos_empresa, text=f"Teléfono: {self.telefono_empresa}").pack()
        tk.Label(frame_datos_empresa, text=f"Correo electrónico {self.correo_empresa}").pack
        
            
            

    

    def configurar_datos_empresa(self):
        conn = sqlite3.connect('almacen.db')
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS datos_empresa (
                id INTEGER PRIMARY KEY,
                nombre_empresa TEXT NOT NULL,
                nif TEXT,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo_electronico TEXT
            )
        """)
        conn.commit()

        # Recuperar los datos de la empresa
        cursor.execute("SELECT * FROM datos_empresa WHERE id = 1")
        datos_empresa = cursor.fetchone()

        ventana_configuracion = tk.Toplevel(self.ventana)
        ventana_configuracion.title("Configurar datos de la empresa")

        tk.Label(ventana_configuracion, text="Nombre de la empresa:").grid(row=0, column=0)
        entry_nombre_empresa = tk.Entry(ventana_configuracion)
        entry_nombre_empresa.grid(row=0, column=1)

        tk.Label(ventana_configuracion, text="NIF:").grid(row=1, column=0)
        entry_nif = tk.Entry(ventana_configuracion)
        entry_nif.grid(row=1, column=1)

        tk.Label(ventana_configuracion, text="Dirección:").grid(row=2, column=0)
        entry_direccion = tk.Entry(ventana_configuracion)
        entry_direccion.grid(row=2, column=1)

        tk.Label(ventana_configuracion, text="Teléfono:").grid(row=3, column=0)
        entry_telefono = tk.Entry(ventana_configuracion)
        entry_telefono.grid(row=3, column=1)

        tk.Label(ventana_configuracion, text="Correo electrónico:").grid(row=4, column=0)
        entry_correo = tk.Entry(ventana_configuracion)
        entry_correo.grid(row=4, column=1)

        # Asignar valores a los campos de entrada si existen datos
        if datos_empresa:
            entry_nombre_empresa.insert(0, datos_empresa[1])
            entry_nif.insert(0, datos_empresa[2])
            entry_direccion.insert(0, datos_empresa[3])
            entry_telefono.insert(0, datos_empresa[4])
            entry_correo.insert(0, datos_empresa[5])

        conn.close()

        def guardar_datos():
            self.nombre_empresa = entry_nombre_empresa.get()
            self.nif_empresa = entry_nif.get()
            self.direccion_empresa = entry_direccion.get()
            self.telefono_empresa = entry_telefono.get()
            self.correo_empresa = entry_correo.get()
            self.guardar_datos_empresa()
            ventana_configuracion.destroy()

        btn_guardar_datos = tk.Button(ventana_configuracion, text="Guardar", bg="green", fg="white", command=guardar_datos)
        btn_guardar_datos.grid(row=5, column=1)        


    def guardar_datos_empresa(self):
        conn = sqlite3.connect('almacen.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO datos_empresa (id, nombre_empresa, nif, direccion, telefono, correo_electronico) VALUES (?, ?, ?, ?, ?, ?)", (1, self.nombre_empresa, self.nif_empresa, self.direccion_empresa, self.telefono_empresa, self.correo_empresa))
        conn.commit()
        conn.close()

    def mostrar_datos_empresa(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS datos_empresa (
                id INTEGER PRIMARY KEY,
                nombre_empresa TEXT NOT NULL,
                nif TEXT,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo_electronico TEXT
            ) 
        """)
        conn.commit()
        cursor.execute("SELECT * FROM datos_empresa WHERE id = 1")
        datos_empresa = cursor.fetchone()
        if datos_empresa is None:
            cursor.execute(""" 
                INSERT INTO datos_empresa (id, nombre_empresa, nif, direccion, telefono, correo_electronico) 
                VALUES (1, '', '', '', '', '') 
            """)
            conn.commit()
            cursor.execute("SELECT * FROM datos_empresa WHERE id = 1")
            datos_empresa = cursor.fetchone()

        if hasattr(self, 'datos_empresa_label'):
            self.datos_empresa_label.destroy()
        self.datos_empresa_label = tk.Label(self.frame_derecho_superior, text=f"Nombre de la empresa: {datos_empresa[1]}\n nif: {datos_empresa[2]}\nDirección: {datos_empresa[3]}\nTeléfono: {datos_empresa[4]}\nCorreo: {datos_empresa[5]}", bg="white", justify=tk.LEFT)
        self.datos_empresa_label.place(relx=0.5, rely=0.1)

        conn.close()



    def cargar_datos_empresa(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos_empresa WHERE id = 1")
        datos = cursor.fetchone()
        self.nombre_empresa = datos[1]
        self.nif_empresa = datos[2]
        self.direccion_empresa = datos[3]
        self.telefono_empresa = datos[4]
        self.correo_empresa = datos[5]
        conn.close()
      
    
    def mostrar_pagado(self):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT estado FROM caja WHERE fecha = ?", (fecha_actual,))
        estado_caja = cursor.fetchone()
        if estado_caja is None or estado_caja[0] != "abierta":
            messagebox.showerror("Error", "La caja está cerrada")
            conn.close()
            return
        cursor.execute("SELECT * FROM ventas ORDER BY id DESC LIMIT 1")
        ultima_venta = cursor.fetchone()
        if ultima_venta:
            texto = f"Venta:\nFecha: {ultima_venta[1]}\nHora: {ultima_venta[2]}\nCódigo QR: {ultima_venta[3]}\nTipo de documento: {ultima_venta[4]}\nPrecio: {ultima_venta[5]}"
        else:
            texto = "No hay ventas registradas"
        conn.close()
        self.ventana_pagado = tk.Toplevel(self.ventana)
        self.ventana_pagado.geometry("800x800")
        self.ventana_pagado.title("Pagado")
        image = Image.open("Imágenes de diseño/Buttons/Buttons/Pagado.png")
        image = image.resize((250, 250))
        photo_image = ImageTk.PhotoImage(image)
        label_image = tk.Label(self.ventana_pagado, image=photo_image)
        label_image.image = photo_image
        label_image.pack()
        self.label_venta = tk.Label(self.ventana_pagado, text=texto, bg="white", justify=tk.LEFT)
        self.label_venta.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        btn_ok_ticket = tk.Button(self.ventana_pagado, text="Tícket", bg="green", fg="white", command=lambda: self.guardar_venta("Tícket"))
        btn_ok_ticket.place(relx=0.4, rely=0.7, anchor=tk.CENTER)
        btn_ok_factura = tk.Button(self.ventana_pagado, text="Factura", bg="blue", fg="white", command=lambda: self.guardar_venta("Factura"))
        btn_ok_factura.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        btn_cancel_pagado = tk.Button(self.ventana_pagado, text="Cancelar", bg="red", fg="white", command=self.cerrar_mostrar_pagado)
        btn_cancel_pagado.place(relx=0.6, rely=0.7, anchor=tk.CENTER)

    
    def guardar_venta(self, tipo_documento):
        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT estado FROM caja WHERE fecha = ?", (fecha_actual,))
        estado_caja = cursor.fetchone()
        if estado_caja is None or estado_caja[0] != "abierta":
            messagebox.showerror("Error", "La caja está cerrada")
            return
        codigo_qr = str(uuid.uuid4())
        fecha = datetime.date.today().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        total = getattr(self, 'total', 0)
        if hasattr(self, 'total_varios') and self.total_varios > 0:
            total += self.total_varios
        cursor.execute("INSERT INTO ventas (fecha, hora, codigo_qr, tipo_documento, precio) VALUES (?, ?, ?, ?, ?)", (fecha, hora, codigo_qr, tipo_documento, total))
        conn.commit()
        conn.close()
        self.label_venta.config(text=f"Venta guardada:\nFecha: {fecha}\nHora: {hora}\nCódigo QR: {codigo_qr}\nTipo de documento: {tipo_documento}")
        messagebox.showinfo("Venta guardada", "La venta se ha guardado correctamente.")
        self.resetear_ticket()

    def cerrar_mostrar_pagado(self):
        self.ventana_pagado.destroy()

    
        
        

        # MOSTRAR EL TEXTO DEL TICKET #

        texto_ticket = self.label_ventas.cget("text")
        label_ticket = tk.Label(self.ventana_pagado, text=texto_ticket, wraplength=250)
        label_ticket.pack()

    def cerrar_ventana_pagado(self):
        self.ticket_text = ""
        self.total = 0
        self.total_varios = 0
        self.label_ventas.config(text="")
        self.ventana_pagado.destroy()
        self.label_codigo_qr.config(image=None, bg="#FFFFFF")
        self.label_codigo_qr.image = None

    def cerrar_mostrar_pagado(self):
        self.ventana_pagado.destroy() # ESTA FUNCIÓN DEBE ESTAR DEBAJO DE CERRAR_VENTANA_PAGADO (INTENTACIÓN)#

    def nueva_venta(self):
        self.total_varios = 0
        self.label_ventas.config(text="")
        
    def salir_app(self):
        respuesta = messagebox.askyesno("Salir", "¿Estás seguro?")
        if respuesta:
            self.ventana.destroy()

    def run(self):
        self.actualizar()
        self.ventana.mainloop()

if __name__ == '__main__':
    tpvbar = TpvBar()
    tpvbar.run() 