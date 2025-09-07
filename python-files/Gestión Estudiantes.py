import sqlite3

# Conexión a la base de datos (se creará si no existe)
conexion = sqlite3.connect("estudiantes.db")

# Crear un cursor para ejecutar comandos SQL
cursor = conexion.cursor()

# Crear la tabla de estudiantes
cursor.execute("""
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres_apellidos TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    edad INTEGER NOT NULL,
    documento_identidad TEXT UNIQUE NOT NULL,
    telefono TEXT NOT NULL,
    nombre_acudiente TEXT NOT NULL
);
""")

# Funciones del menú

def agregar_estudiante():
    nombres_apellidos = input("Ingrese nombres y apellidos: ")
    fecha_nacimiento = input("Ingrese fecha de nacimiento (YYYY-MM-DD): ")
    edad = int(input("Ingrese edad: "))
    documento_identidad = input("Ingrese documento de identidad: ")
    telefono = input("Ingrese teléfono: ")
    nombre_acudiente = input("Ingrese nombre del acudiente: ")

    try:
        cursor.execute("""
        INSERT INTO estudiantes (nombres_apellidos, fecha_nacimiento, edad, documento_identidad, telefono, nombre_acudiente)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombres_apellidos, fecha_nacimiento, edad, documento_identidad, telefono, nombre_acudiente))
        conexion.commit()
        print("✅ Estudiante agregado exitosamente.")
    except sqlite3.IntegrityError:
        print("⚠️ Ya existe un estudiante con ese documento de identidad.")


def listar_estudiantes():
    cursor.execute("SELECT * FROM estudiantes")
    registros = cursor.fetchall()
    if registros:
        print("\n--- Lista de Estudiantes ---")
        for r in registros:
            print(f"ID: {r[0]}, Nombre: {r[1]}, Fecha Nacimiento: {r[2]}, Edad: {r[3]}, Documento: {r[4]}, Teléfono: {r[5]}, Acudiente: {r[6]}")
    else:
        print("⚠️ No hay estudiantes registrados.")


def buscar_estudiante():
    doc = input("Ingrese documento de identidad del estudiante a buscar: ")
    cursor.execute("SELECT * FROM estudiantes WHERE documento_identidad = ?", (doc,))
    r = cursor.fetchone()
    if r:
        print(f"ID: {r[0]}, Nombre: {r[1]}, Fecha Nacimiento: {r[2]}, Edad: {r[3]}, Documento: {r[4]}, Teléfono: {r[5]}, Acudiente: {r[6]}")
    else:
        print("⚠️ Estudiante no encontrado.")


def eliminar_estudiante():
    doc = input("Ingrese documento de identidad del estudiante a eliminar: ")
    cursor.execute("DELETE FROM estudiantes WHERE documento_identidad = ?", (doc,))
    if cursor.rowcount > 0:
        conexion.commit()
        print("✅ Estudiante eliminado exitosamente.")
    else:
        print("⚠️ Estudiante no encontrado.")


# Menú principal
while True:
    print("""
    \n--- Menú de Gestión de Estudiantes ---
    1. Agregar estudiante
    2. Listar estudiantes
    3. Buscar estudiante
    4. Eliminar estudiante
    5. Salir
    """)
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        agregar_estudiante()
    elif opcion == "2":
        listar_estudiantes()
    elif opcion == "3":
        buscar_estudiante()
    elif opcion == "4":
        eliminar_estudiante()
    elif opcion == "5":
        print("👋 Saliendo del sistema...")
        break
    else:
        print("⚠️ Opción inválida. Intente nuevamente.")

# Cerrar la conexión al salir
conexion.close()
