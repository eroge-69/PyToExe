import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib
from datetime import datetime # Para la fecha de registro

# Configuración de apariencia de customtkinter
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

class MedicalRecordsApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de Historias Médicas Oftalmológicas")
        master.geometry("1000x700")

        self.db_name = "oftalmologia.db"
        self.conn = None
        self.cursor = None
        self.connect_db()
        self.create_tables()

        self.logged_in_user = None

        self.create_login_screen()

    def connect_db(self):
        """Establece la conexión con la base de datos SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print("Conectado a la base de datos.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")

    def create_tables(self):
        """Crea las tablas necesarias en la base de datos si no existen."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')
            # Tabla patients actualizada con los nuevos campos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula TEXT UNIQUE NOT NULL, -- Cédula como identificador único
                    nombre TEXT NOT NULL,
                    doctor_asignado TEXT,
                    fecha_registro TEXT, -- Fecha de registro del paciente
                    fecha_nacimiento TEXT,
                    lugar_nacimiento TEXT,
                    edad INTEGER,
                    genero TEXT,
                    profesion TEXT,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    motivo_consulta_inicial TEXT, -- Motivo de consulta inicial del paciente
                    enfermedad_actual_paciente TEXT, -- Enfermedad actual del paciente
                    empresa TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS medical_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    fecha_visita TEXT NOT NULL,
                    motivo_consulta TEXT, -- Motivo de consulta específico de la visita
                    agudeza_visual_od TEXT,
                    agudeza_visual_oi TEXT,
                    pio_od TEXT,
                    pio_oi TEXT,
                    refraccion_od TEXT,
                    refraccion_oi TEXT,
                    diagnostico TEXT,
                    tratamiento TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
            ''')
            self.conn.commit()
            self.add_default_users()
            print("Tablas creadas y usuarios por defecto agregados.")
        except sqlite3.Error as e:
            messagebox.showerror("Error al Crear Tablas", f"No se pudieron crear las tablas: {e}")

    def add_default_users(self):
        """Agrega usuarios por defecto si no existen."""
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        users_to_add = [
            ("admin", hash_password("admin123"), "Administrador"),
            ("doctor", hash_password("doc456"), "Doctor"),
            ("recepcion", hash_password("rec789"), "Recepcionista")
        ]
        for username, password_hash, role in users_to_add:
            try:
                self.cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                                    (username, password_hash, role))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error al agregar usuario {username}: {e}")

    def hash_password(self, password):
        """Hashea una contraseña usando SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_login_screen(self):
        """Crea y muestra la pantalla de inicio de sesión."""
        self.clear_frame()

        self.login_frame = ctk.CTkFrame(self.master, corner_radius=10)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ctk.CTkLabel(self.login_frame, text="Iniciar Sesión", font=("Arial", 24, "bold")).pack(pady=20)

        ctk.CTkLabel(self.login_frame, text="Usuario:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.login_frame, width=250)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.login_frame, text="Contraseña:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", width=250)
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.login_frame, text="Entrar", command=self.attempt_login, width=200).pack(pady=20)

        self.animate_login_screen()

    def animate_login_screen(self):
        """Realiza una animación simple de la ventana al iniciar sesión."""
        initial_width, initial_height = self.master.winfo_width(), self.master.winfo_height()
        target_width, target_height = 1050, 750
        steps = 20
        delay = 10  # ms

        def grow_window(step):
            if step <= steps:
                current_width = initial_width + (target_width - initial_width) * (step / steps)
                current_height = initial_height + (target_height - initial_height) * (step / steps)
                self.master.geometry(f"{int(current_width)}x{int(current_height)}")
                self.master.after(delay, grow_window, step + 1)
            else:
                self.master.after(delay, shrink_window, steps)

        def shrink_window(step):
            if step >= 0:
                current_width = initial_width + (target_width - initial_width) * (step / steps)
                current_height = initial_height + (target_height - initial_height) * (step / steps)
                self.master.geometry(f"{int(current_width)}x{int(current_height)}")
                self.master.after(delay, shrink_window, step - 1)

        self.master.after(100, grow_window, 0)

    def attempt_login(self):
        """Intenta autenticar al usuario."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = self.hash_password(password)

        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = self.cursor.fetchone()

        if user:
            self.logged_in_user = {"id": user[0], "username": user[1], "role": user[3]}
            messagebox.showinfo("Login Exitoso", f"Bienvenido, {self.logged_in_user['username']} ({self.logged_in_user['role']})")
            self.create_main_app_screen()
        else:
            messagebox.showerror("Error de Login", "Usuario o contraseña incorrectos.")

    def clear_frame(self):
        """Limpia todos los widgets del frame principal."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_main_app_screen(self):
        """Crea la pantalla principal de la aplicación después del login."""
        self.clear_frame()

        self.main_frame = ctk.CTkFrame(self.master)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Sidebar para navegación
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=200, corner_radius=10)
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 20), pady=0)
        self.sidebar_frame.pack_propagate(False)

        ctk.CTkLabel(self.sidebar_frame, text="Menú", font=("Arial", 18, "bold")).pack(pady=20)

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.pack(pady=10, padx=10, fill="x")

        self.btn_patients = ctk.CTkButton(self.sidebar_frame, text="Gestionar Pacientes", command=self.show_patient_management)
        self.btn_patients.pack(pady=10, padx=10, fill="x")

        self.btn_medical_records = ctk.CTkButton(self.sidebar_frame, text="Registros Médicos", command=self.show_medical_records)
        self.btn_medical_records.pack(pady=10, padx=10, fill="x")

        # Opciones específicas para el rol de Administrador
        if self.logged_in_user and self.logged_in_user["role"] == "Administrador":
            self.btn_manage_users = ctk.CTkButton(self.sidebar_frame, text="Gestionar Usuarios", command=self.show_user_management)
            self.btn_manage_users.pack(pady=10, padx=10, fill="x")

        ctk.CTkButton(self.sidebar_frame, text="Cerrar Sesión", command=self.logout).pack(pady=30, padx=10, fill="x")

        # Contenido principal - Ahora es un CTkScrollableFrame
        # Este frame contendrá todos los elementos de las diferentes "páginas"
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True, pady=0)

        self.show_dashboard()

    def logout(self):
        """Cierra la sesión del usuario actual y vuelve a la pantalla de login."""
        self.logged_in_user = None
        messagebox.showinfo("Sesión Cerrada", "Has cerrado sesión exitosamente.")
        self.create_login_screen()

    def show_dashboard(self):
        """Muestra la pantalla del dashboard con un resumen de la actividad."""
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Dashboard", font=("Arial", 28, "bold")).pack(pady=20)
        ctk.CTkLabel(self.content_frame, text=f"Bienvenido, {self.logged_in_user['username']} ({self.logged_in_user['role']})", font=("Arial", 16)).pack(pady=10)

        # Contadores rápidos
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = self.cursor.fetchone()[0]
        ctk.CTkLabel(self.content_frame, text=f"Total de Pacientes: {total_patients}", font=("Arial", 14)).pack(pady=5)

        self.cursor.execute("SELECT COUNT(*) FROM medical_records")
        total_records = self.cursor.fetchone()[0]
        ctk.CTkLabel(self.content_frame, text=f"Total de Registros Médicos: {total_records}", font=("Arial", 14)).pack(pady=5)

        # Animación de elementos del dashboard
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Ejemplo de "tarjetas" animadas
        card1 = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="transparent")
        card1.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(card1, text="Resumen de Actividad", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card1, text="Últimas visitas, próximos appointments, etc.").pack(pady=5)
        self.animate_fade_in(card1)

        card2 = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="transparent")
        card2.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(card2, text="Estadísticas Rápidas", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card2, text="Gráficos de datos de pacientes (Placeholder)").pack(pady=5)
        self.animate_fade_in(card2)

    def show_patient_management(self):
        """Muestra la pantalla de gestión de pacientes."""
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Gestión de Pacientes", font=("Arial", 28, "bold")).pack(pady=20)

        # Frame para añadir paciente
        add_patient_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        add_patient_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(add_patient_frame, text="Añadir Nuevo Paciente", font=("Arial", 18, "bold")).pack(pady=10)

        # Nuevos campos para el paciente
        labels = [
            "Cédula:", "Nombre:", "Doctor Asignado:", "Fecha Nacimiento (AAAA-MM-DD):",
            "Lugar de Nacimiento:", "Edad:", "Género:", "Profesión:", "Teléfono:",
            "Email:", "Dirección:", "Motivo Consulta Inicial:", "Enfermedad Actual Paciente:", "Empresa:"
        ]
        self.patient_entries = {}
        for i, label_text in enumerate(labels):
            frame = ctk.CTkFrame(add_patient_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(frame, text=label_text, width=200, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=300)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            self.patient_entries[label_text.replace(":", "").strip()] = entry

        ctk.CTkButton(add_patient_frame, text="Guardar Paciente", command=self.add_patient).pack(pady=10)

        # Separador
        ctk.CTkFrame(self.content_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        # Frame para buscar y listar pacientes
        search_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        search_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Buscar Paciente:", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(search_frame, text="Cédula o Nombre:").pack(side="left", padx=5)
        self.search_patient_entry = ctk.CTkEntry(search_frame, width=250)
        self.search_patient_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Buscar", command=self.search_patients).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Mostrar Todos", command=self.load_patients).pack(side="left", padx=5)

        self.patient_list_frame = ctk.CTkScrollableFrame(self.content_frame, height=200, corner_radius=10)
        self.patient_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.patient_widgets = [] # Para mantener un seguimiento de los widgets de visualización de pacientes para actualizar

        self.load_patients()

    def animate_fade_in(self, widget):
        """Aplica una animación de desvanecimiento (fade-in) a un widget."""
        # CustomTkinter no tiene un método set_opacity directo en todos los widgets,
        # pero podemos simularlo con el color de fondo o usando place/pack con un retraso.
        # Para frames, podemos cambiar el color de fondo gradualmente si es necesario.
        # Para un efecto más general, se necesitarían más librerías o una implementación más compleja.
        # Por ahora, esta es una animación conceptual.
        # Si el widget tiene un método set_opacity, úsalo. Si no, esta función es un placeholder.
        if hasattr(widget, 'configure'):
            widget.configure(fg_color=("gray", "transparent")) # Placeholder para animación visual
            # Una animación real implicaría cambiar el color gradualmente o usar un canvas.
            # Para fines de demostración, el efecto es más conceptual.
        pass # No hay una implementación de fade-in directa para todos los widgets en customtkinter sin canvas/image manipulation.

    def add_patient(self):
        """Añade un nuevo paciente a la base de datos."""
        cedula = self.patient_entries["Cédula"].get()
        nombre = self.patient_entries["Nombre"].get()
        doctor_asignado = self.patient_entries["Doctor Asignado"].get()
        fecha_nacimiento = self.patient_entries["Fecha Nacimiento (AAAA-MM-DD)"].get()
        lugar_nacimiento = self.patient_entries["Lugar de Nacimiento"].get()
        edad_str = self.patient_entries["Edad"].get()
        genero = self.patient_entries["Género"].get()
        profesion = self.patient_entries["Profesión"].get()
        telefono = self.patient_entries["Teléfono"].get()
        email = self.patient_entries["Email"].get()
        direccion = self.patient_entries["Dirección"].get()
        motivo_consulta_inicial = self.patient_entries["Motivo Consulta Inicial"].get()
        enfermedad_actual_paciente = self.patient_entries["Enfermedad Actual Paciente"].get()
        empresa = self.patient_entries["Empresa"].get()

        if not cedula or not nombre:
            messagebox.showerror("Error", "La cédula y el nombre del paciente son obligatorios.")
            return

        try:
            edad = int(edad_str) if edad_str else None
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número válido.")
            return

        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Fecha y hora actual de registro

        try:
            self.cursor.execute("""
                INSERT INTO patients (
                    cedula, nombre, doctor_asignado, fecha_registro, fecha_nacimiento,
                    lugar_nacimiento, edad, genero, profesion, telefono, email,
                    direccion, motivo_consulta_inicial, enfermedad_actual_paciente, empresa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cedula, nombre, doctor_asignado, fecha_registro, fecha_nacimiento,
                lugar_nacimiento, edad, genero, profesion, telefono, email,
                direccion, motivo_consulta_inicial, enfermedad_actual_paciente, empresa
            ))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Paciente agregado exitosamente.")
            for entry in self.patient_entries.values():
                entry.delete(0, tk.END)
            self.load_patients()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un paciente con esa cédula.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al agregar paciente: {e}")

    def load_patients(self):
        """Carga y muestra la lista de pacientes."""
        for widget in self.patient_widgets:
            widget.destroy()
        self.patient_widgets.clear()

        self.cursor.execute("SELECT id, cedula, nombre, telefono FROM patients ORDER BY nombre")
        patients = self.cursor.fetchall()

        if not patients:
            ctk.CTkLabel(self.patient_list_frame, text="No hay pacientes registrados.").pack(pady=10)
            return

        for patient in patients:
            patient_id, cedula, nombre, telefono = patient
            patient_row_frame = ctk.CTkFrame(self.patient_list_frame, fg_color="transparent")
            patient_row_frame.pack(fill="x", pady=2)
            self.patient_widgets.append(patient_row_frame)

            ctk.CTkLabel(patient_row_frame, text=f"Cédula: {cedula} - Nombre: {nombre} - Teléfono: {telefono}",
                         font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkButton(patient_row_frame, text="Ver/Editar", command=lambda p_id=patient_id: self.view_edit_patient(p_id)).pack(side="right", padx=5)

    def search_patients(self):
        """Busca pacientes por cédula o nombre."""
        search_term = self.search_patient_entry.get()
        for widget in self.patient_widgets:
            widget.destroy()
        self.patient_widgets.clear()

        if not search_term:
            messagebox.showerror("Error", "Por favor, introduce una cédula o nombre para buscar.")
            self.load_patients() # Cargar todos si la búsqueda está vacía
            return

        self.cursor.execute("""
            SELECT id, cedula, nombre, telefono FROM patients
            WHERE cedula LIKE ? OR nombre LIKE ?
            ORDER BY nombre
        """, ('%' + search_term + '%', '%' + search_term + '%'))
        patients = self.cursor.fetchall()

        if not patients:
            ctk.CTkLabel(self.patient_list_frame, text="No se encontraron pacientes con esa cédula o nombre.").pack(pady=10)
            return

        for patient in patients:
            patient_id, cedula, nombre, telefono = patient
            patient_row_frame = ctk.CTkFrame(self.patient_list_frame, fg_color="transparent")
            patient_row_frame.pack(fill="x", pady=2)
            self.patient_widgets.append(patient_row_frame)

            ctk.CTkLabel(patient_row_frame, text=f"Cédula: {cedula} - Nombre: {nombre} - Teléfono: {telefono}",
                         font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkButton(patient_row_frame, text="Ver/Editar", command=lambda p_id=patient_id: self.view_edit_patient(p_id)).pack(side="right", padx=5)

    def view_edit_patient(self, patient_id):
        """Muestra los detalles de un paciente para ver o editar."""
        self.clear_content_frame()
        self.cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient_data = self.cursor.fetchone()

        if not patient_data:
            messagebox.showerror("Error", "Paciente no encontrado.")
            self.show_patient_management()
            return

        # Desempaquetar los datos del paciente (asegurarse de que el orden coincide con la tabla)
        (patient_id, cedula, nombre, doctor_asignado, fecha_registro, fecha_nacimiento,
         lugar_nacimiento, edad, genero, profesion, telefono, email, direccion,
         motivo_consulta_inicial, enfermedad_actual_paciente, empresa) = patient_data

        ctk.CTkLabel(self.content_frame, text=f"Detalles del Paciente: {nombre} (Cédula: {cedula})", font=("Arial", 24, "bold")).pack(pady=20)

        details_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        details_frame.pack(pady=10, padx=10, fill="x")

        labels_data = {
            "ID:": patient_id,
            "Cédula:": cedula,
            "Nombre:": nombre,
            "Doctor Asignado:": doctor_asignado,
            "Fecha Registro:": fecha_registro,
            "Fecha Nacimiento (AAAA-MM-DD):": fecha_nacimiento,
            "Lugar de Nacimiento:": lugar_nacimiento,
            "Edad:": edad,
            "Género:": genero,
            "Profesión:": profesion,
            "Teléfono:": telefono,
            "Email:": email,
            "Dirección:": direccion,
            "Motivo Consulta Inicial:": motivo_consulta_inicial,
            "Enfermedad Actual Paciente:": enfermedad_actual_paciente,
            "Empresa:": empresa
        }

        self.edit_patient_entries = {}
        for label_text, value in labels_data.items():
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(frame, text=label_text, width=250, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
            if label_text in ["ID:", "Fecha Registro:"]: # Campos no editables
                ctk.CTkLabel(frame, text=str(value), font=("Arial", 12)).pack(side="left", expand=True, fill="x", padx=5)
            elif label_text == "Cédula:": # Cédula es editable pero con cuidado (UNIQUE)
                entry = ctk.CTkEntry(frame, width=300)
                entry.insert(0, str(value if value else ""))
                entry.pack(side="left", expand=True, fill="x", padx=5)
                self.edit_patient_entries[label_text.replace(":", "").strip()] = entry
            else:
                entry = ctk.CTkEntry(frame, width=300)
                entry.insert(0, str(value if value else "")) # Manejar valores None
                entry.pack(side="left", expand=True, fill="x", padx=5)
                self.edit_patient_entries[label_text.replace(":", "").strip()] = entry

        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(button_frame, text="Actualizar Datos", command=lambda: self.update_patient(patient_id)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Ver Historial Médico", command=lambda: self.show_patient_medical_history(patient_id, nombre)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Eliminar Paciente", fg_color="red", hover_color="darkred", command=lambda: self.delete_patient(patient_id)).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Volver", command=self.show_patient_management).pack(side="right", padx=5)

    def update_patient(self, patient_id):
        """Actualiza los datos de un paciente en la base de datos."""
        new_data = {
            "Cédula": self.edit_patient_entries["Cédula"].get(),
            "Nombre": self.edit_patient_entries["Nombre"].get(),
            "Doctor Asignado": self.edit_patient_entries["Doctor Asignado"].get(),
            "Fecha Nacimiento (AAAA-MM-DD)": self.edit_patient_entries["Fecha Nacimiento (AAAA-MM-DD)"].get(),
            "Lugar de Nacimiento": self.edit_patient_entries["Lugar de Nacimiento"].get(),
            "Edad": self.edit_patient_entries["Edad"].get(),
            "Género": self.edit_patient_entries["Género"].get(),
            "Profesión": self.edit_patient_entries["Profesión"].get(),
            "Teléfono": self.edit_patient_entries["Teléfono"].get(),
            "Email": self.edit_patient_entries["Email"].get(),
            "Dirección": self.edit_patient_entries["Dirección"].get(),
            "Motivo Consulta Inicial": self.edit_patient_entries["Motivo Consulta Inicial"].get(),
            "Enfermedad Actual Paciente": self.edit_patient_entries["Enfermedad Actual Paciente"].get(),
            "Empresa": self.edit_patient_entries["Empresa"].get()
        }

        if not new_data["Cédula"] or not new_data["Nombre"]:
            messagebox.showerror("Error", "La cédula y el nombre del paciente no pueden estar vacíos.")
            return

        try:
            edad = int(new_data["Edad"]) if new_data["Edad"] else None
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número válido.")
            return

        try:
            self.cursor.execute("""
                UPDATE patients SET
                cedula = ?, nombre = ?, doctor_asignado = ?, fecha_nacimiento = ?,
                lugar_nacimiento = ?, edad = ?, genero = ?, profesion = ?,
                telefono = ?, email = ?, direccion = ?, motivo_consulta_inicial = ?,
                enfermedad_actual_paciente = ?, empresa = ?
                WHERE id = ?
            """, (new_data["Cédula"], new_data["Nombre"], new_data["Doctor Asignado"],
                  new_data["Fecha Nacimiento (AAAA-MM-DD)"], new_data["Lugar de Nacimiento"],
                  edad, new_data["Género"], new_data["Profesión"], new_data["Teléfono"],
                  new_data["Email"], new_data["Dirección"], new_data["Motivo Consulta Inicial"],
                  new_data["Enfermedad Actual Paciente"], new_data["Empresa"], patient_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Datos del paciente actualizados exitosamente.")
            self.show_patient_management() # Volver a la lista de pacientes
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "La cédula ingresada ya pertenece a otro paciente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al actualizar paciente: {e}")

    def delete_patient(self, patient_id):
        """Elimina un paciente y todos sus registros médicos asociados."""
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar a este paciente y todos sus registros médicos asociados? Esta acción es irreversible."):
            try:
                # La cláusula ON DELETE CASCADE en la creación de la tabla medical_records
                # debería manejar la eliminación automática de registros médicos.
                # Si no funciona, se necesitaría un DELETE explícito aquí para medical_records.
                self.cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Paciente y sus registros eliminados exitosamente.")
                self.show_patient_management()
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al eliminar paciente: {e}")

    def show_medical_records(self):
        """Muestra la pantalla de gestión de registros médicos."""
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Registros Médicos", font=("Arial", 28, "bold")).pack(pady=20)

        search_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        search_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Buscar Registros por Nombre de Paciente:", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(search_frame, text="Nombre:").pack(side="left", padx=5)
        self.search_record_patient_entry = ctk.CTkEntry(search_frame, width=200)
        self.search_record_patient_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Buscar", command=self.search_records_by_patient_name).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Ver Todos los Registros", command=self.load_all_medical_records).pack(side="left", padx=5)

        self.medical_records_list_frame = ctk.CTkScrollableFrame(self.content_frame, height=300, corner_radius=10)
        self.medical_records_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.medical_record_widgets = []
        self.load_all_medical_records()

    def search_records_by_patient_name(self):
        """Busca registros médicos por el nombre del paciente."""
        search_term = self.search_record_patient_entry.get()
        for widget in self.medical_record_widgets:
            widget.destroy()
        self.medical_record_widgets.clear()

        if not search_term:
            messagebox.showerror("Error", "Por favor, introduce un nombre para buscar.")
            self.load_all_medical_records() # Cargar todos si la búsqueda está vacía
            return

        self.cursor.execute("""
            SELECT mr.id, p.nombre, mr.fecha_visita, mr.motivo_consulta
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.id
            WHERE p.nombre LIKE ?
            ORDER BY mr.fecha_visita DESC
        """, ('%' + search_term + '%',))
        records = self.cursor.fetchall()

        if not records:
            ctk.CTkLabel(self.medical_records_list_frame, text="No se encontraron registros para ese paciente.").pack(pady=10)
            return

        for record in records:
            record_id, patient_name, fecha_visita, motivo_consulta = record
            record_row_frame = ctk.CTkFrame(self.medical_records_list_frame, fg_color="transparent")
            record_row_frame.pack(fill="x", pady=2)
            self.medical_record_widgets.append(record_row_frame)

            ctk.CTkLabel(record_row_frame, text=f"ID: {record_id} - Paciente: {patient_name} - Fecha: {fecha_visita} - Motivo: {motivo_consulta}",
                         font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkButton(record_row_frame, text="Ver Detalles", command=lambda r_id=record_id: self.view_medical_record_details(r_id)).pack(side="right", padx=5)

    def load_all_medical_records(self):
        """Carga y muestra todos los registros médicos."""
        for widget in self.medical_record_widgets:
            widget.destroy()
        self.medical_record_widgets.clear()

        self.cursor.execute("""
            SELECT mr.id, p.nombre, mr.fecha_visita, mr.motivo_consulta
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.id
            ORDER BY mr.fecha_visita DESC
        """)
        records = self.cursor.fetchall()

        if not records:
            ctk.CTkLabel(self.medical_records_list_frame, text="No hay registros médicos.").pack(pady=10)
            return

        for record in records:
            record_id, patient_name, fecha_visita, motivo_consulta = record
            record_row_frame = ctk.CTkFrame(self.medical_records_list_frame, fg_color="transparent")
            record_row_frame.pack(fill="x", pady=2)
            self.medical_record_widgets.append(record_row_frame)

            ctk.CTkLabel(record_row_frame, text=f"ID: {record_id} - Paciente: {patient_name} - Fecha: {fecha_visita} - Motivo: {motivo_consulta}",
                         font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkButton(record_row_frame, text="Ver Detalles", command=lambda r_id=record_id: self.view_medical_record_details(r_id)).pack(side="right", padx=5)

    def view_medical_record_details(self, record_id):
        """Muestra los detalles de un registro médico específico."""
        self.clear_content_frame()
        self.cursor.execute("""
            SELECT mr.*, p.nombre
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.id
            WHERE mr.id = ?
        """, (record_id,))
        record_data = self.cursor.fetchone()

        if not record_data:
            messagebox.showerror("Error", "Registro médico no encontrado.")
            self.show_medical_records()
            return

        (rec_id, patient_id, fecha_visita, motivo_consulta, agudeza_visual_od, agudeza_visual_oi,
         pio_od, pio_oi, refraccion_od, refraccion_oi, diagnostico, tratamiento, patient_name) = record_data

        ctk.CTkLabel(self.content_frame, text=f"Detalles del Registro Médico para {patient_name}", font=("Arial", 24, "bold")).pack(pady=20)

        details_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        details_frame.pack(pady=10, padx=10, fill="x")

        labels_data = {
            "ID del Registro:": rec_id,
            "Paciente ID:": patient_id,
            "Nombre del Paciente:": patient_name,
            "Fecha de Visita (AAAA-MM-DD):": fecha_visita,
            "Motivo de Consulta:": motivo_consulta,
            "Agudeza Visual OD:": agudeza_visual_od,
            "Agudeza Visual OI:": agudeza_visual_oi,
            "PIO OD (mmHg):": pio_od,
            "PIO OI (mmHg):": pio_oi,
            "Refracción OD:": refraccion_od,
            "Refracción OI:": refraccion_oi,
            "Diagnóstico:": diagnostico,
            "Tratamiento:": tratamiento
        }

        self.edit_record_entries = {}
        for label_text, value in labels_data.items():
            frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(frame, text=label_text, width=200, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
            if label_text in ["ID del Registro:", "Paciente ID:", "Nombre del Paciente:"]: # No editables
                ctk.CTkLabel(frame, text=str(value), font=("Arial", 12)).pack(side="left", expand=True, fill="x", padx=5)
            else:
                entry = ctk.CTkEntry(frame, width=400)
                entry.insert(0, str(value if value else ""))
                entry.pack(side="left", expand=True, fill="x", padx=5)
                self.edit_record_entries[label_text.replace(":", "").strip()] = entry

        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(button_frame, text="Actualizar Registro", command=lambda: self.update_medical_record(record_id)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Eliminar Registro", fg_color="red", hover_color="darkred", command=lambda: self.delete_medical_record(record_id)).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Volver", command=self.show_medical_records).pack(side="right", padx=5)

    def update_medical_record(self, record_id):
        """Actualiza un registro médico en la base de datos."""
        new_data = {
            "Fecha de Visita (AAAA-MM-DD)": self.edit_record_entries["Fecha de Visita (AAAA-MM-DD)"].get(),
            "Motivo de Consulta": self.edit_record_entries["Motivo de Consulta"].get(),
            "Agudeza Visual OD": self.edit_record_entries["Agudeza Visual OD"].get(),
            "Agudeza Visual OI": self.edit_record_entries["Agudeza Visual OI"].get(),
            "PIO OD (mmHg)": self.edit_record_entries["PIO OD (mmHg)"].get(),
            "PIO OI (mmHg)": self.edit_record_entries["PIO OI (mmHg)"].get(),
            "Refracción OD": self.edit_record_entries["Refracción OD"].get(),
            "Refracción OI": self.edit_record_entries["Refracción OI"].get(),
            "Diagnóstico": self.edit_record_entries["Diagnóstico"].get(),
            "Tratamiento": self.edit_record_entries["Tratamiento"].get()
        }

        if not new_data["Fecha de Visita (AAAA-MM-DD)"] or not new_data["Motivo de Consulta"]:
            messagebox.showerror("Error", "La fecha de visita y el motivo de consulta son obligatorios.")
            return

        try:
            self.cursor.execute("""
                UPDATE medical_records SET
                fecha_visita = ?, motivo_consulta = ?, agudeza_visual_od = ?, agudeza_visual_oi = ?,
                pio_od = ?, pio_oi = ?, refraccion_od = ?, refraccion_oi = ?, diagnostico = ?, tratamiento = ?
                WHERE id = ?
            """, (new_data["Fecha de Visita (AAAA-MM-DD)"], new_data["Motivo de Consulta"], new_data["Agudeza Visual OD"],
                  new_data["Agudeza Visual OI"], new_data["PIO OD (mmHg)"], new_data["PIO OI (mmHg)"],
                  new_data["Refracción OD"], new_data["Refracción OI"], new_data["Diagnóstico"],
                  new_data["Tratamiento"], record_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro médico actualizado exitosamente.")
            self.show_medical_records()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al actualizar registro médico: {e}")

    def delete_medical_record(self, record_id):
        """Elimina un registro médico de la base de datos."""
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este registro médico?"):
            try:
                self.cursor.execute("DELETE FROM medical_records WHERE id = ?", (record_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Registro médico eliminado exitosamente.")
                self.show_medical_records()
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al eliminar registro médico: {e}")

    def show_patient_medical_history(self, patient_id, patient_name):
        """Muestra el historial médico de un paciente específico."""
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text=f"Historial Médico de {patient_name}", font=("Arial", 28, "bold")).pack(pady=20)

        # Botón para añadir nuevo registro
        ctk.CTkButton(self.content_frame, text="Añadir Nuevo Registro de Visita", command=lambda: self.add_medical_record_for_patient(patient_id, patient_name)).pack(pady=10)

        self.history_list_frame = ctk.CTkScrollableFrame(self.content_frame, height=400, corner_radius=10)
        self.history_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.load_patient_medical_history(patient_id)

    def load_patient_medical_history(self, patient_id):
        """Carga y muestra el historial médico de un paciente."""
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, fecha_visita, motivo_consulta, diagnostico FROM medical_records WHERE patient_id = ? ORDER BY fecha_visita DESC", (patient_id,))
        records = self.cursor.fetchall()

        if not records:
            ctk.CTkLabel(self.history_list_frame, text="No hay registros médicos para este paciente.").pack(pady=10)
            return

        for record in records:
            record_id, fecha_visita, motivo_consulta, diagnostico = record
            record_row_frame = ctk.CTkFrame(self.history_list_frame, fg_color="transparent")
            record_row_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(record_row_frame, text=f"Fecha: {fecha_visita} | Motivo: {motivo_consulta} | Diagnóstico: {diagnostico}",
                         font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkButton(record_row_frame, text="Ver Detalles", command=lambda r_id=record_id: self.view_medical_record_details(r_id)).pack(side="right", padx=5)

    def add_medical_record_for_patient(self, patient_id, patient_name):
        """Muestra el formulario para añadir un nuevo registro médico para un paciente."""
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text=f"Añadir Nuevo Registro para {patient_name}", font=("Arial", 24, "bold")).pack(pady=20)

        record_form_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        record_form_frame.pack(pady=10, padx=10, fill="x")

        labels = [
            "Fecha Visita (AAAA-MM-DD):", "Motivo de Consulta:", "Agudeza Visual OD:",
            "Agudeza Visual OI:", "PIO OD (mmHg):", "PIO OI (mmHg):",
            "Refracción OD:", "Refracción OI:", "Diagnóstico:", "Tratamiento:"
        ]
        self.new_record_entries = {}
        for i, label_text in enumerate(labels):
            frame = ctk.CTkFrame(record_form_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(frame, text=label_text, width=200, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=400)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            self.new_record_entries[label_text.replace(":", "").strip()] = entry

        ctk.CTkButton(record_form_frame, text="Guardar Registro", command=lambda: self.save_new_medical_record(patient_id, patient_name)).pack(pady=10)
        ctk.CTkButton(record_form_frame, text="Cancelar y Volver", command=lambda: self.show_patient_medical_history(patient_id, patient_name)).pack(pady=5)

    def save_new_medical_record(self, patient_id, patient_name):
        """Guarda un nuevo registro médico en la base de datos."""
        fecha_visita = self.new_record_entries["Fecha Visita (AAAA-MM-DD)"].get()
        motivo_consulta = self.new_record_entries["Motivo de Consulta"].get()
        agudeza_visual_od = self.new_record_entries["Agudeza Visual OD"].get()
        agudeza_visual_oi = self.new_record_entries["Agudeza Visual OI"].get()
        pio_od = self.new_record_entries["PIO OD (mmHg)"].get()
        pio_oi = self.new_record_entries["PIO OI (mmHg)"].get()
        refraccion_od = self.new_record_entries["Refracción OD"].get()
        refraccion_oi = self.new_record_entries["Refracción OI"].get()
        diagnostico = self.new_record_entries["Diagnóstico"].get()
        tratamiento = self.new_record_entries["Tratamiento"].get()

        if not fecha_visita or not motivo_consulta:
            messagebox.showerror("Error", "La fecha de visita y el motivo de consulta son obligatorios.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO medical_records (patient_id, fecha_visita, motivo_consulta, agudeza_visual_od,
                agudeza_visual_oi, pio_od, pio_oi, refraccion_od, refraccion_oi, diagnostico, tratamiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, fecha_visita, motivo_consulta, agudeza_visual_od, agudeza_visual_oi,
                  pio_od, pio_oi, refraccion_od, refraccion_oi, diagnostico, tratamiento))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Nuevo registro médico guardado exitosamente.")
            self.show_patient_medical_history(patient_id, patient_name) # Volver a la vista de historial
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al guardar nuevo registro: {e}")

    def show_user_management(self):
        """Muestra la pantalla de gestión de usuarios (solo para administradores)."""
        if self.logged_in_user and self.logged_in_user["role"] != "Administrador":
            messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden gestionar usuarios.")
            self.show_dashboard()
            return

        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Gestión de Usuarios", font=("Arial", 28, "bold")).pack(pady=20)

        # Frame para añadir usuario
        add_user_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        add_user_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(add_user_frame, text="Añadir Nuevo Usuario", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(add_user_frame, text="Usuario:").pack(pady=5)
        self.new_username_entry = ctk.CTkEntry(add_user_frame, width=250)
        self.new_username_entry.pack(pady=5)

        ctk.CTkLabel(add_user_frame, text="Contraseña:").pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(add_user_frame, show="*", width=250)
        self.new_password_entry.pack(pady=5)

        ctk.CTkLabel(add_user_frame, text="Rol:").pack(pady=5)
        self.new_user_role_combobox = ctk.CTkComboBox(add_user_frame, values=["Administrador", "Doctor", "Recepcionista"])
        self.new_user_role_combobox.set("Doctor") # Valor por defecto
        self.new_user_role_combobox.pack(pady=5)

        ctk.CTkButton(add_user_frame, text="Crear Usuario", command=self.add_user).pack(pady=10)

        # Separador
        ctk.CTkFrame(self.content_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        # Listar y gestionar usuarios existentes
        ctk.CTkLabel(self.content_frame, text="Usuarios Existentes", font=("Arial", 18, "bold")).pack(pady=10)
        self.user_list_frame = ctk.CTkScrollableFrame(self.content_frame, height=200, corner_radius=10)
        self.user_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.load_users()

    def add_user(self):
        """Añade un nuevo usuario a la base de datos."""
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        role = self.new_user_role_combobox.get()

        if not username or not password or not role:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        hashed_password = self.hash_password(password)

        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                (username, hashed_password, role))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Usuario creado exitosamente.")
            self.new_username_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.load_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al crear usuario: {e}")

    def load_users(self):
        """Carga y muestra la lista de usuarios."""
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, username, role FROM users ORDER BY username")
        users = self.cursor.fetchall()

        if not users:
            ctk.CTkLabel(self.user_list_frame, text="No hay usuarios registrados.").pack(pady=10)
            return

        for user in users:
            user_id, username, role = user
            user_row_frame = ctk.CTkFrame(self.user_list_frame, fg_color="transparent")
            user_row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(user_row_frame, text=f"ID: {user_id} - Usuario: {username} - Rol: {role}",
                         font=("Arial", 12)).pack(side="left", padx=5)

            if username != self.logged_in_user["username"]: # No se puede eliminar a sí mismo
                ctk.CTkButton(user_row_frame, text="Eliminar", fg_color="red", hover_color="darkred",
                              command=lambda u_id=user_id: self.delete_user(u_id)).pack(side="right", padx=5)
            ctk.CTkButton(user_row_frame, text="Resetear Contraseña",
                          command=lambda u_id=user_id, u_name=username: self.reset_user_password(u_id, u_name)).pack(side="right", padx=5)


    def delete_user(self, user_id):
        """Elimina un usuario de la base de datos."""
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar a este usuario?"):
            try:
                self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Usuario eliminado exitosamente.")
                self.load_users()
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al eliminar usuario: {e}")

    def reset_user_password(self, user_id, username):
        """Permite a un administrador resetear la contraseña de otro usuario."""
        new_password = simpledialog.askstring("Resetear Contraseña", f"Introduce la nueva contraseña para {username}:", show='*')
        if new_password:
            hashed_new_password = self.hash_password(new_password)
            try:
                self.cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new_password, user_id))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Contraseña del usuario reiniciada exitosamente.")
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al resetear contraseña: {e}")
        else:
            messagebox.showinfo("Cancelado", "Operación de reseteo de contraseña cancelada.")

    def clear_content_frame(self):
        """Limpia todos los widgets del frame de contenido principal."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def on_closing(self):
        """Maneja el cierre de la aplicación, cerrando la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            print("Conexión a la base de datos cerrada.")
        self.master.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = MedicalRecordsApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
