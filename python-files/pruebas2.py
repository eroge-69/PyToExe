import os
import shutil

user_temp = os.getenv("TEMP")  
system_temp = "C:\\Windows\\Temp"  

def limpiar_carpeta(temp_folder):
    """ Elimina todos los archivos y carpetas dentro de la carpeta TEMP especificada """
    if temp_folder and os.path.exists(temp_folder):
        print(f"Limpieza en curso: {temp_folder}")
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Archivo eliminado: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
                    print(f"Carpeta eliminada: {file_path}")
            except Exception as e:
                print(f"No se pudo eliminar {file_path}: {e}")
        print("Limpieza completada.\n")
    else:
        print(f"No se encontró la carpeta: {temp_folder}\n")

# Ejecutar limpieza en ambas carpetas TEMP
limpiar_carpeta(user_temp)
limpiar_carpeta(system_temp)
