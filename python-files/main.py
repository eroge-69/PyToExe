import subprocess
import tkinter as tk

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Perfiles detectados en tu máquina
PERFILES = {
    "3055-A": "Default",
    "Perfil 1": "Profile 4"
}

def abrir_perfil(nombre):
    perfil = PERFILES[nombre]
    subprocess.Popen([EDGE_PATH, f'--profile-directory={perfil}'])
    root.destroy()

# Interfaz gráfica
root = tk.Tk()
root.title("Seleccionar perfil de Edge")

for nombre in PERFILES:
    tk.Button(root, text=nombre, width=20, height=2,
              command=lambda n=nombre: abrir_perfil(n)).pack(pady=5)

root.mainloop()
