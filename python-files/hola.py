# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 20:19:52 2025

@author: grupoB
"""

import tkinter as tk
import time
import threading

def close_after_delay():
    time.sleep(60)
    root.destroy()

root = tk.Tk()
root.title("Mensaje educativo")
root.geometry("300x100")
root.resizable(False, False)

label = tk.Label(root, text="Recuerda pensar antes de actuar", font=("Arial", 14))
label.pack(expand=True)

# Evita que el usuario cierre la ventana manualmente
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Cierra la ventana después de 60 segundos en un hilo separado
threading.Thread(target=close_after_delay, daemon=True).start()

root.mainloop()