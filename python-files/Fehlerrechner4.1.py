import tkinter as tk
import numpy as np

#Fenster
root = tk.Tk()
root.title("Fehlerrechner3.1")

#Platzhalter für add_row
button_add_row = None

#Button Commands
#Addition
def mean_command():
    result = 0
    for e in entries:
        values = [float(e.get("1.0", "end").strip()) for e in entries]
        array = np.array(values)
        mean = np.mean(array)
        variance = np.var(array, ddof=1)
        standard = np.std(array, ddof=1)
        meanerror = standard/np.sqrt(len(array))
    mean_label.config(text=f"Mittelwert ⟨·⟩: {mean}")
    variance_label.config(text=f"Varianz σ²: {variance}")
    standard_label.config(text=f"Standardabweichung σ: {standard}")
    mean_error_label.config(text=f"Mittelfehler σ: {meanerror}")
#Zeile hinzufügen
def add_row():
    entry = tk.Text(table_frame, width=15, height=1, relief="solid", borderwidth=1)
    entry.pack(padx=10, pady=5, before=button_add_row)
    entries.append(entry)
#Zeile Entfernen
def remove_row():
    entry = entries.pop()
    entry.destroy()  


#Tabelle
table_frame = tk.LabelFrame(root, text="Tabelle", padx=75, pady=10)
table_frame.pack(padx=10, pady=10)

#Ergebnis Frame
solution_frame = tk.LabelFrame(root, text="Ergebnisse", padx=40, pady=10)
solution_frame.pack(padx=10, pady=10)

#Eingabe
entries = []
for _ in range(2):
    add_row()

#Hinzufügen Button
button_add_row = tk.Button(table_frame, text="Zeile hinzufügen", width=14, height=1, command=add_row)
button_add_row.pack(pady=10)

#Entfernen Button
button_remove_row = tk.Button(table_frame, text="Zeile entfernen", width=14, height=1, command=remove_row)
button_remove_row.pack(pady=(0, 10))

#Ergebnis_Button
solution_button = tk.Button(solution_frame, text="Berechnen", width=14, height=1, command=mean_command)
solution_button.pack(pady=(0, 10))

#Mittelwert
mean_label = tk.Label(solution_frame, text="Mittelwert ⟨·⟩: -", width=30, height=2, relief="solid", borderwidth=1, anchor="w")
mean_label.pack(pady=10)

#Varianz
variance_label = tk.Label(solution_frame, text="Varianz σ²: -", width=30, height=2, relief="solid", borderwidth=1, anchor="w")
variance_label.pack(pady=10)

#Standardabweichung
standard_label = tk.Label(solution_frame, text="Standardabweichung σ: -", width=30, height=2, relief="solid", borderwidth=1, anchor="w")
standard_label.pack(pady=10)

#Statistischer Fehler des Mittelwertes
mean_error_label = tk.Label(solution_frame, text="Mittelfehler σ: -", width=30, height=2, relief="solid", borderwidth=1, anchor="w")
mean_error_label.pack(pady=10)

root.mainloop()