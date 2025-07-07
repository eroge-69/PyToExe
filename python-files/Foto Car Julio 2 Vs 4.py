import os
import csv
import qrcode
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime, timedelta
import hashlib
import time
import webbrowser
import subprocess
import threading
import win32print
import win32api
import re  # Importado para expresiones regulares

class SistemaFotografia:
    def __init__(self, root):
        self.root = root
        self.root.title("FOTO CAR STUDIO - Sistema de Gestión")
        self.root.geometry("1200x900")
        self.root.configure(bg="#f0f0f0")
        
        self.root.bind('<Return>', lambda event: self.aceptar_con_enter())
        
        self.usuario_actual = None
        self.clientes = []
        self.notificaciones = []
        self.icono_negocio = None
        self.cliente_actual = None
        self.servicios_disponibles = [
            "Foto Estudio", 
            "Restauración", 
            "Impresiones de fotos", 
            "Lápidas", 
            "Retablos", 
            "Marcos", 
            "Otros"
        ]
        
        self.archivo_clientes = "clientes.csv"
        self.archivo_usuarios = "usuarios.csv"
        self.carpeta_qr = "codigos_qr"
        self.carpeta_iconos = "iconos"
        os.makedirs(self.carpeta_qr, exist_ok=True)
        os.makedirs(self.carpeta_iconos, exist_ok=True)
        
        self.cargar_icono_negocio()
        
        self.estilo = ttk.Style()
        self.estilo.configure('TFrame', background='#f0f0f0')
        self.estilo.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.estilo.configure('TButton', font=('Arial', 10, 'bold'))
        self.estilo.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
        self.estilo.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        self.estilo.configure('Notificacion.TButton', font=('Arial', 9), foreground='red')
        self.estilo.configure('Moneda.TEntry', font=('Arial', 10))
        
        if not self.iniciar_sesion():
            self.root.destroy()
            return
        
        self.clientes = self.cargar_clientes()
        self.verificar_vencimientos()
        self.crear_interfaz()
        self.crear_menu_principal()

    def aceptar_con_enter(self):
        widget = self.root.focus_get()
        
        if isinstance(widget, ttk.Button):
            widget.invoke()
        elif isinstance(widget, tk.Toplevel):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button) and child['text'].lower() in ['ok', 'aceptar', 'guardar', 'sí']:
                    child.invoke()
                    break

    def cargar_icono_negocio(self):
        icono_path = os.path.join(self.carpeta_iconos, "icono_negocio.png")
        if os.path.exists(icono_path):
            try:
                self.icono_negocio = Image.open(icono_path)
                self.icono_negocio = self.icono_negocio.resize((50, 50), Image.LANCZOS)
                self.icono_negocio_tk = ImageTk.PhotoImage(self.icono_negocio)
            except:
                self.icono_negocio = None

    def cambiar_icono_negocio(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar icono",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                destino = os.path.join(self.carpeta_iconos, "icono_negocio.png")
                shutil.copy(file_path, destino)
                
                self.cargar_icono_negocio()
                
                if hasattr(self, 'lbl_icono'):
                    self.lbl_icono.config(image=self.icono_negocio_tk)
                    self.lbl_icono.image = self.icono_negocio_tk
                
                messagebox.showinfo("Éxito", "Icono actualizado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el icono: {str(e)}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def cargar_usuarios(self):
        if not os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['usuario', 'contrasena'])
                writer.writerow(['admin', self.hash_password('admin123')])
            return [{'usuario': 'admin', 'contrasena': self.hash_password('admin123')}]
        
        usuarios = []
        with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                usuarios.append(fila)
        return usuarios

    def iniciar_sesion(self):
        usuarios = self.cargar_usuarios()
        
        login_window = tk.Toplevel(self.root)
        login_window.title("Inicio de Sesión")
        login_window.geometry("300x200")
        login_window.resizable(False, False)
        
        ttk.Label(login_window, text="Usuario:", font=('Arial', 10)).pack(pady=5)
        entry_usuario = ttk.Entry(login_window)
        entry_usuario.pack(pady=5)
        entry_usuario.focus_set()
        
        ttk.Label(login_window, text="Contraseña:", font=('Arial', 10)).pack(pady=5)
        entry_contrasena = ttk.Entry(login_window, show="*")
        entry_contrasena.pack(pady=5)
        
        intentos = 3
        resultado = tk.BooleanVar(value=False)
        
        def verificar():
            usuario = entry_usuario.get()
            contrasena = entry_contrasena.get()
            
            for u in usuarios:
                if u['usuario'] == usuario and u['contrasena'] == self.hash_password(contrasena):
                    resultado.set(True)
                    self.usuario_actual = usuario
                    login_window.destroy()
                    return
            
            nonlocal intentos
            intentos -= 1
            if intentos > 0:
                messagebox.showwarning("Error", f"Credenciales incorrectas. Te quedan {intentos} intentos.")
            else:
                messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo...")
                login_window.destroy()
        
        btn_ingresar = ttk.Button(login_window, text="Ingresar", command=verificar)
        btn_ingresar.pack(pady=10)
        
        entry_contrasena.bind('<Return>', lambda e: btn_ingresar.invoke())
        
        login_window.transient(self.root)
        login_window.grab_set()
        self.root.wait_window(login_window)
        
        return resultado.get()

    def cargar_clientes(self):
        if not os.path.exists(self.archivo_clientes):
            with open(self.archivo_clientes, 'w', newline='', encoding='utf-8') as f:
                campos = ['nombre', 'cedula', 'telefono', 'servicio', 'descripcion', 'cantidad', 
                         'total', 'abono', 'saldo', 'qr_cliente', 'qr_negocio', 
                         'fecha_creacion', 'fecha_entrega', 'fecha_vencimiento', 'entregado']
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
            return []
        
        clientes = []
        with open(self.archivo_clientes, 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                for campo in ['total', 'abono', 'saldo']:
                    if campo in fila and fila[campo]:
                        try:
                            fila[campo] = str(int(float(fila[campo].replace(',', '').replace('$', ''))))
                        except (ValueError, TypeError):
                            fila[campo] = '0'
                clientes.append(fila)
        return clientes

    def guardar_clientes(self):
        with open(self.archivo_clientes, 'w', encoding='utf-8', newline='') as f:
            campos = ['nombre', 'cedula', 'telefono', 'servicio', 'descripcion', 'cantidad', 
                     'total', 'abono', 'saldo', 'qr_cliente', 'qr_negocio', 
                     'fecha_creacion', 'fecha_entrega', 'fecha_vencimiento', 'entregado']
            escritor = csv.DictWriter(f, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(self.clientes)

    def verificar_vencimientos(self):
        ahora = datetime.now()
        self.notificaciones = []
        
        for cliente in self.clientes:
            if 'fecha_creacion' in cliente and cliente['fecha_creacion']:
                fecha_creacion = datetime.strptime(cliente['fecha_creacion'], "%Y-%m-%d %H:%M:%S")
                dias_transcurridos = (ahora - fecha_creacion).days
                
                if dias_transcurridos >= 25 and dias_transcurridos < 30:
                    self.notificaciones.append(
                        f"PRÓXIMO A VENCER: {cliente['nombre']} - Tel: {cliente['telefono']} - "
                        f"{30 - dias_transcurridos}d restantes - Servicio: {cliente['servicio']} - "
                        f"Descripción: {cliente['descripcion'][:50]}..."
                    )
                elif dias_transcurridos >= 30:
                    self.notificaciones.append(
                        f"VENCIDO: {cliente['nombre']} - Tel: {cliente['telefono']} - "
                        f"Servicio: {cliente['servicio']} - Descripción: {cliente['descripcion'][:50]}..."
                    )
                
                if 'fecha_entrega' in cliente and cliente['fecha_entrega']:
                    try:
                        fecha_entrega = datetime.strptime(cliente['fecha_entrega'], "%Y-%m-%d")
                        dias_faltantes = (fecha_entrega - ahora).days
                        if dias_faltantes == 1:
                            self.notificaciones.append(
                                 f"ENTREGA MAÑANA: {cliente['nombre']} - Tel: {{cliente['telefono'] - "
                                 f"Servicio: {cliente['servicio']} - Descripción: {cliente['descripcion'][:50]}..."
                            )
                        elif dias_faltantes == 0:
                            self.notificaciones.append(
                                f"ENTREGA HOY: {cliente['nombre']} - Tel: {cliente['telefono']} - "
                                f"Servicio: {cliente['servicio']} - Descripción: {cliente['descripcion'][:50]}..."
                            )
                        elif dias_faltantes < 0:
                            self.notificaciones.append(
                                f"ENTREGA ATRASADA: {cliente['nombre']} - Tel: {cliente['telefono']} - "
                                f"Servicio: {cliente['servicio']} - Descripción: {cliente['descripcion'][:50]}..."
                            )
                    except ValueError:
                        pass
        
        if hasattr(self, 'notificaciones_menu'):
            self.actualizar_notificaciones()
        
        self.root.after(3600000, self.verificar_vencimientos)

    def actualizar_notificaciones(self):
        self.notificaciones_menu.delete(0, tk.END)
        if not self.notificaciones:
            self.notificaciones_menu.add_command(label="No hay notificaciones", state=tk.DISABLED)
            self.btn_notificaciones.config(style='TButton')
        else:
            self.btn_notificaciones.config(style='Notificacion.TButton')
            for notif in self.notificaciones:
                self.notificaciones_menu.add_command(label=notif, command=lambda n=notif: self.buscar_desde_notificacion(n))

    def buscar_desde_notificacion(self, notif):
        match = re.search(r"Tel: (\d+)", notif)
        if match:
            telefono = match.group(1)
            self.notebook.select(self.tab_buscar)
            self.buscar_por.set("telefono")
            self.ent_buscar.delete(0, tk.END)
            self.ent_buscar.insert(0, telefono)
            self.buscar_cliente()
        else:
            messagebox.showwarning("Advertencia", "No se pudo extraer el teléfono de la notificación")

    def crear_interfaz(self):
        frame_superior = ttk.Frame(self.root, padding=10)
        frame_superior.pack(fill=tk.X)
        
        if hasattr(self, 'icono_negocio_tk'):
            self.lbl_icono = ttk.Label(frame_superior, image=self.icono_negocio_tk)
            self.lbl_icono.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_superior, text="FOTO CAR STUDIO", style='Title.TLabel').pack(side=tk.LEFT, padx=10)
        
        if self.usuario_actual == 'admin':
            btn_cambiar_icono = ttk.Button(frame_superior, text="Cambiar Icono", command=self.cambiar_icono_negocio)
            btn_cambiar_icono.pack(side=tk.LEFT, padx=10)
        
        self.btn_notificaciones = ttk.Button(frame_superior, text="Notificaciones", command=self.mostrar_notificaciones)
        self.btn_notificaciones.pack(side=tk.RIGHT, padx=10)
        
        self.notificaciones_menu = tk.Menu(self.root, tearoff=0)
        
        self.notebook = ttk.Notebook(self.root)
        
        self.tab_nuevo = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_nuevo, text='Nuevo Cliente')
        self.crear_tab_nuevo()
        
        self.tab_buscar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_buscar, text='Buscar Cliente')
        self.crear_tab_buscar()
        
        self.tab_imprimir = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_imprimir, text='Imprimir QR')
        self.crear_tab_imprimir()
        
        if self.usuario_actual == 'admin':
            self.tab_usuarios = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_usuarios, text='Gestión de Usuarios')
            self.crear_tab_usuarios()
        
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_bar = ttk.Label(self.root, 
                                  text=f"Usuario: {self.usuario_actual} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                  relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)
        
        self.actualizar_hora()
        self.verificar_vencimientos()

    def mostrar_notificaciones(self):
        try:
            self.notificaciones_menu.tk_popup(
                self.btn_notificaciones.winfo_rootx(),
                self.btn_notificaciones.winfo_rooty() + self.btn_notificaciones.winfo_height()
            )
        finally:
            self.notificaciones_menu.grab_release()

    def actualizar_hora(self):
        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status_bar.config(text=f"Usuario: {self.usuario_actual} | {ahora}")
        self.root.after(1000, self.actualizar_hora)

    def crear_tab_nuevo(self):
        canvas = tk.Canvas(self.tab_nuevo)
        scrollbar = ttk.Scrollbar(self.tab_nuevo, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        ttk.Label(scrollable_frame, text="NUEVO CLIENTE", style='Title.TLabel').grid(row=0, column=0, columnspan=3, pady=10)
        
        frame_izquierda = ttk.Frame(scrollable_frame)
        frame_izquierda.grid(row=1, column=0, sticky="nsew", padx=10)
        
        frame_datos = ttk.LabelFrame(frame_izquierda, text="Datos Personales", padding=10)
        frame_datos.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_datos, text="Nombre completo:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_nombre = ttk.Entry(frame_datos, width=35, font=('Arial', 10))
        self.ent_nombre.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        
        ttk.Label(frame_datos, text="Cédula:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_cedula = ttk.Entry(frame_datos, width=15, font=('Arial', 10))
        self.ent_cedula.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(frame_datos, text="Teléfono:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_telefono = ttk.Entry(frame_datos, width=15, font=('Arial', 10))
        self.ent_telefono.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        frame_servicios = ttk.LabelFrame(frame_izquierda, text="Servicio a Prestar", padding=10)
        frame_servicios.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_servicios, text="Tipo de servicio:").grid(row=0, column=0, sticky="w", pady=5)
        self.servicio_var = tk.StringVar()
        self.cb_servicio = ttk.Combobox(frame_servicios, textvariable=self.servicio_var, 
                                      values=self.servicios_disponibles, state="readonly")
        self.cb_servicio.grid(row=0, column=1, sticky="we", pady=5, padx=5)
        self.cb_servicio.bind("<<ComboboxSelected>>", self.actualizar_cantidad_field)
        
        ttk.Label(frame_servicios, text="Especificar (si es Otros):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_especificar = ttk.Entry(frame_servicios, width=25, font=('Arial', 10))
        self.ent_especificar.grid(row=1, column=1, sticky="we", pady=5, padx=5)
        
        ttk.Label(frame_servicios, text="Cantidad:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_cantidad = ttk.Entry(frame_servicios, width=10, font=('Arial', 10))
        self.ent_cantidad.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(frame_servicios, text="Descripción del trabajo:").grid(row=3, column=0, sticky="nw", pady=5)
        self.ent_desc = tk.Text(frame_servicios, width=40, height=5, font=('Arial', 10), wrap=tk.WORD)
        self.ent_desc.grid(row=3, column=1, pady=5, padx=5, sticky="we")
        
        btn_otro_servicio = ttk.Button(frame_servicios, text="+ Agregar Otro Servicio", 
                                      command=self.agregar_otro_servicio)
        btn_otro_servicio.grid(row=4, column=0, columnspan=2, pady=5)
        
        frame_pagos = ttk.LabelFrame(frame_izquierda, text="Pagos y Fechas", padding=10)
        frame_pagos.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_pagos, text="Fecha de entrega (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_fecha_entrega = ttk.Entry(frame_pagos, width=15, font=('Arial', 10))
        self.ent_fecha_entrega.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        self.ent_fecha_entrega.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        
        ttk.Label(frame_pagos, text="Total a pagar:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_total = ttk.Entry(frame_pagos, width=15, font=('Arial', 10), style='Moneda.TEntry')
        self.ent_total.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        self.ent_total.bind("<KeyRelease>", self.formato_moneda)
        
        ttk.Label(frame_pagos, text="Abono inicial:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_abono = ttk.Entry(frame_pagos, width=15, font=('Arial', 10), style='Moneda.TEntry')
        self.ent_abono.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        self.ent_abono.bind("<KeyRelease>", self.formato_moneda)
        
        btn_guardar = ttk.Button(frame_izquierda, text="Guardar Cliente y Generar QR", 
                                command=self.guardar_cliente, style='TButton')
        btn_guardar.pack(pady=15, ipady=5)
        
        frame_derecha = ttk.Frame(scrollable_frame)
        frame_derecha.grid(row=1, column=1, sticky="nsew", padx=10)
        
        frame_qr = ttk.LabelFrame(frame_derecha, text="Código QR Generado", padding=10)
        frame_qr.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_qr_cliente = ttk.Label(frame_qr, text="Generado al guardar")
        self.lbl_qr_cliente.pack(pady=10)
        
        scrollable_frame.columnconfigure(0, weight=2)
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.rowconfigure(1, weight=1)

    def agregar_otro_servicio(self):
        if not self.servicio_var.get():
            messagebox.showwarning("Advertencia", "Seleccione primero un servicio")
            return
            
        if self.servicio_var.get() == "Otros" and not self.ent_especificar.get():
            messagebox.showwarning("Advertencia", "Especifique el servicio")
            return
            
        if self.servicio_var.get() not in ["Foto Estudio", "Otros"] and not self.ent_cantidad.get():
            messagebox.showwarning("Advertencia", "Ingrese la cantidad")
            return
            
        servicio_actual = self.servicio_var.get()
        if self.servicio_var.get() == "Otros":
            servicio_actual += f" ({self.ent_especificar.get()})"
            
        if self.servicio_var.get() not in ["Foto Estudio", "Otros"]:
            servicio_actual += f" - Cantidad: {self.ent_cantidad.get()}"
            
        desc_actual = self.ent_desc.get("1.0", tk.END).strip()
        if desc_actual:
            nueva_desc = f"{desc_actual}\n\n{servicio_actual}"
        else:
            nueva_desc = servicio_actual
            
        self.ent_desc.delete("1.0", tk.END)
        self.ent_desc.insert("1.0", nueva_desc)
        
        self.servicio_var.set("")
        self.ent_especificar.delete(0, tk.END)
        self.ent_cantidad.delete(0, tk.END)

    def actualizar_cantidad_field(self, event=None):
        servicio = self.servicio_var.get()
        if servicio in ["Foto Estudio", "Otros"]:
            self.ent_cantidad.config(state=tk.DISABLED)
            self.ent_cantidad.delete(0, tk.END)
        else:
            self.ent_cantidad.config(state=tk.NORMAL)

    def formato_moneda(self, event):
        widget = event.widget
        value = widget.get().replace(".", "").replace("$", "").replace(",", "").strip()
        if not value:
            widget.delete(0, tk.END)
            return
        try:
            value = int(value)
            formatted = "${:,.0f}".format(value).replace(",", ".")
            widget.delete(0, tk.END)
            widget.insert(0, formatted)
        except ValueError:
            widget.delete(0, tk.END)
            widget.insert(0, "$0")

    def crear_tab_buscar(self):
        main_frame = ttk.Frame(self.tab_buscar)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        ttk.Label(scrollable_frame, text="BUSCAR CLIENTE", style='Title.TLabel').grid(row=0, column=0, columnspan=3, pady=10)
        
        frame_busqueda = ttk.Frame(scrollable_frame)
        frame_busqueda.grid(row=1, column=0, columnspan=3, pady=10, sticky="we")
        
        ttk.Label(frame_busqueda, text="Buscar por:").pack(side=tk.LEFT, padx=5)
        
        self.buscar_por = tk.StringVar(value="telefono")
        ttk.Radiobutton(frame_busqueda, text="Teléfono", variable=self.buscar_por, value="telefono").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_busqueda, text="Cédula", variable=self.buscar_por, value="cedula").pack(side=tk.LEFT, padx=5)
        
        self.ent_buscar = ttk.Entry(frame_busqueda, width=15, font=('Arial', 10))
        self.ent_buscar.pack(side=tk.LEFT, padx=5)
        self.ent_buscar.bind('<Return>', lambda e: self.buscar_cliente())
        
        btn_buscar = ttk.Button(frame_busqueda, text="Buscar", command=self.buscar_cliente)
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        btn_escanear = ttk.Button(frame_busqueda, text="Escanear QR", command=self.leer_qr)
        btn_escanear.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = ttk.Button(frame_busqueda, text="Limpiar", command=self.limpiar_busqueda)
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        frame_resultados = ttk.LabelFrame(scrollable_frame, text="Información del Cliente", padding=10)
        frame_resultados.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")
        
        ttk.Label(frame_resultados, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.lbl_nombre = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_nombre.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Cédula:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.lbl_cedula = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_cedula.grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Teléfono:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.lbl_telefono = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_telefono.grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Servicio:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.lbl_servicio = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_servicio.grid(row=3, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Cantidad:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.lbl_cantidad = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_cantidad.grid(row=4, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Descripción:").grid(row=5, column=0, sticky="nw", padx=5, pady=2)
        self.lbl_descripcion = ttk.Label(frame_resultados, text="", wraplength=400, justify="left", font=('Arial', 10))
        self.lbl_descripcion.grid(row=5, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Total:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.lbl_total = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_total.grid(row=6, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Abono:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        self.lbl_abono = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_abono.grid(row=7, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Saldo:").grid(row=8, column=0, sticky="w", padx=5, pady=2)
        self.lbl_saldo = ttk.Label(frame_resultados, text="", font=("Arial", 10, "bold"))
        self.lbl_saldo.grid(row=8, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Fecha creación:").grid(row=9, column=0, sticky="w", padx=5, pady=2)
        self.lbl_fecha_creacion = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_fecha_creacion.grid(row=9, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Fecha entrega:").grid(row=10, column=0, sticky="w", padx=5, pady=2)
        self.lbl_fecha_entrega = ttk.Label(frame_resultados, text="", font=('Arial', 10))
        self.lbl_fecha_entrega.grid(row=10, column=1, sticky="w", pady=2)
        
        ttk.Label(frame_resultados, text="Estado:").grid(row=11, column=0, sticky="w", padx=5, pady=2)
        self.lbl_entregado = ttk.Label(frame_resultados, text="", font=('Arial', 10, 'bold'))
        self.lbl_entregado.grid(row=11, column=1, sticky="w", pady=2)
        
        frame_botones = ttk.Frame(frame_resultados)
        frame_botones.grid(row=12, column=0, columnspan=2, pady=10)
        
        self.btn_entregado = ttk.Button(frame_botones, text="Marcar como Entregado", command=self.marcar_entregado)
        self.btn_entregado.pack(side=tk.LEFT, padx=5)
        
        self.btn_editar = ttk.Button(frame_botones, text="Editar Información del Cliente", command=self.editar_cliente)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        self.btn_entregado.pack_forget()
        self.btn_editar.pack_forget()
        
        frame_qr = ttk.LabelFrame(scrollable_frame, text="Códigos QR", padding=10)
        frame_qr.grid(row=2, column=2, pady=10, sticky="nsew")
        
        ttk.Label(frame_qr, text="Código para el cliente:").pack(pady=5)
        self.lbl_qr_busqueda_cliente = ttk.Label(frame_qr)
        self.lbl_qr_busqueda_cliente.pack(pady=5)
        
        ttk.Label(frame_qr, text="Código para el negocio:").pack(pady=5)
        self.lbl_qr_busqueda_negocio = ttk.Label(frame_qr)
        self.lbl_qr_busqueda_negocio.pack(pady=5)
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(2, weight=1)
        scrollable_frame.rowconfigure(2, weight=1)

    def limpiar_busqueda(self):
        self.ent_buscar.delete(0, tk.END)
        self.lbl_nombre.config(text="")
        self.lbl_cedula.config(text="")
        self.lbl_telefono.config(text="")
        self.lbl_servicio.config(text="")
        self.lbl_cantidad.config(text="")
        self.lbl_descripcion.config(text="")
        self.lbl_total.config(text="")
        self.lbl_abono.config(text="")
        self.lbl_saldo.config(text="")
        self.lbl_fecha_creacion.config(text="")
        self.lbl_fecha_entrega.config(text="")
        self.lbl_entregado.config(text="")
        self.lbl_qr_busqueda_cliente.config(image="", text="")
        self.lbl_qr_busqueda_negocio.config(image="", text="")
        self.btn_entregado.pack_forget()
        self.btn_editar.pack_forget()
        self.cliente_actual = None

    def leer_qr(self):
        try:
            messagebox.showinfo("Información", "Por favor escanee el código QR con Barcode to PC Server")
            qr_data = simpledialog.askstring("Escanear QR", "Ingrese el código QR escaneado:")
            if qr_data:
                self.buscar_cliente_por_qr(qr_data)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el código QR: {str(e)}")

    def buscar_cliente_por_qr(self, qr_data):
        try:
            lineas = qr_data.split('\n')
            telefono = None
            for linea in lineas:
                if "Teléfono:" in linea:
                    telefono = linea.split(":")[1].strip()
                    break
            if telefono:
                self.ent_buscar.delete(0, tk.END)
                self.ent_buscar.insert(0, telefono)
                self.buscar_por.set("telefono")
                self.buscar_cliente()
            else:
                messagebox.showwarning("Advertencia", "No se pudo extraer el teléfono del código QR")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el código QR: {str(e)}")

    def crear_tab_imprimir(self):
        marco = ttk.Frame(self.tab_imprimir, padding=15)
        marco.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(marco)
        scrollbar = ttk.Scrollbar(marco, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        ttk.Label(scrollable_frame, text="IMPRIMIR CÓDIGOS QR", style='Title.TLabel').grid(row=0, column=0, columnspan=3, pady=10)
        
        frame_busqueda = ttk.Frame(scrollable_frame)
        frame_busqueda.grid(row=1, column=0, columnspan=3, pady=10, sticky="we")
        
        ttk.Label(frame_busqueda, text="Buscar por:").pack(side=tk.LEFT, padx=5)
        
        self.buscar_por_imprimir = tk.StringVar(value="telefono")
        ttk.Radiobutton(frame_busqueda, text="Teléfono", variable=self.buscar_por_imprimir, value="telefono").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_busqueda, text="Cédula", variable=self.buscar_por_imprimir, value="cedula").pack(side=tk.LEFT, padx=5)
        
        self.ent_imprimir = ttk.Entry(frame_busqueda, width=15, font=('Arial', 10))
        self.ent_imprimir.pack(side=tk.LEFT, padx=5)
        self.ent_imprimir.bind('<Return>', lambda e: self.cargar_para_imprimir())
        
        btn_buscar = ttk.Button(frame_busqueda, text="Buscar", command=self.cargar_para_imprimir)
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        btn_escanear = ttk.Button(frame_busqueda, text="Escanear QR", command=self.leer_qr_imprimir)
        btn_escanear.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = ttk.Button(frame_busqueda, text="Limpiar", command=self.limpiar_imprimir)
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        frame_qr = ttk.LabelFrame(scrollable_frame, text="Códigos QR para Imprimir", padding=10)
        frame_qr.grid(row=2, column=1, columnspan=2, pady=10, sticky="nsew")
        
        self.canvas_etiquetas = tk.Canvas(frame_qr, width=600, height=300, bg="white")
        self.canvas_etiquetas.pack(pady=10)
        
        btn_imprimir = ttk.Button(frame_qr, text="Imprimir Ambos Códigos", command=self.seleccionar_impresora, style='TButton')
        btn_imprimir.pack(pady=15, ipady=5)
        
        frame_info = ttk.LabelFrame(scrollable_frame, text="Detalles del Cliente", padding=10)
        frame_info.grid(row=2, column=0, pady=10, sticky="nsew")
        
        ttk.Label(frame_info, text="Cliente:").grid(row=0, column=0, sticky="w", padx=5)
        self.lbl_info_cliente = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_cliente.grid(row=0, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Cédula:").grid(row=1, column=0, sticky="w", padx=5)
        self.lbl_info_cedula = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_cedula.grid(row=1, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Teléfono:").grid(row=2, column=0, sticky="w", padx=5)
        self.lbl_info_telefono = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_telefono.grid(row=2, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Servicio:").grid(row=3, column=0, sticky="w", padx=5)
        self.lbl_info_servicio = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_servicio.grid(row=3, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Saldo:").grid(row=4, column=0, sticky="w", padx=5)
        self.lbl_info_saldo = ttk.Label(frame_info, text="", font=("Arial", 10, "bold"))
        self.lbl_info_saldo.grid(row=4, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Fecha creación:").grid(row=5, column=0, sticky="w", padx=5)
        self.lbl_info_fecha = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_fecha.grid(row=5, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Fecha entrega:").grid(row=6, column=0, sticky="w", padx=5)
        self.lbl_info_fecha_entrega = ttk.Label(frame_info, text="", font=('Arial', 10))
        self.lbl_info_fecha_entrega.grid(row=6, column=1, sticky="w")
        
        ttk.Label(frame_info, text="Estado:").grid(row=7, column=0, sticky="w", padx=5)
        self.lbl_info_estado = ttk.Label(frame_info, text="", font=('Arial', 10, 'bold'))
        self.lbl_info_estado.grid(row=7, column=1, sticky="w")
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(2, weight=1)
        scrollable_frame.rowconfigure(2, weight=1)

    def leer_qr_imprimir(self):
        try:
            messagebox.showinfo("Información", "Por favor escanee el código QR con Barcode to PC Server")
            qr_data = simpledialog.askstring("Escanear QR", "Ingrese el código QR escaneado:")
            if qr_data:
                lineas = qr_data.split('\n')
                telefono = None
                for linea in lineas:
                    if "Teléfono:" in linea:
                        telefono = linea.split(":")[1].strip()
                        break
                if telefono:
                    self.ent_imprimir.delete(0, tk.END)
                    self.ent_imprimir.insert(0, telefono)
                    self.buscar_por_imprimir.set("telefono")
                    self.cargar_para_imprimir()
                else:
                    messagebox.showwarning("Advertencia", "No se pudo extraer el teléfono del código QR")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el código QR: {str(e)}")

    def limpiar_imprimir(self):
        self.ent_imprimir.delete(0, tk.END)
        self.lbl_info_cliente.config(text="")
        self.lbl_info_cedula.config(text="")
        self.lbl_info_telefono.config(text="")
        self.lbl_info_servicio.config(text="")
        self.lbl_info_saldo.config(text="")
        self.lbl_info_fecha.config(text="")
        self.lbl_info_fecha_entrega.config(text="")
        self.lbl_info_estado.config(text="")
        self.canvas_etiquetas.delete("all")
        if hasattr(self, 'img_cliente_tk'):
            del self.img_cliente_tk
        if hasattr(self, 'img_negocio_tk'):
            del self.img_negocio_tk

    def seleccionar_impresora(self):
        if not hasattr(self, 'img_cliente') or not hasattr(self, 'img_negocio'):
            messagebox.showwarning("Advertencia", "No hay códigos QR para imprimir. Busque un cliente primero.")
            return
            
        impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        if not impresoras:
            messagebox.showerror("Error", "No se encontraron impresoras instaladas")
            return
        
        impresora_window = tk.Toplevel(self.root)
        impresora_window.title("Seleccionar Impresora")
        impresora_window.geometry("400x300")
        
        ttk.Label(impresora_window, text="Seleccione una impresora:").pack(pady=10)
        
        lista_impresoras = tk.Listbox(impresora_window, width=50, height=10)
        lista_impresoras.pack(pady=10, padx=10)
        
        for i, impresora in enumerate(impresoras):
            lista_impresoras.insert(tk.END, impresora[2])
        
        def imprimir_seleccion():
            seleccion = lista_impresoras.curselection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una impresora")
                return
            impresora_seleccionada = impresoras[seleccion[0]][2]
            impresora_window.destroy()
            self.imprimir_qr(impresora_seleccionada)
        
        btn_imprimir = ttk.Button(impresora_window, text="Imprimir", command=imprimir_seleccion)
        btn_imprimir.pack(pady=10)

    def crear_tab_usuarios(self):
        marco = ttk.Frame(self.tab_usuarios, padding=15)
        marco.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(marco, text="GESTIÓN DE USUARIOS", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        
        self.tree_usuarios = ttk.Treeview(marco, columns=('usuario',), show='headings')
        self.tree_usuarios.heading('usuario', text='Usuario')
        self.tree_usuarios.grid(row=1, column=0, columnspan=2, pady=10, sticky='nsew')
        
        btn_agregar = ttk.Button(marco, text="Agregar Usuario", command=self.agregar_usuario)
        btn_agregar.grid(row=2, column=0, pady=10, padx=5, sticky='ew')
        
        btn_eliminar = ttk.Button(marco, text="Eliminar Usuario", command=self.eliminar_usuario)
        btn_eliminar.grid(row=2, column=1, pady=10, padx=5, sticky='ew')
        
        self.actualizar_lista_usuarios()

    def actualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        usuarios = self.cargar_usuarios()
        for usuario in usuarios:
            if usuario['usuario'] != 'admin':
                self.tree_usuarios.insert('', 'end', values=(usuario['usuario'],))

    def agregar_usuario(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar Usuario")
        add_window.geometry("300x200")
        add_window.resizable(False, False)
        
        ttk.Label(add_window, text="Nuevo Usuario:").pack(pady=5)
        entry_usuario = ttk.Entry(add_window)
        entry_usuario.pack(pady=5)
        entry_usuario.focus_set()
        
        ttk.Label(add_window, text="Contraseña:").pack(pady=5)
        entry_contrasena = ttk.Entry(add_window, show="*")
        entry_contrasena.pack(pady=5)
        
        def guardar_usuario():
            usuario = entry_usuario.get().strip()
            contrasena = entry_contrasena.get().strip()
            if not usuario or not contrasena:
                messagebox.showwarning("Error", "Debe ingresar usuario y contraseña")
                return
            usuarios = self.cargar_usuarios()
            if any(u['usuario'] == usuario for u in usuarios):
                messagebox.showwarning("Error", "El usuario ya existe")
                return
            usuarios.append({'usuario': usuario, 'contrasena': self.hash_password(contrasena)})
            with open(self.archivo_usuarios, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['usuario', 'contrasena'])
                writer.writeheader()
                writer.writerows(usuarios)
            messagebox.showinfo("Éxito", "Usuario agregado correctamente")
            self.actualizar_lista_usuarios()
            add_window.destroy()
        
        btn_guardar = ttk.Button(add_window, text="Guardar", command=guardar_usuario)
        btn_guardar.pack(pady=10)
        entry_contrasena.bind('<Return>', lambda e: btn_guardar.invoke())

    def eliminar_usuario(self):
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un usuario")
            return
        usuario = self.tree_usuarios.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario {usuario}?"):
            usuarios = self.cargar_usuarios()
            usuarios = [u for u in usuarios if u['usuario'] != usuario]
            with open(self.archivo_usuarios, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['usuario', 'contrasena'])
                writer.writeheader()
                writer.writerows(usuarios)
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            self.actualizar_lista_usuarios()

    def generar_etiqueta(self, data, tipo, telefono):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img_qr = img_qr.resize((250, 250), Image.LANCZOS)
        
        img_final = Image.new("RGB", (600, 600), "white")
        draw = ImageDraw.Draw(img_final)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_bold = ImageFont.truetype("arialbd.ttf", 18)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        if self.icono_negocio:
            icono = self.icono_negocio.copy().resize((40, 40), Image.LANCZOS)
            img_final.paste(icono, (20, 20), icono if icono.mode == 'RGBA' else None)
        
        y_pos = 20
        titulo = "COMPROBANTE CLIENTE" if tipo == "cliente" else "REGISTRO NEGOCIO"
        draw.text((70 if self.icono_negocio else 20, y_pos), titulo, fill="black", font=font_bold)
        y_pos += 40
        
        lineas = data.split("\n")
        for linea in lineas:
            if linea.strip():
                palabras = linea.strip().split()
                linea_actual = ""
                for palabra in palabras:
                    if draw.textlength(linea_actual + palabra, font=font) < 300:
                        linea_actual += palabra + " "
                    else:
                        draw.text((20, y_pos), linea_actual.strip(), fill="black", font=font)
                        y_pos += 20
                        linea_actual = palabra + " "
                if linea_actual:
                    draw.text((20, y_pos), linea_actual.strip(), fill="black", font=font)
                    y_pos += 20
                if y_pos > 400:
                    break
        
        nota = "WhatsApp: 3196917534\nDespués de 30 días no respondemos\npor su trabajo ni abonos realizados"
        draw.text((20, 500), nota, fill="black", font=font)
        
        img_final.paste(img_qr, (320, 50))
        
        qr_path = os.path.join(self.carpeta_qr, f"qr_{tipo}_{telefono}_{int(time.time())}.png")
        img_final.save(qr_path)
        
        return qr_path, img_final

    def guardar_cliente(self):
        try:
            if not self.validar_campos():
                return
                
            nombre = self.ent_nombre.get().strip()
            cedula = self.ent_cedula.get().strip()
            telefono = self.ent_telefono.get().strip()
            servicio = self.servicio_var.get()
            especificar = self.ent_especificar.get().strip() if servicio == "Otros" else ""
            cantidad = self.ent_cantidad.get().strip() if servicio not in ["Foto Estudio", "Otros"] else "1"
            descripcion = self.ent_desc.get("1.0", tk.END).strip()
            
            total = self.ent_total.get().replace("$", "").replace(".", "").strip()
            abono = self.ent_abono.get().replace("$", "").replace(".", "").strip()
            
            try:
                total_num = int(total)
                abono_num = int(abono) if abono else 0
                if abono_num > total_num:
                    messagebox.showwarning("Advertencia", "El abono no puede ser mayor al total")
                    return
                saldo = total_num - abono_num
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos para total y abono")
                return
            
            fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fecha_entrega = self.ent_fecha_entrega.get().strip()
            
            if not cedula.isdigit() or not telefono.isdigit():
                messagebox.showwarning("Advertencia", "Cédula y teléfono deben ser números")
                return
            
            try:
                datetime.strptime(fecha_entrega, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato de fecha inválido (YYYY-MM-DD)")
                return
            
            hora_actual = datetime.now().strftime("%I:%M %p")
            qr_data = f"""
            📷 FOTO CAR STUDIO
            --------------------------
            Cliente: {nombre}
            Cédula: {cedula}
            Teléfono: {telefono}
            Servicio: {servicio} {especificar}
            Cantidad: {cantidad}
            Abono: ${abono_num:,}
            Saldo: ${saldo:,}
            Fecha: {fecha_creacion.split()[0]}
            Hora: {hora_actual}
            Entrega: {fecha_entrega}
            --------------------------
            Descripción: {descripcion}
            """
            
            qr_cliente, img_cliente = self.generar_etiqueta(qr_data, "cliente", telefono)
            qr_negocio, img_negocio = self.generar_etiqueta(qr_data, "negocio", telefono)
            
            self.mostrar_qr(img_cliente, self.lbl_qr_cliente)
            
            fecha_vencimiento = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            nuevo_cliente = {
                'nombre': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'servicio': f"{servicio} {especificar}".strip(),
                'descripcion': descripcion,
                'cantidad': cantidad,
                'total': str(total_num),
                'abono': str(abono_num),
                'saldo': str(saldo),
                'qr_cliente': os.path.basename(qr_cliente),
                'qr_negocio': os.path.basename(qr_negocio),
                'fecha_creacion': fecha_creacion,
                'fecha_entrega': fecha_entrega,
                'fecha_vencimiento': fecha_vencimiento,
                'entregado': "No"
            }
            
            self.clientes.append(nuevo_cliente)
            self.guardar_clientes()
            
            self.ent_nombre.delete(0, tk.END)
            self.ent_cedula.delete(0, tk.END)
            self.ent_telefono.delete(0, tk.END)
            self.servicio_var.set("")
            self.ent_especificar.delete(0, tk.END)
            self.ent_cantidad.delete(0, tk.END)
            self.ent_desc.delete("1.0", tk.END)
            self.ent_total.delete(0, tk.END)
            self.ent_abono.delete(0, tk.END)
            self.ent_fecha_entrega.delete(0, tk.END)
            self.ent_fecha_entrega.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
            
            messagebox.showinfo("Éxito", "Cliente guardado correctamente\nDos códigos QR generados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")

    def validar_campos(self):
        campos = [
            (self.ent_nombre, "nombre del cliente"),
            (self.ent_cedula, "cédula del cliente"),
            (self.ent_telefono, "teléfono del cliente"),
            (self.ent_total, "total a pagar"),
            (self.ent_abono, "abono inicial"),
            (self.ent_fecha_entrega, "fecha de entrega")
        ]
        for campo, nombre in campos:
            if not campo.get().strip():
                messagebox.showwarning("Advertencia", f"Debe ingresar el {nombre}")
                return False
        
        if not self.servicio_var.get():
            messagebox.showwarning("Advertencia", "Debe seleccionar un servicio")
            return False
            
        servicio = self.servicio_var.get()
        if servicio == "Otros" and not self.ent_especificar.get().strip():
            messagebox.showwarning("Advertencia", "Debe especificar el servicio")
            return False
            
        if servicio not in ["Foto Estudio", "Otros"] and not self.ent_cantidad.get().strip():
            messagebox.showwarning("Advertencia", f"Debe ingresar la cantidad para {servicio}")
            return False
            
        return True

    def mostrar_qr(self, img, label_widget=None):
        try:
            if img is None:
                if hasattr(self, 'img_cliente') and hasattr(self, 'img_negocio'):
                    self.canvas_etiquetas.delete("all")
                    cliente_img = self.img_cliente.resize((300, 300), Image.LANCZOS)
                    negocio_img = self.img_negocio.resize((300, 300), Image.LANCZOS)
                    self.img_cliente_tk = ImageTk.PhotoImage(cliente_img)
                    self.img_negocio_tk = ImageTk.PhotoImage(negocio_img)
                    self.canvas_etiquetas.create_image(0, 0, anchor=tk.NW, image=self.img_cliente_tk)
                    self.canvas_etiquetas.create_image(300, 0, anchor=tk.NW, image=self.img_negocio_tk)
                return
                
            if isinstance(img, str):
                img = Image.open(img)
            
            if label_widget:
                img_resized = img.resize((400, 400), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img_resized)
                label_widget.config(image=img_tk)
                label_widget.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el QR: {str(e)}")

    def buscar_cliente(self):
        criterio = self.buscar_por.get()
        valor = self.ent_buscar.get().strip()
        
        if not valor:
            messagebox.showwarning("Advertencia", f"Ingrese un {criterio}")
            return
            
        cliente_encontrado = None
        for cliente in self.clientes:
            if cliente.get(criterio, "") == valor:
                cliente_encontrado = cliente
                break
        
        if not cliente_encontrado:
            messagebox.showinfo("No encontrado", "Cliente no registrado")
            self.limpiar_busqueda()
            return
        
        self.cliente_actual = cliente_encontrado
        
        self.lbl_nombre.config(text=cliente_encontrado['nombre'])
        self.lbl_cedula.config(text=cliente_encontrado.get('cedula', ''))
        self.lbl_telefono.config(text=cliente_encontrado['telefono'])
        self.lbl_servicio.config(text=cliente_encontrado.get('servicio', ''))
        self.lbl_cantidad.config(text=cliente_encontrado.get('cantidad', ''))
        self.lbl_descripcion.config(text=cliente_encontrado.get('descripcion', ''))
        
        try:
            total = int(cliente_encontrado.get('total', '0'))
            abono = int(cliente_encontrado.get('abono', '0'))
            saldo = int(cliente_encontrado.get('saldo', '0'))
            self.lbl_total.config(text=f"${total:,}".replace(",", "."))
            self.lbl_abono.config(text=f"${abono:,}".replace(",", "."))
            self.lbl_saldo.config(text=f"${saldo:,}".replace(",", "."), foreground="red" if saldo > 0 else "black")
        except ValueError as e:
            messagebox.showerror("Error", f"Error en datos monetarios: {e}")
            return
        
        if 'fecha_creacion' in cliente_encontrado and cliente_encontrado['fecha_creacion']:
            fecha = datetime.strptime(cliente_encontrado['fecha_creacion'], "%Y-%m-%d %H:%M:%S")
            self.lbl_fecha_creacion.config(text=fecha.strftime("%d/%m/%Y %I:%M %p"))
        else:
            self.lbl_fecha_creacion.config(text="No registrada")
        
        if 'fecha_entrega' in cliente_encontrado and cliente_encontrado['fecha_entrega']:
            try:
                fecha = datetime.strptime(cliente_encontrado['fecha_entrega'], "%Y-%m-%d")
                self.lbl_fecha_entrega.config(text=fecha.strftime("%d/%m/%Y"))
                ahora = datetime.now().date()
                fecha_entrega = fecha.date()
                dias_restantes = (fecha_entrega - ahora).days
                
                if cliente_encontrado.get('entregado', 'No') == 'Sí':
                    color = "green"
                elif dias_restantes < 0:
                    color = "red"
                elif dias_restantes <= 2:
                    color = "orange"
                else:
                    color = "black"
                self.lbl_fecha_entrega.config(foreground=color)
            except ValueError:
                self.lbl_fecha_entrega.config(text=cliente_encontrado['fecha_entrega'])
        else:
            self.lbl_fecha_entrega.config(text="No registrada")
        
        entregado = cliente_encontrado.get('entregado', 'No')
        self.lbl_entregado.config(text="ENTREGADO" if entregado == 'Sí' else "NO ENTREGADO", 
                                foreground="green" if entregado == 'Sí' else "red")
        
        if entregado == 'No':
            self.btn_entregado.pack(side=tk.LEFT, padx=5)
            self.btn_editar.pack(side=tk.LEFT, padx=5)
        else:
            self.btn_entregado.pack_forget()
            self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        qr_cliente = os.path.join(self.carpeta_qr, cliente_encontrado['qr_cliente'])
        qr_negocio = os.path.join(self.carpeta_qr, cliente_encontrado['qr_negocio'])
        
        if os.path.exists(qr_cliente) and os.path.exists(qr_negocio):
            self.img_cliente = Image.open(qr_cliente)
            self.img_negocio = Image.open(qr_negocio)
            self.mostrar_qr(self.img_cliente, self.lbl_qr_busqueda_cliente)
            self.mostrar_qr(self.img_negocio, self.lbl_qr_busqueda_negocio)
        else:
            messagebox.showwarning("Advertencia", "No se encontraron los archivos QR")
            self.lbl_qr_busqueda_cliente.config(text="QR no disponible")
            self.lbl_qr_busqueda_negocio.config(text="QR no disponible")

    def editar_cliente(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
            
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Cliente")
        edit_window.geometry("500x600")
        
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        ent_nombre = ttk.Entry(edit_window, width=40)
        ent_nombre.pack(pady=5)
        ent_nombre.insert(0, self.cliente_actual['nombre'])
        ent_nombre.focus_set()
        
        ttk.Label(edit_window, text="Cédula:").pack(pady=5)
        ent_cedula = ttk.Entry(edit_window, width=20)
        ent_cedula.pack(pady=5)
        ent_cedula.insert(0, self.cliente_actual.get('cedula', ''))
        
        ttk.Label(edit_window, text="Teléfono:").pack(pady=5)
        ent_telefono = ttk.Entry(edit_window, width=20)
        ent_telefono.pack(pady=5)
        ent_telefono.insert(0, self.cliente_actual['telefono'])
        
        ttk.Label(edit_window, text="Servicio:").pack(pady=5)
        ent_servicio = ttk.Entry(edit_window, width=40)
        ent_servicio.pack(pady=5)
        ent_servicio.insert(0, self.cliente_actual.get('servicio', ''))
        
        ttk.Label(edit_window, text="Descripción:").pack(pady=5)
        ent_desc = tk.Text(edit_window, width=50, height=5, wrap=tk.WORD)
        ent_desc.pack(pady=5)
        ent_desc.insert("1.0", self.cliente_actual.get('descripcion', ''))
        
        ttk.Label(edit_window, text="Total:").pack(pady=5)
        ent_total = ttk.Entry(edit_window, width=15)
        ent_total.pack(pady=5)
        ent_total.insert(0, f"${int(self.cliente_actual.get('total', '0')):,}".replace(",", "."))
        ent_total.bind("<KeyRelease>", self.formato_moneda)
        
        ttk.Label(edit_window, text="Abono:").pack(pady=5)
        ent_abono = ttk.Entry(edit_window, width=15)
        ent_abono.pack(pady=5)
        ent_abono.insert(0, f"${int(self.cliente_actual.get('abono', '0')):,}".replace(",", "."))
        ent_abono.bind("<KeyRelease>", self.formato_moneda)
        
        ttk.Label(edit_window, text="Fecha de entrega (YYYY-MM-DD):").pack(pady=5)
        ent_fecha_entrega = ttk.Entry(edit_window, width=15)
        ent_fecha_entrega.pack(pady=5)
        ent_fecha_entrega.insert(0, self.cliente_actual.get('fecha_entrega', ''))
        
        def guardar_cambios():
            try:
                if not ent_cedula.get().strip().isdigit() or not ent_telefono.get().strip().isdigit():
                    messagebox.showwarning("Advertencia", "Cédula y teléfono deben ser números")
                    return
                
                try:
                    datetime.strptime(ent_fecha_entrega.get().strip(), "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Advertencia", "Formato de fecha inválido (YYYY-MM-DD)")
                    return
                
                total_str = ent_total.get().replace("$", "").replace(".", "").strip()
                abono_str = ent_abono.get().replace("$", "").replace(".", "").strip()
                
                try:
                    total_num = int(total_str)
                    abono_num = int(abono_str) if abono_str else 0
                    if abono_num > total_num:
                        messagebox.showwarning("Advertencia", "El abono no puede ser mayor al total")
                        return
                    saldo = total_num - abono_num
                except ValueError:
                    messagebox.showerror("Error", "Ingrese valores numéricos válidos para total y abono")
                    return
                
                self.cliente_actual['nombre'] = ent_nombre.get().strip()
                self.cliente_actual['cedula'] = ent_cedula.get().strip()
                self.cliente_actual['telefono'] = ent_telefono.get().strip()
                self.cliente_actual['servicio'] = ent_servicio.get().strip()
                self.cliente_actual['descripcion'] = ent_desc.get("1.0", tk.END).strip()
                self.cliente_actual['total'] = str(total_num)
                self.cliente_actual['abono'] = str(abono_num)
                self.cliente_actual['saldo'] = str(saldo)
                self.cliente_actual['fecha_entrega'] = ent_fecha_entrega.get().strip()
                
                nombre = self.cliente_actual['nombre']
                cedula = self.cliente_actual['cedula']
                telefono = self.cliente_actual['telefono']
                servicio = self.cliente_actual['servicio']
                descripcion = self.cliente_actual['descripcion']
                fecha_creacion = self.cliente_actual['fecha_creacion']
                fecha_entrega = self.cliente_actual['fecha_entrega']
                
                hora_actual = datetime.now().strftime("%I:%M %p")
                qr_data = f"""
                📷 FOTO CAR STUDIO
                --------------------------
                Cliente: {nombre}
                Cédula: {cedula}
                Teléfono: {telefono}
                Servicio: {servicio}
                Abono: ${abono_num:,}
                Saldo: ${saldo:,}
                Fecha: {fecha_creacion.split()[0]}
                Hora: {hora_actual}
                Entrega: {fecha_entrega}
                --------------------------
                Descripción: {descripcion}
                """
                
                qr_cliente, img_cliente = self.generar_etiqueta(qr_data, "cliente", telefono)
                qr_negocio, img_negocio = self.generar_etiqueta(qr_data, "negocio", telefono)
                
                self.cliente_actual['qr_cliente'] = os.path.basename(qr_cliente)
                self.cliente_actual['qr_negocio'] = os.path.basename(qr_negocio)
                
                self.guardar_clientes()
                messagebox.showinfo("Éxito", "Cambios guardados correctamente")
                edit_window.destroy()
                self.buscar_cliente()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar cambios: {str(e)}")
        
        btn_guardar = ttk.Button(edit_window, text="Guardar Cambios", command=guardar_cambios)
        btn_guardar.pack(pady=10)

    def marcar_entregado(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
            
        self.cliente_actual['entregado'] = 'Sí'
        self.guardar_clientes()
        messagebox.showinfo("Éxito", "Cliente marcado como entregado")
        self.buscar_cliente()

    def imprimir_qr(self, impresora_seleccionada):
        try:
            qr_cliente = os.path.join(self.carpeta_qr, self.cliente_actual['qr_cliente'])
            qr_negocio = os.path.join(self.carpeta_qr, self.cliente_actual['qr_negocio'])
            
            if not os.path.exists(qr_cliente) or not os.path.exists(qr_negocio):
                messagebox.showerror("Error", "No se encontraron los archivos QR para imprimir")
                return
            
            img_cliente = Image.open(qr_cliente)
            img_negocio = Image.open(qr_negocio)
            
            img_cliente_resized = img_cliente.resize((600, 600), Image.LANCZOS)
            img_negocio_resized = img_negocio.resize((600, 600), Image.LANCZOS)
            
            img_combinada = Image.new("RGB", (1200, 600), "white")
            img_combinada.paste(img_cliente_resized, (0, 0))
            img_combinada.paste(img_negocio_resized, (600, 0))
            
            temp_path = os.path.join(self.carpeta_qr, f"temp_combinada_{self.cliente_actual['telefono']}.png")
            img_combinada.save(temp_path)
            
            win32api.ShellExecute(
                0,
                "print",
                temp_path,
                f'"{impresora_seleccionada}"',
                ".",
                0
            )
            
            messagebox.showinfo("Impresión", f"Se envió la imagen combinada a la impresora: {impresora_seleccionada}")
            time.sleep(2)
            os.remove(temp_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir: {str(e)}")

    def cargar_para_imprimir(self):
        criterio = self.buscar_por_imprimir.get()
        valor = self.ent_imprimir.get().strip()
        
        if not valor:
            messagebox.showwarning("Advertencia", f"Ingrese un {criterio}")
            return
            
        cliente_encontrado = None
        for cliente in self.clientes:
            if cliente.get(criterio, "") == valor:
                cliente_encontrado = cliente
                break
        
        if not cliente_encontrado:
            messagebox.showinfo("No encontrado", "Cliente no registrado")
            self.limpiar_imprimir()
            return
        
        self.cliente_actual = cliente_encontrado
        
        self.lbl_info_cliente.config(text=cliente_encontrado['nombre'])
        self.lbl_info_cedula.config(text=cliente_encontrado.get('cedula', ''))
        self.lbl_info_telefono.config(text=cliente_encontrado['telefono'])
        self.lbl_info_servicio.config(text=cliente_encontrado.get('servicio', ''))
        
        try:
            saldo = int(cliente_encontrado.get('saldo', '0'))
            self.lbl_info_saldo.config(text=f"${saldo:,}".replace(",", "."), foreground="red" if saldo > 0 else "black")
        except ValueError:
            self.lbl_info_saldo.config(text="$0")
        
        if 'fecha_creacion' in cliente_encontrado and cliente_encontrado['fecha_creacion']:
            self.lbl_info_fecha.config(text=datetime.strptime(cliente_encontrado['fecha_creacion'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %I:%M %p"))
        else:
            self.lbl_info_fecha.config(text="No registrada")
            
        if 'fecha_entrega' in cliente_encontrado and cliente_encontrado['fecha_entrega']:
            self.lbl_info_fecha_entrega.config(text=datetime.strptime(cliente_encontrado['fecha_entrega'], "%Y-%m-%d").strftime("%d/%m/%Y"))
        else:
            self.lbl_info_fecha_entrega.config(text="No registrada")
            
        entregado = cliente_encontrado.get('entregado', 'No')
        self.lbl_info_estado.config(text="ENTREGADO" if entregado == 'Sí' else "NO ENTREGADO", 
                                  foreground="green" if entregado == 'Sí' else "red")
        
        qr_cliente = os.path.join(self.carpeta_qr, cliente_encontrado['qr_cliente'])
        qr_negocio = os.path.join(self.carpeta_qr, cliente_encontrado['qr_negocio'])
        
        if os.path.exists(qr_cliente) and os.path.exists(qr_negocio):
            self.img_cliente = Image.open(qr_cliente)
            self.img_negocio = Image.open(qr_negocio)
            self.mostrar_qr(None)
        else:
            messagebox.showwarning("Advertencia", "No se encontraron los archivos QR")
            self.canvas_etiquetas.delete("all")

    def exportar_clientes(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Guardar lista de clientes como"
            )
            if not file_path:
                return
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                campos = ['nombre', 'cedula', 'telefono', 'servicio', 'descripcion', 'cantidad', 
                         'total', 'abono', 'saldo', 'fecha_creacion', 'fecha_entrega', 'entregado']
                escritor = csv.DictWriter(f, fieldnames=campos)
                escritor.writeheader()
                for cliente in self.clientes:
                    cliente_export = {k: v for k, v in cliente.items() if k in campos}
                    escritor.writerow(cliente_export)
            messagebox.showinfo("Éxito", f"Lista de clientes exportada correctamente a:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la lista: {str(e)}")

    def crear_menu_principal(self):
        menubar = tk.Menu(self.root)
        
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Exportar clientes", command=self.exportar_clientes)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        if self.usuario_actual == 'admin':
            menu_herramientas = tk.Menu(menubar, tearoff=0)
            menu_herramientas.add_command(label="Respaldar datos", command=self.respaldar_datos)
            menu_herramientas.add_command(label="Restaurar datos", command=self.restaurar_datos)
            menubar.add_cascade(label="Herramientas", menu=menu_herramientas)
        
        self.root.config(menu=menubar)

    def respaldar_datos(self):
        try:
            carpeta_respaldo = "respaldos"
            os.makedirs(carpeta_respaldo, exist_ok=True)
            fecha_respaldo = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_respaldo = os.path.join(carpeta_respaldo, f"respaldo_{fecha_respaldo}.zip")
            import zipfile
            with zipfile.ZipFile(archivo_respaldo, 'w') as zipf:
                zipf.write(self.archivo_clientes, os.path.basename(self.archivo_clientes))
                zipf.write(self.archivo_usuarios, os.path.basename(self.archivo_usuarios))
                if os.path.exists(self.carpeta_qr):
                    for root, _, files in os.walk(self.carpeta_qr):
                        for file in files:
                            zipf.write(os.path.join(root, file), 
                                      os.path.relpath(os.path.join(root, file), 
                                      os.path.join(self.carpeta_qr, '..')))
            messagebox.showinfo("Éxito", f"Respaldo creado correctamente en:\n{archivo_respaldo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el respaldo: {str(e)}")

    def restaurar_datos(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")],
                title="Seleccionar archivo de respaldo"
            )
            if not file_path:
                return
            if not messagebox.askyesno("Confirmar", "¿Restaurar datos? Esto sobrescribirá los datos actuales."):
                return
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(".")
            self.clientes = self.cargar_clientes()
            messagebox.showinfo("Éxito", "Datos restaurados correctamente")
            self.notebook.select(self.tab_buscar)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar el respaldo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaFotografia(root)
    root.mainloop()
