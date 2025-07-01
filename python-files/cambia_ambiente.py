import os
import shutil
    
def copiar_archivo(origen, destino):   
    try:
        print(f"Copiando {origen} a {destino}")
        shutil.copy(origen, destino)
    except (FileNotFoundError, shutil.Error) as error:
        print(error)
    return

def leer_estado(nombre_archivo):
    try:
        with open(nombre_archivo, "r") as archivo:
            contenido = archivo.read()
            estado_actual = contenido.split("\n")[0].strip()
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no se encuentra.")
    
    return estado_actual

def cambiar_estado(nombre_archivo, estado_nuevo):
    realizado = bool(0)
    try:
        with open(nombre_archivo, "r") as archivo:
            linea = archivo.readline().strip()
            if linea == estado_nuevo:
                print(f"El SIT ya esta en estado'{estado_nuevo}'.")
                print("El estado no ha sido cambiado.")
                realizado = bool(0)
            else:
                with open(nombre_archivo, "w") as archivo_escritura:
                    archivo_escritura.write(estado_nuevo)
                    print(f"El estado ha sido cambiado a '{estado_nuevo}'.")
                    realizado = bool(1)

    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
        realizado = bool(0)
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        realizado = bool(0)
        
    return realizado
        

def contar_archivos_con_cadena(ruta_raiz, cadena):
    contador = 0
    contador_e = 0
    contador_o = 0
    archivos_encontrados = []
    
    for root, dirs, files in os.walk(ruta_raiz):
        for file in files:
            archivo_path = os.path.join(root, file)
            try:
                with open(archivo_path, 'r') as f:
                    contenido = f.read()
                    if cadena in contenido:
                        contador += 1
                        archivos_encontrados.append(archivo_path)
                        
            except UnicodeDecodeError:
                contador_e +=1
            except Exception as e:
                print(f"Error leyendo archivo {archivo_path}: {e}")
                contador_o +=1
    
    return contador, contador_e, contador_o, archivos_encontrados

def reemplazar_cadena_en_archivos(ruta_raiz, cadena_original, cadena_nueva):
    archivos_modificados = []
    contador_we = 0
    contador_wo = 0
    contador_w = 0
    
    for root, dirs, files in os.walk(ruta_raiz):
        for file in files:
            archivo_path = os.path.join(root, file)
            try:
                with open(archivo_path, 'r') as f:
                    contenido = f.read()
                    if cadena_original in contenido:
                        contenido_nuevo = contenido.replace(cadena_original, cadena_nueva)
                        with open(archivo_path, 'w') as f:
                            f.write(contenido_nuevo)
                        archivos_modificados.append(archivo_path)
                        contador_w += 1
            except UnicodeDecodeError:
                contador_we += 1
            except Exception as e:
                print(f"Error modificando archivo {archivo_path}: {e}")
                contador_wo += 1
    
    return contador_w, contador_we, contador_wo, archivos_modificados

def main():
    cadena_original = ""
    cadena_nueva = ""
    imagen= ""
    pasar_a = ""
    ruta_raiz = "C:\\SIT 2018\\Sistema Catastral"
    estado = leer_estado(".\\estado.txt")
    if estado == "TESTING":
        cadena_original = "https://migracion.test.cba.gov.ar"
        cadena_nueva = "https://sitservicios.cba.gov.ar"
        imagen= "PROD login.jpg"
        pasar_a = "PRODUCCION"
    elif estado == "PRODUCCION":
        cadena_original = "https://sitservicios.cba.gov.ar"
        cadena_nueva = "https://migracion.test.cba.gov.ar"
        pasar_a="TESTING"
        imagen="TEST login.jpg"
    else:
        print("Estado no es válido")
      
    contador, contador_e, contador_o, archivos_encontrados = contar_archivos_con_cadena(ruta_raiz, cadena_original)
        
    for archivo in archivos_encontrados:
        print(archivo)
    
    print(f"{contador} archivos CON {cadena_original}")
    print(f"{contador_e} archivos exe y dll")
    print(f"{contador_o} otros errores")
    print(f"Total: {contador} archivos")
    
    modificar = input("¿Pasa el SIT a "+pasar_a+"? (s/n): ")
    if modificar.lower() == 's':
        contador_w, contador_we, contador_wo, archivos_modificados = reemplazar_cadena_en_archivos(ruta_raiz, cadena_original, cadena_nueva)
        print(f"Se modificaron {len(archivos_modificados)} archivos:")
        if archivos_modificados != 0 :
            for archivo in archivos_modificados:
                print(archivo)
            if cambiar_estado(".\\estado.txt", pasar_a):
                copiar_archivo (".\\"+imagen, ruta_raiz+"\\Archivos\\login.jpg")
                print("EL SIT PASO A ESTADO "+pasar_a)
            else:
                print("EL SIT NO PASO A ESTADO "+pasar_a)
        else:
            print("EL SIT NO PASO A ESTADO "+pasar_a)
            
        print(f"{contador_w} archivos modificados {cadena_nueva}")
        print(f"{contador_we} archivos exe y dll")
        print(f"{contador_wo} otros errores")
   
    input("Presione una tecla para cerrar el programa")
    
    
if __name__ == "__main__":
    main()
