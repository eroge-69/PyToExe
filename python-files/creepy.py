import tkinter as tk
from PIL import Image, ImageTk
    label = tk.Label(root, image=img, bg='black')
    label.pack(expand=True)

    root.bind("<Escape>", lambda e: root.destroy())  # Esci premendo ESC
    root.mainloop()

# Dialogo in console
input("Ciao! Come ti senti oggi? ")
input("Hai mai sentito qualcosa di... strano? ")
input("Davvero? E se non fossi solo? ")
input("Ne sei sicuro? ")
import time
nome_utente = "Mattilfanta14"
print(f"{nome_utente}, sicuro sicuro?")
time.sleep(1.5)
print("...")
time.sleep(1.5)
print("Ultima possibilità per tornare indietro.")
input("Premi INVIO per scoprire la verità...")
ù