import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib

# --- Base de datos ---
conexion = sqlite3.connect("usuarios_notas.db")
cursor = conexion.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena_hash TEXT NOT NULL,
    color TEXT DEFAULT 'white'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    titulo TEXT,
    contenido TEXT,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS credenciales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    servicio TEXT,
    usuario TEXT,
    contrasena TEXT,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

# Intentar agregar la columna 'color' si no existe (por compatibilidad con versiones anteriores)
try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN color TEXT DEFAULT 'white'")
    conexion.commit()
except sqlite3.OperationalError:
    pass  # Ya existe

conexion.commit()

# --- Funciones de seguridad y DB ---
def encriptar_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

def verificar_contrasena(contrasena, hash_contra):
    return encriptar_contrasena(contrasena) == hash_contra

def registrar_usuario(usuario, contrasena):
    try:
        hash_contra = encriptar_contrasena(contrasena)
        cursor.execute("INSERT INTO usuarios (usuario, contrasena_hash) VALUES (?, ?)", (usuario, hash_contra))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def obtener_usuario(usuario):
    cursor.execute("SELECT id, contrasena_hash FROM usuarios WHERE usuario = ?", (usuario,))
    return cursor.fetchone()

def guardar_nota(usuario_id, titulo, contenido):
    cursor.execute("INSERT INTO notas (usuario_id, titulo, contenido) VALUES (?, ?, ?)", (usuario_id, titulo, contenido))
    conexion.commit()

def obtener_notas(usuario_id):
    cursor.execute("SELECT id, titulo, contenido FROM notas WHERE usuario_id = ?", (usuario_id,))
    return cursor.fetchall()

def borrar_nota(nota_id):
    cursor.execute("DELETE FROM notas WHERE id = ?", (nota_id,))
    conexion.commit()

def guardar_credencial(usuario_id, servicio, usuario_cred, contrasena_cred):
    cursor.execute(
        "INSERT INTO credenciales (usuario_id, servicio, usuario, contrasena) VALUES (?, ?, ?, ?)",
        (usuario_id, servicio, usuario_cred, contrasena_cred)
    )
    conexion.commit()

def obtener_credenciales(usuario_id):
    cursor.execute("SELECT id, servicio, usuario, contrasena FROM credenciales WHERE usuario_id = ?", (usuario_id,))
    return cursor.fetchall()

def borrar_credencial(cred_id):
    cursor.execute("DELETE FROM credenciales WHERE id = ?", (cred_id,))
    conexion.commit()

# --- Interfaz gráfica ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor Seguro de Usuarios, Notas y Contraseñas")
        self.geometry("600x500")
        self.usuario_id = None
        self.usuario = None
        self.color_actual = "white"
        self.frame_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def establecer_color_fondo(self, color):
        self.config(bg=color)
        self.color_actual = color
        for widget in self.winfo_children():
            try:
                widget.config(bg=color, fg="black" if color != "black" else "white")
            except:
                pass

    def cambiar_color(self):
        colores = ["white", "lightblue", "lightgreen", "lightyellow", "lightgray", "black"]
        try:
            indice = colores.index(self.color_actual)
            nuevo_color = colores[(indice + 1) % len(colores)]
        except ValueError:
            nuevo_color = "white"
        self.establecer_color_fondo(nuevo_color)
        # Guardar color en base de datos
        cursor.execute("UPDATE usuarios SET color = ? WHERE id = ?", (nuevo_color, self.usuario_id))
        conexion.commit()

    def frame_login(self):
        self.limpiar_pantalla()
        self.establecer_color_fondo("white")
        tk.Label(self, text="Iniciar Sesión", font=("Arial", 18)).pack(pady=10)

        tk.Label(self, text="Usuario:").pack()
        self.entry_usuario = tk.Entry(self)
        self.entry_usuario.pack()

        tk.Label(self, text="Contraseña:").pack()
        self.entry_contrasena = tk.Entry(self, show="*")
        self.entry_contrasena.pack()

        tk.Button(self, text="Iniciar Sesión", command=self.login).pack(pady=5)
        tk.Button(self, text="Registrar nuevo usuario", command=self.frame_registro).pack()

    def frame_registro(self):
        self.limpiar_pantalla()
        self.establecer_color_fondo("white")
        tk.Label(self, text="Registrar Usuario", font=("Arial", 18)).pack(pady=10)

        tk.Label(self, text="Usuario:").pack()
        self.entry_reg_usuario = tk.Entry(self)
        self.entry_reg_usuario.pack()

        tk.Label(self, text="Contraseña:").pack()
        self.entry_reg_contrasena = tk.Entry(self, show="*")
        self.entry_reg_contrasena.pack()

        tk.Button(self, text="Registrar", command=self.registrar).pack(pady=5)
        tk.Button(self, text="Volver a login", command=self.frame_login).pack()

    def frame_panel(self):
        self.limpiar_pantalla()
        self.establecer_color_fondo(self.color_actual)

        tk.Label(self, text=f"Bienvenido, {self.usuario}", font=("Arial", 16)).pack(pady=10)

        # Notas
        tk.Label(self, text="Notas guardadas:", font=("Arial", 12, "bold")).pack()
        self.lista_notas = tk.Listbox(self, height=7)
        self.lista_notas.pack(fill=tk.X, padx=20)
        self.actualizar_lista_notas()

        frame_botones_notas = tk.Frame(self, bg=self.color_actual)
        frame_botones_notas.pack(pady=5)
        tk.Button(frame_botones_notas, text="Agregar nota", command=self.agregar_nota).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones_notas, text="Borrar nota seleccionada", command=self.borrar_nota).pack(side=tk.LEFT, padx=5)

        # Credenciales
        tk.Label(self, text="Credenciales guardadas:", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.lista_credenciales = tk.Listbox(self, height=7)
        self.lista_credenciales.pack(fill=tk.X, padx=20)
        self.actualizar_lista_credenciales()

        frame_botones_cred = tk.Frame(self, bg=self.color_actual)
        frame_botones_cred.pack(pady=5)
        tk.Button(frame_botones_cred, text="Agregar credencial", command=self.agregar_credencial).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botones_cred, text="Borrar credencial seleccionada", command=self.borrar_credencial).pack(side=tk.LEFT, padx=5)

        # Botones finales
        tk.Button(self, text="Cambiar color", command=self.cambiar_color).pack(pady=5)
        tk.Button(self, text="Cerrar sesión", command=self.cerrar_sesion).pack(pady=5)

    def login(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        if not usuario or not contrasena:
            messagebox.showwarning("Error", "Rellena usuario y contraseña")
            return
        resultado = obtener_usuario(usuario)
        if resultado and verificar_contrasena(contrasena, resultado[1]):
            self.usuario_id = resultado[0]
            self.usuario = usuario
            # Obtener color del usuario
            cursor.execute("SELECT color FROM usuarios WHERE id = ?", (self.usuario_id,))
            color = cursor.fetchone()[0] or "white"
            self.establecer_color_fondo(color)
            self.color_actual = color
            self.frame_panel()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def registrar(self):
        usuario = self.entry_reg_usuario.get()
        contrasena = self.entry_reg_contrasena.get()
        if not usuario or not contrasena:
            messagebox.showwarning("Error", "Rellena usuario y contraseña")
            return
        if registrar_usuario(usuario, contrasena):
            messagebox.showinfo("Éxito", "Usuario registrado. Ya puedes iniciar sesión.")
            self.frame_login()
        else:
            messagebox.showerror("Error", "El usuario ya existe")

    def actualizar_lista_notas(self):
        self.lista_notas.delete(0, tk.END)
        notas = obtener_notas(self.usuario_id)
        for nota in notas:
            self.lista_notas.insert(tk.END, f"{nota[1]}: {nota[2]}")

    def agregar_nota(self):
        titulo = simpledialog.askstring("Nueva nota", "Título de la nota:")
        if titulo:
            contenido = simpledialog.askstring("Nueva nota", "Contenido de la nota:")
            if contenido:
                guardar_nota(self.usuario_id, titulo, contenido)
                self.actualizar_lista_notas()

    def borrar_nota(self):
        seleccion = self.lista_notas.curselection()
        if seleccion:
            indice = seleccion[0]
            notas = obtener_notas(self.usuario_id)
            nota_id = notas[indice][0]
            borrar_nota(nota_id)
            self.actualizar_lista_notas()
        else:
            messagebox.showwarning("Atención", "Selecciona una nota para borrar")

    def actualizar_lista_credenciales(self):
        self.lista_credenciales.delete(0, tk.END)
        creds = obtener_credenciales(self.usuario_id)
        for c in creds:
            self.lista_credenciales.insert(tk.END, f"{c[1]} - {c[2]} : {c[3]}")

    def agregar_credencial(self):
        servicio = simpledialog.askstring("Nueva credencial", "Nombre del servicio o web:")
        if servicio:
            usuario_cred = simpledialog.askstring("Nueva credencial", "Usuario para el servicio:")
            if usuario_cred:
                contrasena_cred = simpledialog.askstring("Nueva credencial", "Contraseña para el servicio:")
                if contrasena_cred:
                    guardar_credencial(self.usuario_id, servicio, usuario_cred, contrasena_cred)
                    self.actualizar_lista_credenciales()

    def borrar_credencial(self):
        seleccion = self.lista_credenciales.curselection()
        if seleccion:
            indice = seleccion[0]
            creds = obtener_credenciales(self.usuario_id)
            cred_id = creds[indice][0]
            borrar_credencial(cred_id)
            self.actualizar_lista_credenciales()
        else:
            messagebox.showwarning("Atención", "Selecciona una credencial para borrar")

    def cerrar_sesion(self):
        self.usuario_id = None
        self.usuario = None
        self.frame_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()

conexion.close()
