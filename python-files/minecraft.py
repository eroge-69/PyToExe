#feito em 8-8-25 - primeiro ano DS
import tkinter as tk
import random
import ctypes
import os

colors = ["#ff0000", "#0000ff", "#ff9100", "#29daa3", "#ff00f2", "#33ff00", "#f2ff00"]

#criação de janelas
def criar_janelas():
    for i in range(2**8):
        window = tk.Toplevel()
        rngcolors = random.randint(0, 6)
        window.configure(bg=f"{colors[rngcolors]}")
        rng_x = random.randint(90, 1800)
        rng_y = random.randint(120, 300)
        rng_resx = random.randint(20, 1800)
        rng_resy = random.randint(70, 800)
        window.geometry(f"{rng_resx}x{rng_resy}")
main_window = tk.Tk()
main_window.configure(bg="#2d2d86")
main_window.geometry("600x400")

#texto
label = tk.Label(
    main_window, 
    text="Você foi hackeado, que triste (muito triste)",
    font="20"
)
label.pack(pady=20)
label.configure(bg="#ff0000")

#botão
botao = tk.Button(
    main_window, 
    text="Clique aqui para remover todos o vírus do seu computador.",
    font="40",
    command=main_window.destroy
)
botao.pack(pady=40)

criar_janelas()
main_window.mainloop()