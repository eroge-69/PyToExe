import tkinter as tk

# Fenster erstellen
root = tk.Tk()
root.title("Mein erstes Windows-Programm")
root.geometry("300x200")  # Breite x Höhe in Pixeln

# Funktion, die beim Klick ausgeführt wird
def hallo():
    tk.messagebox.showinfo("Hallo", "Willkommen in meinem Programm!")

# Messagebox-Import (sonst Fehler)
from tkinter import messagebox

# Button hinzufügen
button = tk.Button(root, text="Klick mich!", command=hallo)
button.pack(pady=50)

# Hauptschleife starten (Fenster anzeigen)
root.mainloop()