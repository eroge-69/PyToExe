# Dieses Programm ist ein Generator
# Version 1.0 03.08.2025
# nach test.xml

# tkinter GUI
import tkinter as tk

# Definition der Variablen
dienst = ''
ausgabestring = ''
nato = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot',
        'golf', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike',
        'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango',
        'uniform', 'victor', 'whiskey', 'xray', 'yankee', 'zulu']

# Berechnung und Ausgabe
def funktion(dienst):
    dienst = eingabe.get()
    dienst=dienst.lower()

    # Berechnung
    i = 0
    laenge = len(dienst)

    if laenge < 4:
        laenge = len(dienst) - 1
    else:
        laenge = 3

    while i < 26:
        nator = nato[i]
        if nator[0] == dienst[laenge]:
            i = 26
            nator = nator[0] + nator[1].upper() + nator[2:]
        else:
            i = i + 1

    labelausgabe2.config(text='Ka..' + nator + '?fEr2!0' + dienst[0])


# Fenster erstellen 600x240 Pixel
window = tk.Tk()
window.geometry("600x240")
window.title("Ausgabe")

# Eingabefelder
labeleingabe = tk.Label(window, bg='orange', text="Dienstnamen eingeben:")
labeleingabe.place(x=100,y=100, width=200, height=20)
eingabe = tk.Entry(window)
eingabe.place(x=300,y=100, width=200, height=20)
window.bind("<Return>", funktion)

#Ausgabefelder
labelausgabe1 = tk.Label(window, bg='orange', text="Ausgabe:")
labelausgabe1.place(x=100,y=120, width=200, height=20)
labelausgabe2 = tk.Label(window, bg='lightgray', text='')
labelausgabe2.place(x=300,y=120, width=200, height=20)
window.mainloop()
