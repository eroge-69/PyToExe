import tkinter as tk
from tkinter import messagebox
import random

class SorteoElegante:
    def __init__(self, root):
        self.root = root
        self.root.title("🎉 Sorteo Elegante")
        self.root.geometry("400x500")
        self.root.configure(bg="#2c3e50")

        self.numeros_sorteados = set()

        # Título
        tk.Label(root, text="Sorteo de Números", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)

        # Entrada de rango
        self.min_entry = self.crear_entrada("Desde:")
        self.max_entry = self.crear_entrada("Hasta:")

        # Botón de sorteo
        self.sortear_btn = tk.Button(root, text="Sortear", font=("Helvetica", 14), bg="#27ae60", fg="white", command=self.iniciar_animacion)
        self.sortear_btn.pack(pady=20)

        # Resultado
        self.resultado_label = tk.Label(root, text="", font=("Helvetica", 80, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.resultado_label.pack(pady=20)

        # Lista de sorteados
        self.lista_label = tk.Label(root, text="Ya sorteados:", font=("Helvetica", 12), bg="#2c3e50", fg="#bdc3c7")
        self.lista_label.pack(pady=10)
        self.lista_text = tk.Text(root, height=8, width=30, bg="#34495e", fg="white", font=("Helvetica", 10))
        self.lista_text.pack()

    def crear_entrada(self, texto):
        tk.Label(self.root, text=texto, font=("Helvetica", 12), bg="#2c3e50", fg="white").pack()
        entry = tk.Entry(self.root, font=("Helvetica", 12))
        entry.pack(pady=5)
        return entry

    def iniciar_animacion(self):
        self.resultado_label.config(text="")
        self.contador = 3
        self.animar_cuenta_regresiva()

    def animar_cuenta_regresiva(self):
        if self.contador > 0:
            self.resultado_label.config(text=str(self.contador))
            self.contador -= 1
            self.root.after(700, self.animar_cuenta_regresiva)
        else:
            self.sortear()

    def sortear(self):
        try:
            minimo = int(self.min_entry.get())
            maximo = int(self.max_entry.get())
            if minimo > maximo:
                raise ValueError("El mínimo no puede ser mayor que el máximo.")

            posibles = set(range(minimo, maximo + 1)) - self.numeros_sorteados
            if not posibles:
                messagebox.showinfo("Fin del sorteo", "Ya se han sorteado todos los números.")
                return

            numero = random.choice(list(posibles))
            self.numeros_sorteados.add(numero)
            self.lista_text.insert(tk.END, f"{numero}\n")
            self.animar_resultado(numero)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos.")

    def animar_resultado(self, numero, parpadeos=6):
        if parpadeos % 2 == 0:
            self.resultado_label.config(text=str(numero), fg="#f1c40f")
        else:
            self.resultado_label.config(text=str(numero), fg="#2c3e50")
        if parpadeos > 0:
            self.root.after(300, lambda: self.animar_resultado(numero, parpadeos - 1))
        else:
            self.resultado_label.config(fg="#f1c40f")

# Ejecutar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = SorteoElegante(root)
    root.mainloop()