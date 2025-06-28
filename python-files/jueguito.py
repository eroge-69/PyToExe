import os
import subprocess
from win32com.client import Dispatch  # Requiere pywin32

def ejecutar_acceso_directo(ruta_lnk):
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_lnk):
            raise FileNotFoundError(f"No se encontró el acceso directo: {ruta_lnk}")

        # Leer información del acceso directo
        shell = Dispatch("WScript.Shell")
        acceso = shell.CreateShortCut(ruta_lnk)
        
        print(f"Acceso directo encontrado: {ruta_lnk}")
        print(f"Ejecutable destino: {acceso.TargetPath}")
        print(f"Directorio de trabajo: {acceso.WorkingDirectory}")
        print(f"Argumentos: {acceso.Arguments or 'Ninguno'}")
        
        # Ejecutar el juego
        subprocess.Popen(
            acceso.TargetPath,
            cwd=acceso.WorkingDirectory,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("¡Plants vs. Zombies se está iniciando!")
        
    except Exception as e:
        print(f"Error: {e}")
        input("Presiona Enter para salir...")

# Ruta al acceso directo (AJUSTA ESTA RUTA)
RUTA_ACCESO_DIRECTO = r"C:\Users\HP\Desktop\joel\PlantsVsZombies.lnk"

if __name__ == "__main__":
    ejecutar_acceso_directo(RUTA_ACCESO_DIRECTO)
