import tkinter as tk

from tkinter import messagebox
from login import Login
from carrusel import Carrusel

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inicio")
        self.geometry("750x500")

        contenedor = tk.Frame(self)
        contenedor.pack(side="top", fill="both", expand=True)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Login, Carrusel):
            nombrePagina = F.__name__
            frame = F(parent=contenedor, controller=self)
            self.frames[nombrePagina] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.cambiarPagina("Login")

    def cambiarPagina(self, nombrePagina):
        frame = self.frames[nombrePagina]
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()