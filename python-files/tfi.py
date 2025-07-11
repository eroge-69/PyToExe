# Aplicación que permite: Registrar, Visualizar, Actualizar por ID, Eliminar por ID, Buscar por ID, Reporte de bajo stock e Importar base de datos en archivo TXT.

import sqlite3
import datetime
from colorama import Fore, init
    # **** Iniciamos colorama **************************************************
init (autoreset=True)

    # **** Conectar o crear base de datos **************************************
conexion = sqlite3.connect("inventario.db")
cursor = conexion.cursor()

    # **** Crear tabla productos ***********************************************
cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL,
        categoria TEXT,
        fechamodificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

    # **** Confirmar los cambios y cerrar la conección **********************
conexion.commit()
conexion.close()

print(Fore.GREEN + "\nBase de datos de productos creada con éxito!!!\n")


# ------------------------------- CREAR FUNCION AGREGAR PRODUCTOS ----------------------------------------------

def agregar_producto():
    """
        Función que agrega un producto a la base de datos inventario.db
    """
    try:
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()

        cursor.execute("BEGIN TRANSACTION")
        
        # **** Pedimos datos del producto a agregar a la base
        
        nombre = input(" 📦  Ingrese el nombre del producto a agregar: ").strip().title()
        descripcion = input(" 📝 Ingrese la descripción del producto: ").strip().title()
        cantidad = int(input(" 🔢 Ingrese la cantidad (expresado en Kg): "))
        precio = float(input(" 💲 Ingrese el precio $ : "))
        categoria = input(" 🏷️ Ingrese la categoría del producto: ").strip().title()



        # **** Validaciones simples con raise que detiene la ejecución por ingresar un valor que no correspondeS
        if not nombre or cantidad < 0 or precio < 0:
            raise ValueError(" ❌ Datos inválidos: nombre vacío, cantidad o precio negativo.")

        # Inserción de los datos ingresados a la base de datos: inventario
        cursor.execute('''
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, fechamodificacion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, descripcion, cantidad, precio, categoria, datetime.datetime.now().strftime("%d\%m\%Y")))

        conexion.commit()
        print(Fore.GREEN + f" ✅ Producto {nombre} agregado con éxito!")

    except Exception as e:
        conexion.rollback()
        print(Fore.RED + f" ❌ Error al agregar producto: {e}")

    finally:
        conexion.close()

# --------------------------------------------------------------------------------------------------------------

        
# ------------------------------ CREAR FUNCION VISUALIZAR PRODUCTOS --------------------------------------------

def visualizar_productos():
    """
        Permite consultar los productos que se encuentran en stock en la base de datos. No utilizo BEGIN TRANSACTION porque solamente hago consultas a la base de datos
    """
    import sqlite3
    from colorama import Fore, init
    # **** Iniciamos colorama
    init (autoreset=True)

    # **** Conectamos con la base de datos
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, descripcion, cantidad, precio, categoria, fechamodificacion FROM productos")
    productos = cursor.fetchall()

    if not productos:
        print(Fore.YELLOW + "INFO!! No hay productos registrados en la base de datos")
        return
    print(Fore.GREEN + f"\n=====================| Listados de Productos en Inventario |========================\n")
    for producto in productos:
        print(Fore.LIGHTGREEN_EX + f"ID: {producto[0]}, Producto: {producto[1]}, Descripción: {producto[2]}, Cantidad: {producto[3]}, Precio: {producto[4]}, Categoría: {producto[5]}, Fecha de Cambio: {producto[6]}")
    
    conexion.close()
    
# --------------------------------------------------------------------------------------------------------------
   
   
# ------------------------------ CREAR FUNCION ACTUALIZAR PRODUCTOS --------------------------------------------

def actualizar_productos():
    """
    Permite actualizar los datos de los productos que se encuentran en el inventario, mediante el N° de ID.
    """
    try:
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()

        print(Fore.LIGHTMAGENTA_EX + "\n*** Listado de productos existentes en la base de datos ***")
        visualizar_productos()

        id_producto = input("\nIngrese el ID del producto a modificar: ").strip()

        if not id_producto.isdigit():
            print(Fore.RED + "ERROR: El ID debe ser un número válido.")
            return

        cursor.execute("SELECT id, nombre, descripcion, cantidad, precio, categoria FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()

        if not producto:
            print(Fore.YELLOW + "INFO: No se encontraron productos con ese ID.")
            return

        print(Fore.GREEN + f"\n=== Producto con el ID {id_producto} ===")
        print(Fore.LIGHTCYAN_EX + f"ID: {producto[0]}, Nombre: {producto[1]}, Descripción: {producto[2]}, Cantidad: {producto[3]}, Precio: {producto[4]}, Categoría: {producto[5]}")

        # **** Nuevos datos
        nuevo_nombre = input("Nuevo nombre (dejar vacío para no modificar): ").strip().title() or producto[1]
        nueva_descripcion = input("Nueva descripción (dejar vacío para no modificar): ").strip().title() or producto[2]
        nueva_cantidad = input("Nueva cantidad (dejar vacío para no modificar): ").strip()
        nuevo_precio = input("Nuevo precio (dejar vacío para no modificar): ").strip()
        nueva_categoria = input("Nueva categoría (dejar vacío para no modificar): ").strip().title() or producto[5]

        # **** Validaciones numéricas
        if nueva_cantidad:
            if not nueva_cantidad.isdigit() or int(nueva_cantidad) < 0:
                print(Fore.RED + "ERROR: El stock debe ser un número entero no negativo.")
                return
            nueva_cantidad = int(nueva_cantidad)
        else:
            nueva_cantidad = producto[3]

        if nuevo_precio:
            try:
                nuevo_precio = float(nuevo_precio)
                if nuevo_precio <= 0:
                    raise ValueError
            except ValueError:
                print(Fore.RED + "ERROR: El precio debe ser un número válido mayor que cero.")
                return
        else:
            nuevo_precio = producto[4]

        fecha_modificacion = datetime.datetime.now().strftime("%d\%m\%Y")
        
        try:
            cursor.execute("BEGIN TRANSACTION")

            cursor.execute("""
                UPDATE productos
                SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?, fechamodificacion = ?
                WHERE id = ?
            """, (nuevo_nombre, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_categoria, fecha_modificacion, id_producto))

            conexion.commit()
            print(Fore.GREEN + f" ✅ Producto con ID {id_producto} actualizado correctamente.")

        except Exception as e:
            conexion.rollback()
            print(Fore.RED + f" ❌ Error al actualizar producto: {e}")
            
    except sqlite3.Error as e:
        print(Fore.RED + f"[ERROR] Problema general con la base de datos: {e}")

    finally:
        conexion.close()
# --------------------------------------------------------------------------------------------------------------

# ---------------------------------- CREAR FUNCION ELIMINAR PRODUCTO -------------------------------------------

def eliminar_producto():
    """
    Permite eliminar productos que se encuentran en el inventario, mediante el N° de ID.
    """
    
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id, nombre, descripcion, cantidad, precio, categoria, fechamodificacion FROM productos")
        
        productos = cursor.fetchall()
        
        if not productos:
            print(Fore.GREEN + "\n INFO: No hay productos registrados")
            return
        
        print(Fore.GREEN + "\n ==== Lista de Productos ====")
        for producto in productos:
            print(Fore.LIGHTGREEN_EX + f"ID: {producto[0]}, Producto: {producto[1]}, Descripción: {producto[2]}, Cantidad: {producto[3]}, Precio: {producto[4]}, Categoría: {producto[5]}, Fecha y Hora: {producto[6]}")

    # **** Solicitar el ID del producto a eliminar
        id_producto = input("\nIngresá el ID del producto a eliminar: ").strip()
            
        if not id_producto.isdigit():
            print(Fore.RED + "[ERROR] El ID ingresado no es válido.")
            return
        id_producto = int(id_producto)
            
    # **** Verificar si el producto existe en la base de datos
        cursor.execute("SELECT nombre, descripcion, cantidad, precio, categoria, fechamodificacion FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()
            
        if not producto:
            print(Fore.YELLOW + "[INFO] No se encontró un producto con ese ID.")
            return
    # **** Confirmamos si realmente se quiere eliminar el producto seleccionado
        confirmacion = input(Fore.YELLOW + f"¿Estás seguro de que querés eliminar a {producto[0]}? S/N: ").strip().lower()
        
        if confirmacion != "s":
            print(Fore.GREEN + "[CANCELADO] La eliminación ha sido cancelada.")
            return
        
    # **** Eliminar el producto por su ID
        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            conexion.commit()
            print(Fore.GREEN + f"[ÉXITO] Producto {producto[0]} eliminado correctamente.")
            
        except Exception as e:
            conexion.rollback()
            print(Fore.RED + f"[ERROR] No se pudo eliminar el producto. Se ha revertido la operación.\nDetalles: {e}")
    
    except sqlite3.Error as e:
        print(Fore.RED + f"[ERROR] Problema general con la base de datos: {e}")

    finally:
        conexion.close()
# --------------------------------------------------------------------------------------------------------------

# ------------------------ CREAR LA FUNCION BUSCAR PRODUCTO POR ID ---------------------------------------------

def buscar_producto_por_id():
    """
    Permite buscar productos mediante su ID. No uso BEGIN TRANSACTION porque solo consultamos la base de datos
    """
    import sqlite3
    from colorama import Fore, init
# Iniciamos colorama
    init (autoreset=True)
    
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    visualizar_productos()
    try:
        id_producto = input("Ingresá el ID del producto a buscar: ").strip()

        if not id_producto.isdigit():
            print(Fore.RED + "ERROR: El ID debe ser un número.")
            return

        cursor.execute("""
            SELECT id, nombre, descripcion, precio, categoria, fechamodificacion
            FROM productos
            WHERE id = ?
        """, (int(id_producto),))

        producto = cursor.fetchone()

        if producto:
            print(Fore.GREEN + "\n=== Producto encontrado ===")
            print(Fore.LIGHTGREEN_EX + f"ID: {producto[0]}")
            print(f"Nombre: {producto[1]}")
            print(f"Descripción: {producto[2]}")
            print(f"Precio: $ {producto[3]}")
            print(f"Categoría: {producto[4]}")
            print(f"Fecha de modificación: {producto[5]}")
        else:
            print(Fore.YELLOW + "INFO: No se encontró un producto con ese ID.")

    except sqlite3.Error as e:
        print(Fore.RED + f"[ERROR] Problema con la base de datos: {e}")

    finally:
        conexion.close()

# ------------------ CREAR UN REPORTE DE BAJA CANTIDAD DE PRODUCTOS --------------------------------------------

def reporte_stock_bajo():
    """
    Genera un reporte de productos cuyo stock es igual o inferior al valor ingresado por el usuario.
    """
    import sqlite3
    from colorama import Fore, init
# Iniciamos colorama
    init (autoreset=True)
    
    try:
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()

        print(Fore.LIGHTMAGENTA_EX + "\n=== Reporte de Cantidad Baja ===")
        limite = input("Ingresá el límite de cantidad para visualizar productos: ").strip()

        if not limite.isdigit() or int(limite) < 0:
            print(Fore.RED + "ERROR: El valor debe ser un número entero no negativo.")
            return

        limite = int(limite)

        cursor.execute("""
            SELECT id, nombre, descripcion, cantidad, precio, categoria, fechamodificacion
            FROM productos
            WHERE cantidad <= ?
            ORDER BY cantidad ASC
        """, (limite,))

        productos = cursor.fetchall()

        if not productos:
            print(Fore.YELLOW + f"No hay productos con cantidad igual o inferior a {limite}.")
            return

        print(Fore.GREEN + f"\nProductos con cantidad ≤ {limite}:\n")
        for p in productos:
            print(Fore.LIGHTGREEN_EX + f"ID: {p[0]}, Nombre: {p[1]}, Descripción: {p[2]}, Cantidad: {p[3]}, Precio: ${p[4]}, Categoría: {p[5]}, Última modificación: {p[6]}")

    except sqlite3.Error as e:
        print(Fore.RED + f"[ERROR] Problema con la base de datos: {e}")

    finally:
        conexion.close()

# --------------------------------------------------------------------------------------------------------------

# -------------------------- CREAR REPORTE EN ARCHIVO TXT ------------------------------------------------------

def generar_reporte_txt():
    """
    Genera un archivo TXT con todos los productos de la base de datos incluyendo
    ID, nombre, descripción, cantidad, precio, categoría y fecha de modificación.
    """
    import sqlite3
    from colorama import Fore, init
    import datetime

# Iniciar colorama
    init(autoreset=True)


    try:
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()

        cursor.execute("BEGIN TRANSACTION")

        cursor.execute("""
            SELECT id, nombre, descripcion, cantidad, precio, categoria, fechamodificacion
            FROM productos
        """)
        productos = cursor.fetchall()

        if not productos:
            print(Fore.YELLOW + "[INFO] No hay productos para exportar.")
            return

        nombre_archivo = "reporte_inventario.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(" 📦 REPORTE DE INVENTARIO\n")
            archivo.write(f"Generado: {datetime.datetime.now()}\n\n")
            archivo.write("ID | NOMBRE | DESCRIPCIÓN | CANTIDAD | PRECIO | CATEGORÍA | FECHAMODIFICACIÓN\n")
            archivo.write("-" * 90 + "\n")

            for producto in productos:
                linea = f"{producto[0]} | {producto[1]} | {producto[2]} | {producto[3]} | ${producto[4]:.2f} | {producto[5]} | {producto[6]}\n"
                archivo.write(linea)

        conexion.commit()
        print(Fore.GREEN + f" ✅ Reporte generado con éxito en el archivo: {nombre_archivo}")

    except Exception as e:
        conexion.rollback()
        print(Fore.RED + f" ❌ Error al generar el reporte. Se canceló la operación.\nDetalles: {e}")

    finally:
        conexion.close()

# -------------------------------------------------------------------------------------------------------------


# ------------------------ CREA LA FUNCION DE MENU PRINCIPAL --------------------------------------------------

def menu(): 
    """ 
    Muestra el menú principal y permite seleccionar las acciones a 
realizar en la base de datos. 
    """ 
    
    while True: 
        print(Fore.BLUE + "\n=== Menú de Gestión de Productos ===\n") 
        print(Fore.MAGENTA + "1. Registrar nuevo producto") 
        print(Fore.MAGENTA + "2. Visualizar productos registrados")
        print(Fore.MAGENTA + "3. Actualizar datos de un producto") 
        print(Fore.MAGENTA + "4. Eliminar un producto") 
        print(Fore.MAGENTA + "5. Buscar un producto por su id")
        print(Fore.MAGENTA + "6. Crear un reporte de cantidad baja")
        print(Fore.MAGENTA + "7. Generar reporte en archivo txt")
        print(Fore.MAGENTA + "8. Salir") 
        
        opcion = input(Fore.CYAN + "\nSeleccioná una opción: \n").strip() 
        
        if opcion == "1":
            agregar_producto() 
        elif opcion == "2": 
            visualizar_productos() 
        elif opcion == "3": 
            actualizar_productos() 
        elif opcion == "4": 
            eliminar_producto()
        elif opcion == "5":
            buscar_producto_por_id()
        elif opcion == "6":
            reporte_stock_bajo()
        elif opcion == "7":
            generar_reporte_txt()    
        elif opcion =="8":
            print(Fore.GREEN + "\nGracias por usar el sistema. ¡Hasta luego!\n")
            break 
        
        else: 
            print(Fore.RED + "[ERROR] Opción no válida. Intentá nuevamente.") 
            
# Ejecutar el menú 

menu()

