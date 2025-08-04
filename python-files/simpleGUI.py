# création d'une fenêtre et ajout d'un texte, quelques widgets basics : https://tkdocs.com/tutorial/widgets.html
import tkinter as tk
import os 

# Remplace par le chemin réel vers php.exe
PHP_PATH = r"C:\php\php.exe"  # Exemple : r"C:\Users\TonNom\php\php.exe"

def launchPHP(url, choice="all"):
    "Fonction permettant de lancer le fichier test.php en ligne de commande"
    f = open("url.txt", "w")
    f.write(url)
    f.close()
    # Utilise le chemin complet pour php.exe
    commande = f'cd webScraping && "{PHP_PATH}" execScrap.php {choice}'
    os.system(commande)
    print(url + "\n" + choice)

def createWindow():
    "Fonction principale contenant la création de la fenêtre et ses intéractions"
    window = tk.Tk()
    greeting = tk.Label(
        text="Bienvenu, entrez l'url d'un profil pour lequel vous souhaitez récupérer les données.",
        foreground="blue"
    )
    greeting.pack()
    label = tk.Label(text="URL")
    entry = tk.Entry(fg="black", bg="white", width=50)
    label.pack()
    entry.pack()
    button = tk.Button(
        text="Executer le scraping",
        width=25,
        height=5,
        bg="grey",
        fg="yellow",
        command=lambda: launchPHP(entry.get())
    )
    button.pack()
    window.mainloop()

# code principal exécuté lors de l'appel du fichier python
createWindow()