
import subprocess
import os
import tkinter as tk
from tkinter import messagebox

def launch_minecraft():
    path = r"C:\Program Files (x86)\Minecraft Launcher\minecraft-launcher.exe"
    if os.path.exists(path):
        subprocess.Popen([path])
    else:
        messagebox.showerror("Error", "No se encontró el launcher de Minecraft.\nEdita el .exe para poner la ruta correcta.")

root = tk.Tk()
root.title("Pixel Client")
root.geometry("400x300")
root.configure(bg="#0b0c10")

# Logo (solo texto por ahora, puedes cambiarlo por una imagen si lo deseas)
label = tk.Label(root, text="PIXEL CLIENT", font=("Arial", 24), fg="#00ffff", bg="#0b0c10")
label.pack(pady=40)

# Botón de jugar
play_button = tk.Button(root, text="JUGAR", command=launch_minecraft, font=("Arial", 16), bg="#00ffff", fg="#0b0c10", padx=20, pady=10)
play_button.pack(pady=20)

root.mainloop()
