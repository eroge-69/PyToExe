import ctypes
import psutil
import tkinter as tk
from tkinter import messagebox

# Funci�n para intentar limpiar el Working Set de un proceso
def empty_working_set(pid):
    try:
        handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid) # PROCESS_ALL_ACCESS
        if handle:
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
    except Exception as e:
        # print(f"Error al limpiar PID {pid}: {e}") # Descomentar para depuraci�n
        pass # Ignorar errores para procesos que no se pueden limpiar
    return False

# Funci�n principal para limpiar memoria
def clean_memory():
    cleaned_count = 0
    total_processes = 0
    current_pid = psutil.Process().pid # PID del script actual

    for proc in psutil.process_iter(['pid', 'name', 'username']):
        total_processes += 1
        # Intentar limpiar solo procesos que no son del sistema y no son el propio script
        if proc.pid != current_pid and proc.username() and proc.username() == psutil.Process(current_pid).username():
            if empty_working_set(proc.pid):
                cleaned_count += 1
    
    # Mostrar mensaje de finalizaci�n
    messagebox.showinfo("Limpieza de Memoria", f"Se intent� limpiar el Working Set de {cleaned_count} procesos.")

# Crear la ventana de la interfaz gr�fica
root = tk.Tk()
root.title("Limpiador de Memoria RAM")
root.geometry("300x100") # Tama�o de la ventana
root.resizable(False, False) # Evitar que la ventana sea redimensionable

# Etiqueta de instrucci�n
label = tk.Label(root, text="Haz clic para liberar memoria RAM.")
label.pack(pady=10)

# Bot�n de limpieza
clean_button = tk.Button(root, text="Limpiar Memoria", command=clean_memory)
clean_button.pack(pady=5)

# Centrar la ventana al inicio (opcional)
root.update_idletasks()
x = root.winfo_x() + (root.winfo_width() // 2)
y = root.winfo_y() + (root.winfo_height() // 2)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (root.winfo_width() // 2)
y = (screen_height // 2) - (root.winfo_height() // 2)
root.geometry(f"+{x}+{y}")

# Iniciar el bucle principal de la interfaz gr�fica
root.mainloop()