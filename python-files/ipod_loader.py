
import os
import shutil
from tkinter import Tk, filedialog, Button, Label, messagebox
from pathlib import Path

# Cambia esto si tu iPod no está en la unidad E:\
IPOD_DRIVE_LETTER = "E:"

# Subcarpeta típica del iPod donde se guardan los archivos de música
IPOD_MUSIC_FOLDER = os.path.join(IPOD_DRIVE_LETTER, "iPod_Control", "Music")

# Extensiones de audio permitidas
ALLOWED_EXTENSIONS = ['.mp3', '.m4a', '.aac']

def is_audio_file(file):
    return any(file.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def copy_files_to_ipod(files):
    if not os.path.exists(IPOD_MUSIC_FOLDER):
        messagebox.showerror("Error", f"No se encontró la carpeta {IPOD_MUSIC_FOLDER}")
        return

    for file in files:
        if not is_audio_file(file):
            continue
        try:
            filename = os.path.basename(file)
            dest_path = os.path.join(IPOD_MUSIC_FOLDER, filename)
            shutil.copy2(file, dest_path)
        except Exception as e:
            messagebox.showerror("Error al copiar", str(e))
            return

    messagebox.showinfo("Éxito", "Archivos copiados al iPod con éxito.")

def select_files():
    files = filedialog.askopenfilenames(title="Seleccionar música",
                                        filetypes=[("Archivos de audio", "*.mp3 *.m4a *.aac")])
    if files:
        copy_files_to_ipod(files)

def select_folder():
    folder = filedialog.askdirectory(title="Seleccionar carpeta de música")
    if folder:
        files = [str(p) for p in Path(folder).rglob("*") if is_audio_file(str(p))]
        if not files:
            messagebox.showwarning("Vacío", "No se encontraron archivos de audio válidos.")
            return
        copy_files_to_ipod(files)

# Interfaz gráfica simple
root = Tk()
root.title("Cargar música al iPod Nano 7")
root.geometry("300x160")

Label(root, text="Agregar música al iPod Nano 7", font=("Helvetica", 12)).pack(pady=10)
Button(root, text="Seleccionar archivos de música", command=select_files).pack(pady=5)
Button(root, text="Seleccionar carpeta de música", command=select_folder).pack(pady=5)

root.mainloop()
