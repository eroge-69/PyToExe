import tkinter as tk
from tkinter import messagebox
import os
import sys

# Permite encontrar archivos al empaquetar con PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # cuando es .exe
    except Exception:
        base_path = os.path.abspath(".")  # cuando es .py
    return os.path.join(base_path, relative_path)

class ZenixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zenix App")
        self.root.iconbitmap(resource_path("zenix.ico"))  # usa icono correctamente
        self.root.geometry("300x400")

        self.entry = tk.Entry(root, font=("Arial", 20), borderwidth=2, relief="solid")
        self.entry.pack(pady=10, padx=10, fill="both")

        buttons_frame = tk.Frame(root)
        buttons_frame.pack()

        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+'),
        ]

        for row in buttons:
            row_frame = tk.Frame(buttons_frame)
            row_frame.pack(expand=True, fill='both')
            for btn_text in row:
                btn = tk.Button(row_frame, text=btn_text, font=("Arial", 18), height=2, width=4, command=lambda txt=btn_text: self.click(txt))
                btn.pack(side="left", expand=True, fill='both', padx=2, pady=2)

        clear_btn = tk.Button(root, text="C", font=("Arial", 18), command=self.clear)
        clear_btn.pack(pady=5, padx=5, fill='x')

    def click(self, value):
        if value == "=":
            try:
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(result))
            except Exception as e:
                messagebox.showerror("Error", f"Error de cálculo: {e}")
        else:
            self.entry.insert(tk.END, value)

    def clear(self):
        self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZenixApp(root)
    root.mainloop()
