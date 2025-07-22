
import tkinter as tk
import time

def mise_a_jour_horloge():
    heure_actuelle = time.strftime('%H:%M:%S')
    label_heure.config(text=heure_actuelle)
    fenetre.after(1000, mise_a_jour_horloge)

fenetre = tk.Tk()
fenetre.title("Horloge Numérique")
fenetre.geometry("300x100")
fenetre.resizable(False, False)

label_heure = tk.Label(fenetre, font=('Helvetica', 40), fg='black')
label_heure.pack(expand=True)

mise_a_jour_horloge()
fenetre.mainloop()
