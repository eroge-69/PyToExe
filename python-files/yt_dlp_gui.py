import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def baixar_video():
    link = entrada_link.get().strip()
    if not link:
        messagebox.showwarning("Atenção", "Por favor, insira um link do YouTube.")
        return

    comando = f'start cmd /k ".\\yt-dlp.exe -f bv+ba/b {link}"'
    subprocess.Popen(comando, shell=True, cwd=os.path.dirname(__file__))

janela = tk.Tk()
janela.title("YT-DLP Downloader")
janela.geometry("400x120")

tk.Label(janela, text="Cole o link do YouTube abaixo:").pack(pady=10)
entrada_link = tk.Entry(janela, width=50)
entrada_link.pack(pady=5)
tk.Button(janela, text="Baixar", command=baixar_video).pack(pady=10)

janela.mainloop()
