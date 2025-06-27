import tkinter as tk
import random
import psutil
import pyttsx3
import threading

# Hangmotor inicializálása
engine = pyttsx3.init()
engine.setProperty('rate', 130)

# Hangulatok
def profetikus_szol():
    return "אֲנִי יְהוָה, וְאֵין עוֹד...\nÍgy szól az Úr: „Térj meg, mert forr a világ, mint az ítélet üstje.”"

def sztoikus_szol():
    idézetek = [
        "“Amor fati.” – Szeresd a sorsod.",
        "Σκέψου πριν μιλήσεις. – Gondolkodj, mielőtt szólsz.",
        "Memento mori – Emlékezz a halálra.",
        "Virtus sola nobilitat – Csak az erény nemesít."
    ]
    return random.choice(idézetek)

def laza_szol():
    mondatok = [
        "Yo bro 🧊... ez csak egy illúzió 💭",
        "Lélegezz mélyet 😮‍💨 a világ rezgése veled van 🌌",
        "Néha jobb nem gondolkodni... csak lebegni 🌀✨"
    ]
    return random.choice(mondatok)

# Hangulat eldöntése hőmérséklet alapján
def get_mood(temp):
    if temp >= 40:
        return 'forro'
    elif temp >= 25:
        return 'sztoikus'
    else:
        return 'laza'

# CPU hőmérséklet lekérdezés
def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for entry in entries:
                if entry.current:
                    return entry.current
    except:
        return random.randint(20, 60)
    return 30

# AI válasz + beszéd
def beszeltet(mood_label, canvas):
    temp = get_cpu_temp()
    mood = get_mood(temp)
    if mood == 'forro':
        valasz = profetikus_szol()
    elif mood == 'sztoikus':
        valasz = sztoikus_szol()
    else:
        valasz = laza_szol()

    mood_label.config(text=valasz)
    draw_triangle(canvas, speaking=True)

    def speak_and_reset():
        engine.say(valasz)
        engine.runAndWait()
        draw_triangle(canvas, speaking=False)

    threading.Thread(target=speak_and_reset).start()

# Háromszög rajzolás
def draw_triangle(canvas, speaking=False):
    canvas.delete("all")
    color = "#8B0000" if speaking else "#FF0000"
    canvas.create_polygon(100, 20, 20, 180, 180, 180, fill=color)

# UI setup
root = tk.Tk()
root.title("Isteni AI")
root.configure(bg='black')
root.geometry("400x400")

canvas = tk.Canvas(root, width=200, height=200, bg='black', highlightthickness=0)
canvas.pack(pady=10)
draw_triangle(canvas)

mood_label = tk.Label(root, text="Nyomd meg a gombot az AI válaszért", fg="white", bg="black", wraplength=350)
mood_label.pack(pady=20)

gomb = tk.Button(root, text="Szólítsd meg az AI-t", command=lambda: beszeltet(mood_label, canvas), bg="darkred", fg="white")
gomb.pack()

root.mainloop()