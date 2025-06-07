import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta, date
import sqlite3
import calendar
import os
import sys
from tkcalendar import Calendar  # Necesitarás instalar esto: pip install tkcalendar

class PsicologoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PsicoGest - Gestión de Pacientes")
        self.root.geometry("1200x800")
        self.setup_icons()
        
        # Conexión a la base de datos
        self.db_path = self.get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        self.crear_tablas()
        
        # Variables
        self.fecha_actual = datetime.now()
        self.fecha_seleccionada = date.today()
        
        # Estilos
        self.setup_styles()
        
        # Interfaz
        self.crear_interfaz()
        self.actualizar_pacientes()
        self.actualizar_citas_dia()
        
        # Recordatorios al iniciar
        self.verificar_recordatorios()
    
    def get_db_path(self):
        # Para cuando se convierta a ejecutable
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(application_path, 'psicogest_db.db')
    
    def setup_icons(self):
        # Aquí podrías cargar iconos si los tienes
        pass
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Bold.TButton', font=('Arial', 9, 'bold'))
        style.configure('Red.TButton', foreground='red')
        style.configure('Green.TButton', foreground='green')
    
    def crear_tablas(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS pacientes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         nombre TEXT NOT NULL,
                         telefono TEXT,
                         email TEXT,
                         direccion TEXT,
                         fecha_nacimiento TEXT,
                         notas TEXT)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS citas
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         paciente_id INTEGER,
                         fecha TEXT NOT NULL,
                         hora TEXT NOT NULL,
                         duracion INTEGER DEFAULT 60,
                         estado TEXT DEFAULT 'pendiente',
                         notas TEXT,
                         FOREIGN KEY(paciente_id) REFERENCES pacientes(id))''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS recordatorios
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         cita_id INTEGER,
                         enviado INTEGER DEFAULT 0,
                         fecha_envio TEXT,
                         FOREIGN KEY(cita_id) REFERENCES citas(id))''')
        self.conn.commit()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo (calendario y controles)
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Calendario interactivo
        cal_frame = ttk.Frame(left_frame)
        cal_frame.pack(fill=tk.X, pady=10)
        self.cal = Calendar(cal_frame, selectmode='day', date_pattern='y-mm-dd',
                          mindate=date.today()-timedelta(days=365),
                          maxdate=date.today()+timedelta(days=365))
        self.cal.pack(fill=tk.X)
        self.cal.bind('<<CalendarSelected>>', self.seleccionar_fecha_calendario)
        
        # Controles rápidos
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Hoy", command=self.ir_a_hoy).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="+ Semana", command=self.avanzar_semana).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="- Semana", command=self.retroceder_semana).pack(side=tk.LEFT, padx=2)
        
        # Estadísticas rápidas
        stats_frame = ttk.LabelFrame(left_frame, text="Estadísticas")
        stats_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(stats_frame, text="Citas hoy:").pack(anchor='w')
        self.lbl_citas_hoy = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
        self.lbl_citas_hoy.pack(anchor='w')
        
        ttk.Label(stats_frame, text="Pacientes totales:").pack(anchor='w')
        self.lbl_total_pacientes = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
        self.lbl_total_pacientes.pack(anchor='w')
        
        # Panel derecho (detalles)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Pestañas
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de citas
        citas_frame = ttk.Frame(notebook)
        notebook.add(citas_frame, text="Citas")
        
        # Treeview de citas
        self.citas_tree = ttk.Treeview(citas_frame, columns=('hora', 'nombre', 'telefono', 'duracion', 'estado'), show='headings')
        self.citas_tree.heading('hora', text='Hora')
        self.citas_tree.heading('nombre', text='Paciente')
        self.citas_tree.heading('telefono', text='Teléfono')
        self.citas_tree.heading('duracion', text='Duración (min)')
        self.citas_tree.heading('estado', text='Estado')
        
        self.citas_tree.column('hora', width=80, anchor='center')
        self.citas_tree.column('nombre', width=150)
        self.citas_tree.column('telefono', width=100, anchor='center')
        self.citas_tree.column('duracion', width=80, anchor='center')
        self.citas_tree.column('estado', width=80, anchor='center')
        
        scroll_y = ttk.Scrollbar(citas_frame, orient=tk.VERTICAL, command=self.citas_tree.yview)
        self.citas_tree.configure(yscrollcommand=scroll_y.set)
        
        self.citas_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de pacientes
        pacientes_frame = ttk.Frame(notebook)
        notebook.add(pacientes_frame, text="Pacientes")
        
        # Treeview de pacientes
        self.pacientes_tree = ttk.Treeview(pacientes_frame, columns=('telefono', 'email', 'ultima_visita'), show='headings')
        self.pacientes_tree.heading('#0', text='Nombre')
        self.pacientes_tree.heading('telefono', text='Teléfono')
        self.pacientes_tree.heading('email', text='Email')
        self.pacientes_tree.heading('ultima_visita', text='Última Visita')
        
        self.pacientes_tree.column('#0', width=200)
        self.pacientes_tree.column('telefono', width=100, anchor='center')
        self.pacientes_tree.column('email', width=150)
        self.pacientes_tree.column('ultima_visita', width=100, anchor='center')
        
        scroll_y_p = ttk.Scrollbar(pacientes_frame, orient=tk.VERTICAL, command=self.pacientes_tree.yview)
        self.pacientes_tree.configure(yscrollcommand=scroll_y_p.set)
        
        self.pacientes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y_p.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(right_frame)
        toolbar_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar_frame, text="Nueva Cita", command=self.nueva_cita).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Nuevo Paciente", command=self.nuevo_paciente).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Editar", command=self.editar_seleccion).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Eliminar", command=self.eliminar_seleccion).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Registrar Pago", command=self.registrar_pago).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Reportes", command=self.mostrar_reportes).pack(side=tk.LEFT, padx=2)
        
        # Barra de estado
        self.status_bar = ttk.Label(right_frame, text="Listo", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5,0))
        
        # Actualizar estadísticas
        self.actualizar_estadisticas()
    
    def seleccionar_fecha_calendario(self, event=None):
        self.fecha_seleccionada = self.cal.selection_get()
        self.actualizar_citas_dia()
    
    def ir_a_hoy(self):
        self.cal.selection_set(date.today())
        self.fecha_seleccionada = date.today()
        self.actualizar_citas_dia()
    
    def avanzar_semana(self):
        nueva_fecha = self.cal.selection_get() + timedelta(days=7)
        self.cal.selection_set(nueva_fecha)
        self.fecha_seleccionada = nueva_fecha
        self.actualizar_citas_dia()
    
    def retroceder_semana(self):
        nueva_fecha = self.cal.selection_get() - timedelta(days=7)
        self.cal.selection_set(nueva_fecha)
        self.fecha_seleccionada = nueva_fecha
        self.actualizar_citas_dia()
    
    def actualizar_citas_dia(self):
        for item in self.citas_tree.get_children():
            self.citas_tree.delete(item)
        
        fecha_str = self.fecha_seleccionada.strftime("%Y-%m-%d")
        self.c.execute('''SELECT citas.id, citas.hora, pacientes.nombre, pacientes.telefono, 
                         citas.duracion, citas.estado
                         FROM citas JOIN pacientes ON citas.paciente_id = pacientes.id
                         WHERE citas.fecha=? ORDER BY citas.hora''', (fecha_str,))
        citas = self.c.fetchall()
        
        for cita in citas:
            estado = cita[5]
            tags = ('pendiente',) if estado == 'pendiente' else ('completada',) if estado == 'completada' else ('cancelada',)
            
            self.citas_tree.insert('', tk.END, values=(
                cita[1], cita[2], cita[3], cita[4], estado.capitalize()
            ), iid=cita[0], tags=tags)
        
        # Configurar colores por estado
        self.citas_tree.tag_configure('pendiente', background='#fffacd')
        self.citas_tree.tag_configure('completada', background='#e6ffe6')
        self.citas_tree.tag_configure('cancelada', background='#ffe6e6')
        
        self.status_bar.config(text=f"Mostrando citas para {self.fecha_seleccionada.strftime('%d/%m/%Y')}")
    
    def actualizar_pacientes(self):
        for item in self.pacientes_tree.get_children():
            self.pacientes_tree.delete(item)
        
        self.c.execute('''SELECT p.id, p.nombre, p.telefono, p.email, 
                         MAX(c.fecha) as ultima_visita
                         FROM pacientes p LEFT JOIN citas c ON p.id = c.paciente_id
                         GROUP BY p.id ORDER BY p.nombre''')
        pacientes = self.c.fetchall()
        
        for paciente in pacientes:
            ultima_visita = paciente[4] if paciente[4] else "Nunca"
            self.pacientes_tree.insert('', tk.END, text=paciente[1], values=(
                paciente[2], paciente[3], ultima_visita
            ), iid=paciente[0])
    
    def actualizar_estadisticas(self):
        # Citas hoy
        hoy = date.today().strftime("%Y-%m-%d")
        self.c.execute("SELECT COUNT(*) FROM citas WHERE fecha=?", (hoy,))
        citas_hoy = self.c.fetchone()[0]
        self.lbl_citas_hoy.config(text=str(citas_hoy))
        
        # Total pacientes
        self.c.execute("SELECT COUNT(*) FROM pacientes")
        total_pacientes = self.c.fetchone()[0]
        self.lbl_total_pacientes.config(text=str(total_pacientes))
    
    def nueva_cita(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Cita")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        paciente_var = tk.StringVar()
        fecha_var = tk.StringVar(value=self.fecha_seleccionada.strftime("%Y-%m-%d"))
        hora_var = tk.StringVar(value="09:00")
        duracion_var = tk.IntVar(value=60)
        notas_var = tk.StringVar()
        
        # Controles
        ttk.Label(dialog, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        # Combo de pacientes
        self.c.execute("SELECT id, nombre FROM pacientes ORDER BY nombre")
        pacientes = self.c.fetchall()
        paciente_names = [p[1] for p in pacientes]
        paciente_dict = {p[1]: p[0] for p in pacientes}
        
        paciente_cb = ttk.Combobox(dialog, textvariable=paciente_var, values=paciente_names)
        paciente_cb.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Fecha:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=fecha_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Hora:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=hora_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Spinbox(dialog, from_=30, to=180, increment=15, textvariable=duracion_var).grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Notas:").grid(row=4, column=0, padx=5, pady=5, sticky='ne')
        ttk.Entry(dialog, textvariable=notas_var).grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=lambda: self.guardar_cita(
            paciente_dict.get(paciente_var.get()), fecha_var.get(), hora_var.get(), 
            duracion_var.get(), notas_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Validación
        paciente_cb.focus()
    
    def guardar_cita(self, paciente_id, fecha, hora, duracion, notas, dialog):
        if not paciente_id:
            messagebox.showerror("Error", "Debe seleccionar un paciente")
            return
        
        try:
            self.c.execute('''INSERT INTO citas (paciente_id, fecha, hora, duracion, notas)
                            VALUES (?, ?, ?, ?, ?)''', 
                            (paciente_id, fecha, hora, duracion, notas))
            self.conn.commit()
            
            # Crear recordatorio
            self.c.execute("SELECT last_insert_rowid()")
            cita_id = self.c.fetchone()[0]
            self.c.execute('''INSERT INTO recordatorios (cita_id) VALUES (?)''', (cita_id,))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Cita guardada correctamente")
            dialog.destroy()
            self.actualizar_citas_dia()
            self.actualizar_pacientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la cita: {str(e)}")
    
    def nuevo_paciente(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Paciente")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        nombre_var = tk.StringVar()
        telefono_var = tk.StringVar()
        email_var = tk.StringVar()
        direccion_var = tk.StringVar()
        fnac_var = tk.StringVar()
        notas_var = tk.StringVar()
        
        # Controles
        ttk.Label(dialog, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=nombre_var).grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=telefono_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=email_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=direccion_var).grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Fecha nacimiento:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=fnac_var).grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Notas:").grid(row=5, column=0, padx=5, pady=5, sticky='ne')
        ttk.Entry(dialog, textvariable=notas_var).grid(row=5, column=1, padx=5, pady=5, sticky='we')
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=lambda: self.guardar_paciente(
            nombre_var.get(), telefono_var.get(), email_var.get(),
            direccion_var.get(), fnac_var.get(), notas_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        nombre_var.focus()
    
    def guardar_paciente(self, nombre, telefono, email, direccion, fnac, notas, dialog):
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            self.c.execute('''INSERT INTO pacientes 
                            (nombre, telefono, email, direccion, fecha_nacimiento, notas)
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                            (nombre, telefono, email, direccion, fnac, notas))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Paciente guardado correctamente")
            dialog.destroy()
            self.actualizar_pacientes()
            self.actualizar_estadisticas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el paciente: {str(e)}")
    
    def editar_seleccion(self):
        # Determinar qué pestaña está activa
        notebook = self.root.nametowidget(self.citas_tree.winfo_parent()).master
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # Pestaña de citas
            seleccion = self.citas_tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una cita para editar")
                return
            
            cita_id = seleccion[0]
            self.editar_cita(cita_id)
        else:  # Pestaña de pacientes
            seleccion = self.pacientes_tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un paciente para editar")
                return
            
            paciente_id = seleccion[0]
            self.editar_paciente(paciente_id)
    
    def editar_cita(self, cita_id):
        # Obtener datos de la cita
        self.c.execute('''SELECT paciente_id, fecha, hora, duracion, estado, notas 
                       FROM citas WHERE id=?''', (cita_id,))
        cita = self.c.fetchone()
        
        if not cita:
            messagebox.showerror("Error", "Cita no encontrada")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Cita")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        paciente_var = tk.StringVar()
        fecha_var = tk.StringVar(value=cita[1])
        hora_var = tk.StringVar(value=cita[2])
        duracion_var = tk.IntVar(value=cita[3])
        estado_var = tk.StringVar(value=cita[4])
        notas_var = tk.StringVar(value=cita[5] if cita[5] else "")
        
        # Obtener nombre del paciente
        self.c.execute("SELECT nombre FROM pacientes WHERE id=?", (cita[0],))
        nombre_paciente = self.c.fetchone()[0]
        paciente_var.set(nombre_paciente)
        
        # Controles
        ttk.Label(dialog, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Label(dialog, text=nombre_paciente).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Fecha:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=fecha_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Hora:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=hora_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Spinbox(dialog, from_=30, to=180, increment=15, textvariable=duracion_var).grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Estado:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        ttk.Combobox(dialog, textvariable=estado_var, values=['pendiente', 'completada', 'cancelada']).grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Notas:").grid(row=5, column=0, padx=5, pady=5, sticky='ne')
        ttk.Entry(dialog, textvariable=notas_var).grid(row=5, column=1, padx=5, pady=5, sticky='we')
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=lambda: self.actualizar_cita(
            cita_id, fecha_var.get(), hora_var.get(), duracion_var.get(),
            estado_var.get(), notas_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def actualizar_cita(self, cita_id, fecha, hora, duracion, estado, notas, dialog):
        try:
            self.c.execute('''UPDATE citas SET fecha=?, hora=?, duracion=?, estado=?, notas=?
                            WHERE id=?''', 
                            (fecha, hora, duracion, estado, notas, cita_id))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Cita actualizada correctamente")
            dialog.destroy()
            self.actualizar_citas_dia()
            self.actualizar_pacientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la cita: {str(e)}")
    
    def editar_paciente(self, paciente_id):
        # Obtener datos del paciente
        self.c.execute('''SELECT nombre, telefono, email, direccion, fecha_nacimiento, notas
                       FROM pacientes WHERE id=?''', (paciente_id,))
        paciente = self.c.fetchone()
        
        if not paciente:
            messagebox.showerror("Error", "Paciente no encontrado")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Paciente")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        nombre_var = tk.StringVar(value=paciente[0])
        telefono_var = tk.StringVar(value=paciente[1] if paciente[1] else "")
        email_var = tk.StringVar(value=paciente[2] if paciente[2] else "")
        direccion_var = tk.StringVar(value=paciente[3] if paciente[3] else "")
        fnac_var = tk.StringVar(value=paciente[4] if paciente[4] else "")
        notas_var = tk.StringVar(value=paciente[5] if paciente[5] else "")
        
        # Controles
        ttk.Label(dialog, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=nombre_var).grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=telefono_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=email_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=direccion_var).grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Fecha nacimiento:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=fnac_var).grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(dialog, text="Notas:").grid(row=5, column=0, padx=5, pady=5, sticky='ne')
        ttk.Entry(dialog, textvariable=notas_var).grid(row=5, column=1, padx=5, pady=5, sticky='we')
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=lambda: self.actualizar_paciente(
            paciente_id, nombre_var.get(), telefono_var.get(), email_var.get(),
            direccion_var.get(), fnac_var.get(), notas_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        nombre_var.focus()
    
    def actualizar_paciente(self, paciente_id, nombre, telefono, email, direccion, fnac, notas, dialog):
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            self.c.execute('''UPDATE pacientes SET nombre=?, telefono=?, email=?, 
                            direccion=?, fecha_nacimiento=?, notas=?
                            WHERE id=?''', 
                            (nombre, telefono, email, direccion, fnac, notas, paciente_id))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
            dialog.destroy()
            self.actualizar_pacientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el paciente: {str(e)}")
    
    def eliminar_seleccion(self):
        notebook = self.root.nametowidget(self.citas_tree.winfo_parent()).master
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # Pestaña de citas
            seleccion = self.citas_tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una cita para eliminar")
                return
            
            cita_id = seleccion[0]
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta cita?"):
                self.eliminar_cita(cita_id)
        else:  # Pestaña de pacientes
            seleccion = self.pacientes_tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un paciente para eliminar")
                return
            
            paciente_id = seleccion[0]
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este paciente y todas sus citas?"):
                self.eliminar_paciente(paciente_id)
    
    def eliminar_cita(self, cita_id):
        try:
            self.c.execute("DELETE FROM citas WHERE id=?", (cita_id,))
            self.c.execute("DELETE FROM recordatorios WHERE cita_id=?", (cita_id,))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Cita eliminada correctamente")
            self.actualizar_citas_dia()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la cita: {str(e)}")
    
    def eliminar_paciente(self, paciente_id):
        try:
            # Primero eliminamos las citas asociadas
            self.c.execute("SELECT id FROM citas WHERE paciente_id=?", (paciente_id,))
            citas = self.c.fetchall()
            
            for cita in citas:
                self.c.execute("DELETE FROM recordatorios WHERE cita_id=?", (cita[0],))
            
            self.c.execute("DELETE FROM citas WHERE paciente_id=?", (paciente_id,))
            
            # Luego el paciente
            self.c.execute("DELETE FROM pacientes WHERE id=?", (paciente_id,))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
            self.actualizar_pacientes()
            self.actualizar_citas_dia()
            self.actualizar_estadisticas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el paciente: {str(e)}")
    
    def registrar_pago(self):
        seleccion = self.citas_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para registrar pago")
            return
        
        cita_id = seleccion[0]
        
        # Verificar si la cita está completada
        self.c.execute("SELECT estado FROM citas WHERE id=?", (cita_id,))
        estado = self.c.fetchone()[0]
        
        if estado != 'completada':
            if not messagebox.askyesno("Confirmar", "Esta cita no está marcada como completada. ¿Desea marcarla como completada y registrar el pago?"):
                return
            
            self.c.execute("UPDATE citas SET estado='completada' WHERE id=?", (cita_id,))
            self.conn.commit()
        
        monto = simpledialog.askfloat("Registrar Pago", "Ingrese el monto pagado:")
        if monto is not None:
            # Aquí podrías guardar en una tabla de pagos
            messagebox.showinfo("Éxito", f"Pago de ${monto:.2f} registrado correctamente")
            self.actualizar_citas_dia()
    
    def mostrar_reportes(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Reportes")
        dialog.geometry("600x400")
        
        # Pestañas de reportes
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Reporte de citas por mes
        citas_frame = ttk.Frame(notebook)
        notebook.add(citas_frame, text="Citas por Mes")
        
        # Aquí podrías agregar gráficos o tablas con datos estadísticos
        ttk.Label(citas_frame, text="Gráfico de citas por mes aquí").pack(pady=50)
        
        # Reporte de ingresos
        ingresos_frame = ttk.Frame(notebook)
        notebook.add(ingresos_frame, text="Ingresos")
        
        ttk.Label(ingresos_frame, text="Reporte de ingresos aquí").pack(pady=50)
    
    def verificar_recordatorios(self):
        hoy = date.today().strftime("%Y-%m-%d")
        
        # Citas para mañana que no tienen recordatorio enviado
        manana = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.c.execute('''SELECT c.id, p.nombre, c.hora 
                       FROM citas c JOIN pacientes p ON c.paciente_id = p.id
                       LEFT JOIN recordatorios r ON c.id = r.cita_id
                       WHERE c.fecha=? AND (r.id IS NULL OR r.enviado=0)''', (manana,))
        citas = self.c.fetchall()
        
        if citas:
            mensaje = "Recordatorios pendientes para mañana:\n\n"
            for cita in citas:
                mensaje += f"- {cita[1]} a las {cita[2]}\n"
            
            mensaje += "\n¿Desea marcar estos recordatorios como enviados?"
            
            if messagebox.askyesno("Recordatorios Pendientes", mensaje):
                for cita in citas:
                    self.c.execute('''INSERT OR REPLACE INTO recordatorios 
                                  (cita_id, enviado, fecha_envio) 
                                  VALUES (?, 1, ?)''', (cita[0], hoy))
                self.conn.commit()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configurar icono (opcional)
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(application_path, 'icon.ico')
        root.iconbitmap(icon_path)
    except:
        pass
    
    app = PsicologoApp(root)
    root.mainloop()