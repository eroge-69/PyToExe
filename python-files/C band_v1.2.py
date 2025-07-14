import tkinter as tk
from tkinter import ttk
from math import pi

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculo Banda C")
        self.geometry("400x200+0+0")
        self.configure(bg='#0b779c')

        # Variables de control
        self.largo = tk.DoubleVar(value=5925.0)
        self.alto = tk.DoubleVar(value=3700.0)
        self.imc_resultado = tk.StringVar(value="_____")

        self.volumenlts = tk.DoubleVar(value=0.0)



        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        # Etiqueta y entrada para peso
        lbl_largo = ttk.Label(self, text="Frecuencia de Tx (MHz):", background='#0b779c')
        lbl_largo.place(x=50, y=50)

        entry_largo = ttk.Entry(self, textvariable=self.largo, width=10)
        entry_largo.place(x=190, y=50)

        # Etiqueta y entrada para altura


        # Botón de cálculo
        btn_calcular = ttk.Button(self, text="Frec. Analizador (MHz):", command=self.calcular_imc)
        btn_calcular.place(x=50, y=100)

        # Etiqueta de resultado
        self.lbl_resultado = ttk.Label(self,
                                       text="_____",
                                       background='#EEE',
                                       font=('Arial', 15),
                                       anchor='center')
        self.lbl_resultado.place(x=190, y=100, width=80, height=30)







    def calcular_imc(self):
        try:
            largo = self.largo.get()
            alto = self.alto.get()
            im = largo-2225
            imc= 5150-im
            imc_redondeado = imc









            self.lbl_resultado.configure(text=str(imc_redondeado))



        except Exception as e:
            self.lbl_resultado.configure(text="Error", background='#EEE')








if __name__ == "__main__":
    app = Application()
    app.mainloop()

