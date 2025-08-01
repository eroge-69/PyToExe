import tkinter as tk
from PIL import Image, ImageTk

def mostra_immagine():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='black')

    img = Image.open('immagine.jpg')  # Inserisci il tuo file!
    img = ImageTk.PhotoImage(img)

    label = tk.Label(root, image=img, bg='black')
    label.pack(expand=True)

    root.bind("<Escape>", lambda e: root.destroy())  # Esci premendo ESC
    root.mainloop()

# Dialogo in console
input("Ciao! Come ti senti oggi? ")
input("Hai mai sentito qualcosa di... strano? ")
input("Davvero? E se non fossi solo? ")

# Boom: sorpresa!
mostra_immagine()
