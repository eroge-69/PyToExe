import tkinter as tk
from PIL import Image, ImageTk
import glob
import os
print("                                                                    ")
print(" ██████╗ ██╗██████╗  █████╗ ████████╗███████╗                       ")
print(" ██╔══██╗██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝                       ")
print(" ██████╔╝██║██████╔╝███████║   ██║   █████╗                         ")
print(" ██╔═══╝ ██║██╔══██╗██╔══██║   ██║   ██╔══╝                         ")
print(" ██║     ██║██║  ██║██║  ██║   ██║   ███████╗                       ")
print(" ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝                       ")
print("                                                                    ")
print(" ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ ")
print(" ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗")
print(" ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝")
print(" ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗")
print(" ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║")
print(" ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝")
print("                                                                    ")
print(" Currently running version 0.4.0 Uncompiled                         ")
print(" (please do not close this window until your game launched)         ")

def launch_game(relative_path, game_name):
    full_path = os.path.join(os.path.dirname(__file__), relative_path)
    if os.path.exists(full_path):
        print(f"\n     Lancement de {game_name}")
        print(f"     Bonne partie moussaillon !")
        os.startfile(full_path)
    else:
        print(f"\n        Erreur : {game_name} introuvable !")
        print(f"        Fichier ciblé : {relative_path}")
        print("     Vérifiez:")
        print("         Que le fichier .lnk renvoie au bon endroit")
        print("         Que le fichier de jeu est présent à cet endroit")
        print("         Que le jeu fonctionne depuis ce fichier de jeu")

games = {}
shortcuts_folder = os.path.join(os.path.dirname(__file__), "Shortcuts")

for lnk_path in glob.glob(os.path.join(shortcuts_folder, "*.lnk")):
    name = os.path.splitext(os.path.basename(lnk_path))[0] 
    rel_path = os.path.relpath(lnk_path, os.path.dirname(__file__)) 
    games[name] = rel_path

root = tk.Tk()
root.title("Pirate launcher 0.4.0")
root.geometry("1000x600")

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

nb_colonnes = 6
ligne = 0
colonne = 0

images = {}

for name, rel_path in games.items():
    frame = tk.Frame(scrollable_frame)

    icon_path = os.path.join(os.path.dirname(__file__), "Icons", f"{name}.png")
    if os.path.exists(icon_path):
        img = Image.open(icon_path).resize((64, 64))
        img_tk = ImageTk.PhotoImage(img)
        images[name] = img_tk
        img_label = tk.Label(frame, image=img_tk)
        img_label.pack()
    else:
        img_label = tk.Label(frame, text="aucune image")
        img_label.pack()

    btn = tk.Button(frame, text=name, width=20, height=2, command=lambda p=rel_path, n=name: launch_game(p, n))
    btn.pack()

    frame.grid(row=ligne, column=colonne, padx=5, pady=5)

    colonne += 1
    if colonne >= nb_colonnes:
        colonne = 0
        ligne += 1


root.mainloop()