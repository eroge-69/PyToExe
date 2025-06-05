import tkinter as tk
import random

# Gewünschte Farben in einer Liste definieren
farben = ['red', 'green', 'blue', 'yellow', 'lightblue', 'orange']


# Hauptfenster erstellen
fenster = tk.Tk()
fenster.config(bg="white")
fenster.title("Matching Colors Game")


# Label erstellen
ausgabefeld = tk.Label(fenster, text = "Match the colors!")

# Buttons erstellen
button1 = tk.Button(fenster, text = "", width = 5)
button2 = tk.Button(fenster, text = "", width = 5)
button3 = tk.Button(fenster, text = "", width = 5)
button4 = tk.Button(fenster, text = "", width = 5)
neustartButton = tk.Button(fenster, text = "Neustart", width = 15)

# Teile platzieren mit grid
ausgabefeld.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
button1.grid(row = 1, column = 0, padx = 10, pady = 10)
button2.grid(row = 1, column = 1, padx = 10, pady = 10)
button3.grid(row = 2, column = 0, padx = 10, pady = 10)
button4.grid(row = 2, column = 1, padx = 10, pady = 10)
neustartButton.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10)

# Funktionen definieren
# Ändert die Buttonfarbe zufällig und überprüft, ob alle die gleiche Farbe haben
def button1_clicked():
    button1.config(bg = random.choice(farben)) 
    if hatGewonnen():
        ausgabefeld.config(text = "Gewonnen")

def button2_clicked():
    button2.config(bg = random.choice(farben)) 
    if hatGewonnen():
        ausgabefeld.config(text = "Gewonnen") 

def button3_clicked():
    button3.config(bg = random.choice(farben)) 
    if hatGewonnen():
        ausgabefeld.config(text = "Gewonnen")

def button4_clicked():
    button4.config(bg = random.choice(farben)) 
    if hatGewonnen():
        ausgabefeld.config(text = "Gewonnen")

# Deaktiviert die Buttons 1 bis 4
def buttonsDeaktivieren():
    button1.config(state=tk.DISABLED)
    button2.config(state=tk.DISABLED)
    button3.config(state=tk.DISABLED)
    button4.config(state=tk.DISABLED)

# Aktiviert die Buttons 1 bis 4
def buttonsAktivieren():
    button1.config(state=tk.NORMAL)
    button2.config(state=tk.NORMAL)
    button3.config(state=tk.NORMAL)
    button4.config(state=tk.NORMAL)

# Prüft, ob jeder Button die gleiche Farbe hat und deaktiviert dann die Buttons
def hatGewonnen():
    if button1.cget("bg") == button2.cget("bg") and button2.cget("bg") == button3.cget("bg") and button3.cget("bg") == button4.cget("bg"):
        buttonsDeaktivieren()
        return True
    else:
        return False

# Startet das Programm neu und aktiviert die Buttons wieder
def neustart():
    buttonsAktivieren()
    button1.config(bg = random.choice(farben))
    button2.config(bg = random.choice(farben))
    button3.config(bg = random.choice(farben))
    button4.config(bg = random.choice(farben))
    ausgabefeld.config(text = "Match the colors!")


# Buttons mit Funktionen verknüpfen
button1.config(command = button1_clicked)
button2.config(command = button2_clicked)
button3.config(command = button3_clicked)
button4.config(command = button4_clicked)
neustartButton.config(command = neustart)



# Zum Programmstart wird einmal die Neustartfunktion aufgerufen
neustart()






