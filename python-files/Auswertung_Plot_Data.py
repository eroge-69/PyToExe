import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, simpledialog

#Tkinter-Fenster initialisieren (ohne sichtbares Fenster)
root = tk.Tk()
root.withdraw()  # Das Hauptfenster verstecken

# Dateiauswahldialog öffnen
dateipfad = filedialog.askopenfilename(
    title="Wähle die Auswertedatei aus",
    filetypes=[("Alle Dateien", "*.*")]  # Optional: nur bestimmte Dateitypen
)

name_data = simpledialog.askstring("Input", "Name der Messung?")

# Datei einlesen
file_path = dateipfad
#file_path = '../../Test_Data/Messwerte_Ansicht.txt'
df = pd.read_csv(file_path, delimiter=';', header=None, names=['max_torque', 'avg_torque', 'avg_current'])

#print(df.head())
# Erstelle eine Figur mit 3 Unterplots (vertikal)
#fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Max Torque Plot
plt.subplot(311)
plt.plot(df['max_torque'])
plt.title('Max Torque')
plt.ylabel('Max Torque')
plt.grid(True)

# Avg Torque Plot
plt.subplot(312)
plt.plot(df['avg_torque'], color='orange')
plt.title('Average Torque')
plt.ylabel('Avg Torque')
plt.grid(True)

# Avg Current Plot
plt.subplot(313)
plt.plot(df['avg_current'], color='green')
plt.title('Average Current')
plt.xlabel('Loop')
plt.ylabel('Avg Current')
plt.grid(True)

# Layout anpassen
plt.suptitle(name_data)
plt.tight_layout()
plt.show()