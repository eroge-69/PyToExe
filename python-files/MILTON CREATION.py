from tkinter import *

# créer la fenêtre principale
fenetre = Tk()
fenetre.title('milton creation')
fenetre.geometry('1000x1000')
fenetre.configure(bg='green')

# créer la frame
Frame1 = Frame(fenetre, bg='green')
Frame1.pack(expand='yes')

# ajouter un label
label = Label(Frame1, text="bienvenu sur milton creation", font=("Courier", 30), bg='green', fg='white')
label.pack()

# 2e label
label_subtitle = Label(Frame1, text="bienvenu sur milton creation", font=("Courier", 15), bg='green', fg='white')
label_subtitle.pack()

# fonction pour ouvrir une nouvelle fenêtre
def ouvrir_nouvelle_fenetre():
    nouvelle_fenetre = Toplevel(fenetre)
    nouvelle_fenetre.title("Deuxième fenêtre")
    nouvelle_fenetre.geometry("600x800")
    nouvelle_fenetre.configure(bg='lightblue')

    label_nouvelle = Label(nouvelle_fenetre, text="Bienvenue dans la deuxième fenêtre !", font=("Arial", 20), bg='lightblue')
    label_nouvelle.pack(pady=50)

# bouton pour ouvrir la nouvelle fenêtre
bouton = Button(Frame1, text="Aller à l'autre fenêtre", command=ouvrir_nouvelle_fenetre, font=("Courier", 20), bg='white', fg='green')
bouton.pack(pady=30)

# lancer la fenêtre
fenetre.mainloop()