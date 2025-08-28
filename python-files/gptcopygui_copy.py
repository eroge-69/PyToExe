import os
import tkinter as tk
from tkinter import filedialog, messagebox

def choose_source():
    filepath = filedialog.askopenfilename(title="Quelldatei auswählen")
    if filepath:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, filepath)

def choose_destination():
    filepath = filedialog.asksaveasfilename(title="Zieldatei auswählen")
    if filepath:
        destination_entry.delete(0, tk.END)
        destination_entry.insert(0, filepath)

def copy_file():
    source = source_entry.get()
    destination = destination_entry.get()
    
    if not os.path.isfile(source):
        messagebox.showerror("Fehler", "Die Quelldatei existiert nicht!")
        return
    if not destination:
        messagebox.showerror("Fehler", "Bitte wähle einen Zielpfad!")
        return
    
    # Windows copy Befehl
    command = f'copy "{source}" "{destination}"'
    result = os.system(command)
    
    if result == 0:
        messagebox.showinfo("Erfolg", "Datei erfolgreich kopiert!")
    else:
        messagebox.showerror("Fehler", "Datei konnte nicht kopiert werden.")

# GUI erstellen
root = tk.Tk()
root.title("Datei kopieren")

tk.Label(root, text="Quelldatei:").grid(row=0, column=0, padx=5, pady=5)
source_entry = tk.Entry(root, width=50)
source_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Durchsuchen", command=choose_source).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Zieldatei:").grid(row=1, column=0, padx=5, pady=5)
destination_entry = tk.Entry(root, width=50)
destination_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Durchsuchen", command=choose_destination).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Kopieren", command=copy_file).grid(row=2, column=1, pady=10)

root.mainloop()
