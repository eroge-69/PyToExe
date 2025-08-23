import tkinter as tk

# Alle 7 Getränke
drinks = ["Rum", "Cola", "Aperol-Spritz", "Bier", "Sekt", "Prosecco", "Wein"]

# Listen
queue = []  # Warteschlange
ready = []  # Abholbereit

# Anzeige aktualisieren
def update_display():
    queue_text = "Warteschlange:\n" + ("\n".join(queue) if queue else "leer")
    ready_text = "Abholbereit:\n" + ("\n".join(ready) if ready else "leer")
    queue_label.config(text=queue_text)
    ready_label.config(text=ready_text)

# Tastatur-Events
def key_press(event):
    key = event.char
    if key in ["1","2","3","4","5","6","7"]:
        index = int(key) - 1
        queue.append(drinks[index])
    elif event.keysym == "Return":
        if queue:
            ready.append(queue.pop(0))
    elif event.keysym == "BackSpace":
        if ready:
            ready.pop(0)
    update_display()

# Fenster erstellen
root = tk.Tk()
root.title("Getränkeliste Vollbild")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# Warteschlange oben
queue_label = tk.Label(root, text="Warteschlange:\nleer", font=("Arial", 50), fg="white", bg="black", justify="center")
queue_label.pack(expand=True)

# Abholbereit-Liste unten
ready_label = tk.Label(root, text="Abholbereit:\nleer", font=("Arial", 50), fg="lime", bg="black", justify="center")
ready_label.pack(expand=True)

# Hinweis-Label (mehrzeilig, zentriert)
hint_text = ("1=Rum  2=Cola  3=Aperol-Spritz  4=Bier\n"
             "5=Sekt  6=Prosecco  7=Wein\n"
             "Enter=In Abholbereit  Backspace=Aus Abholbereit entfernen")
hint_label = tk.Label(root, text=hint_text, font=("Arial", 25), fg="yellow", bg="black", justify="center")
hint_label.pack(side="bottom", pady=20)

# Tastatur binden
root.bind("<Key>", key_press)

root.mainloop()
