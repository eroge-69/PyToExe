import tkinter as tk
import time

def aggiorna_ora():
    ora_attuale = time.strftime("%H:%M:%S")
    etichetta_ora.config(text=ora_attuale)
    finestra.after(1000, aggiorna_ora)

finestra = tk.Tk()
finestra.title("Ora Corrente")
finestra.geometry("200x80")

etichetta_ora = tk.Label(finestra, font=("Helvetica", 24))
etichetta_ora.pack(expand=True)

aggiorna_ora()
finestra.mainloop()
