#begin van de code
import time
import random
import tkinter as tk
import threading


def make_popup(text):
    popup = tk.Toplevel()
    popup.overrideredirect(True)  
    popup.attributes("-topmost", True)  
    popup.configure(bg="black")

    kleuren = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan", "magenta", "lime", "teal", "lavender", "brown"]
    random_kleur = random.choice(kleuren)

    # grootte en positie
    popup.geometry("300x100+100+100")

    label = tk.Label(popup, text=text, fg=random_kleur, bg="black", font=("Helvetica", 12, "bold"))
    label.pack(expand=True, padx=10, pady=10)

    popup.after(1500, popup.destroy)
#kleur en tekst van de pop-up
def show_popup(text):
    popup = tk.Toplevel()
    popup.title("error 404")
    popup.geometry(f"300x100+{random.randint(0, 1920)}+{random.randint(0, 1080)}")
    popup.configure(bg="black")
    popup.attributes("-topmost", True)

    kleuren = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan", "magenta", "lime", "teal", "lavender", "brown"]
    random_kleur = random.choice(kleuren)

    label = tk.Label(popup, text=text, fg=random_kleur, bg="black", font=("Arial", 12, "bold"))
    label.pack(expand=True, padx=10, pady=10)

#text pop-up
def loop():
    global root
    teksten = [
        "JE MAIL IS GEWIST!", "HAHA!", "SUKKEL!", "LOSER!", "1 HERSENCEL!",
        "WAAROM KLIK JE?", "ZELF GEDAAN", "CHROMOSOOM FOUTJE", "WOWOWOW", "LOL!", "KWIBUS!", "DAK DUIF", "LAMPENKAP", "SCHOBBEJAK", "KLOOTVIOOL", "STUMPERT", "KAKGARNAAL", "SLAPTAKJE","das pech, gegevens weg!","kwarkje","💀","FOSIEL","KAKERLAK","BURGERKING KROON", "WORM VOOR BREIN","DOM BLONDJE","AARDAPPEL","KAKKERKAK","FOUTJE KAN GEBEUREN","CHROMOSOOM VERZAMELAAR","KLEUTER","YOU ARE AN IDIOT!","TRIEST GEVALLETJE","OPLOSSING=LAPTOP WEG!","KOOP MAAR NIEUWE LAPTOP!"
    ]

    def spam():
        while True:
            text = random.choice(teksten)
            root.after(0, show_popup, text)
            time.sleep(0.0005)  

    threading.Thread(target=spam, daemon=True).start()

root = tk.Tk()
root.withdraw() 
loop()
root.mainloop()
# einde van de code