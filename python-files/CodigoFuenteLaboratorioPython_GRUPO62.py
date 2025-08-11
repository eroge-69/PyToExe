from datetime import datetime #USA LA LIBRERIA DE PYTHON DE DATETIME PARA TOMAR LA FECHA

# Función para ingresar datos del perfil

def ingresar_perfil():
    global nombre, apellido, edad # HACE QUE LAS VARIABLES SE VUELVAN GLOBAL PARA USARLAS EN TODO EL PROGRAMA 
    nombre = input("Ingrese nombre: ")
    apellido = input("Ingrese apellido: ")
    edad = int(input("Ingrese su edad: ")) # INT -> CONVIERTE LA VARIABLE INGRESADA EN UN ENTERO
    return nombre, apellido, edad


# Función para registrar recolección

def ingreso_recoleccion():
    try:
        fecha = input("Ingrese la fecha de recolección (YYYY-MM-DD): ")
        datetime.strptime(fecha, "%Y-%m-%d")  # Valida formato
        kg = float(input("Ingrese la cantidad de kilos recolectados: ")) #CONVIERTE LA VARIABLE EN UN TIPO DE DATO FLOTANTE 

        with open("recoleccion.txt", "a") as archivo: #ABRE EL ARCHIVO DE TEXTO PARA PODER LUEGO USAR LA ACCION "a", LO CUAL AGREGA AL ARCHIVO LOS DATOS QUE SE INGRESAN POR CONSOLA
            archivo.write(f"{fecha}, {kg}\n") #ESCRIBE EN EL TEXTO (.TXT)

        print("✅ Recolección registrada correctamente")
    except ValueError:
        print("❌ Error: Formato de fecha o cantidad inválida. Use YYYY-MM-DD y un número válido")

# Función para consultar progreso

def consulta_progreso():
    try:
        with open("recoleccion.txt", "r") as archivo:
            lineas = archivo.readlines()

        if not lineas:
            print("No hay datos de recolección aún")
            return

        total_kg = 0
        recoleccion_por_dia = []

        for linea in lineas:
            fecha_str, kg_str = linea.strip().split(",") #"STRIP" ELIMINA ESPACIOS Y CARACTERES ESPECIALES A AMBOS LADOS Y "SPLIT", DIVIDE EL TEXTO EN PARTES CREANDO UNA LISTA USANDO EL SEPARADOR QUE SE ELIJA (EJ ",")
            fecha = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
            kg = float(kg_str.strip())
            total_kg += kg
            recoleccion_por_dia.append((fecha, kg))

        print("\nPROGRESO DE RECOLECCIÓN DE: ", nombre + " " + apellido)
        print(f"Total recolectado: {total_kg:.2f} kg")

        print("\nDetalle por día:")
        for fecha, kg in recoleccion_por_dia:
            print(f"{fecha.strftime('%d/%m/%Y')}: {kg:.2f} kg")

    except FileNotFoundError:
        print("❌ No se encontró el archivo 'recoleccion.txt'. Aún no se registró ninguna recolección.")
    except Exception as e:
        print(f"Ocurrió un error al consultar el progreso: {e}")

# Función para calcular las recompensas

def calcular_recompensas():
    try:
        with open("recoleccion.txt", "r") as archivo:
            lineas = archivo.readlines()

        if not lineas:
            print("📭 No hay datos de recolección aún.")
            return

        total_kg = 0
        for linea in lineas:
            _, kg_str = linea.strip().split(",")
            kg = float(kg_str.strip())
            total_kg += kg

        recompensa = total_kg * 10  # $10 por kilo
        print("\n🎁 RECOMPENSAS 🎁")
        print(f"Total recolectado: {total_kg:.2f} kg")
        print(f"💵 Recompensa total: ${recompensa:.2f}")
        print("¡Gracias por cuidar el planeta! 🌱")

    except FileNotFoundError:
        print("❌ No se encontró el archivo 'recoleccion.txt'. Aún no se registró ninguna recolección.")
    except Exception as e:
        print(f"⚠️ Ocurrió un error al calcular las recompensas: {e}")



# --- PROGRAMA PRINCIPAL ---
print("🌱 APLICACION DE RECOLECCION NEA 2.0 ♻️ ", "\n")
print("Integrantes: ", "\n", "👩 Ailin", "\n", "👩 Mailén", "\n", "👩 Laura", "\n", "👨 Sebastián", "\n")

opcion = 0
opcion1 = int(input("Para iniciar el programa presione 1: "))

if opcion1 == 1:
    while opcion != 5:
        print("\n 🌱 ===== MENÚ DE OPCIONES ===== ♻️")
        print("1. Ingreso de datos 🌿")
        print("2. Ingreso de recolección ♻️")
        print("3. Consulta de progreso 📊")
        print("4. Recompensas (en desarrollo) 💵")
        print("5. Salir del programa 🚪")
        print("============================")

        try:
            opcion = int(input("➡️ Ingrese su opción: "))

            if opcion == 1:
                ingresar_perfil()
                print("📌 Datos ingresados:")
                print(f"Nombre: {nombre}")
                print(f"Apellido: {apellido}")
                print(f"Edad: {edad} años")

            elif opcion == 2:
                ingreso_recoleccion()

            elif opcion == 3:
                consulta_progreso()

            elif opcion == 4:
                calcular_recompensas()

            elif opcion == 5:
                print("Fin del programa. ¡Gracias por contribuir con espacios más limpios!")

            else:
                print("Opción incorrecta. Intente nuevamente.")

        except ValueError:
            print("Error: debe ingresar un número válido.")

else:
    print("Fin del programa.")
