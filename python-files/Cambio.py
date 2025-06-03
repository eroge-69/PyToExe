import os
import time
import subprocess
import getpass

# Definir la nueva contraseña
new_password = "Apo272727."
admin_account = "Local-Admin"

# Función para cambiar la contraseña de la cuenta de administrador
def change_admin_password():
    try:
        # Comando para cambiar la contraseña de la cuenta de administrador
        command = f"net user {admin_account} {new_password}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"La contraseña de la cuenta '{admin_account}' ha sido cambiada exitosamente.")
        else:
            print("Error: No se pudo cambiar la contraseña de la cuenta.")
            print(f"Detalles del error: {result.stderr}")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Función para programar la tarea en el Planificador de Tareas
def schedule_task():
    try:
        # Ruta al script actual (asumiendo que está guardado como .py)
        script_path = os.path.abspath(__file__)
        
        # Comando para crear la tarea en el Planificador de Tareas
        task_command = f'schtasks /create /tn "ChangeAdminPassword" /tr "python {script_path}" /sc daily /mo 0.5 /ru SYSTEM'
        result = subprocess.run(task_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("La tarea ha sido programada para ejecutarse cada 12 horas.")
        else:
            print("Error: No se pudo programar la tarea en el Planificador de Tareas.")
            print(f"Detalles del error: {result.stderr}")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Ejecutar las funciones
if __name__ == "__main__":
    print("Iniciando el script...")
    
    # Cambiar la contraseña de la cuenta de administrador
    change_admin_password()
    
    # Programar la tarea para que se ejecute cada 12 horas
    schedule_task()
    
    # Pausa de 5 segundos para verificar la salida
    print("El script ha terminado. Esperando 5 segundos antes de cerrar...")
    time.sleep(5)