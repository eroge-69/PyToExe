import pyodbc
import tkinter as tk
from tkinter import messagebox
from datetime import date

# Connexion SQL Server
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=.;DATABASE=BD_POPCULTURE;Trusted_Connection=yes;')
cursor = conn.cursor()

def add_movie():
    id_movie = entry_id.get()
    note = entry_note.get() or None
    coup_coeur = 1 if var_coup.get() else 0
    first_time = 1 if var_first.get() else 0
    date_seen = entry_date.get() or None
    cursor.execute("""
        INSERT INTO SEEN_MOVIES (ID_MOVIE, NOTE, COUP_COEUR, DATE, FIRST_TIME)
        VALUES (?, ?, ?, ?, ?)
    """, id_movie, note, coup_coeur, date_seen, first_time)
    conn.commit()
    messagebox.showinfo("Succès", "Film ajouté !")

# Interface Tkinter
root = tk.Tk()
root.title("Ajouter un film")

tk.Label(root, text="ID Film").grid(row=0, column=0)
entry_id = tk.Entry(root)
entry_id.grid(row=0, column=1)

tk.Label(root, text="Note").grid(row=1, column=0)
entry_note = tk.Entry(root)
entry_note.grid(row=1, column=1)

tk.Label(root, text="Date (YYYY-MM-DD)").grid(row=2, column=0)
entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)

var_coup = tk.IntVar()
tk.Checkbutton(root, text="Coup de coeur", variable=var_coup).grid(row=3, column=0, columnspan=2)

var_first = tk.IntVar(value=1)
tk.Checkbutton(root, text="First time", variable=var_first).grid(row=4, column=0, columnspan=2)

tk.Button(root, text="Ajouter", command=add_movie).grid(row=5, column=0, columnspan=2)

root.mainloop()
