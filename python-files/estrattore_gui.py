
import tkinter as tk
import random

def estrai_numeri():
    numeri = random.sample(range(1, 91), 6)
    numeri.sort()
    risultato.set("Numeri estratti: " + ", ".join(map(str, numeri)))

app = tk.Tk()
app.title("Estrazione 6 Numeri")
app.geometry("300x150")
app.resizable(False, False)

risultato = tk.StringVar()
tk.Button(app, text="Estrai numeri", command=estrai_numeri).pack(pady=10)
tk.Label(app, textvariable=risultato, font=("Arial", 12)).pack()

app.mainloop()
