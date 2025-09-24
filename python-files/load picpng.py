from tkinter import *
# Création de la fenêtre principale
root = Tk()
root.title("Affichage d'une Image")
root.geometry("400x300")
photo = PhotoImage(file = "d:\\dd.png")
imgreduit = photo.subsample(20, 3)
lbl = Label(root,image=imgreduit)
lbl.pack()
root.mainloop()

# Lire adresse url
url = input("Saisir une url :")
# Lire le texte du lien hypertexte
text_lien = input("saisir le texte du lien")
# convert the url text to a link 
url = "<a href='"+ url + "'> " + text_lien + "</a>"
print(url)