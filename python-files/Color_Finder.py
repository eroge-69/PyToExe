import keyboard
import pyautogui
import tkinter
from PIL import ImageGrab

dico_col={"Black" : (82, 82, 82),"Dark Grey" : (118, 118, 118),"Grey" : (154, 154, 154),"Light Grey" : (208, 208, 208),"White" : (235, 235, 235),"Deep Red" : (139, 82, 96),"Red" : (224, 98, 103),"Orange" : (235, 158, 105),"Gold" : (229, 184, 87),"Yellow" : (231, 214, 117),"Light Yellow" : (235, 232, 194),"Dark Green" : (90, 193, 144),"Green" : (93, 220, 155),"Light Green" : (163, 235, 138),"Dark Teal" : (89, 159, 148),"Teal" : (91, 186, 181),"Light Teal" : (93, 217, 196),"Dark Blue" : (106, 130, 176),"Blue" : (120, 170, 218),"Cyan" : (139, 230, 227),"Indigo" : (146, 130, 229),"Light Indigo" : (173, 188, 232),"Dark Purple" : (154, 89, 173),"Purple" : (184, 115, 193),"Light Purple" : (216, 177, 231),"Dark Pink" : (203, 82, 155),"Pink" : (223, 100, 158),"Light Pink" : (227, 166, 183),"Dark Brown" : (144, 124, 113),"Brown" : (171, 144, 107),"Beige" : (230, 188, 153),}

pyautogui.PAUSE=0.001
pyautogui.MINIMUM_DURATION=0.0
def update_position():
    x, y = pyautogui.position()
    image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    color = image.getpixel((0, 0))
    color_label.config(text=f"couleur : {color}")
    position_label.config(text=f"Position : x = {x}, y = {y}")

    #cas d'arret
    if keyboard.is_pressed('x'):
        killer()

    #check couleur
    if keyboard.is_pressed('c'):
        copy_color()
    root.after(50, update_position)

def killer():
    exit()

def copy_color():
    x, y = pyautogui.position()
    image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    color = image.getpixel((0, 0))
    display_color_label.config(text=f"unknown")
    for col,code in dico_col.items():
        if color == code:
            display_color_label.config(text=f"{col}")

#fenetre
root = tkinter.Tk()
root.title("Détecteur de couleur")
root.geometry("300x150")

instruction = tkinter.Label(root, text="'c' pour copier, 'k' pour killer", font=("Arial", 12), fg="grey")
instruction.pack(pady=0)

#affichage couleur et pos curseur
color_label = tkinter.Label(root, text="", font=("Arial", 12))
color_label.pack(pady=0)
position_label = tkinter.Label(root, text="", font=("Arial", 12))
position_label.pack(pady=0)

display_color_label = tkinter.Label(root, text="", font=("Arial", 12))
display_color_label.pack(pady=0)

#mise à jour
update_position()

# Lancer la boucle principale
root.mainloop()
