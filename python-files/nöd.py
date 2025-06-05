import tkinter as tk
from tkinter import messagebox

def show_info():
    """Zeigt die Infobox mit dem Rick Astley Zitat an."""
    messagebox.showinfo("Info", "Never gonna give you up, never gonna let you down!")

# Hauptfenster erstellen
root = tk.Tk()
root.title("Menü mit Button")
root.geometry("300x150")  # Fenstergröße einstellen

# Button erstellen
press_button = tk.Button(root, text="Press It", command=show_info)
press_button.pack(pady=50)  # Button im Fenster platzieren, mit etwas Abstand nach oben/unten

# Hauptloop starten
root.mainloop()

