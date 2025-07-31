
import tkinter as tk
import pyautogui

def write_detalle():
    pyautogui.typewrite("DETALLE")

def write_mayor():
    pyautogui.typewrite("MAYOR")

def write_botella():
    pyautogui.typewrite("BOTELLA")

def write_lata():
    pyautogui.typewrite("LATA")

def write_dulce():
    pyautogui.typewrite("DULCE")

def write_torta():
    pyautogui.typewrite("TORTA")

root = tk.Tk()
root.title("Botones de Texto")
root.geometry("350x280")

btn_detalle = tk.Button(root, text="DETALLE", command=write_detalle, width=12, height=2, bg="#4CAF50", fg="white")
btn_mayor = tk.Button(root, text="MAYOR", command=write_mayor, width=12, height=2, bg="#2196F3", fg="white")
btn_botella = tk.Button(root, text="BOTELLA", command=write_botella, width=12, height=2, bg="#FFC107", fg="black")
btn_lata = tk.Button(root, text="LATA", command=write_lata, width=12, height=2, bg="#FF5722", fg="white")
btn_dulce = tk.Button(root, text="DULCE", command=write_dulce, width=12, height=2, bg="#9C27B0", fg="white")
btn_torta = tk.Button(root, text="TORTA", command=write_torta, width=12, height=2, bg="#E91E63", fg="white")

btn_detalle.grid(row=0, column=0, padx=10, pady=10)
btn_mayor.grid(row=0, column=1, padx=10, pady=10)
btn_botella.grid(row=1, column=0, padx=10, pady=10)
btn_lata.grid(row=1, column=1, padx=10, pady=10)
btn_dulce.grid(row=2, column=0, padx=10, pady=10)
btn_torta.grid(row=2, column=1, padx=10, pady=10)

root.mainloop()
