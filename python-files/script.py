import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta, date


# Crear base de datos si no existe
conn = sqlite3.connect("gimnasio.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS miembros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    cedula_id TEXT,
    fecha_inicio DATE,
    duracion_meses INTEGER,
    fecha_vencimiento DATE
)
""")
conn.commit()
today = date.today()
nombre = ""
cedula_id = ""
duracion = 1
fecha_inicio = datetime.today()
fecha_vencimiento = fecha_inicio + timedelta(days=30*duracion)



def existe_dato(nombre_tabla, nombre_columna, nombre, nombre_db):
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        # Query con parámetros seguros (para evitar SQL injection)
        query = f"SELECT 1 FROM {nombre_tabla} WHERE {nombre_columna} = ? LIMIT 1"
        cursor.execute(query, (nombre,))
        
        # Si encuentra algo, fetchone() devuelve un registro, si no, None
        resultado = cursor.fetchone()
        
        return resultado is not None
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return False


def obtener_fecha_vencimiento (cedula_id, nombre_db):
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        # Buscar la fecha de vencimiento del usuario
        cursor.execute("SELECT fecha_vencimiento FROM miembros WHERE cedula_id = ? LIMIT 1", (cedula_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            return resultado[0]  # la fecha viene como string (ej: '2025-11-03')
        else:
            return None  # no existe el usuario
        
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return None


# Función para guardar miembro


def registrar():
    nombre = entry_nombre.get()
    cedula_id = str(entry_cedula.get())
    duracion = 1
    fecha_inicio = datetime.today()
    fecha_vencimiento = fecha_inicio + timedelta(days=30*duracion)
    cursor.execute("INSERT INTO miembros (nombre, cedula_id, fecha_inicio, duracion_meses, fecha_vencimiento) VALUES (?, ?, ?, ?, ?)",(nombre, cedula_id, fecha_inicio.date(), duracion, fecha_vencimiento.date()))
    conn.commit()
    messagebox.showinfo("Registro", f"{nombre} registrado hasta {fecha_vencimiento.date()}")

def revisar_mens():
    nombre = entry_nombre.get()
    cedula_id = str(entry_cedula.get())
    
    proof_1 = existe_dato("miembros", "nombre", nombre, "gimnasio.db")
    proof_2 = existe_dato("miembros", "cedula_id", cedula_id, "gimnasio.db")
    fecha_vencimiento = obtener_fecha_vencimiento(cedula_id, "gimnasio.db")

    if proof_1 and proof_2:
        if fecha_vencimiento:
            # Convertir string a fecha
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
            if today == fecha_vencimiento:
                messagebox.showinfo("Información", "Lo lamento, su mensualidad ha expirado")
            else:
                messagebox.showinfo("Información", f"Puedes pasar, válido hasta {fecha_vencimiento}")
        else:
            messagebox.showinfo("Información", "No se encontró fecha de vencimiento")
    else:
        messagebox.showinfo("Información", "Usuario no registrado")


def eliminar_usr():
    nombre = entry_nombre.get()
    cedula_id = str(entry_cedula.get())
    cursor.execute("DELETE FROM miembros WHERE cedula_id = ?", (cedula_id,))
    conn.commit()
    messagebox.showinfo("Información", f"Usuario {nombre} eliminado")

        
    
# Crear ventana
root = tk.Tk()
root.title("Registro Gimnasio")
root.geometry("1000x2000")

tk.Label(root, text="Nombre:").pack()
entry_nombre = tk.Entry(root)
entry_nombre.pack()

tk.Label(root, text="cedula:").pack()
entry_cedula = tk.Entry(root)
entry_cedula.pack()



btn2 = tk.Button(root, text="revisar", command=revisar_mens)
btn2.pack(pady=10)

btn = tk.Button(root, text="Registrar", command=registrar)
btn.pack(pady=10)

btn3 = tk.Button(root, text="ELIMINAR", command=eliminar_usr)
btn3.pack(pady=10)

#btn4 = tk.Button(root, text="comprobar registro", command=comprobar_registro())
#btn4.pack(pady=10)




root.mainloop()
