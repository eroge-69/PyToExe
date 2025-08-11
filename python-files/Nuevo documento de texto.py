import os
import tkinter as tk
from tkinter import messagebox
import subprocess

def abrir_carpeta(ruta):
    if os.path.exists(ruta):
        subprocess.Popen(f'explorer "{ruta}"')
    else:
        messagebox.showerror("Error", "La ruta no existe o no está disponible.")

def main():
    root = tk.Tk()
    root.title("Selector de Carpeta")
    root.geometry("300x180")
    root.resizable(False, False)

    btn_manga = tk.Button(root, text="Manga", width=30, height=2, 
                          command=lambda: abrir_carpeta(r'D:\DANGER\jjjj\Hentai\Manga'))
    btn_manga.pack(pady=10)

    btn_vr = tk.Button(root, text="VR Background", width=30, height=2, 
                       command=lambda: abrir_carpeta(r'F:\Oculus\Support\oculus-dash\dash\assets\raw\textures\environment\the_void\VrEnverioment'))
    btn_vr.pack(pady=10)

    btn_salir = tk.Button(root, text="Salir", width=30, height=2, command=root.destroy)
    btn_salir.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
