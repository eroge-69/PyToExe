import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Pasta do script
base_path = os.path.dirname(os.path.abspath(__file__))

# Procura a �nica subpasta
subfolders = [f.path for f in os.scandir(base_path) if f.is_dir()]
if len(subfolders) == 1:
    destino = subfolders[0]
else:
    destino = os.path.join(base_path, "Convertidos")
    os.makedirs(destino, exist_ok=True)

arquivos = []

def adicionar_arquivos():
    files = filedialog.askopenfilenames(title="Selecione arquivos de v�deo",
                                        filetypes=[("V�deos", "*.mkv *.avi *.mov *.flv *.wmv *.mp4")])
    for f in files:
        if f not in arquivos:
            arquivos.append(f)
            listbox.insert(tk.END, os.path.basename(f))

def converter():
    if not arquivos:
        messagebox.showwarning("Aviso", "Nenhum arquivo adicionado!")
        return
    for arquivo in arquivos:
        nome, _ = os.path.splitext(os.path.basename(arquivo))
        output = os.path.join(destino, nome + ".mp4")
        subprocess.run([
            "ffmpeg", "-i", arquivo, "-c:v", "libx264", "-crf", "23",
            "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "-y", output
        ])
    messagebox.showinfo("Conclu�do", f"Arquivos convertidos para {destino}!")
    arquivos.clear()
    listbox.delete(0, tk.END)

root = tk.Tk()
root.title("Conversor de V�deos para MP4")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_add = tk.Button(frame, text="Adicionar Arquivos", command=adicionar_arquivos)
btn_add.pack(fill=tk.X, pady=5)

listbox = tk.Listbox(frame, width=50)
listbox.pack(pady=5)

btn_convert = tk.Button(frame, text="Converter para MP4", command=converter)
btn_convert.pack(fill=tk.X, pady=5)

root.mainloop()
