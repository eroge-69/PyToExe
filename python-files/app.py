
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def pokreni_aplikaciju():
    def ucitaj_fajlove():
        files = filedialog.askopenfilenames(title="Odaberi fajlove")
        if files:
            tekst = "\n".join(files)
            rezultat["text"] = f"Učitani fajlovi:\n{tekst}"
        else:
            rezultat["text"] = "Nijedan fajl nije izabran."

    app = tk.Tk()
    app.title("ARINEX LIQUID")
    app.geometry("500x300")

    dugme = tk.Button(app, text="Učitaj fajlove", command=ucitaj_fajlove)
    dugme.pack(pady=20)

    rezultat = tk.Label(app, text="", wraplength=450, justify="left")
    rezultat.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    pokreni_aplikaciju()
