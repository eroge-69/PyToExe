import tkinter as tk

def disable_event():
    pass  # Ignorar el evento de cerrar ventana

root = tk.Tk()
root.title("Mensaje Importante")

# Deshabilitar el botón de cerrar (X)
root.protocol("WM_DELETE_WINDOW", disable_event)

# Evitar minimizar o cambiar tamaño
root.resizable(False, False)

# Crear etiqueta con el mensaje
label = tk.Label(root, text="intento de broma", font=("Arial", 20))
label.pack(padx=50, pady=50)

# Poner la ventana siempre encima
root.attributes("-topmost", True)

# Ejecutar ventana
root.mainloop()
